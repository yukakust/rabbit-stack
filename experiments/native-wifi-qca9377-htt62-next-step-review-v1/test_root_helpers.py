"""Pure function extraction; no imports of routes/state/key/controller operations."""
import pathlib,ast,types,json,copy,struct,importlib.util,sys,hashlib,tempfile
ROOT=pathlib.Path(__file__).resolve().parent;REPO=ROOT.parents[1];RTE=REPO/'experiments/native-wifi-qca9377-htt62-root-route-v1';OBS=REPO/'experiments/native-wifi-qca9377-htt62-observer-v2'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sys.path.insert(0,str(OBS));d=mod('rootreview_decode',OBS/'decode_htt.py');sys.modules['decode_htt']=d;f=mod('rootreview_fixture',OBS/'fixtures.py')
def extract(path,names,env):
 tree=ast.parse(path.read_text());tree.body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names];assert len(tree.body)==len(names);exec(compile(tree,str(path),'exec'),env);return env
x=extract(RTE/'classify_htt62.py',{'no_fixture','capture_from_logs'},{'json':json,'gate':types.SimpleNamespace(need=need),'decode':d});y=extract(RTE/'continue62.py',{'progress'},{'json':json,'gate':types.SimpleNamespace(need=need)})
def main():
 raw=f.capture();raw.pop('fixture_kind');rows=[{'stage':s,'peripheral':d.PEER,'writes':0,'NSError_code':0,'NSError_domain':'','cached_value_possible':False} for s in ['services','characteristics','services','characteristics']]
 expected=[(0,0,0x2f,raw['status_hex'][0])]+[(1,i,0x80+i,v) for i,v in enumerate(raw['pages_hex'][0])]+[(2,0,0x2f,raw['status_hex'][1])]+[(3,i,0x80+i,v) for i,v in enumerate(raw['pages_hex'][1])]+[(4,0,0x2f,raw['status_hex'][2])]
 for stage,page,uuid,v in expected:rows.append({'stage':'read','peripheral':d.PEER,'writes':0,'NSError_code':0,'NSError_domain':'','cached_value_possible':False,'capture_stage':stage,'page':page,'expected':f'52414242-4954-4649-8000-{uuid:012X}','raw_hex':v,'raw_bytes':len(bytes.fromhex(v))})
 parse=lambda rr,cb:x['capture_from_logs'](json.dumps(rr), '\n'.join(json.dumps(v) for v in cb))
 assert parse(raw,rows)==raw;assert d.decode_capture(raw,f.CONTAINER.read_bytes())['version_only_pass'];checks=['exact63reads_shape_accepted']
 mutations=[('fixture_raw',lambda rr,cb:rr.update(fixture_kind='synthetic')),('fixture_row',lambda rr,cb:cb[4].update(model_capture=True)),('write',lambda rr,cb:cb[4].update(writes=1)),('peer',lambda rr,cb:cb[4].update(peripheral='OTHER')),('error',lambda rr,cb:cb[4].update(NSError_code=6)),('cached',lambda rr,cb:cb[4].update(cached_value_possible=True)),('wrong_uuid',lambda rr,cb:cb[5].update(expected='WRONG')),('wrong_phase',lambda rr,cb:cb[5].update(capture_stage=3)),('wrong_page',lambda rr,cb:cb[5].update(page=2)),('raw_bytes',lambda rr,cb:cb[5].update(raw_bytes=511)),('missing_callback',lambda rr,cb:cb.pop()),('swapped_callbacks',lambda rr,cb:cb.__setitem__(slice(5,7),cb[5:7][::-1])),('raw_json_mismatch',lambda rr,cb:cb[5].update(raw_hex='00'))]
 for name,mutation in mutations:
  rr,cb=copy.deepcopy(raw),copy.deepcopy(rows);mutation(rr,cb)
  try:parse(rr,cb)
  except (ValueError,KeyError,AssertionError):checks.append(name+'_rejected')
  else:raise AssertionError('tamper accepted:'+name)
 for name in ['unsupported_raw_major','status_raw_major_mismatch','VERSION_wrong_pipe','stale_completion_floor']:
  rr=copy.deepcopy(raw)
  if name=='stale_completion_floor':
   st=bytearray.fromhex(rr['status_hex'][0]);struct.pack_into('<I',st,8+13*4,11);rr['status_hex']=[st.hex()]*3
  elif name=='status_raw_major_mismatch':
   st=bytearray.fromhex(rr['status_hex'][0]);struct.pack_into('<I',st,8+8*4,2);rr['status_hex']=[st.hex()]*3
  else:
   pages=[bytes.fromhex(v) for v in rr['pages_hex'][0]];record=bytearray(b''.join(pages[:5]))
   if name=='unsupported_raw_major':record[56+8+2]=4
   else:struct.pack_into('<I',record,36,2)
   pages[:5]=[bytes(record[i:i+512]) for i in range(0,2104,512)];rr['pages_hex']=[[v.hex() for v in pages]]*2
  try:d.decode_capture(rr,f.CONTAINER.read_bytes())
  except ValueError:checks.append(name+'_rejected')
  else:raise AssertionError('invalidVERSION accepted:'+name)
 # A released but failed VERSION diagnostic remains capturable, never success.
 rr=copy.deepcopy(raw);st=bytearray.fromhex(rr['status_hex'][0]);struct.pack_into('<I',st,8,4);struct.pack_into('<I',st,12,7);rr['status_hex']=[st.hex()]*3;dec=d.decode_capture(rr,f.CONTAINER.read_bytes());assert dec['actual_released']==1 and dec['version_only_pass'] is False;checks.append('released_fault_never_version_success')
 code=(RTE/'classify_htt62.py').read_text();assert "base_runtime=bytes.fromhex('305d0171c3c2e296fdf00f82a01cc838d67c0a1f3ffa836a847f4f12770ce074')" in code and 'counter=61)' in code;checks.append('signature_base_exact_actual61')
 runs=ROOT/'runs';runs.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(dir=runs) as folder:
  session=pathlib.Path(folder);boot=bytearray(160);boot[:8]=b'QWBT0001';boot[128:]=bytes.fromhex('8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01');report={'sender_steps':[{'mode':'--send','exit_code':1,'chunk':2}]};log=[{'stage':'boot-read','NSError_code':0,'raw_bytes':160,'raw_hex':boot.hex(),'confirmed_floor':16},{'stage':'bounded-timeout','NSError_domain':'RabbitAssetObserver','NSError_code':1,'confirmed_floor':64}]
  path=session/'prefix-2-0.jsonl'
  def progress(rr,ll):path.write_text('\n'.join(json.dumps(v) for v in ll));return y['progress'](rr,session)
  assert progress(report,log)==2*65760+64;checks.append('only_real_sender_timeout_with_forward_RFCS_floor_shape')
  for name in ['disconnect','same_floor','wrong_sender_mode','wrong_timeout_domain','wrong_boot_digest']:
   rr,ll=copy.deepcopy(report),copy.deepcopy(log)
   if name=='disconnect':ll.insert(0,{'stage':'disconnected'})
   elif name=='same_floor':ll[-1]['confirmed_floor']=16
   elif name=='wrong_sender_mode':rr['sender_steps'][0]['mode']='--query'
   elif name=='wrong_timeout_domain':ll[-1]['NSError_domain']='CBErrorDomain'
   else:ll[0]['raw_hex']=(bytes(160)).hex()
   try:progress(rr,ll)
   except ValueError:checks.append('progress_'+name+'_rejected')
   else:raise AssertionError('unsafe resume shape accepted:'+name)
 report={'status':'READ-ONLY-ROOT62-CLASSIFIER-CALLBACK-REVIEW-PASS','fixture_kind':'synthetic-host-only','physical_admission':False,'checks':checks,'source_sha256':{str(p.relative_to(REPO)):h(p) for p in [pathlib.Path(__file__),RTE/'classify_htt62.py',RTE/'continue62.py',OBS/'decode_htt.py',OBS/'fixtures.py']},'device_operations':0,'state_operations':0,'key_accesses':0};(ROOT/'evidence/root-helper-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(checks),h(ROOT/'evidence/root-helper-tests.json'))
if __name__=='__main__':main()
