import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parent
def check():
 pin=json.loads((R/'references/pin.json').read_text())
 assert pin['linux_commit']=='6b5a2b7d9bc156e505f09e698d85d6a1547c1206'
 for name,v in pin['files'].items():assert hashlib.sha256((R/'references'/name).read_bytes()).hexdigest()==v['sha256'],name
 desc=(R/'references/rx_desc.h').read_text()
 bits={'PEER_IDX_INVALID':3,'PEER_IDX_TIMEOUT':4,'ENCRYPT_REQUIRED':24,'TKIP_MIC_ERR':28,'DECRYPT_ERR':29,'FCS_ERR':30,'MSDU_DONE':31}
 for name,bit in bits.items():assert re.search(r'RX_ATTENTION_FLAGS_'+name+r'\s*=\s*BIT\('+str(bit)+r'\)',desc),name
 rx=(R/'references/htt_rx.c').read_text()
 assert 'is_decrypted = (enctype != HTT_RX_MPDU_ENCRYPT_NONE &&' in rx
 assert '!has_fcs_err &&' in rx and '!has_crypto_err &&' in rx and '!has_peer_idx_invalid);' in rx
 assert 'skb_trim(msdu, msdu->len - FCS_LEN);' in rx
 assert 'if (status->flag & RX_FLAG_IV_STRIPPED)' in rx
 assert 'ath10k_htt_rx_h_mpdu(ar,&amsdu,status,false,NULL,NULL,peer_id,frag);' in re.sub(r'\s+','',rx)
 return {'primary_commit':pin['linux_commit'],'attention_bits':bits,'RAW_only':True,'full_reorder_INORD_fill_crypto_header':False,'HW_authentication_requires_official_live_firmware_bridge':True}
if __name__=='__main__':print(json.dumps(check(),indent=2))
