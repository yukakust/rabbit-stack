"""Public signed module chunks only. No signer, credential or private-key API."""
import hashlib
import struct

MAX = 65824

def validate_chunk(chunk):
    if not isinstance(chunk, bytes) or not 289 <= len(chunk) <= MAX:
        raise ValueError('bounded signed module chunk required')
    role, abi = struct.unpack_from('<II', chunk, 196)
    if abi != 1 or (chunk[:8], role) not in [(b'RABMOD01', 1), (b'RABRSN01', 2)]:
        raise ValueError('exact module role domain required')
    # This envelope check grants NO signature, execution or parent authority.
    return hashlib.sha256(chunk).digest()

def begin(chunk, session):
    digest = validate_chunk(chunk)
    if not isinstance(session, bytes) or len(session) != 8 or not any(session):
        raise ValueError('saved nonzero session required')
    return b'\x01' + session + struct.pack('<I', len(chunk)) + digest

def data(chunk, session, offset, limit=244):
    begin(chunk, session)
    if isinstance(offset, bool) or not isinstance(offset, int) or not 0 <= offset < len(chunk):
        raise ValueError('offset')
    if not isinstance(limit, int) or isinstance(limit, bool) or not 14 <= limit <= 244:
        raise ValueError('MTU value budget')
    return b'\x02' + session + struct.pack('<I', offset) + chunk[offset:offset+limit-13]

def receipt(raw, epoch, session, chunk):
    digest = validate_chunk(chunk)
    begin(chunk, session)
    if not isinstance(epoch, int) or isinstance(epoch, bool) or not 0 < epoch < 2**64:
        raise ValueError('current epoch')
    if not isinstance(raw, bytes) or len(raw) != 80 or raw[:8] != b'QMT00001':
        raise ValueError('exact public status')
    e, state, error, length, received, result, reserved = struct.unpack_from('<QIIIIiI', raw, 8)
    if e != epoch or reserved or state > 5 or length > MAX or received > length:
        raise ValueError('status envelope')
    if state == 0:
        if error or length or received or result or any(raw[40:]):
            raise ValueError('noncanonical idle')
        return {'state': 'idle', 'received': 0, 'result': 0}
    if raw[40:48] != session or raw[48:] != digest or length != len(chunk):
        raise ValueError('different retained session; never overwrite automatically')
    if state in (2, 3) and received != length:
        raise ValueError('incomplete pending/accepted')
    if state in (1, 2, 3) and error:
        raise ValueError('success state with error')
    if state == 3 and result < 0:
        raise ValueError('negative acceptance')
    if state in (1, 2) and result:
        raise ValueError('uncompleted callback result')
    return {'state': ['idle', 'staging', 'pending', 'accepted', 'rejected', 'closed'][state],
            'received': received, 'result': result, 'error': error}
