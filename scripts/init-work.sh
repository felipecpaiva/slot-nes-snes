#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
work="$root/work/slot"

. "$root/scripts/lib.sh"
read_pin

usage() {
	echo "usage: $0" >&2
	exit 2
}

init() {
	if [ -e "$work/.git" ]; then
		echo "slot-nes-snes: $work is already a git checkout, use task work:resume or delete work/slot yourself" >&2
		exit 1
	fi
	short="$(printf %s "$commit" | cut -c1-7)"
	sh "$root/scripts/fetch-slot.sh" fetch "$work"
	git -C "$work" init -q -b nes-snes
	own_repo "$work" || { echo "slot-nes-snes: git init did not make $work its own repo" >&2; exit 1; }
	git -C "$work" add -A -f -- . ':!vendor'
	GIT_AUTHOR_NAME=slot-nes-snes GIT_COMMITTER_NAME=slot-nes-snes \
		GIT_AUTHOR_EMAIL=slot-nes-snes@users.noreply.github.com \
		GIT_COMMITTER_EMAIL=slot-nes-snes@users.noreply.github.com \
		GIT_AUTHOR_DATE="2000-01-01T00:00:00Z" GIT_COMMITTER_DATE="2000-01-01T00:00:00Z" \
		git -C "$work" -c commit.gpgsign=false commit -q -m "slot $tag ($short)"
	git -C "$work" tag "slot-$tag"
	git -C "$work" log --oneline -1 nes-snes
}

[ $# -eq 0 ] || usage
init
