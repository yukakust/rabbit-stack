"""Pure exact QWBT envelope decoder. No generation/readiness/release inference."""
import struct
FIELDS='phase error plan_phase plan_error submitted completed board_address calibration_result offset ready_bytes credit_count credit_size max_endpoints boot_round ram_phase ram_error asset_ready asset_pinned hardware_stage hardware_error adapter_phase cleanup_slot dma_users bmi_version bmi_type board_phase board_error board_result asset_bitmap boot_once'.split()
def decode(raw,firmware_digest):
 if not isinstance(raw,bytes) or len(raw)!=160 or raw[:8]!=b'QWBT0001':raise ValueError('exact160 QWBT0001 required')
 if not isinstance(firmware_digest,bytes) or len(firmware_digest)!=32 or raw[128:]!=firmware_digest:raise ValueError('immutable packet firmware digest mismatch')
 return {'fields':dict(zip(FIELDS,struct.unpack('<30I',raw[8:128]))),'firmware_digest':raw[128:].hex(),'native_generation_verified':False,'readiness_verified':False,'resource_release_verified':False,'device_attestation':False}
