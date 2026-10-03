"""Bounded host-side ath10k container preflight; NEVER uploads or selects a board by guess."""
import hashlib
import struct
MAX_FILE=4*1024*1024
class Invalid(ValueError):pass
def digest(data):return hashlib.sha256(data).hexdigest()
def elements(data):
    if len(data)>MAX_FILE:raise Invalid('container exceeds budget')
    result=[];pos=0
    while pos<len(data):
        if len(data)-pos<8:raise Invalid('truncated TLV header')
        kind,length=struct.unpack_from('<II',data,pos);pos+=8
        padded=(length+3)&~3
        if padded>len(data)-pos:raise Invalid('truncated TLV payload/padding')
        result.append((kind,data[pos:pos+length]));pos+=padded
        if len(result)>4096:raise Invalid('too many elements')
    return result
def container(data,magic):
    if len(data)>MAX_FILE or not data.startswith(magic+b'\0'):raise Invalid('bad container magic/size')
    start=(len(magic)+1+3)&~3
    if len(data)<start:raise Invalid('truncated magic padding')
    return elements(data[start:])
def firmware(data):
    items=container(data,b'QCA-ATH10K');seen={};unknown=[]
    for kind,body in items:
        if kind in seen:raise Invalid('duplicate firmware element')
        seen[kind]=body
        if kind not in range(8):unknown.append(kind)
    if not seen.get(3):raise Invalid('missing firmware image')
    for kind in (1,5,6):
        if kind in seen and len(seen[kind])!=4:raise Invalid('invalid scalar element')
    try:version=seen.get(0,b'').rstrip(b'\0').decode('ascii')
    except UnicodeError as error:raise Invalid('invalid version text') from error
    if len(version)>256:raise Invalid('version too long')
    return {'container_sha256':digest(data),'bytes':len(data),'version':version,
            'wmi_op':struct.unpack('<I',seen[5])[0] if 5 in seen else None,
            'htt_op':struct.unpack('<I',seen[6])[0] if 6 in seen else None,
            'firmware_image_bytes':len(seen[3]),'firmware_image_sha256':digest(seen[3]),
            'otp_image_bytes':len(seen.get(4,b'')),'code_swap_present':7 in seen,
            'features_hex':seen.get(2,b'').hex(),'unknown_elements':unknown,
            'hardware_compatible':None,'upload_authorized':False}
def boards(data):
    records={}
    for outer,body in container(data,b'QCA-ATH10K-BOARD'):
        if outer not in (0,1):raise Invalid('unsupported board group')
        names=[];payload=None
        for kind,value in elements(body):
            if kind==0:
                try:name=value.decode('ascii')
                except UnicodeError as error:raise Invalid('invalid board name') from error
                if not name or len(name)>512 or '\0' in name:raise Invalid('invalid board name length')
                names.append(name)
            elif kind==1:
                if payload is not None or not value:raise Invalid('duplicate/empty board data')
                payload=value
            else:raise Invalid('unsupported board element')
        if not names or payload is None:raise Invalid('incomplete board group')
        for name in names:
            identity=(outer,name)
            if identity in records:raise Invalid('ambiguous board identity')
            records[identity]={'group':outer,'name':name,'bytes':len(payload),'sha256':digest(payload)}
    return list(records.values())
def select_board(records,exact_identity):
    # Identity must come from physical PCI subsystem/BMI/board-variant evidence.
    if not exact_identity:raise Invalid('fresh physical board identity required')
    matches=[r for r in records if r['group']==0 and r['name']==exact_identity]
    if len(matches)!=1:raise Invalid('no unique exact board match')
    return matches[0]
