"""Deterministic RFS receipt correlation; never device authentication."""
import base64
import re
import struct


def parse_status(text, session):
    matches = re.findall(r'^RFS STATUS HEX=([0-9a-f]{120})$', text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('need exactly one complete read-only RFS status')
    raw = bytes.fromhex(matches[0])
    received, length = struct.unpack_from('<II', raw, 12)
    state, error = raw[20:22]
    counter = struct.unpack_from('<I', raw, 24)[0]
    if raw[:4] != b'RFS\1' or raw[22:24] != b'\0\0' or state > 4 or received > length or length > 262176:
        raise ValueError('invalid RFS status envelope')
    stream = base64.b64decode(session['stream_base64'], validate=True)
    same = raw[4:12] == base64.b64decode(session['session_base64'], validate=True)
    exact = same and length == len(stream)
    receipt = exact and received == length and counter == session['counter'] and raw[28:60] == stream[:32]
    if state == 0 and not error and not received and not length:
        outcome = 'idle'
    elif state == 1 and not error and length:
        outcome = 'staging' if exact else 'foreign-staging'
    elif state == 4 and not error and received == length and length:
        outcome = 'pending' if exact else 'foreign-pending'
    elif state == 2 and not error and received == length and length:
        outcome = 'applied' if receipt else 'foreign-final'
    elif state == 3 and error == 2 and received == length and length:
        outcome = 'rejected' if receipt else 'foreign-final'
    else:
        outcome = 'invalid'
    return {'outcome': outcome, 'state': state, 'error': error, 'received': received,
            'length': length, 'counter': counter, 'sha256': raw[28:60].hex(),
            'session_matches': same, 'raw_hex': raw.hex(), 'device_attestation': False}


def confirmed_prefix(text, length):
    values = [int(n) for n, total in re.findall(r'^(?:RESUME OFFSET|STAGING CHECKPOINT)=(\d+)/(\d+)', text, re.MULTILINE)
              if int(total) == length and int(n) <= length]
    return max(values, default=0)
