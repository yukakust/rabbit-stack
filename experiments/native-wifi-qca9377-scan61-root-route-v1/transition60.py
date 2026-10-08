"""Public-only exact60 verification and durable retirement; no key/radio APIs.

Caller owns the sole state lock. `fresh` accepts a zero-write Root observation
with receipt.log (RFS60 callback) and collector.jsonl (fixed60 --collect output).
`retire` requires independent exact61 candidate admission, not merely this proof.
"""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import struct
import sys
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OLD = REPO / 'experiments/native-wifi-qca9377-fullboot60-root-route-v1'
# Load the frozen60 implementation under a distinct module name; never replace a
# future scan61 launch module or edit frozen source.
sys.path.insert(0, str(OLD))
_spec = importlib.util.spec_from_file_location('_scan61_prior_launch60', OLD / 'launch.py')
prior60 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prior60)
prior = prior60.prior
flow, engine = prior60.flow, prior60.engine
need = prior60.t.need
NATIVE_PACKET = 'b12c2ee8ae3eac069adfc5b907b65f1b8edf442884e72510d3c9badd382b087e'
PAYLOAD = '3984d3f5d1c9a3c3540bf2ef00972bea52406a6f78edc56bd215507110668fd6'
BASE59 = 'eb38baaf0b8e2ee120290744a116d02c33ff7bf2f011a73e945a10e239d51e55'
PHYSICAL = OLD / 'evidence/physical60-fullboot-READY'
PHYSICAL_HASHES = {
 'QPFX.hex': '019f87fa515613144a968d0cfcc11da9c5eb1f42d0e70fe1ee33510e6b8b606e',
 'QWBT.hex': 'c09b1ec0d2ab2f828e8e124b94f5d830d6ba19ba92e89d0785f4bffeb039481e',
 'QWIN.hex': 'ed51a97c8a88f88a62ec8eed4a88286e0c20c1bf4c9685954942ed5625f27c8f',
 'QWOP.hex': '942a2eb48547add05e76338a091c4197425db3edda4e4d768d5c5e4561cb999f',
 'classification.json': '5e33b0457844d07c515d9e1294f8781e5ebd7f4991d0e4d68197496833fafa0d',
 'controller.log': '2189e1a4208c5213e0292e5a386c261b519741103e00594310c3be34ad4d660a',
 'monitor.jsonl': 'a2a39579256ccf6d10066acb2b158ba7240ac84d62b17268043f0b687a19dfd4',
}
PREFIX_FIELDS = '''generation prefix_phase prefix_reason stop_calls prefix_released stop_offset stop_submitted stop_completed stop_plan stop_io boot_phase boot_error plan_phase plan_error plan_offset plan_submitted plan_completed io_phase stage failed adapter_phase cleanup_slot held dma_users claimed access_count bus_owned boot_owns_pin asset_pinned irq_owned link_owned wake_owned reset_owned ble_state pending connected credits inflight stream_used stream_goal usb_polls usb_reads usb_timeouts usb_observation last_usb_status_lo last_usb_status_hi last_usb_result last_usb_bytes raw_count raw_overflow usb_fault frames max_poll_us max_qca_us started_lo started_hi last_lo last_hi'''.split()

def prefix(raw):
 need(len(raw) == 240 and raw[:8] == b'QPFX0001', 'exact QPFX240')
 fields = dict(zip(PREFIX_FIELDS, struct.unpack('<58I', raw[8:])))
 need(fields['generation'] == 60 and fields['prefix_phase'] == 3 and fields['prefix_reason'] == 0 and fields['prefix_released'] == 1 and fields['stop_calls'] == 1, 'checked actual60 release')
 need(fields['stop_submitted'] == fields['stop_completed'] == fields['plan_submitted'] == fields['plan_completed'] == 3114 and fields['stop_plan'] == fields['plan_phase'] == 20 and fields['boot_phase'] == fields['stage'] == 5 and fields['adapter_phase'] == 12 and fields['cleanup_slot'] == 14, 'full60 transport and all14 closure')
 need(not any(fields[k] for k in ('stop_io','boot_error','plan_error','io_phase','failed','held','dma_users','claimed','access_count','bus_owned','boot_owns_pin','asset_pinned','irq_owned','link_owned','wake_owned','reset_owned','raw_overflow','usb_fault')), 'remaining60 owner/error')
 return fields

def physical():
 for name, digest in PHYSICAL_HASHES.items():
  need(prior.sha(PHYSICAL / name) == digest, 'pinned physical60 changed: ' + name)
 fields = prefix(bytes.fromhex((PHYSICAL / 'QPFX.hex').read_text()))
 win = bytes.fromhex((PHYSICAL / 'QWIN.hex').read_text())
 need(len(win) == 244 and win[:8] == b'QWIN0002', 'exact owned QWIN0002')
 # The immutable exact bytes include the complete owned HTC/READY frame;
 # independently verify the frame rather than trusting classification booleans.
 frame = win[116:184]
 need(len(frame) == 68 and flow.sha(frame) == '0a1b20ca3e98a407251e307093d53f64a1625cc461e0e090dc5d65319c91275e', 'exact owned raw READY frame')
 need(frame[:8] == bytes.fromhex('01003c0000050000') and int.from_bytes(frame[8:12], 'little') == 2 and int.from_bytes(frame[12:16], 'little') == (35 << 16 | 52) and int.from_bytes(frame[16:20], 'little') == 0x01000000 and int.from_bytes(frame[20:24], 'little') == 574 and frame[40:46] == bytes.fromhex('c0b5d778c3fb') and frame[48:52] == b'\0' * 4, 'raw READY endpoint/event/TLV/ABI/MAC/status')
 need(struct.unpack('<8I', win[8:40]) == (2,0,4,0,1,2,1,1), 'actual INIT TX and READY completion')
 c = flow.read_json(PHYSICAL / 'classification.json')
 need(c['generation'] == 60 and c['WMI_READY'] is True and c['INIT_TX_completed'] is True and c['all14_owners_released'] is True and c['MAC'] == 'c0:b5:d7:78:c3:fb' and c['ABI_minor'] == 574 and c['SERVICE_READY_regdomain'] == 108 and c['SERVICE_READY_bands'] == [2312,2732,4920,6100] and c['memory_requests'] == 0, 'exact physical60 completion')
 return fields

def verify(s):
 policy, public, gate = prior60.current(s, prior60.CHECKED)
 need(s.get('hardware_trial_pending'), 'completed exact60 asset session required')
 d = Path(s['hardware_trial_pending'])
 r = flow.read_json(d / 'report.json')
 need(r['status'] == 'EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and r['completed_chunks'] == 12 and len(r['packets']) == 12 and r['policy'] == policy and r['gate'] == gate and r['native_counter'] == 60 and r['world_counter'] == 19 and r['native_payload_sha256'] == PAYLOAD and r['world_sha256'] == prior.SEMANTIC, 'actual full60 signed session')
 receipt = r['last_receipt']
 need(receipt['bitmap'] == 4095 and receipt['ready'] == 1 and receipt['action'] == 4 and receipt['peripheral'].upper() == prior.PEER, 'actual full60 accepted receipt')
 offset = 0
 for item in r['packets']:
  p = d / prior.safe(item['file'])
  decoded = prior60.t.assets.validate(p.read_bytes(), public)
  need(decoded == {k:v for k,v in item.items() if k != 'file'} and decoded['generation'] == 60 and decoded['offset'] == offset and decoded['asset_bytes'] == 751436, 'immutable exact60 asset signature/ordering')
  # Signed immutable metadata fixes exact offsets; the container is hash-bound.
  offset += min(65536, 751436 - offset)
 native = Path(s['engine']['last_release_report']).parent
 packet = (native / 'native.rrt').read_bytes()
 verified = engine.verify(packet, target=bytes.fromhex(prior.TARGET), owner=public, base_runtime=bytes.fromhex(BASE59), world=Path(s['package']).read_bytes(), counter=59)
 need(verified.counter == 60 and flow.sha(verified.payload) == PAYLOAD and flow.sha(packet) == NATIVE_PACKET, 'actual public60 signature on base59/world19')
 physical()
 return d, native

def observation_tools():
 """Public-only pinned helper/source provenance; never creates a manager."""
 reader = prior.REPO / 'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
 proof = flow.read_json(prior.ROOT / 'evidence/root-proof.json')
 reader_digest = proof['source_sha256'][str(reader.relative_to(prior.REPO))]
 need(prior.sha(reader) == reader_digest, 'frozen receipt reader changed')
 spec = importlib.util.spec_from_file_location('_scan61_fixed_collector60', OLD / 'collector_gate.py')
 module = importlib.util.module_from_spec(spec)
 spec.loader.exec_module(module)
 collector = module.checked()
 return {'receipt_reader_sha256':reader_digest, 'collector_sha256':prior.sha(collector),
         'observer_source_sha256':prior.sha(ROOT / 'observe60.py')}

def fresh(q, state):
 q = Path(q)
 r = flow.read_json(q / 'report.json')
 need(r.get('status') == 'ACTUAL60-RELEASE14-PRE61-OBSERVATION', 'actual observation status required')
 forbidden = ('fixture_kind','synthetic_only','mocked','test_clock','host_fixture')
 need(not any(key in r for key in forbidden), 'synthetic observation prohibited')
 tools = observation_tools()
 need(all(r.get(key) == digest for key,digest in tools.items()), 'actual observation helper/source provenance')
 need(type(r['writes']) is int and r['writes'] == 0 and r['state_sha256'] == flow.sha(state)
      and type(r['observed_at']) in (int,float) and 0 <= time.time() - r['observed_at'] <= 300, 'fresh unchanged actual60 context')
 for name in ('receipt.log','collector.jsonl'):
  need(prior.sha(q / name) == r['inputs'][name], 'fresh raw callback changed: ' + name)
 raw = prior60.t.raw_callback(q / 'receipt.log', 60)
 need(raw[:4] == b'RFS\1' and raw[20:24] == b'\2\0\0\0' and int.from_bytes(raw[24:28], 'little') == 60 and raw[28:].hex() == NATIVE_PACKET, 'physical60 still applied; no reset')
 rows = [json.loads(line) for line in (q / 'collector.jsonl').read_text().splitlines() if line.startswith('{')]
 need(bool(rows), 'fresh fixed60 collector callbacks absent')
 for row in rows:
  need(not any(key in row for key in forbidden), 'synthetic callback prohibited')
  need(type(row.get('writes')) is int and row['writes'] == 0 and row.get('peripheral','').upper() == prior.PEER
       and row.get('NSError_code') == 0 and not row.get('NSError_domain'), 'actual fixed60 read error/wrong peer/write')
 values = [row for row in rows if row.get('stage') == 'value-read']
 expected = ((240,b'QPFX0001'),(160,b'QWBT0001'),(488,b'QWOP0003'),(244,b'QWIN0002'))
 need(len(values) == 4, 'four ordered fixed60 values required')
 raw_values = []
 for row,(size,magic) in zip(values,expected):
  value = bytes.fromhex(row['raw_hex'])
  need(type(row.get('raw_bytes')) is int and row['raw_bytes'] == size and len(value) == size and value[:8] == magic, 'ordered fixed60 envelope size/magic')
  raw_values.append(value)
 fields = prefix(raw_values[0])
 boot = struct.unpack('<30I',raw_values[1][8:128])
 need(boot[0] == 5 and boot[1] == 0 and boot[2] == 20 and boot[3] == 0
      and boot[4] == boot[5] == 3114 and boot[18] == 5 and boot[19] == 0
      and boot[20] == 12 and boot[21] == 14 and boot[22] == 0, 'fresh full60 QWBT boot/plan/owners')
 win = raw_values[3]
 need(prior.sha(PHYSICAL / 'QWIN.hex') == PHYSICAL_HASHES['QWIN.hex'], 'frozen owned READY reference changed')
 frozen_win = bytes.fromhex((PHYSICAL / 'QWIN.hex').read_text())
 need(struct.unpack('<8I',win[8:40]) == (2,0,4,0,1,2,1,1)
      and win[116:184] == frozen_win[116:184], 'fresh actual60 INIT TX and exact owned READY frame')
 return fields

def inventory(d):
 d = Path(d)
 need(d.is_dir() and not d.is_symlink(), 'archive source must be real directory')
 paths = {}
 for p in d.rglob('*'):
  need(not p.is_symlink(), 'session symlink forbidden')
  if p.is_file(): paths[str(p.relative_to(d))] = prior.sha(p)
 return paths

def _sync_tree(directory):
 for p in directory.rglob('*'):
  if p.is_file():
   with p.open('rb') as handle: os.fsync(handle.fileno())
 for p in sorted([directory, *[p for p in directory.rglob('*') if p.is_dir()]], key=lambda p: len(p.parts), reverse=True):
  fd = os.open(p, os.O_RDONLY)
  try: os.fsync(fd)
  finally: os.close(fd)
 fd = os.open(directory.parent, os.O_RDONLY)
 try: os.fsync(fd)
 finally: os.close(fd)

def retire(state_path, s, q, candidate_admission):
 """Called only under caller's sole lock, after independent exact61 admission."""
 state_path, q = Path(state_path), Path(q)
 need(candidate_admission.get('native_counter') == 61 and candidate_admission.get('world_package_sha256') == prior.WORLD and candidate_admission.get('source_model_verified') is True, 'independent Root61 candidate gate required')
 before = state_path.read_bytes()
 need(flow.read_json(state_path) == s, 'unchanged actual state')
 assets_dir, native_dir = verify(s)
 fields = fresh(q, before)
 directory = ROOT / 'runs/retired60'
 need(not directory.exists(), 'retirement exists; inspect manifest, never overwrite')
 directory.mkdir(parents=True)
 manifests = {}
 for name, source in (('assets',assets_dir),('native',native_dir),('fresh-observation',q),('physical60-evidence',PHYSICAL)):
  expected = inventory(source)
  target = directory / name
  shutil.copytree(source,target)
  need(inventory(target) == expected and inventory(source) == expected, 'archive/original changed: ' + name)
  manifests[name] = expected
 (directory / 'before-state.json').write_bytes(before)
 report = {'status':'ACTUAL60-FULL-READY-MAC-RELEASE14-ARCHIVED','native_counter':60,'world_counter':19,'session':str(assets_dir),'inventory':manifests,'prior_state_sha256':flow.sha(before),'fields':fields,'new_candidate':candidate_admission,'native_packet_sha256':NATIVE_PACKET,'physical_evidence_hashes':PHYSICAL_HASHES,'reboot_command':False,'new_signatures':0}
 flow.save(directory / 'retirement.json',report)
 _sync_tree(directory)
 # All archived files, nested directories and parent directory are durable before
 # pending-state retirement. No original packet/log/proof is changed or removed.
 need(state_path.read_bytes() == before, 'state changed before retirement')
 for name,source in (('assets',assets_dir),('native',native_dir),('fresh-observation',q),('physical60-evidence',PHYSICAL)):
  need(inventory(source) == manifests[name] and inventory(directory / name) == manifests[name], 'source/archive changed before state transition')
 after = dict(s)
 after['hardware_trial_pending'] = None
 after['last_hardware_trial_retirement'] = str(directory / 'retirement.json')
 flow.save(state_path,after)
 return after,directory
