#!/usr/bin/env python3
"""Physical controlled staging stop/resume; does NOT simulate an RF fault or reboot."""
import argparse
import json
from unittest.mock import patch
from pathlib import Path
import ask_connected_world as flow
from world_control import Controller


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True); p.add_argument('--intent', required=True)
    p.add_argument('--stop-after', type=int, default=3000)
    p.add_argument('--state', type=Path, default=flow.ROOT / 'runs/text-world/state.json')
    a = p.parse_args()
    if not 1 <= a.stop_after <= 5000: p.error('controlled prefix must be1..5000 bytes')
    controller = Controller(a.state); real_step = flow.sender_step; stopped = False
    def step(directory, report, name, flags, **kwargs):
        nonlocal stopped
        if name == 'paced-stage' and not stopped:
            flags = list(flags); index = flags.index('--stage-only-bytes')
            if a.stop_after >= int(flags[index+1]): raise ValueError('trial prefix must be smaller than full stream')
            flags[index+1] = str(a.stop_after); stopped = True
            print('CONTROLLED PHYSICAL STAGING STOP: acknowledged prefix, deliberate disconnect, no COMMIT', flush=True)
        return real_step(directory, report, name, flags, **kwargs)
    with patch.object(flow, 'sender_step', side_effect=step):
        result = controller.execute(a.intent, plan=flow.read_json(a.plan))
    print(json.dumps({'trial': 'controlled-physical-prefix-stop-same-session-resume',
                      'unexpected_rf_failure_induced': False, 'controlled_stop_exercised': stopped,
                      'request': result}, ensure_ascii=False, indent=2))
    return 0 if stopped and result['status'] == 'APPLIED' else 1


if __name__ == '__main__': raise SystemExit(main())
