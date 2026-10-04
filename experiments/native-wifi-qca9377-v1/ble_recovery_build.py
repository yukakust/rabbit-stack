"""Separate actor profile: re-advertise after an untracked peer disconnect.

Do not edit immutable/bootstrap sources or invalidate signed native15/native16.
"""
import struct
from pathlib import Path
import diagnostic_build as base
ROOT = Path(__file__).resolve().parent
actors = base.actors
one = base.one


def link_source():
    source = (actors.LINK / 'hci_link.c').read_text()
    old = 'if(p[0]==5&&n==6&&l->state==RL_CONNECTED&&u16(p+3)==l->handle){'
    new = '''if(p[0]==5&&n==6&&(
  (l->state==RL_CONNECTED&&u16(p+3)==l->handle)||
  (l->state==RL_ADVERTISING&&!l->connected&&!l->pending&&u16(p+3)<=0x0eff))){
  /* The controller can auto-disable advertising on a connection whose event
   * was not received intact. A valid successful disconnect is then the only
   * observed evidence of that link. Re-enable advertising, without inventing a
   * connection, resetting the controller, accepting ACL or clearing file state.
   * A foreign handle must never tear down a known live connection. */'''
    return one(source, old, new)


def compile_driver(directory, crypto):
    actors.sources(directory)
    (directory / 'ble_recovery_link.c').write_text(link_source())
    payload = actors.compile_efi(directory, 'ble-recovery-driver', [directory/'driver.c', directory/'city_core.c',
        actors.LINK/'usb_port.c', directory/'ble_recovery_link.c', actors.LINK/'gatt_core.c',
        actors.LINK/'file_core.c', actors.NATIVE/'sha256.c', *crypto], driver=True, definitions=('SCENE_REVISION=1',))
    offset = struct.unpack_from('<I', payload,60)[0]
    if struct.unpack_from('<I',payload,offset+24+56)[0] > 4*1024*1024:
        raise ValueError('mapped actor driver exceeds immutable root bound')
    return payload
