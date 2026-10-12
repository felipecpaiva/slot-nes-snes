#!/bin/sh
# slot-nes-snes-src-<release>.tar.gz: the patched slot tree at work/slot HEAD plus this repo at HEAD,
# the GPL-3 corresponding source of System/slot. Task runs patches:check first so work/slot HEAD
# is known to be what patches/ rebuild.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

usage() {
	echo "usage: $0" >&2
	exit 2
}

build() {
	name="$(release_name)"
	src="slot-nes-snes-src-${name#slot-nes-snes-}"
	tree="$root/build/dist/$name"

	own_repo "$root/work/slot" || {
		echo "slot-nes-snes: work/slot is not a git checkout, run task work:init" >&2
		exit 1
	}
	[ -d "$tree/System/licenses" ] || {
		echo "slot-nes-snes: $tree is missing, run task dist:device" >&2
		exit 1
	}
	[ -z "$(git -C "$root" status --porcelain --untracked-files=no)" ] ||
		echo "slot-nes-snes: this repo has uncommitted changes, the tarball holds HEAD only" >&2

	stage="$(mktemp -d "$root/build/src-tarball.XXXXXX")"
	trap 'rm -rf "$stage"' EXIT
	mkdir "$stage/$src" "$stage/$src/slot" "$stage/$src/slot-nes-snes"
	git -C "$root/work/slot" archive --format=tar HEAD | tar -x -C "$stage/$src/slot"
	git -C "$root" archive --format=tar HEAD | tar -x -C "$stage/$src/slot-nes-snes"
	tar -czf "$root/build/$src.tar.gz" -C "$stage" "$src"
	cp "$root/build/$src.tar.gz" "$tree/System/licenses/"
	echo "built build/$src.tar.gz and copied it into $tree/System/licenses/"
}

[ $# -eq 0 ] || usage
build
