"""Exact frozen release-safe63 monitor, separately from pipeline pass."""
import host_gate
ROOT=host_gate.ROOT
NAME='native-wifi-qca9377-filter63-progress-monitor-v2'
def checked():return host_gate.checked()[NAME]
if __name__=='__main__':print(checked())
