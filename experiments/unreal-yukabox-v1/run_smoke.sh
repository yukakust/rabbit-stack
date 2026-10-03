#!/usr/bin/env bash
# Runs only on Yukabox/Linux. Logs/frame are evidence; success requires inspection.
set -euo pipefail
[[ $(uname -s) == Linux ]] || { echo 'Run on Yukabox/Linux'; exit 2; }
root=${1:?Pass the remote experiment root}
engine="$root/engine"
project="$root/projects/project/RabbitDistrict.uproject"
[[ -x "$engine/Engine/Binaries/Linux/UnrealEditor" ]] || { echo 'Engine missing'; exit 2; }
[[ -f "$project" ]] || { echo 'Project missing'; exit 2; }
trial=$(mktemp -d "$root/logs/smoke-XXXXXXXX")
echo "Trial: $trial"
bash "$engine/Engine/Build/BatchFiles/Linux/Build.sh" RabbitDistrictEditor Linux Development \
    -Project="$project" -WaitMutex -MaxParallelActions=4 -NoUBA > "$trial/build.log" 2>&1
timeout --kill-after=15s 900s nice -n 10 "$engine/Engine/Binaries/Linux/UnrealEditor" "$project" \
    /Engine/Maps/Entry -game -vulkan -RenderOffscreen -unattended -NoSound \
    -ResX=1280 -ResY=720 -windowed -NoSplash -CoreLimit=4 -stdout -FullStdOutLogOutput \
    -RabbitFrame="$trial/frame.png" -abslog="$trial/engine.log" > "$trial/stdout.log" 2>&1
[[ -s "$trial/frame.png" ]] || { echo 'No captured frame'; exit 1; }
echo 'Frame captured. Inspect image and Vulkan device log before declaring GPU success.'
