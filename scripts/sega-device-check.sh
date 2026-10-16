#!/bin/sh
# Sega device check on the RG34XXSP, run by the maintainer with the device on adb. Deploys the current
# build (Genesis Plus GX included), copies four of the maintainer's own dumps from the ROM library onto the
# card (never into this repo), then plays each for MINUTES with scripts/auto-play.sh and prints the boot
# time, audio starved and dropped samples and the frame times from play-eval.md.
#
#   sh scripts/sega-device-check.sh                 deploy, push, play 2 minutes per cart
#   NODEPLOY=1 sh scripts/sega-device-check.sh      skip task deploy:device (System/ already current)
# Env: LIB=/Volumes/MuOs/ROMS SD=/mnt/sdcard ADB=adb MINUTES=2 RUNS=1 DATE=<today>
#
# Carts (heavy Mega Drive on the SVP chip, a light Mega Drive, one Master System, one Game Gear), the same
# ids as the genesis_plus_gx rows of the pair table in scripts/auto-play.sh:
#   megadrive/Virtua Racing (USA).zip
#   megadrive/Sonic The Hedgehog (USA, Europe).zip
#   mastersystem/Alex Kidd in Miracle World (USA, Europe, Brazil) (Rev 1).zip
#   gamegear/Sonic Chaos (USA, Europe).zip
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
LIB="${LIB:-/Volumes/MuOs/ROMS}"
SD="${SD:-/mnt/sdcard}"
ADB="${ADB:-adb}"
MINUTES="${MINUTES:-2}"
RUNS="${RUNS:-1}"
DATE="${DATE:-$(date +%Y-%m-%d)}"
export SD ADB MINUTES RUNS DATE

die() {
	echo "slot-nes-snes: $*" >&2
	exit 1
}
shq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

carts="MD|megadrive/Virtua Racing (USA).zip
MD|megadrive/Sonic The Hedgehog (USA, Europe).zip
SMS|mastersystem/Alex Kidd in Miracle World (USA, Europe, Brazil) (Rev 1).zip
GG|gamegear/Sonic Chaos (USA, Europe).zip"

[ -d "$LIB" ] || die "no ROM library at $LIB (set LIB)"
[ "$($ADB get-state 2>/dev/null)" = device ] || die "no adb device in state device, connect the RG34XXSP"

if [ -z "${NODEPLOY:-}" ]; then
	(cd "$root" && task deploy:device SD="$SD")
	n=0
	until [ "$($ADB shell "[ -f $(shq "$SD/Config/slot.state") ] && echo yes" </dev/null 2>/dev/null | tr -d '\r')" = yes ]; do
		[ "$n" -lt 90 ] || die "slot did not come up after the reboot (no $SD/Config/slot.state)"
		sleep 2
		n=$((n + 2))
	done
fi
[ "$($ADB shell "[ -f $(shq "$SD/System/genesis_plus_gx_libretro.so") ] && echo yes" </dev/null 2>/dev/null | tr -d '\r')" = yes ] ||
	die "no genesis_plus_gx_libretro.so in $SD/System, deploy first"

stage="$(mktemp -d "${TMPDIR:-/tmp}/sega-check.XXXXXX")"
trap 'rm -rf "$stage"' EXIT
while IFS='|' read -r dir zip; do
	[ -f "$LIB/$zip" ] || {
		echo "  missing in the library, skipped: $zip" >&2
		continue
	}
	rom="$(unzip -Z1 "$LIB/$zip" | grep -iE '\.(gg|sms|md|gen|bin)$' | head -n 1)"
	[ -n "$rom" ] || {
		echo "  no ROM inside $zip, skipped" >&2
		continue
	}
	dest="$SD/Games/$dir/$rom"
	# This device's adbd does not pass the shell's exit status back, so read an answer instead.
	if [ "$($ADB shell "[ -f $(shq "$dest") ] && echo yes" </dev/null 2>/dev/null | tr -d '\r')" = yes ]; then
		echo "  on the card already: Games/$dir/$rom"
		continue
	fi
	mkdir -p "$stage/$dir"
	unzip -q -o "$LIB/$zip" "$rom" -d "$stage/$dir"
	$ADB shell "mkdir -p $(shq "$SD/Games/$dir")" </dev/null >/dev/null
	$ADB push "$stage/$dir/$rom" "$dest" </dev/null >/dev/null || die "adb push of $rom failed"
	rm -f "$stage/$dir/$rom"
	echo "  pushed Games/$dir/$rom"
done <<EOF2
$carts
EOF2

CORE=genesis_plus_gx sh "$root/scripts/auto-play.sh"

eval="$root/docs/perf/$DATE/play-eval.md"
[ -f "$eval" ] || die "no $eval, see the auto-play output above"
echo
echo "== Sega rows of $eval (median / worst over runs)"
awk '
/^## / { section = substr($0, 4) }
/^\| (md|sms|gg)-genesis_plus_gx/ && section ~ /^(Boot to first frame|Insert or resume|Audio starved samples, session|Audio dropped samples, session|Work per frame|Present interval|Presents that missed|Crash)/ {
	split($0, c, "|"); gsub(/ /, "", c[2]); printf "%-60s %-28s median %s worst %s\n", section, c[2], c[4], c[5]
}' "$eval"
