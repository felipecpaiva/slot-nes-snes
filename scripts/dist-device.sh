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

check_cores() {
	for f in vendor/fceumm_libretro.so vendor/fceumm_libretro.so.meta vendor/fceumm-src.tar.gz \
		vendor/fceumm-src.meta licenses/fceumm-GPL-2.0.txt licenses/fceumm-headerless-files.txt \
		vendor/snes9x_libretro.so vendor/snes9x_libretro.so.meta vendor/snes9x-src.tar.gz \
		vendor/snes9x-src.meta licenses/snes9x-LICENSE.txt \
		vendor/nestopia_libretro.so vendor/nestopia_libretro.so.meta vendor/nestopia-src.tar.gz \
		vendor/nestopia-src.meta licenses/nestopia-GPL-2.0.txt \
		vendor/snes9x2005_plus_libretro.so vendor/snes9x2005_plus_libretro.so.meta \
		vendor/snes9x2005_plus-src.tar.gz vendor/snes9x2005_plus-src.meta licenses/snes9x2005-LICENSE.txt \
		vendor/genesis_plus_gx_libretro.so vendor/genesis_plus_gx_libretro.so.meta \
		vendor/genesis_plus_gx-src.tar.gz vendor/genesis_plus_gx-src.meta licenses/genesis_plus_gx-LICENSE.txt \
		vendor/pcsx_rearmed_libretro.so vendor/pcsx_rearmed_libretro.so.meta \
		vendor/pcsx_rearmed-src.tar.gz vendor/pcsx_rearmed-src.meta licenses/pcsx_rearmed-GPL-2.0.txt; do
		[ -f "$root/$f" ] || missing "$f"
	done
	for c in fceumm snes9x nestopia snes9x2005_plus genesis_plus_gx pcsx_rearmed; do
		is_aarch64 "$root/vendor/${c}_libretro.so" || {
			echo "slot-nes-snes: vendor/${c}_libretro.so is not an aarch64 ELF" >&2
			exit 1
		}
	done
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
		got="$(file_sha256 "$f" 2>/dev/null)"
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
	check_cores
	task_bin="$(sh "$root/scripts/fetch-task.sh")"

	DEVICE_ROOT=1 sh "$root/scripts/device-sh.sh" "'${task_bin#"$root"/}' -d build/slot dist:device OUT=../dist/$name"

	check_gpsp_tarball

	sys="$root/$dist/System"
	cp "$root/vendor/fceumm_libretro.so" "$root/vendor/snes9x_libretro.so" \
		"$root/vendor/nestopia_libretro.so" "$root/vendor/snes9x2005_plus_libretro.so" \
		"$root/vendor/genesis_plus_gx_libretro.so" "$root/vendor/pcsx_rearmed_libretro.so" "$sys/"
	cp "$root/vendor/fceumm_libretro.so.meta" "$root/vendor/fceumm-src.tar.gz" \
		"$root/vendor/fceumm-src.meta" "$root/vendor/snes9x_libretro.so.meta" \
		"$root/vendor/snes9x-src.tar.gz" "$root/vendor/snes9x-src.meta" \
		"$root/vendor/nestopia_libretro.so.meta" "$root/vendor/nestopia-src.tar.gz" "$root/vendor/nestopia-src.meta" \
		"$root/vendor/snes9x2005_plus_libretro.so.meta" "$root/vendor/snes9x2005_plus-src.tar.gz" \
		"$root/vendor/snes9x2005_plus-src.meta" "$root/vendor/genesis_plus_gx_libretro.so.meta" \
		"$root/vendor/genesis_plus_gx-src.tar.gz" "$root/vendor/genesis_plus_gx-src.meta" \
		"$root/vendor/pcsx_rearmed_libretro.so.meta" "$root/vendor/pcsx_rearmed-src.tar.gz" \
		"$root/vendor/pcsx_rearmed-src.meta" "$sys/licenses/"
	for f in "$root"/licenses/*; do
		[ -f "$f" ] && [ ! -L "$f" ] && cp "$f" "$sys/licenses/"
	done
	for p in "$root"/patches/*.patch; do
		cp "$p" "$sys/licenses/slot-nes-snes-$(basename "$p")"
	done
	(cd "$sys" && $(command -v sha256sum >/dev/null 2>&1 && echo sha256sum || echo shasum -a 256) mgba_libretro.so gpsp_libretro.so fceumm_libretro.so snes9x_libretro.so \
		nestopia_libretro.so snes9x2005_plus_libretro.so genesis_plus_gx_libretro.so \
		pcsx_rearmed_libretro.so >licenses/cores.sha256)
	echo "device tree ready at $dist"
}

[ $# -eq 0 ] || usage
build
