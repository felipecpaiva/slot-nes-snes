#!/bin/sh
# T13: check a release zip before it ships. Fails on every missing piece it finds, not just the first.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"

cores="mgba gpsp fceumm"

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
		set -- $lic/$pattern
		[ -f "$1" ] || bad "System/licenses/$pattern is missing"
	done
}

aarch64() {
	file "$1" | grep -q 'ELF 64-bit.*aarch64' || bad "${1#"$d"/} is not an aarch64 ELF: $(file -b "$1")"
}

tops="$(unzip -Z1 "$zip" | cut -d/ -f1 | sort -u)"
[ "$(printf '%s\n' "$tops" | wc -l | tr -d ' ')" = 1 ] || {
	bad "expected one top folder, found: $(printf '%s' "$tops" | tr '\n' ' ')"
	exit 1
}
want="$(basename "$zip" -h700.zip)"
[ "$tops" = "$want" ] || bad "top folder is $tops, the zip name wants $want"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
unzip -q "$zip" -d "$work"
d="$work/$tops"
sys="$d/System"
lic="$sys/licenses"

for dir in System BIOS Config Labels Saves States Wallpapers Games/GBA Games/GB Games/GBC Games/NES; do
	[ -d "$d/$dir" ] || bad "$dir/ is missing"
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

need 'slot-nes-snes-src-*.tar.gz' 'slot-nes-snes-*.patch'
set -- "$lic"/slot-nes-snes-src-*.tar.gz
if [ -f "$1" ]; then
	tar -tzf "$1" | grep -q '/slot/Cargo.toml$' && tar -tzf "$1" | grep -q '/slot-nes-snes/patches/' ||
		bad "$(basename "$1") does not hold slot/ and slot-nes-snes/patches/"
fi

[ "$failed" = 0 ] || exit 1
echo "zip-check: $(basename "$zip") ok"
