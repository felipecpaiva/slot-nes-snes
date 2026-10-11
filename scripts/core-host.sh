#!/bin/sh
# Fail unless the fetched gpSP host dylib has the sha256 SLOT_PIN records for this machine's
# architecture as gpsp_host_sha256_<arch> (arm64 or x86_64). To accept a new build on purpose, or to
# support a new architecture, update that line in SLOT_PIN.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
	echo "usage: $0 [DYLIB]   (default vendor/gpsp_libretro.dylib)" >&2
	exit 2
}

[ $# -le 1 ] || usage
dylib="${1:-$root/vendor/gpsp_libretro.dylib}"
[ -f "$dylib" ] || {
	echo "slot-nes-snes: $dylib is missing, run task core:host" >&2
	exit 1
}

case "$(uname -m)" in
arm64 | aarch64) arch=arm64 ;;
x86_64) arch=x86_64 ;;
*) echo "slot-nes-snes: unsupported architecture $(uname -m), gpsp host dylib is pinned for arm64 and x86_64" >&2; exit 1 ;;
esac
key="gpsp_host_sha256_$arch"

. "$root/SLOT_PIN"
eval "want=\${$key:-}"
[ -n "$want" ] || {
	echo "slot-nes-snes: SLOT_PIN lacks $key, fetch the gpSP host dylib on this $arch machine and add the line with its sha256 (shasum -a 256 vendor/gpsp_libretro.dylib)" >&2
	exit 1
}

got="$(shasum -a 256 "$dylib" | cut -d' ' -f1)"
[ "$got" = "$want" ] || {
	echo "slot-nes-snes: $dylib has sha256 $got, SLOT_PIN $key wants $want, update SLOT_PIN if the change is on purpose" >&2
	exit 1
}
echo "gpsp host dylib matches SLOT_PIN ($got)"
