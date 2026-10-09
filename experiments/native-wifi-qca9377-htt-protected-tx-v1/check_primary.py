import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for original,h in json.loads((R/'frozen-inputs.json').read_text()).items():
 name=Path(original).name
 p=R/'references'/name if 'references' in Path(original).parts else R/'copied'/name
 assert sha(p)==h,(original,p)
s=(R/'references/htt.h').read_text();chunks=[]
for n in ['enum htt_data_tx_desc_flags0','enum htt_data_tx_desc_flags1','enum htt_data_tx_ext_tid','struct htt_data_tx_desc']:
 start=s.index(n+' {');end=s.index('};',start)+2 if n.startswith('enum') else s.index('} __packed;',s.index('u8 prefetch[0]',start))+len('} __packed;')
 chunks.append(s[start:end])
header=(R/'primary_htt.h').read_text()
for c in chunks:assert c.replace('htt_data_tx','peth_data_tx').replace('HTT_DATA_TX','PETH_DATA_TX') in header
s=(R/'references/wmi-tlv.c').read_text();start=s.index('static struct sk_buff *\nath10k_wmi_tlv_op_gen_vdev_set_param');end=s.index('\n}\n',start)+3
assert s[start:end] in (R/'primary_wmi_generator.h').read_text()
for name,file in [('wmi_tlv_grp_id','wmi-tlv.h'),('wmi_tlv_cmd_id','wmi-tlv.h'),('wmi_tlv_tag','wmi-tlv.h'),('wmi_tlv_vdev_param','wmi-tlv.h')]:
 s=(R/'references'/file).read_text();m=re.search(r'enum '+name+r'\s*\{.*?\};',s,re.S);assert m and m[0] in (R/'primary_wmi.h').read_text(),name
print('EXACT PINNED PRIMARY HEADER/FUNCTION AND FROZEN INPUT COPIES PASS')
