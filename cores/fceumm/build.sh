#!/bin/sh
# Fetch, verify and build libretro-fceumm from its pinned source tarball. The tarball is the
# corresponding source (see LICENSING.md) and ships beside the core. OUT ending .dylib builds for macOS,
# OUT ending .so builds for the device (run it through scripts/device-sh.sh).
set -eu

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"

device_cflags="-mcpu=cortex-a53"

usage() {
	echo "usage: $0 fetch COMMIT TARBALL | builder | stamp COMMIT host|device | build COMMIT TARBALL WORKDIR OUT" >&2
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
		echo "slot-nes-snes: delete vendor/fceumm-src.* and run task core:fceumm:src" >&2
		exit 1
	fi
}

# What built the core: the container image and its digest for the device, the host cc otherwise.
# FCEUMM_BUILDER is set by the caller (device-sh.sh passes it in), because docker is not
# available inside the container.
builder() {
	if [ "$1" = host ]; then
		cc --version | head -1
	elif [ -n "${FCEUMM_BUILDER:-}" ]; then
		echo "$FCEUMM_BUILDER"
	elif [ "$(uname -s)-$(uname -m)" = "Linux-aarch64" ]; then
		cc --version | head -1
	else
		image=rust:1-bullseye
		digest="$(docker image inspect --format '{{index .RepoDigests 0}}' $image 2>/dev/null ||
			{ docker pull -q $image >/dev/null && docker image inspect --format '{{index .RepoDigests 0}}' $image; })"
		echo "$image $digest"
	fi
}

stamp() {
	pin "$1"
	echo "commit=$1"
	echo "source=https://github.com/libretro/libretro-fceumm/archive/$1.tar.gz"
	echo "source_sha256=$fceumm_tarball_sha256"
	echo "git_version=-$(printf %s "$1" | cut -c1-7)"
	echo "builder=$(builder "$2")"
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
	curl -fsSL -o "$2.part" "https://github.com/libretro/libretro-fceumm/archive/$1.tar.gz"
	(verify "$2.part") || { rm -f "$2.part"; exit 1; }
	mv "$2.part" "$2"
}

build() {
	rev="$1" tarball="$2" work="$3" out="$4"
	src="$work/libretro-fceumm-$rev"
	pin "$rev"
	verify "$tarball"

	case "$out" in
	*.dylib) kind=host platform=osx want="Mach-O 64-bit.*shared library.*$(uname -m)" ;;
	*.so) kind=device platform=unix want='ELF 64-bit LSB shared object, ARM aarch64' ;;
	*) usage ;;
	esac

	command -v make >/dev/null 2>&1 || {
		echo "slot-nes-snes: make is not installed; install it (macOS: xcode-select --install)" >&2
		exit 1
	}

	rm -rf "$work"
	mkdir -p "$work"
	tar -xzf "$tarball" -C "$work"
	if [ ! -f "$src/Makefile.libretro" ]; then
		echo "$tarball does not hold libretro-fceumm-$rev/Makefile.libretro" >&2
		exit 1
	fi

	if [ "$kind" = device ]; then
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
		echo "slot-nes-snes: $built does not match '$want' (host arch is $(uname -m)), got: $(file "$built")" >&2
		exit 1
	fi

	mkdir -p "$(dirname "$out")"
	cp "$built" "$out"
	stamp "$rev" "$kind" >"$out.meta"
	if [ "$kind" = device ]; then
		{
			cat "$out.meta"
			echo "tarball=$(basename "$tarball")"
			echo "tarball_sha256=$(sha256 "$tarball")"
		} >"$(dirname "$tarball")/fceumm-src.meta"
	fi
}

case "${1:-}" in
fetch)
	[ $# -eq 3 ] && [ -n "$2" ] && [ -n "$3" ] || usage
	fetch "$2" "$3"
	;;
builder)
	builder device
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
