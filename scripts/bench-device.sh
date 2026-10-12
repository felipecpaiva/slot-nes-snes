#!/bin/sh
# core_bench on a connected device over adb. Builds core_bench for aarch64 through slot's own
# bench:device task (same docker path as dist-device.sh), pushes the binary and the ROM to a temp
# dir on the SD card, runs it against the core already deployed in System/, prints the output and
# removes the temp dir. Use task deploy:device first so the core under test is the one you built.
#   CORE=mgba|gpsp|fceumm|nestopia|snes9x|snes9x2005_plus   ROM=path/to/local/rom   SD=/mnt/sdcard   ARGS='--frames 3000 ...'
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

case "$CORE" in
mgba | gpsp | fceumm | nestopia | snes9x | snes9x2005_plus) ;;
*)
	echo "slot-nes-snes: CORE is '$CORE', want mgba, gpsp, fceumm, nestopia, snes9x or snes9x2005_plus" >&2
	exit 2
	;;
esac
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

task_bin="$(sh "$root/scripts/fetch-task.sh")"
DEVICE_ROOT=1 sh "$root/scripts/device-sh.sh" "'${task_bin#"$root"/}' -d build/slot bench:device"
bin="$root/build/slot/target-device/device/examples/core_bench"
is_aarch64 "$bin" || {
	echo "slot-nes-snes: $bin is not an aarch64 ELF" >&2
	exit 1
}

[ "$($ADB get-state 2>/dev/null)" = device ] || {
	echo "slot-nes-snes: no adb device in state device ($ADB get-state), connect the RG34XXSP" >&2
	exit 1
}
$ADB shell "test -f '$SD/System/${CORE}_libretro.so'" || {
	echo "slot-nes-snes: $SD/System/${CORE}_libretro.so is not on the device, run task deploy:device" >&2
	exit 1
}
$ADB shell "rm -rf '$tmp' && mkdir -p '$tmp'"
$ADB push "$bin" "$tmp/core_bench" >/dev/null
$ADB push "$ROM" "$tmp/rom.$ext" >/dev/null
gov="$($ADB shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null | tr -d '\r' || true)"
echo "bench:device governor: ${gov:-unknown}"
echo "bench:device core $CORE rom $(basename "$ROM")"
rc=0
# Same loader slot's launch_frontend.sh uses.
$ADB shell "cd '$tmp' && /lib/ld-linux-aarch64.so.1 ./core_bench '$SD/System/${CORE}_libretro.so' './rom.$ext' $ARGS" || rc=$?
exit "$rc"
