"""Verify existing public world bytes only; no signing/key loads or BLE."""
import argparse,json,struct
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from context import CREATOR,OWNER,WORLD,PACKAGE,load
from decode_prefix import need,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--world',type=Path,required=True);ap.add_argument('--source',type=Path,required=True);a=ap.parse_args()
 packet=a.world.read_bytes();source=load(a.source)
 need(sha(packet)==PACKAGE and struct.unpack_from('<I',packet,8)[0]==18,'actual immutable public world18')
 need(sha(json.dumps(source,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==WORLD,'actual original canonical source18')
 Ed25519PublicKey.from_public_bytes(bytes.fromhex(CREATOR)).verify(packet[-64:],packet[:-64])
 for key,signature,body in [(OWNER,packet[-64:],packet[:-64]),(CREATOR,bytes([packet[-64]^1])+packet[-63:],packet[:-64]),(CREATOR,packet[-64:],packet[:-65]+bytes([packet[-65]^1]))]:
  try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(signature,body)
  except InvalidSignature:pass
  else:raise ValueError('wrong-authority or corrupted existing public packet accepted')
 print(json.dumps({'status':'EXISTING-PUBLIC-WORLD18-CREATOR-AUTHORITY-PASS','world_sha256':PACKAGE,'world_source_sha256':sha(a.source.read_bytes()),'canonical_world_sha256':WORLD,'creator_public_hex':CREATOR,'runtime_owner_rejected':True,'tampered_signature_and_body_rejected':True,'signatures_created':0,'private_key_loads':0,'physical_verified':False},indent=2))
if __name__=='__main__':main()
