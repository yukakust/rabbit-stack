#!/usr/bin/env python3
"""Loopback-only UI adapter; text and speech transcripts use one Controller."""
import argparse
import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import ask_connected_world as flow
from world_control import Controller


class Server(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, controller, connection_path):
        super().__init__(('127.0.0.1', 0), Handler)
        self.controller = controller; self.token = secrets.token_hex(32); self.busy = threading.Lock()
        self.last_error = None; self.connection_path = connection_path
        connection_path.parent.mkdir(parents=True, exist_ok=True)
        flow.save(connection_path, {'url': f'http://127.0.0.1:{self.server_port}', 'token': self.token, 'pid': os.getpid()})
        connection_path.chmod(0o600)
        if controller.status()['active']: self.start_job('resume', {})

    def start_job(self, operation, data):
        if not self.busy.acquire(blocking=False): raise ValueError('Операция уже выполняется.')
        def run():
            try:
                self.last_error = None
                if operation == 'request': self.controller.execute(data['intent'], data.get('source', 'text'), data.get('id'))
                elif operation == 'restore': self.controller.execute('Восстановить сохранённую версию', restore=data['version'])
                elif operation == 'recover' or flow.read_json(self.controller.state_path).get('recovery_pending'):
                    result = flow.city_module('city_recovery').recover(self.controller.state_path,self.controller.private_path,
                                                                   dell_rebooted=operation=='recover',resume=operation!='recover')
                    if result['status'] != 'APPLIED': self.last_error = 'Восстановление пока не подтверждено. Продолжите сохранённую передачу.'
                else: self.controller.execute(resume=True)
            except Exception as error: self.last_error = str(error)
            finally: self.busy.release()
        threading.Thread(target=run, daemon=False).start()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass  # No tokens, user requests or private paths in HTTP logs.
    def send_json(self, code, value):
        body = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body))); self.send_header('Cache-Control', 'no-store')
        self.end_headers(); self.wfile.write(body)
    def authorized(self):
        if not secrets.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + self.server.token):
            self.send_json(403, {'error': 'Local controller authorization required'}); return False
        return True
    def do_GET(self):
        if not self.authorized(): return
        if self.path == '/health': self.send_json(200, {'ready': True, 'busy': self.server.busy.locked()}); return
        if self.path != '/status': self.send_json(404, {'error': 'unknown endpoint'}); return
        try:
            value = self.server.controller.status()
            value.update(busy=self.server.busy.locked(), server_error=self.server.last_error)
            self.send_json(200, value)
        except Exception as error: self.send_json(503, {'error': str(error)})
    def do_POST(self):
        if not self.authorized(): return
        if self.path not in ('/request', '/resume', '/restore', '/recover', '/shutdown'):
            self.send_json(404, {'error': 'unknown endpoint'}); return
        try:
            length = int(self.headers.get('Content-Length', '-1'))
            if not 0 < length <= 8192 or self.headers.get('Content-Type') != 'application/json':
                raise ValueError('bounded JSON body required')
            data = json.loads(self.rfile.read(length), object_pairs_hook=__import__('compile_world').unique_pairs)
            if type(data) is not dict: raise ValueError('object required')
            if self.path == '/request':
                if set(data) != {'id', 'intent', 'source'}: raise ValueError('request fields differ')
                self.server.controller.request_path(data['id'])
                if type(data['intent']) is not str or not 1 <= len(data['intent'].strip()) <= 4000 or data['source'] not in ('text', 'voice'):
                    raise ValueError('invalid request')
            elif self.path == '/restore':
                if set(data) != {'version'} or type(data['version']) is not str: raise ValueError('restore version required')
            elif self.path == '/recover':
                if set(data) != {'dell_rebooted'} or data['dell_rebooted'] is not True:
                    raise ValueError('explicit owner observation of Dell reboot required')
            elif data: raise ValueError('resume takes an empty object')
            if self.path == '/shutdown':
                if self.server.busy.locked(): raise ValueError('Дождитесь завершения текущей операции.')
                self.send_json(202, {'stopping': True})
                threading.Thread(target=self.server.shutdown, daemon=True).start(); return
            self.server.start_job(self.path[1:], data)
            self.send_json(202, {'accepted': True})
        except (ValueError, TypeError, KeyError) as error: self.send_json(409, {'error': str(error)})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state', type=Path, default=flow.ROOT / 'runs/text-world/state.json')
    p.add_argument('--private', type=Path, default=Path.home() / '.rabbit-owner/runtime.key')
    p.add_argument('--connection', type=Path, default=flow.ROOT / 'runs/text-world/control/server.json')
    a = p.parse_args(); server = Server(Controller(a.state, a.private), a.connection)
    try: server.serve_forever()
    finally: server.server_close()


if __name__ == '__main__': main()
