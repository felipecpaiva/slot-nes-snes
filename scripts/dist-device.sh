#!/bin/sh
# Build build/dist/<release name>/ for the H700: slot's own dist:device, run unmodified inside
# rust:1-bullseye with the whole repo mounted (so the relative build/slot/vendor symlink resolves),
# then add the cores slot does not know about, with their .meta, source and licences.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

task_version=v3.54.0

usage() {
	echo "usage: $0" >&2
	exit 2
}

missing() {
	echo "slot-nes-snes: $1 is missing, run task core:device" >&2
	exit 1
}

check_fceumm() {
	for f in vendor/fceumm_libretro.so vendor/fceumm_libretro.so.meta vendor/fceumm-src.tar.gz \
		vendor/fceumm-src.meta licenses/fceumm-GPL-2.0.txt licenses/fceumm-headerless-files.txt; do
		[ -f "$root/$f" ] || missing "$f"
	done
	file "$root/vendor/fceumm_libretro.so" | grep -q 'ELF 64-bit.*aarch64' || {
		echo "slot-nes-snes: vendor/fceumm_libretro.so is not an aarch64 ELF" >&2
		exit 1
	}
}

build() {
	name="$(release_name)"
	dist="build/dist/$name"
	check_fceumm

	DEVICE_ROOT=1 sh "$root/scripts/device-sh.sh" "
		test -x build/task-linux/task ||
			curl -fsSL https://taskfile.dev/install.sh | sh -s -- -b build/task-linux $task_version
		build/task-linux/task -d build/slot dist:device OUT=../dist/$name"

	sys="$root/$dist/System"
	cp "$root/vendor/fceumm_libretro.so" "$sys/"
	cp "$root/vendor/fceumm_libretro.so.meta" "$root/vendor/fceumm-src.tar.gz" \
		"$root/vendor/fceumm-src.meta" "$sys/licenses/"
	cp "$root"/licenses/* "$sys/licenses/"
	for p in "$root"/patches/*.patch; do
		cp "$p" "$sys/licenses/slot-nes-snes-$(basename "$p")"
	done
	echo "device tree ready at $dist"
}

[ $# -eq 0 ] || usage
build
