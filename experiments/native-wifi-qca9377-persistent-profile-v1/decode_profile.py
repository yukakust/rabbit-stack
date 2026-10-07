"""Decode cached read-only telemetry; no Bluetooth calls or attestation."""
import struct
NAMES=('trial_phase','trial_error','expired','stop_requested','actual_owners_released',
 'lifecycle_phase','lifecycle_error','bridge_error','polls','rx_phase','rx_error','rx_completed','rx_posts',
 'queue_count','backpressure','rx1_posted','rx2_posted','held_buffers','dma_users','pci_owned','wake_owned',
 'link_owned','irq_owned','pin_owned','bus_owned','access_count','adapter_phase','cleanup_slots',
 'startup_phase','startup_error','transaction_phase','ready_seen','tx_complete','credit_available',
 'credit_outstanding','credit_reserved','credit_total','rx1_cookie','rx2_cookie','started_low','started_high',
 'last_low','last_high','stop_latched','generation','reserved')
def decode(raw):
 b=bytes.fromhex(raw['raw_hex'])
 if len(b)!=192 or b[:8]!=b'QWRX0001':raise ValueError('exact QWRX1 envelope required')
 d=dict(zip(NAMES,struct.unpack('<46I',b[8:])))
 if d['generation']!=53 or d['reserved']:raise ValueError('exact provisional53 profile required')
 for n in ('expired','stop_requested','actual_owners_released','backpressure','rx1_posted','rx2_posted',
           'pci_owned','wake_owned','link_owned','irq_owned','pin_owned','bus_owned','ready_seen','tx_complete','stop_latched'):
  if d[n]>1:raise ValueError('invalid boolean '+n)
 if d['queue_count']>2 or any(d[n]>14 for n in ('held_buffers','dma_users','access_count','cleanup_slots')):raise ValueError('owner/queue bounds')
 if d['credit_available']+d['credit_outstanding']+d['credit_reserved']!=d['credit_total']:raise ValueError('credit ledger inconsistent')
 if d['actual_owners_released'] and any(d[n] for n in ('held_buffers','dma_users','access_count','pci_owned','wake_owned','link_owned','irq_owned','pin_owned','bus_owned')):raise ValueError('release contradicts owners')
 d['bounded_rx_trial_pass']=bool(d['trial_phase']==3 and not d['trial_error'] and d['expired'] and d['stop_requested']
  and d['actual_owners_released'] and d['lifecycle_phase']==4 and not d['lifecycle_error'] and not d['bridge_error']
  and d['startup_phase']==2 and not d['startup_error'] and d['ready_seen'] and d['tx_complete'])
 d['wifi_connected']=False;d['device_attestation']=False
 return d
