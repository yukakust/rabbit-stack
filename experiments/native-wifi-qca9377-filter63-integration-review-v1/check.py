"""Pure byte-storage handover oracle; NOT native ABI, DMA or physical proof."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parent
PRODUCER = ROOT.parent / 'native-wifi-qca9377-filter63-native-v1'

def event(completion):
    return {'completion': completion, 'raw': bytes((completion + i) % 256 for i in range(2048))}

def handover(count, archives, response, response_first=True):
    slots = [None] * 16
    for i in range(count): slots[i] = event(i + 1)
    # Exact current htt_native_begin: response13, archives14..15.
    if response: slots[13] = event(100)
    for i in range(archives): slots[14 + i] = event(101 + i)
    expected = [slots[i] for i in range(count)]
    sources = ([13] if response else []) + list(range(14, 14 + archives))
    expected += [slots[i] for i in sources]
    if not response_first: sources = list(range(14, 14 + archives)) + ([13] if response else [])
    retained_response_completion = 100 if response else 0
    for source in sources:
        item = slots[source]
        if item is None or any(slots[i]['completion'] == item['completion'] for i in range(count)):
            return False
        slots[count] = item.copy()  # QcaRxEvent value copy, raw owned by value.
        count += 1
    ok = slots[:count] == expected
    # After pointer revocation, later scan appends may overwrite remaining staging.
    for i in range(count, 16): slots[i] = event(200 + i)
    assert (retained_response_completion == 100) == bool(response)
    return ok and slots[:count] == expected

def run():
    cases = 0
    for count in range(14):
        for archives in range(3):
            for response in (False, True):
                assert handover(count, archives, response)
                cases += 1
    # This mutation concretely overwrites response slot13 before it is copied.
    assert not handover(13, 1, True, response_first=False)
    assert not handover(13, 2, True, response_first=False)
    cases += 2
    pipeline = (PRODUCER / 'components/pipeline.inc').read_text()
    htt = (PRODUCER / 'components/htt_native.c').read_text()
    status = (PRODUCER / 'components/pipeline_status.inc').read_text()
    coordinator = (PRODUCER / 'components/coordinator.c').read_text()
    rx = (PRODUCER / 'components/rx.c').read_text()
    assert 's->response=storage;s->archive=storage+1;' in htt
    assert 'native_scan.archive_count>13' in pipeline
    transfer = pipeline[pipeline.index('if(rc){'):pipeline.index('if(rc<0){pipeline_fault(112')]
    assert transfer.index('archive_owned(htt_query.response)') < transfer.index('archive_owned(&htt_query.archive[i])')
    assert 'htt_query.response=0;htt_query.archive=0;' in transfer
    assert 'htt_query.response->' not in status
    assert 'htt_query.response_completion' in status
    post = pipeline.index('qca_tx_poll(t,now)')
    assert post < pipeline.index('qca_filter_post(', post) < pipeline.index('qca_rx_take(', post)
    assert pipeline.index('htt_query.phase!=QCA_HTTN_READY') < pipeline.index('qca_native_scan_begin(')
    assert '!head->bytes||(head->pipe==1&&head->endpoint==r->htt.endpoint)' in coordinator
    assert 'qca_htc_credit_receive' not in pipeline + coordinator
    assert rx.count('qca_htc_credit_receive') == 1
    assert 'f.payload!=p+8' in rx
    cases += 12
    inputs = ['pipeline.inc','htt_native.c','htt_native.h','pipeline_status.inc',
              'coordinator.c','scan_native.c','rx.c','rx.h','tx.c','pipeline_gatt.c']
    report = {'status':'PURE-STORAGE-HANDOVER-AND-SOURCE-GUARDS-PASS',
              'cases':cases,'native_abi_tested':False,'actual_producer_asan_tested':False,
              'physical_admission':False,'source_sha256':{
                  'components/'+f: hashlib.sha256((PRODUCER/'components'/f).read_bytes()).hexdigest() for f in inputs}}
    (ROOT/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'], cases)

if __name__ == '__main__': run()
