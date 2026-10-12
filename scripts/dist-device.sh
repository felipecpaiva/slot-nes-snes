#!/bin/sh
# Build build/dist/<release name>/ for the H700: slot's own dist:device, run unmodified inside
# rust:1-bullseye with the whole repo mounted (so the relative build/slot/vendor symlink resolves),
# then add the cores slot does not know about, with their .meta, source and licences.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

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
	is_aarch64 "$root/vendor/fceumm_libretro.so" || {
		echo "slot-nes-snes: vendor/fceumm_libretro.so is not an aarch64 ELF" >&2
		exit 1
	}
}

# Upstream's core:gpsp downloads the gpSP tarball with no checksum, deletes any cached one first, and
# its status check cannot be satisfied from outside, so the file is checked here, against
# gpsp_tarball_sha256 in SLOT_PIN, once upstream's dist is done. A bad one removes the dist tree and
# every gpSP artifact in vendor/ so no cache is left for upstream's status check to trust.
check_gpsp_tarball() {
	: "${gpsp_tarball_sha256:?SLOT_PIN lacks gpsp_tarball_sha256}"
	gc="$(slot_var GPSP_COMMIT)"
	[ -n "$gc" ] || {
		echo "slot-nes-snes: no GPSP_COMMIT in build/slot/taskfile.yml" >&2
		exit 1
	}
	for f in "$root/vendor/gpsp-src.tar.gz" "$root/$dist/System/licenses/gpsp-$gc.tar.gz"; do
		got="$(shasum -a 256 "$f" 2>/dev/null | cut -d' ' -f1)"
		[ "$got" = "$gpsp_tarball_sha256" ] || {
			rm -rf "$root/$dist" "$root"/vendor/gpsp_libretro.so* "$root"/vendor/gpsp-src.*
			echo "slot-nes-snes: ${f#"$root"/} has sha256 '$got', SLOT_PIN gpsp_tarball_sha256 wants $gpsp_tarball_sha256 (gpSP $gc), removed the dist tree and the gpSP cache" >&2
			exit 1
		}
	done
}

build() {
	name="$(release_name)"
	dist="build/dist/$name"
	check_fceumm
	task_bin="$(sh "$root/scripts/fetch-task.sh")"

	DEVICE_ROOT=1 sh "$root/scripts/device-sh.sh" "'${task_bin#"$root"/}' -d build/slot dist:device OUT=../dist/$name"

	check_gpsp_tarball

	sys="$root/$dist/System"
	cp "$root/vendor/fceumm_libretro.so" "$sys/"
	cp "$root/vendor/fceumm_libretro.so.meta" "$root/vendor/fceumm-src.tar.gz" \
		"$root/vendor/fceumm-src.meta" "$sys/licenses/"
	for f in "$root"/licenses/*; do
		[ -f "$f" ] && [ ! -L "$f" ] && cp "$f" "$sys/licenses/"
	done
	for p in "$root"/patches/*.patch; do
		cp "$p" "$sys/licenses/slot-nes-snes-$(basename "$p")"
	done
	(cd "$sys" && shasum -a 256 mgba_libretro.so gpsp_libretro.so fceumm_libretro.so >licenses/cores.sha256)
	echo "device tree ready at $dist"
}

[ $# -eq 0 ] || usage
build
