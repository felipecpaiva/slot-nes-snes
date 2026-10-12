#!/bin/sh
# slot-nes-snes-src-<release>.tar.gz: the patched slot tree at work/slot HEAD plus this repo at HEAD,
# the GPL-3 corresponding source of System/slot. Task runs patches:check first so work/slot HEAD
# is known to be what patches/ rebuild. Reproducible: sorted names, owner 0, every mtime the
# commit time of this repo's HEAD (SOURCE_DATE_EPOCH if set), gzip -n. bsdtar (macOS) has no
# --mtime or --sort, so the staged files are touched and the names listed in order instead.
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

	epoch="${SOURCE_DATE_EPOCH:-$(git -C "$root" log -1 --format=%ct HEAD)}"
	stamp="$(date -u -r "$epoch" +%Y%m%d%H%M.%S 2>/dev/null || date -u -d "@$epoch" +%Y%m%d%H%M.%S)"
	find "$stage" -exec touch -h -t "$stamp" {} +
	(cd "$stage" && find "$src" | LC_ALL=C sort >list)
	if tar --version | grep -q bsdtar; then
		own="--uid 0 --gid 0 --uname root --gname root --no-xattrs --format gnutar"
	else
		own="--owner=0 --group=0 --numeric-owner"
	fi
	# shellcheck disable=SC2086
	(cd "$stage" && COPYFILE_DISABLE=1 tar -cf - $own --no-recursion -T list) | gzip -n >"$root/build/$src.tar.gz"
	cp "$root/build/$src.tar.gz" "$tree/System/licenses/"
	echo "built build/$src.tar.gz and copied it into $tree/System/licenses/"
}

[ $# -eq 0 ] || usage
build
