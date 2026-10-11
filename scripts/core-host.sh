#!/bin/sh
# Fail unless the fetched gpSP host dylib has the sha256 SLOT_PIN records as gpsp_host_sha256.
# To accept a new build on purpose, update that line in SLOT_PIN.
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

. "$root/SLOT_PIN"
: "${gpsp_host_sha256:?SLOT_PIN lacks gpsp_host_sha256}"

got="$(shasum -a 256 "$dylib" | cut -d' ' -f1)"
[ "$got" = "$gpsp_host_sha256" ] || {
	echo "slot-nes-snes: $dylib has sha256 $got, SLOT_PIN gpsp_host_sha256 wants $gpsp_host_sha256, update SLOT_PIN if the change is on purpose" >&2
	exit 1
}
echo "gpsp host dylib matches SLOT_PIN ($got)"
