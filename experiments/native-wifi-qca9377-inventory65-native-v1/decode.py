"""Public diagnostic decoder. No key/credential/RNG/radio/state operations."""
import struct,hashlib,json
from pathlib import Path

def decode(first,second,rng_object_sha256,cpuid_source_sha256):
 if len(first)!=512 or len(second)!=448 or second[:4]!=b'QIC\x02' or second[4:36]!=hashlib.sha256(first).digest():raise ValueError('512/448 exact QIC2 integrity')
 raw=first+second[36:]
 u32=lambda o:struct.unpack_from('<I',raw,o)[0]
 u64=lambda o:struct.unpack_from('<Q',raw,o)[0]
 if len(raw)!=924 or raw[:8]!=b'QINV0065' or u32(8)!=1 or u32(12)!=924 or u64(16)!=65 or u32(24)!=256 or u32(28)!=352 or u32(32) or u32(36) or any(raw[72:80]) or any(raw[708:]):raise ValueError('exact diagnostic65 schema/epoch/reserved/CPU result')
 expected=bytes.fromhex(rng_object_sha256);cpu_source=bytes.fromhex(cpuid_source_sha256)
 if len(expected)!=32 or len(cpu_source)!=32 or raw[40:72]!=expected or raw[656:688]!=expected:raise ValueError('actual compiled RNG adapter provenance')
 cpu=raw[80:336]
 if cpu[:8]!=b'QRNG0001' or struct.unpack_from('<IIQ',cpu,8)!=(1,256,65) or cpu[24:56]!=cpu_source or any(cpu[236:256]):raise ValueError('CPU source/schema/no entropy/no MSR')
 flags,count=struct.unpack_from('<II',cpu,56)
 if flags&~15 or not 1<=count<=7:raise ValueError('CPU flags/count')
 rng=raw[336:688];phase,error,algorithms,owned,uncertain=struct.unpack_from('<IIIII',rng)
 if algorithms>16 or owned>1 or uncertain>1 or any(rng[20:24]) or any(rng[64+16*algorithms:320]):raise ValueError('bounded algorithms/owner/reserved')
 cleanup,after_owned,after_uncertain,closed=struct.unpack_from('<IIII',raw,692)
 if any(x>1 for x in (cleanup,after_owned,after_uncertain,closed)) or closed!=int(bool(cleanup and not after_owned and not after_uncertain)):raise ValueError('cleanup owner join')
 return {'status':'DECODED-PUBLIC-CPU-GETINFO-INVENTORY65','generation':65,'source_code_provenance_verified':True,'cpu_flags':flags,'cpu_leaf_count':count,'cpu_vendor':cpu[176:188].decode('ascii',errors='replace'),'cpu_brand':cpu[188:236].rstrip(b'\0 ').decode('ascii',errors='replace'),'CPUID_leaf1_signature':struct.unpack_from('<I',cpu,80)[0],'GetInfo':{'phase':phase,'error':error,'status':struct.unpack_from('<Q',rng,24)[0],'algorithm_count':algorithms,'algorithm_GUID_bytes':[rng[64+i*16:80+i*16].hex() for i in range(algorithms)],'pool_before_cleanup':owned,'uncertain_before_cleanup':uncertain,'pool_after_cleanup':after_owned,'uncertain_after_cleanup':after_uncertain,'closed':bool(closed)},'entropy_approved':False,'MSR_read':False,'GetRNG_calls':0,'RDSEED_calls':0,'physical_admission':False,'raw_sha256':hashlib.sha256(raw).hexdigest()}
