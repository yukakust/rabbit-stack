#!/usr/bin/env python3
"""Finite QCA9377 initialization data; no PCI, signing, or transmission API.

Directions are relative to the host: IN=1, OUT=2, INOUT=3. CE6 is
target-autonomous, CE7 diagnostic is host-only and absent from these tables.
Table contents follow the pinned Linux QCA6174/QCA9377 override, without
inventing a smaller firmware configuration for our incomplete host driver.
"""
import hashlib
import struct

# pipe, direction, target entries, max transfer, flags, reserved
PIPES = (
    (0, 2, 32, 256, 0, 0),
    (1, 1, 32, 2048, 0, 0),
    (2, 1, 64, 2048, 0, 0),
    (3, 2, 32, 2048, 0, 0),
    (4, 2, 256, 256, 0, 0),
    (5, 2, 32, 2048, 0, 0),
    (6, 3, 32, 4096, 0, 0),
)
# service, direction, pipe; final all-zero record is the terminator.
SERVICES = (
    (0x104, 2, 3), (0x104, 1, 2),
    (0x102, 2, 3), (0x102, 1, 2),
    (0x101, 2, 3), (0x101, 1, 2),
    (0x103, 2, 3), (0x103, 1, 2),
    (0x100, 2, 3), (0x100, 1, 2),
    (0x001, 2, 0), (0x001, 1, 1),
    (0xfe00, 2, 0), (0xfe00, 1, 1),
    (0x300, 2, 4), (0x300, 1, 1),
    (0, 0, 0),
)


def table_bytes():
    """Return two exact little-endian blobs, never an address or write command."""
    return (b''.join(struct.pack('<6I', *row) for row in PIPES),
            b''.join(struct.pack('<3I', *row) for row in SERVICES))


def describe_tables():
    pipe, service = table_bytes()
    return {
        'pipe_records': [list(row) for row in PIPES],
        'service_records': [list(row) for row in SERVICES],
        'pipe_bytes': len(pipe), 'service_bytes': len(service),
        'pipe_sha256': hashlib.sha256(pipe).hexdigest(),
        'service_sha256': hashlib.sha256(service).hexdigest(),
        'target_writes_enabled': False,
    }


def required_host_resources():
    # Target nentries are NOT a host-ring allocation size. In particular CE4
    # target256 does not require changing Rabbit's bounded host ring32 here.
    # Upstream disables host CE5 and redirects HTT RX to CE1. No service
    # references CE5 after the override; do not invent a new host CE5 queue.
    return [{'pipe': p, 'direction': d, 'max_transfer': n}
            for p, d, _, n, _, _ in PIPES if p not in (5, 6)] + [
                {'pipe': 7, 'direction': 3, 'max_transfer': 2048}]


def validate_host_resources(resources):
    """Check a proposed resource inventory, not a proof of actual DMA ownership.

    A native adapter must construct this from live mapped buffers, owned rings,
    posted RX capacity and guarded cleanup. Caller-supplied JSON is insufficient
    to authorize hardware writes. This pure checker is not wired to native_route.
    """
    if not isinstance(resources, list) or len(resources) != 6:
        raise ValueError('exact six active host channel resources required')
    by_pipe = {}
    for resource in resources:
        if not isinstance(resource, dict) or set(resource) != {
                'pipe', 'direction', 'max_transfer', 'owned', 'mapped',
                'ring_entries', 'receive_capacity'}:
            raise ValueError('invalid resource schema')
        for name in ('pipe', 'direction', 'max_transfer', 'ring_entries', 'receive_capacity'):
            if type(resource[name]) is not int:
                raise ValueError('integer resource fields required')
        p = resource['pipe']
        if p in by_pipe or p not in (0, 1, 2, 3, 4, 7):
            raise ValueError('duplicate or unsupported host channel')
        by_pipe[p] = resource
    for needed in required_host_resources():
        r = by_pipe[needed['pipe']]
        entries = r['ring_entries']
        if (r['direction'] != needed['direction'] or
                r['owned'] is not True or r['mapped'] is not True or
                r['max_transfer'] != needed['max_transfer'] or
                entries < 2 or entries > 32 or entries & (entries - 1)):
            raise ValueError('unprepared host channel: ' + str(needed['pipe']))
        if needed['direction'] & 1:
            if r['receive_capacity'] < needed['max_transfer'] or r['receive_capacity'] > 4096:
                raise ValueError('insufficient bounded receive buffer')
        elif r['receive_capacity'] != 0:
            raise ValueError('unexpected receive buffer on transmit channel')
    return True
