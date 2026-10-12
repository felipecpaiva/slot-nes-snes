#!/bin/sh
# T13: check a release zip before it ships. Fails on every missing piece it finds, not just the first.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

cores="mgba gpsp fceumm"
# Games/ folders the zip may hold. SNES joins in issue 12.
games="GBA GB GBC NES"
# Folders that ship empty, the user's own data lives there.
empty="Config Saves States Labels BIOS Wallpapers"

usage() {
	echo "usage: $0 ZIP" >&2
	exit 2
}

[ $# -eq 1 ] && [ -n "$1" ] || usage
zip="$1"
[ -f "$zip" ] || zip="$root/build/$1"
[ -f "$zip" ] || {
	echo "zip-check: $1 not found" >&2
	exit 1
}

failed=0
bad() {
	echo "zip-check: $*" >&2
	failed=1
}

need() {
	for pattern in "$@"; do
		set -- "$lic"/$pattern
		[ -f "$1" ] || bad "System/licenses/$pattern is missing"
	done
}

aarch64() {
	is_aarch64 "$1" || bad "${1#"$d"/} is not an aarch64 ELF: $(file -b "$1")"
}

release="$(release_name)"
want="$release"
src="slot-nes-snes-src-${release#slot-nes-snes-}"
tops="$(unzip -Z1 "$zip" | cut -d/ -f1 | sort -u)"
[ "$(printf '%s\n' "$tops" | wc -l | tr -d ' ')" = 1 ] || {
	bad "expected one top folder, found: $(printf '%s' "$tops" | tr '\n' ' ')"
	exit 1
}
[ "$tops" = "$want" ] || bad "top folder is $tops, SLOT_PIN and VERSION want $want"
[ "$(basename "$zip")" = "$want-h700.zip" ] || bad "zip is named $(basename "$zip"), want $want-h700.zip"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
unzip -q "$zip" -d "$work"
d="$work/$tops"
sys="$d/System"
lic="$sys/licenses"

# A symlink in a release zip can point anywhere on the machine that unpacks it.
find "$d" -type l | while read -r l; do echo "zip-check: symlink in zip: ${l#"$d"/}" >&2; done
[ -z "$(find "$d" -type l)" ] || failed=1

for dir in System $empty $(for g in $games; do echo "Games/$g"; done); do
	[ -d "$d/$dir" ] || bad "$dir/ is missing"
done
for dir in $empty; do
	[ -z "$(find "$d/$dir" ! -type d 2>/dev/null)" ] || bad "$dir/ must hold no files: $(find "$d/$dir" ! -type d | sed "s|^$d/||" | tr '\n' ' ')"
done
for g in "$d"/Games/*; do
	[ -e "$g" ] || continue
	case " $games " in *" $(basename "$g") "*) ;; *) bad "Games/$(basename "$g") is not a folder this release ships ($games)" ;; esac
done

# System/ holds exactly this set: upstream's dist output plus our core and licence files.
req="bezels/640x480.png bootlogo.bmp coresave.sh launch_frontend.sh led.sh slotlink.sh slot
mgba_libretro.so gpsp_libretro.so fceumm_libretro.so"
for f in $req; do
	[ -f "$sys/$f" ] || bad "System/$f is missing"
done
find "$sys" ! -type d | sed "s|^$sys/||" | sort | while read -r f; do
	case $f in
	bezels/640x480.png | bootlogo.bmp | coresave.sh | launch_frontend.sh | led.sh | slotlink.sh | slot) ;;
	mgba_libretro.so | gpsp_libretro.so | fceumm_libretro.so) ;;
	licenses/bezel-CC-BY-SA-4.0.txt | licenses/shaders.txt) ;;
	licenses/mgba-MPL-2.0.txt | licenses/mgba-*.meta | licenses/mgba-*.patch) ;;
	licenses/gpsp-GPL-2.0.txt | licenses/gpsp-*.meta | licenses/gpsp-*.tar.gz | licenses/gpsp-*.patch) ;;
	licenses/fceumm_libretro.so.meta | licenses/fceumm-src.meta | licenses/fceumm-src.tar.gz) ;;
	licenses/fceumm-GPL-2.0.txt | licenses/fceumm-headerless-files.txt) ;;
	licenses/slot-nes-snes-*.patch | "licenses/$src.tar.gz") ;;
	*) echo "zip-check: System/$f is not expected in a release" >&2 ;;
	esac
done 2>"$work/stray"
if [ -s "$work/stray" ]; then
	cat "$work/stray" >&2
	failed=1
fi

for f in "$sys/slot" "$sys"/*_libretro.so; do
	[ ! -f "$f" ] || [ -x "$f" ] || bad "${f#"$d"/} is not executable"
done

[ -x "$sys/slot" ] || bad "System/slot is missing or not executable"
[ ! -f "$sys/slot" ] || aarch64 "$sys/slot"

for f in "$sys"/*_libretro.*; do
	[ -e "$f" ] || continue
	core="$(basename "$f")"
	core="${core%%_libretro.*}"
	case " $cores " in *" $core "*) ;; *) bad "$(basename "$f") is not a core this release ships ($cores)" ;; esac
	case $f in *.so) aarch64 "$f" ;; *) bad "$(basename "$f") is not a device core (.so)" ;; esac
done

for core in $cores; do
	[ -f "$sys/${core}_libretro.so" ] || bad "System/${core}_libretro.so is missing"
	case $core in
	mgba) need 'mgba-*.meta' mgba-MPL-2.0.txt ;;
	gpsp) need 'gpsp-*.tar.gz' 'gpsp-*.meta' gpsp-GPL-2.0.txt ;;
	fceumm) need fceumm_libretro.so.meta fceumm-src.tar.gz fceumm-src.meta fceumm-GPL-2.0.txt fceumm-headerless-files.txt ;;
	*) bad "no file list for core $core in zip-check.sh" ;;
	esac
done

need 'slot-nes-snes-*.patch'
n="$(find "$lic" -name 'slot-nes-snes-src-*' | wc -l | tr -d ' ')"
if [ "$n" != 1 ] || [ ! -f "$lic/$src.tar.gz" ]; then
	bad "System/licenses must hold exactly one slot-nes-snes-src-*, named $src.tar.gz"
else
	list="$(tar -tzf "$lic/$src.tar.gz")"
	for f in slot/crates/slot-store/src/platform_policy.rs slot/crates/slot-retro/src/canvas.rs \
		slot-nes-snes/patches/0001-step0-exhaustive-matches.patch; do
		printf '%s\n' "$list" | grep -qxF "$src/$f" || bad "$src.tar.gz does not hold $f"
	done
fi

[ "$failed" = 0 ] || exit 1
echo "zip-check: $(basename "$zip") ok"
