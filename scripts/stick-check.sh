#!/bin/sh
# Stick check on the RG34XXSP, run by the maintainer with the device on adb. Asks for one stick move at a
# time, records the raw events of the stick node for a few seconds each, prints every axis that moved
# (min, max) and the code that moved most, then prints the Config/sticks.txt that matches (issue 65).
#
#   sh scripts/stick-check.sh          guided: left stick right, left stick down, right stick right,
#                                      right stick down, click left stick, click right stick
#   sh scripts/stick-check.sh live     print every stick and key event until Ctrl-C
#   sh scripts/stick-check.sh parse F  summarise a raw event file F (input_event, 24 bytes each)
# Env: ADB=adb NODE=/dev/input/event1 SD=/mnt/sdcard SECS=3
# Run on the device itself (no adb) and it reads NODE directly.
set -eu

ADB="${ADB:-adb}"
NODE="${NODE:-/dev/input/event1}"
SD="${SD:-/mnt/sdcard}"
SECS="${SECS:-3}"

die() {
	echo "slot-nes-snes: $*" >&2
	exit 1
}

usage() {
	echo "usage: $0 [live | parse FILE]" >&2
	exit 2
}

on_device() { [ -r "$NODE" ] && ! command -v "$ADB" >/dev/null 2>&1; }

stream() {
	if on_device; then
		cat "$NODE"
	else
		$ADB exec-out cat "$NODE"
	fi
}

# input_event on aarch64: 16 bytes of time, u16 type, u16 code, s32 value, so six 32-bit words.
events() {
	od -An -v -t d4 | awk '{
		for (i = 1; i <= NF; i++) {
			w[n % 6] = $i; n++
			if (n % 6 == 0) {
				tc = w[4] < 0 ? w[4] + 4294967296 : w[4]
				printf "%d %d %d\n", tc % 65536, int(tc / 65536), w[5]
				fflush()
			}
		}
	}'
}

summarise() {
	events <"$1" | awk '
	$1 == 3 && $2 != 16 && $2 != 17 {
		c = $2
		if (!(c in lo)) { lo[c] = $3; hi[c] = $3; order[++n] = c }
		if ($3 < lo[c]) lo[c] = $3
		if ($3 > hi[c]) hi[c] = $3
	}
	$1 == 1 && $3 == 1 && !($2 in down) { down[$2] = 1; keys[++k] = $2 }
	END {
		best = -1; peak = 0
		for (i = 1; i <= n; i++) {
			c = order[i]
			printf "  axis 0x%02x: min %d max %d\n", c, lo[c], hi[c]
			m = -lo[c] > hi[c] ? -lo[c] : hi[c]
			if (m > peak) { peak = m; best = c; sign = -lo[c] > hi[c] ? "-" : "" }
		}
		for (i = 1; i <= k; i++) printf "  key 0x%03x pressed\n", keys[i]
		if (best >= 0) printf "AXIS %s0x%02x\n", sign, best
		else if (k == 0) print "  nothing moved"
		if (k > 0) printf "KEY 0x%03x\n", keys[1]
	}'
}

capture() {
	f="$1"
	stream >"$f" &
	pid=$!
	sleep "$SECS"
	kill "$pid" 2>/dev/null || true
	wait "$pid" 2>/dev/null || true
}

step() {
	printf '\n%s\nPress Enter, then do it within %s s and hold until this prints again. ' "$1" "$SECS" >&2
	read -r _
	capture "$tmp/step"
	summarise "$tmp/step" >"$tmp/out"
	grep -v -e '^AXIS ' -e '^KEY ' "$tmp/out" >&2 || true
	grep "^$2 " "$tmp/out" | head -n 1 | cut -d' ' -f2
}

guided() {
	on_device || [ "$($ADB get-state 2>/dev/null)" = device ] || die "no adb device in state device, connect the RG34XXSP"
	tmp="$(mktemp -d "${TMPDIR:-/tmp}/stick-check.XXXXXX")"
	trap 'rm -rf "$tmp"' EXIT
	echo "Reading $NODE. Leave the other stick alone in each step."
	lx="$(step 'LEFT stick: push it fully RIGHT.' AXIS)"
	ly="$(step 'LEFT stick: push it fully DOWN.' AXIS)"
	rx="$(step 'RIGHT stick: push it fully RIGHT.' AXIS)"
	ry="$(step 'RIGHT stick: push it fully DOWN.' AXIS)"
	l3="$(step 'LEFT stick: click it in (L3), once.' KEY)"
	r3="$(step 'RIGHT stick: click it in (R3), once.' KEY)"
	echo
	echo "Right and down are positive in libretro, so a code that went negative is written with a minus."
	echo "L3 key: ${l3:-none seen}   R3 key: ${r3:-none seen}"
	for v in "$lx" "$ly" "$rx" "$ry"; do
		[ -n "$v" ] || die "a step saw no axis move, run it again"
	done
	text="left_x=$lx
left_y=$ly
right_x=$rx
right_y=$ry"
	echo
	echo "$SD/Config/sticks.txt:"
	echo "$text"
	if [ "$text" = "left_x=0x02
left_y=0x03
right_x=0x04
right_y=0x05" ]; then
		echo "(this is slot's default, no file needed)"
	else
		echo
		echo "to write it:"
		printf '%s shell "printf %s > %s"\n' "$ADB" "'left_x=$lx\nleft_y=$ly\nright_x=$rx\nright_y=$ry\n'" "$SD/Config/sticks.txt"
	fi
}

live() {
	on_device || [ "$($ADB get-state 2>/dev/null)" = device ] || die "no adb device in state device, connect the RG34XXSP"
	echo "Reading $NODE, Ctrl-C to stop."
	stream | events | awk '
	$1 == 3 { printf "axis 0x%02x %6d\n", $2, $3; fflush() }
	$1 == 1 { printf "key 0x%03x %s\n", $2, $3 ? "down" : "up"; fflush() }'
}

case "${1:-}" in
"") guided ;;
live) live ;;
parse)
	[ $# -eq 2 ] || usage
	summarise "$2"
	;;
*) usage ;;
esac
