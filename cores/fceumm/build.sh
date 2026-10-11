#!/bin/sh
# Fetch, verify and build libretro-fceumm from its pinned source tarball. The tarball is the
# GPL-2.0 corresponding source and ships beside the core. OUT ending .dylib builds for macOS,
# OUT ending .so builds for the device (run it through scripts/device-sh.sh).
set -eu

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"

device_cflags="-mcpu=cortex-a53"

usage() {
	echo "usage: $0 fetch COMMIT TARBALL | stamp COMMIT host|device | build COMMIT TARBALL WORKDIR OUT" >&2
	exit 2
}

sha256() {
	if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi |
		cut -d' ' -f1
}

pin() {
	. "$root/SLOT_PIN"
	: "${fceumm_commit:?SLOT_PIN lacks fceumm_commit}"
	: "${fceumm_tarball_sha256:?SLOT_PIN lacks fceumm_tarball_sha256}"
	if [ "$1" != "$fceumm_commit" ]; then
		echo "slot-nes-snes: fceumm commit $1 is not the pinned $fceumm_commit" >&2
		exit 1
	fi
}

verify() {
	got="$(sha256 "$1")"
	if [ "$got" != "$fceumm_tarball_sha256" ]; then
		echo "slot-nes-snes: $1 has sha256 $got, SLOT_PIN wants $fceumm_tarball_sha256" >&2
		exit 1
	fi
}

stamp() {
	pin "$1"
	echo "commit=$1"
	echo "source=https://github.com/libretro/libretro-fceumm/archive/$1.tar.gz"
	echo "source_sha256=$fceumm_tarball_sha256"
	case "$2" in
	host) echo "recipe=make -f Makefile.libretro platform=osx" ;;
	device)
		echo "recipe=make -f Makefile.libretro platform=unix"
		echo "device_cflags=$device_cflags"
		;;
	*) usage ;;
	esac
}

fetch() {
	pin "$1"
	mkdir -p "$(dirname "$2")"
	curl -fsSL -o "$2" "https://github.com/libretro/libretro-fceumm/archive/$1.tar.gz"
	verify "$2"
}

build() {
	rev="$1" tarball="$2" work="$3" out="$4"
	src="$work/libretro-fceumm-$rev"
	pin "$rev"
	verify "$tarball"

	case "$out" in
	*.dylib) kind=host platform=osx want='Mach-O 64-bit dynamically linked shared library arm64' ;;
	*.so) kind=device platform=unix want='ELF 64-bit LSB shared object, ARM aarch64' ;;
	*) usage ;;
	esac

	rm -rf "$work"
	mkdir -p "$work"
	tar -xzf "$tarball" -C "$work"
	if [ ! -f "$src/Makefile.libretro" ]; then
		echo "$tarball does not hold libretro-fceumm-$rev/Makefile.libretro" >&2
		exit 1
	fi

	if [ "$kind" = device ]; then
		command -v make >/dev/null 2>&1 || { apt-get update -qq && apt-get install -y -qq build-essential; }
		CFLAGS="$device_cflags" CXXFLAGS="$device_cflags" make -C "$src" -f Makefile.libretro \
			platform=$platform GIT_VERSION="-$(printf %s "$rev" | cut -c1-7)" \
			-j"$(getconf _NPROCESSORS_ONLN)"
	else
		make -C "$src" -f Makefile.libretro platform=$platform \
			GIT_VERSION="-$(printf %s "$rev" | cut -c1-7)" \
			-j"$(getconf _NPROCESSORS_ONLN)"
	fi

	built="$src/fceumm_libretro.${out##*.}"
	if ! file "$built" | grep -q "$want"; then
		echo "slot-nes-snes: $built is not '$want': $(file "$built")" >&2
		exit 1
	fi

	mkdir -p "$(dirname "$out")"
	cp "$built" "$out"
	stamp "$rev" "$kind" >"$out.meta"
}

case "${1:-}" in
fetch)
	[ $# -eq 3 ] && [ -n "$2" ] && [ -n "$3" ] || usage
	fetch "$2" "$3"
	;;
stamp)
	[ $# -eq 3 ] && [ -n "$2" ] || usage
	stamp "$2" "$3"
	;;
build)
	[ $# -eq 5 ] && [ -n "$2" ] && [ -n "$3" ] && [ -n "$4" ] && [ -n "$5" ] || usage
	build "$2" "$3" "$4" "$5"
	;;
*)
	usage
	;;
esac
