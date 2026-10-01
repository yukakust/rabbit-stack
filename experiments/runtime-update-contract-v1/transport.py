"""NON-DEPLOYED RP v3 reference framing for up to 256KiB runtime envelopes.

Not understood by installed God Runtime v2/v3. Checksums only detect accidents;
the complete RRT1 signature is the authority boundary. No Bluetooth calls here.
"""
from update import MAX_BYTES, UpdateError


def fnv(data):
    result = 0x811c9dc5
    for value in data:
        result = ((result ^ value) * 0x01000193) & 0xffffffff
    return result


def frame(kind, transfer, sequence, payload):
    if kind not in (1, 2, 3) or type(transfer) is not int or not 1 <= transfer <= 255 or type(sequence) is not int or not 0 <= sequence <= 65535 or len(payload) > 6:
        raise UpdateError("invalid runtime frame")
    head = b"RP" + bytes((0x30 | kind, transfer)) + sequence.to_bytes(2, "little") + payload.ljust(6, b"\0")
    return head + fnv(head).to_bytes(4, "big")


def parse(value):
    if type(value) is not bytes or len(value) != 16 or value[:2] != b"RP" or value[2] not in (0x31, 0x32, 0x33) or not value[3] or fnv(value[:12]) != int.from_bytes(value[12:], "big"):
        raise UpdateError("invalid runtime frame envelope/checksum")
    return value[2] & 15, value[3], int.from_bytes(value[4:6], "little"), value[6:12]


def encode(data):
    if type(data) is not bytes or not 1 <= len(data) <= MAX_BYTES:
        raise UpdateError("runtime transfer budget exceeded")
    checksum = fnv(data)
    transfer = checksum & 255 or 1
    count = (len(data) + 5)//6
    result = [frame(1, transfer, 0, len(data).to_bytes(4, "little") + b"\0\0")]
    result.extend(frame(2, transfer, i, data[i*6:(i+1)*6]) for i in range(count))
    result.append(frame(3, transfer, count, checksum.to_bytes(4, "big") + b"\0\0"))
    return result


def decode(frames):
    if len(frames) < 3:
        raise UpdateError("missing runtime frames")
    kind, transfer, sequence, payload = parse(frames[0])
    length = int.from_bytes(payload[:4], "little")
    count = (length+5)//6
    if (kind, sequence, payload[4:]) != (1, 0, b"\0\0") or not 1 <= length <= MAX_BYTES or len(frames) != count+2:
        raise UpdateError("invalid BEGIN/budget/frame count")
    data = bytearray()
    for i, raw in enumerate(frames[1:-1]):
        kind, tid, sequence, payload = parse(raw)
        if (kind, tid, sequence) != (2, transfer, i):
            raise UpdateError("missing, reordered or mixed runtime chunks")
        data.extend(payload)
    if any(data[length:]):
        raise UpdateError("nonzero last-chunk padding")
    data = bytes(data[:length])
    kind, tid, sequence, payload = parse(frames[-1])
    if (kind, tid, sequence, payload[4:]) != (3, transfer, count, b"\0\0") or int.from_bytes(payload[:4], "big") != fnv(data):
        raise UpdateError("runtime COMMIT/hash mismatch")
    return data
