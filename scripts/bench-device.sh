#!/bin/sh
# core_bench on a connected device over adb. Builds core_bench for aarch64 through slot's own
# bench:device task (same docker path as dist-device.sh), pushes the binary and the ROM to a temp
# dir on the SD card, runs it against the core already deployed in System/, prints the output and
# removes the temp dir. Use task deploy:device first so the core under test is the one you built.
#   CORE=mgba|gpsp|fceumm|nestopia|snes9x|snes9x2005_plus|genesis_plus_gx|pcsx_rearmed|picodrive|stella2014|prosystem|mednafen_vb|fbneo|fake08|mednafen_supergrafx   ROM=path/to/local/rom   SD=/mnt/sdcard   ARGS='--frames 3000 ...'
#   ROM_ON_DEVICE=/mnt/sdcard/Games/...   run a ROM that is already on the card: nothing is pushed, nothing is copied to
#     this machine, and the ROM name is left out of the printed output (core_bench's header line is redacted).
#   BENCH_NO_BUILD=1   reuse an existing build/slot/target-device core_bench (scripts/perf-eval.sh builds once)
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

CORE="${CORE:-mgba}"
ROM="${ROM:-$root/harness/roms/240pee_mb.gba}"
SD="${SD:-/mnt/sdcard}"
ARGS="${ARGS:---frames 3000 --warmup 300 --repeats 5}"
ADB="${ADB:-adb}"
tmp="$SD/bench-tmp"
trap '$ADB shell "rm -rf \"$tmp\"" >/dev/null 2>&1 || true' EXIT
trap 'exit 130' INT TERM
ROM_ON_DEVICE="${ROM_ON_DEVICE:-}"
# Single-quote one string for the device shell, whatever it holds (spaces, parentheses, apostrophes).
shq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

case "$CORE" in
mgba | gpsp | fceumm | nestopia | snes9x | snes9x2005_plus | genesis_plus_gx | pcsx_rearmed | picodrive | stella2014 | prosystem | mednafen_vb | fbneo | fake08 | mednafen_supergrafx) ;;
*)
	echo "slot-nes-snes: CORE is '$CORE', want mgba, gpsp, fceumm, nestopia, snes9x, snes9x2005_plus, genesis_plus_gx, pcsx_rearmed, picodrive, stella2014, prosystem, mednafen_vb, fbneo, fake08 or mednafen_supergrafx" >&2
	exit 2
	;;
esac
if [ -n "$ROM_ON_DEVICE" ]; then
	case "$ROM_ON_DEVICE" in
	/*) ;;
	*)
		echo "slot-nes-snes: ROM_ON_DEVICE must be an absolute path on the device" >&2
		exit 2
		;;
	esac
else
	[ -f "$ROM" ] || {
		echo "slot-nes-snes: ROM '$ROM' is not a file" >&2
		exit 2
	}
	base="$(basename "$ROM")"
	case "$base" in
	*.*) ext="$(printf '%s' "${base##*.}" | tr '[:upper:]' '[:lower:]')" ;;
	*)
		echo "slot-nes-snes: ROM '$base' has no extension, the core picks its loader from it" >&2
		exit 2
		;;
	esac
	case "$ext" in
	*[!a-z0-9]*)
		echo "slot-nes-snes: ROM extension '$ext' must be letters and digits only" >&2
		exit 2
		;;
	esac
fi

if [ -z "${BENCH_NO_BUILD:-}" ]; then
	task_bin="$(sh "$root/scripts/fetch-task.sh")"
	DEVICE_ROOT=1 sh "$root/scripts/device-sh.sh" "'${task_bin#"$root"/}' -d build/slot bench:device"
fi
bin="$root/build/slot/target-device/device/examples/core_bench"
is_aarch64 "$bin" || {
	echo "slot-nes-snes: $bin is not an aarch64 ELF" >&2
	exit 1
}

[ "$($ADB get-state 2>/dev/null)" = device ] || {
	echo "slot-nes-snes: no adb device in state device ($ADB get-state), connect the RG34XXSP" >&2
	exit 1
}
# This device's adbd does not pass the shell's exit status back, so read an answer instead.
[ "$($ADB shell "[ -f '$SD/System/${CORE}_libretro.so' ] && echo yes" </dev/null 2>/dev/null | tr -d '\r')" = yes ] || {
	echo "slot-nes-snes: $SD/System/${CORE}_libretro.so is not on the device, run task deploy:device" >&2
	exit 1
}
$ADB shell "rm -rf '$tmp' && mkdir -p '$tmp'"
$ADB push "$bin" "$tmp/core_bench" >/dev/null
if [ -n "$ROM_ON_DEVICE" ]; then
	[ "$($ADB shell "[ -f $(shq "$ROM_ON_DEVICE") ] && echo yes" </dev/null 2>/dev/null | tr -d '\r')" = yes ] || {
		echo "slot-nes-snes: ROM_ON_DEVICE is not a file on the device" >&2
		exit 1
	}
	rom_arg="$ROM_ON_DEVICE"
	label="on-device cart (name withheld)"
else
	$ADB push "$ROM" "$tmp/rom.$ext" >/dev/null
	rom_arg="./rom.$ext"
	label="$(basename "$ROM")"
fi
gov="$($ADB shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null | tr -d '\r' || true)"
echo "bench:device governor: ${gov:-unknown}"
echo "bench:device core $CORE rom $label"
rc=0
# Same loader slot's launch_frontend.sh uses.
out="$($ADB shell "cd '$tmp' && /lib/ld-linux-aarch64.so.1 ./core_bench '$SD/System/${CORE}_libretro.so' $(shq "$rom_arg") $ARGS" 2>&1)" || rc=$?
if [ -n "$ROM_ON_DEVICE" ]; then
	# core_bench prints the ROM path in its header line.
	out="$(printf '%s\n' "$out" | sed 's/ rom .* state / rom <withheld> state /')"
fi
printf '%s\n' "$out"
exit "$rc"
