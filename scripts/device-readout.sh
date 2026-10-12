#!/bin/sh
# Read the gate numbers out of slot.log. With no argument it pulls slot.log off the connected
# device; with one argument it reads that file (so a saved log can be re-read).
# What the log really says (work/slot crates/slot/src/emu.rs, latency.rs):
#   slot: audio: N samples dropped, M starved          once at session end, if dropped or starved is above 0 or SLOT_TRACE is set
#   slot: audio: Q/T queued, D dropped, S starved, ... every 300 paced frames, only with SLOT_TRACE set
#   slot: latency: ... total X ms                      per input, only with trace-latency.on or SLOT_TRACE_LATENCY
# "starved" counts samples, not events. Latency is input to screen swap, not frame time. There is no
# per-frame wall time line anywhere in slot, so p99 frame time cannot be read from the log.
set -eu

SD="${SD:-/mnt/sdcard}"
ADB="${ADB:-adb}"
if [ $# -gt 1 ]; then
	echo "usage: device-readout.sh [saved-slot.log]" >&2
	exit 2
elif [ $# -eq 1 ]; then
	log="$1"
else
	log="${TMPDIR:-/tmp}/slot.log.$$"
	trap 'rm -f "$log"' EXIT
	[ "$($ADB get-state 2>/dev/null)" = device ] || {
		echo "slot-nes-snes: no adb device in state device ($ADB get-state), connect the RG34XXSP" >&2
		exit 1
	}
	$ADB pull "$SD/slot.log" "$log" >/dev/null
fi
[ -f "$log" ] || {
	echo "slot-nes-snes: no log at $log" >&2
	exit 1
}

echo "audio summary lines (end of session):"
grep -E '^slot: audio: [0-9]+ samples dropped' "$log" || echo "  none (session did not end cleanly, or SLOT_TRACE was off and nothing starved or dropped)"
echo "audio trace lines (SLOT_TRACE only): $(grep -cE '^slot: audio: [0-9]+/[0-9]+ queued' "$log")"
sed -n 's/^slot: audio: [0-9]*\/[0-9]* queued, [0-9]* dropped, \([0-9]*\) starved.*/\1/p' "$log" |
	awk '{ if ($1 > m) m = $1 } END { print "max starved samples seen in trace: " (NR ? m : "n/a") }'
echo "latency (input to swap, ms):"
sed -n 's/^slot: latency: .*total \([0-9.]*\) ms.*/\1/p' "$log" | sort -n |
	awk '{ v[NR] = $1 } END {
		if (!NR) { print "  no latency lines"; exit }
		i = int(NR * 0.99); if (i < NR * 0.99) i++; if (i < 1) i = 1
		printf "  n %d, median %.1f, p99 %.1f, max %.1f\n", NR, v[int((NR + 1) / 2)], v[i], v[NR]
	}'
