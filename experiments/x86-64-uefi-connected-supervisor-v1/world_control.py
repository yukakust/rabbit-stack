#!/usr/bin/env python3
"""Persistent text/voice requests, versions and shared checked world/native execution."""
import argparse
import copy
import json
import re
import tempfile
import traceback
import uuid
from pathlib import Path
import ask_connected_world as flow
import world_planner as planner
import engine_route as native


class Controller:
    def __init__(self, state_path=flow.ROOT / 'runs/text-world/state.json', private_path=Path.home() / '.rabbit-owner/runtime.key'):
        self.state_path = Path(state_path).resolve()
        self.private_path = Path(private_path)
        self.directory = self.state_path.parent / 'control'
        self.directory.mkdir(parents=True, exist_ok=True)
        self.journal_path = self.directory / 'journal.json'
        with flow.state_lock(self.state_path):
            state = flow.read_json(self.state_path); flow.current(state)
            if 'engine' not in state:
                state['engine'] = native.initialize_engine(state)
                state['native_pending'] = None; flow.save(self.state_path, state)
            if not self.journal_path.exists():
                flow.save(self.journal_path, {'schema_version': 1, 'requests': [], 'active': None,
                    'versions': [self.version('initial', 'Исходный мир', state)]})

    def version(self, identity, request, state):
        return {'id': identity, 'request': request, 'world': state['world'], 'world_sha256': state['world_sha256'],
                'package': state['package'], 'package_sha256': state['package_sha256'],
                'world_counter': state['counter'], 'native_counter': state['engine']['native_counter'],
                'background': state['engine']['background']}

    def request_path(self, identity):
        if not re.fullmatch('[0-9a-f]{32}', identity): raise ValueError('invalid request identity')
        return self.directory / identity / 'request.json'

    def status(self):
        state = flow.read_json(self.state_path); journal = flow.read_json(self.journal_path, 2 * 1024 * 1024)
        return {'schema_version': 1, 'world': {'counter': state['counter'], 'sha256': state['world_sha256']},
                'engine': {'background': state['engine']['background'], 'native_counter': state['engine']['native_counter']},
                'pending': bool(state['pending'] or state.get('native_pending') or state.get('recovery_pending')),
                'active': journal['active'] or ('city-recovery' if state.get('recovery_pending') else None),
                'city': flow.current(state).get('schema_version') in (4,5),
                'requests': [flow.read_json(self.request_path(i)) for i in journal['requests'][-100:]],
                'versions': journal['versions'][-100:]}

    def update(self, record, **fields):
        record.update(fields); flow.save(self.request_path(record['id']), record)

    def delivery_reason(self, state):
        directory = state.get('native_pending') or state['pending']
        if not directory: return 'Пакет отклонён; предыдущая версия сохранена.'
        report = flow.read_json(Path(directory) / 'report.json')
        reasons = {'RECOVERY-REQUIRED-RECEIVER-LOSS': 'Dell потерял уже подтверждённые данные или перезапустился. Повторная передача остановлена: нужно проверить состояние Dell.',
                   'RECEIVER-STATE-BLOCKED': 'На Dell другая активная операция или несовместимое состояние. Она сохранена; новая передача остановлена.',
                   'RECEIVER-APPLICATION-PENDING': 'Пакет получен полностью, но применение ещё не подтверждено.',
                   'INVALID-RECEIVER-STATUS': 'Ответ Dell не прошёл проверку. Изменение мира не подтверждено.'}
        return reasons.get(report['status'], 'Связь или результат применения пока не подтверждены. Сохранённую операцию можно продолжить без нового пакета.')

    def execute(self, intent=None, source='text', identity=None, plan=None, restore=None, resume=False):
        """One serialized operation; retries keep its identity and exact pending session."""
        with flow.state_lock(self.state_path):
            state = flow.read_json(self.state_path); journal = flow.read_json(self.journal_path, 2 * 1024 * 1024)
            if resume:
                identity = journal['active']
                if not identity: raise ValueError('no pending request')
                record = flow.read_json(self.request_path(identity))
            else:
                identity = identity or uuid.uuid4().hex
                path = self.request_path(identity)
                if path.exists(): return flow.read_json(path)  # Idempotent client retry, no replay.
                if journal['active'] or state['pending'] or state.get('native_pending') or state.get('recovery_pending'):
                    raise ValueError('finish the saved pending operation before a new request')
                if source not in ('text', 'voice') or type(intent) is not str or not 1 <= len(intent.strip()) <= 4000:
                    raise ValueError('request must contain1..4000 characters and text/voice source')
                path.parent.mkdir()
                record = {'schema_version': 1, 'id': identity, 'intent': intent.strip(), 'source': source,
                          'status': 'PLANNING', 'base_world_sha256': state['world_sha256'],
                          'engine_done': False, 'world_done': False, 'explanation': '', 'error': None}
                flow.save(path, record)
                journal['requests'].append(identity); journal['active'] = identity; flow.save(self.journal_path, journal)
            try:
                if not (self.request_path(identity).parent / 'plan.json').exists():
                    if restore:
                        plan = {'status': 'ready', 'explanation': 'Возвращаю сохранённую версию новым пакетом.',
                                'base_world_sha256': state['world_sha256'], 'objects': None, 'programs': None,
                                'inventory_assets': [], 'created_sprites': [], 'background': None,
                                'restore_version': restore, 'missing_capabilities': []}
                    plan = planner.parse_plan(json.dumps(plan)) if plan is not None else planner.propose(record['intent'], state, journal['versions'])
                    flow.save(self.request_path(identity).parent / 'plan.json', plan)
                else: plan = flow.read_json(self.request_path(identity).parent / 'plan.json')
                self.update(record, explanation=plan['explanation'])
                if plan['status'] == 'unsupported':
                    self.update(record, status='UNSUPPORTED', missing_capabilities=plan['missing_capabilities'])
                    journal['active'] = None; flow.save(self.journal_path, journal); return record
                directory = self.request_path(identity).parent
                if not (directory / 'candidate.json').exists():
                    if plan['restore_version']:
                        versions = [v for v in journal['versions'] if v['id'] == plan['restore_version']]
                        if len(versions) != 1: raise ValueError('unknown history version')
                        v = versions[0]; world = flow.read_json(v['world'], 2 * 1024 * 1024)
                        if flow.sha(flow.canonical(world)) != v['world_sha256'] or flow.sha(Path(v['package']).read_bytes()) != v['package_sha256']:
                            raise ValueError('saved history changed')
                        background = v['background']; provenance = [{'kind': 'restored-version', 'id': v['id']}]
                    else:
                        world, background, provenance = planner.compose(state, plan)
                    flow.save(directory / 'candidate.json', world)
                    self.update(record, background=background, candidate_sha256=flow.sha(flow.canonical(world)), provenance=provenance)
                world = flow.read_json(directory / 'candidate.json', 2 * 1024 * 1024)
                if flow.sha(flow.canonical(world)) != record['candidate_sha256']: raise ValueError('saved request candidate changed')
                if record['status'] == 'PLANNING' and not record.get('engine_done') and not record.get('world_done') and not state['pending'] and not state.get('native_pending') and \
                   record['candidate_sha256'] == state['world_sha256'] and record['background'] == state['engine']['background']:
                    self.update(record, status='UNCHANGED', explanation='Мир уже соответствует этой просьбе. Новое обновление не требуется.')
                    journal['active'] = None; flow.save(self.journal_path, journal); return record
                # Validate the ENTIRE requested data candidate before any engine effect/key access.
                if not record.get('candidate_checked'):
                    self.update(record, status='CHECKING-CANDIDATE')
                    check_path = directory / 'candidate.rup'
                    check_path.write_bytes(flow.compile_world(directory / 'candidate.json', state['counter'] + 1, flow.CREATOR))
                    flow.decode_package(check_path.read_bytes(), flow.PUBLIC)
                    checks = flow.check_world(check_path, self.state_path.parent / 'host-check')
                    self.update(record, candidate_checked=True, candidate_checks=checks)
                if not record['engine_done']:
                    if record['background'] != state['engine']['background']:
                        if state['engine'].get('family') in ('reviewed-city-v1','reviewed-city-v2'):
                            raise ValueError('city sky/ground must use city data; legacy background engine would remove city support')
                        self.update(record, status='CHECKING-ENGINE')
                        if not state.get('native_pending'):
                            native.prepare_engine(self.state_path, state, record['background'], self.private_path)
                        self.update(record, status='DELIVERING-ENGINE')
                        result = native.deliver_engine(self.state_path, state, self.private_path)
                        if result:
                            self.update(record, status='REJECTED' if result == 2 else 'PENDING', error=self.delivery_reason(state))
                            if result == 2: journal['active'] = None; flow.save(self.journal_path, journal)
                            return record
                    self.update(record, engine_done=True)
                if not record['world_done']:
                    if flow.sha(flow.canonical(world)) != state['world_sha256']:
                        self.update(record, status='CHECKING-WORLD')
                        if not state['pending']:
                            flow.prepare_world(self.state_path, state, record['intent'], world, plan)
                        self.update(record, status='DELIVERING-WORLD')
                        result = flow.deliver(self.state_path, state)
                        if result:
                            self.update(record, status='PENDING', error=self.delivery_reason(state)); return record
                    self.update(record, world_done=True)
                self.update(record, status='APPLIED', error=None, world_counter=state['counter'],
                            native_counter=state['engine']['native_counter'], receiver_reported_applied=True)
                if not any(v['id'] == identity for v in journal['versions']):
                    journal['versions'].append(self.version(identity, record['intent'], state))
                journal['active'] = None; flow.save(self.journal_path, journal)
                return record
            except Exception as error:
                # A request with possible radio effects remains resumable; never silently replace it.
                uncertain = bool(state['pending'] or state.get('native_pending') or record.get('engine_done') or record.get('world_done') or
                                 record['status'] in ('DELIVERING-ENGINE', 'DELIVERING-WORLD'))
                self.update(record, status='PENDING' if uncertain else 'FAILED', error=str(error))
                if not uncertain: journal['active'] = None; flow.save(self.journal_path, journal)
                (self.request_path(identity).parent / 'error.log').write_text(traceback.format_exc())
                return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('intent', nargs='?'); p.add_argument('--state', type=Path, default=flow.ROOT / 'runs/text-world/state.json')
    p.add_argument('--private', type=Path, default=Path.home() / '.rabbit-owner/runtime.key')
    p.add_argument('--status', action='store_true'); p.add_argument('--resume', action='store_true')
    p.add_argument('--restore'); p.add_argument('--source', choices=('text', 'voice'), default='text')
    p.add_argument('--plan', type=Path, help='saved strict plan; same checks and delivery')
    a = p.parse_args(); controller = Controller(a.state, a.private)
    if a.status:
        if a.intent or a.resume or a.restore or a.plan: p.error('--status does not execute a request')
        result = controller.status()
    else:
        result = controller.execute(a.intent or ('Восстановить версию ' + a.restore if a.restore else None),
                                    a.source, plan=flow.read_json(a.plan) if a.plan else None, restore=a.restore, resume=a.resume)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if a.status or result['status'] in ('APPLIED', 'UNSUPPORTED', 'UNCHANGED') else 1


if __name__ == '__main__': raise SystemExit(main())
