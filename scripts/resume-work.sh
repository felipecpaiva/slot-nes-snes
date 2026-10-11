#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
work="$root/work/slot"

. "$root/scripts/lib.sh"

usage() {
	echo "usage: $0" >&2
	exit 2
}

resume() {
	if ! own_repo "$work"; then
		echo "slot-nes-snes: $work is not a git checkout, run task work:init" >&2
		exit 1
	fi
	if ! git -C "$work" rev-parse -q --verify HEAD >/dev/null; then
		echo "slot-nes-snes: $work has no commits, run task work:init first" >&2
		exit 1
	fi
	if [ "$(git -C "$work" rev-list --count HEAD)" != 1 ] || [ -n "$(git -C "$work" status --porcelain)" ]; then
		echo "slot-nes-snes: $work is not a fresh base checkout, delete work/slot and run task work:init" >&2
		exit 1
	fi
	for p in "$root"/patches/*.patch; do
		[ -f "$p" ] || continue
		GIT_COMMITTER_NAME=slot-nes-snes GIT_COMMITTER_EMAIL=slot-nes-snes@users.noreply.github.com \
			GIT_COMMITTER_DATE="2000-01-01T00:00:00Z" \
			git -C "$work" -c commit.gpgsign=false am -q --whitespace=nowarn "$p" ||
			{
				git -C "$work" am --abort >/dev/null 2>&1 || true
				echo "slot-nes-snes: $(basename "$p") does not apply to $work, aborted the am and left the work tree as it was" >&2
				exit 1
			}
	done
	git -C "$work" log --oneline nes-snes
}

[ $# -eq 0 ] || usage
resume
