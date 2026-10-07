# Generation 59 transport observation — offline candidate

Frozen boot-prefix57 production behavior with exactly three changed generation
constants. This is telemetry and authenticated firmware-delivery observation,
with unchanged USB/HCI/watchdog behavior; it is not a transport or timer fix.

Public target/owner/full firmware policy is unchanged except generation 59.
MAIN remains bounded to 32984 bytes / 133 descriptors and 600 seconds; no
134th MAIN, BMI_DONE, HTC, INIT or scan command is admitted by this profile.
Model cleanup proof does not prove that chip ROM is ready for a later trial.

On Yukabox only, in an isolated source tree and dedicated TMPDIR:

```
python3 verify_native.py
python3 prove_prefix.py --world runs/world19.rup --world-json runs/world19.json --tmpdir /home/yuka/rabbit-world/parallel-observation59-native-v1/tmp
python3 verify_production_diff.py --baseline /home/yuka/rabbit-world/parallel-boot-prefix57-native-v1/source/experiments/native-wifi-qca9377-boot-prefix57-native-v1/runs/checked-candidate --candidate runs/checked-candidate
```

Eight actual C models, current signed world19 ASAN, normal and EMPTY supervisor
QEMU, three equal whole EFI builds and exact generated production-source diff
are required. Public fixture keys are used only in models. No hardware operation,
owner private key, actual admission, counter reservation or signing is performed.
Root must review the proof before any separately gated future physical trial.
