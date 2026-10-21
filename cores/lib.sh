# Shared by cores/<core>/build.sh (POSIX sh, sourced). The core's script sets only variables:
#   core      name in SLOT_PIN keys, vendor/ names and <core>_libretro.<ext>   (fceumm)
#   repo      upstream repository name under github.com/<owner>                 (libretro-fceumm)
#   owner     optional, the GitHub owner of repo, libretro when empty              (jtothebell)
#   makefile  makefile to pass with -f, empty for the default                   (Makefile.libretro)
#   subdir    directory of the makefile inside the source, empty for the root   (libretro)
#   make_args optional, extra make variables for both builds                        (USE_BLARGG_APU=1)
#   device_ldflags  optional, extra LDFLAGS for the device build only. A C++ core sets
#             "-static-libstdc++ -static-libgcc" because the handheld's OS may lack libstdc++.so.6
#   device_include  optional, a header under the repo root force-included into every device compile
#             (cores/mednafen_pce_fast/glibc-2.17.h pins a libm symbol to its GLIBC_2.17 version)
#   host_cflags  optional, extra CFLAGS for the macOS build only (-Dfdopen=fdopen: zlib 1.2.11 takes the
#             SDK's TARGET_OS_MAC for classic Mac OS and defines fdopen away)
#   modules   optional, git submodules the GitHub archive leaves out, as name:path:owner/repo words
#             (emu2413:pico/sound/emu2413:digital-sound-antiques/emu2413). SLOT_PIN holds
#             <core>_<name>_commit and <core>_<name>_tarball_sha256; the tarball is
#             vendor/<core>-<name>-src.tar.gz, unpacked at path inside the source, and ships beside it
#   source_patch  optional, a patch under the repo root applied with patch -p1 to the unpacked source
#             before both builds (cores/fake08/slot.patch); its path and sha256 go into the stamp
# then calls core_main "$@". SLOT_PIN holds <core>_commit and <core>_tarball_sha256. The tarball is
# the corresponding source (see LICENSING.md) and ships beside the core. OUT ending .dylib builds for
# macOS, OUT ending .so builds for the device (run it through scripts/device-sh.sh).
set -eu

root="$(cd "$(dirname "$0")/../.." && pwd)"
device_cflags="-mcpu=cortex-a53"
device_ldflags="${device_ldflags:-}"
device_include="${device_include:-}"
host_cflags="${host_cflags:-}"
modules="${modules:-}"
owner="${owner:-libretro}"
source_patch="${source_patch:-}"

usage() {
	echo "usage: $0 fetch COMMIT TARBALL | builder | stamp COMMIT host|device | srcmeta COMMIT TARBALL | build COMMIT TARBALL WORKDIR OUT" >&2
	exit 2
}

sha256() {
	if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi |
		cut -d' ' -f1
}

pin() {
	. "$root/SLOT_PIN"
	eval "pin_commit=\${${core}_commit:-} pin_sha=\${${core}_tarball_sha256:-}"
	: "${pin_commit:?SLOT_PIN lacks ${core}_commit}"
	: "${pin_sha:?SLOT_PIN lacks ${core}_tarball_sha256}"
	if [ "$1" != "$pin_commit" ]; then
		echo "slot-nes-snes: $core commit $1 is not the pinned $pin_commit" >&2
		exit 1
	fi
}

verify() {
	want_sha="${2:-$pin_sha}"
	got="$(sha256 "$1")"
	if [ "$got" != "$want_sha" ]; then
		echo "slot-nes-snes: $1 has sha256 $got, SLOT_PIN wants $want_sha" >&2
		echo "slot-nes-snes: delete vendor/$core-src.* and vendor/$core-*-src.* and run task core:$core:src" >&2
		exit 1
	fi
}

# Sets mod_name, mod_path, mod_slug, mod_commit and mod_sha for one name:path:owner/repo word.
module() {
	mod_name="${1%%:*}" mod_rest="${1#*:}"
	mod_path="${mod_rest%%:*}" mod_slug="${mod_rest#*:}"
	. "$root/SLOT_PIN"
	eval "mod_commit=\${${core}_${mod_name}_commit:-} mod_sha=\${${core}_${mod_name}_tarball_sha256:-}"
	: "${mod_commit:?SLOT_PIN lacks ${core}_${mod_name}_commit}"
	: "${mod_sha:?SLOT_PIN lacks ${core}_${mod_name}_tarball_sha256}"
}

module_tarball() {
	echo "$(dirname "$1")/$core-$mod_name-src.tar.gz"
}

# What built the core: the container image and its digest for the device, the host cc otherwise.
# CORE_BUILDER is set by the caller (device-sh.sh passes it in), because docker is not
# available inside the container.
builder() {
	if [ "$1" = host ]; then
		cc --version | head -1
	elif [ -n "${CORE_BUILDER:-}" ]; then
		echo "$CORE_BUILDER"
	elif [ "$(uname -s)-$(uname -m)" = "Linux-aarch64" ]; then
		cc --version | head -1
	else
		image=rust:1-bullseye
		digest="$(docker image inspect --format '{{index .RepoDigests 0}}' $image 2>/dev/null ||
			{ docker pull -q --platform linux/arm64 $image >/dev/null && docker image inspect --format '{{index .RepoDigests 0}}' $image; })"
		echo "$image $digest"
	fi
}

recipe() {
	echo "make${subdir:+ -C $subdir}${makefile:+ -f $makefile} platform=$1${make_args:+ $make_args}"
}

stamp() {
	pin "$1"
	echo "commit=$1"
	echo "source=https://github.com/$owner/$repo/archive/$1.tar.gz"
	echo "source_sha256=$pin_sha"
	if [ -n "$source_patch" ]; then
		echo "source_patch=$source_patch"
		echo "source_patch_sha256=$(sha256 "$root/$source_patch")"
	fi
	echo "git_version=-$(printf %s "$1" | cut -c1-7)"
	for m in $modules; do
		module "$m"
		echo "module_$mod_name=https://github.com/$mod_slug/archive/$mod_commit.tar.gz at $mod_path"
		echo "module_${mod_name}_sha256=$mod_sha"
	done
	echo "builder=$(builder "$2")"
	case "$2" in
	host)
		echo "recipe=$(recipe osx)"
		[ -z "$host_cflags" ] || echo "host_cflags=$host_cflags"
		;;
	device)
		echo "recipe=$(recipe unix)"
		echo "device_cflags=$device_cflags"
		[ -z "$device_ldflags" ] || echo "device_ldflags=$device_ldflags"
		[ -z "$device_include" ] || echo "device_include=$device_include"
		;;
	*) usage ;;
	esac
}

# The device stamp plus the tarball it was built from: what vendor/<core>-src.meta must hold.
srcmeta() {
	stamp "$1" device
	echo "tarball=$(basename "$2")"
	echo "tarball_sha256=$pin_sha"
}

fetch() {
	pin "$1"
	mkdir -p "$(dirname "$2")"
	curl -fsSL -o "$2.part" "https://github.com/$owner/$repo/archive/$1.tar.gz"
	(verify "$2.part") || { rm -f "$2.part"; exit 1; }
	mv "$2.part" "$2"
	for m in $modules; do
		module "$m"
		t="$(module_tarball "$2")"
		curl -fsSL -o "$t.part" "https://github.com/$mod_slug/archive/$mod_commit.tar.gz"
		(verify "$t.part" "$mod_sha") || { rm -f "$t.part"; exit 1; }
		mv "$t.part" "$t"
	done
}

build() {
	rev="$1" tarball="$2" work="$3" out="$4"
	src="$work/$repo-$rev"
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
	for m in $modules; do
		module "$m"
		t="$(module_tarball "$tarball")"
		verify "$t" "$mod_sha"
		mkdir -p "$src/$mod_path"
		tar -xzf "$t" -C "$src/$mod_path" --strip-components=1
	done
	if [ -n "$source_patch" ]; then
		patch -s -p1 -d "$src" <"$root/$source_patch"
	fi
	mdir="$src${subdir:+/$subdir}"
	if [ ! -f "$mdir/${makefile:-Makefile}" ]; then
		echo "$tarball does not hold $repo-$rev/${subdir:+$subdir/}${makefile:-Makefile}" >&2
		exit 1
	fi

	# CFLAGS and CXXFLAGS come in through the environment so the makefiles' += keeps them.
	if [ "$kind" = device ]; then
		export CFLAGS="$device_cflags" CXXFLAGS="$device_cflags"
		if [ -n "$device_include" ]; then
			CFLAGS="$CFLAGS -include $root/$device_include" CXXFLAGS="$CXXFLAGS -include $root/$device_include"
		fi
		[ -z "$device_ldflags" ] || export LDFLAGS="$device_ldflags"
	elif [ -n "$host_cflags" ]; then
		export CFLAGS="$host_cflags" CXXFLAGS="$host_cflags"
	fi
	make -C "$mdir" ${makefile:+-f "$makefile"} platform=$platform ${make_args:-} \
		GIT_VERSION="-$(printf %s "$rev" | cut -c1-7)" \
		-j"$(getconf _NPROCESSORS_ONLN)"

	built="$mdir/${core}_libretro.${out##*.}"
	if ! file "$built" | grep -q "$want"; then
		echo "slot-nes-snes: $built does not match '$want' (host arch is $(uname -m)), got: $(file "$built")" >&2
		exit 1
	fi

	mkdir -p "$(dirname "$out")"
	cp "$built" "$out"
	stamp "$rev" "$kind" >"$out.meta"
	if [ "$kind" = device ]; then
		srcmeta "$rev" "$tarball" >"$(dirname "$tarball")/$core-src.meta"
	fi
}

core_main() {
	case "${1:-}" in
	fetch)
		[ $# -eq 3 ] && [ -n "$2" ] && [ -n "$3" ] || usage
		fetch "$2" "$3"
		;;
	builder)
		builder device
		;;
	srcmeta)
		[ $# -eq 3 ] && [ -n "$2" ] && [ -n "$3" ] || usage
		srcmeta "$2" "$3"
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
}
