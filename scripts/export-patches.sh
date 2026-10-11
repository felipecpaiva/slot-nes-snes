#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
work="$root/work/slot"
branch="nes-snes"

. "$root/scripts/lib.sh"

if ! own_repo "$work"; then
	echo "slot-nes-snes: $work is not a git checkout, run task work:init" >&2
	exit 1
fi
if [ -n "$(git -C "$work" status --porcelain)" ]; then
	echo "slot-nes-snes: $work has uncommitted changes, commit your work in work/slot first" >&2
	exit 1
fi

if ! git -C "$work" rev-parse -q --verify "refs/heads/$branch" >/dev/null; then
	echo "slot-nes-snes: $work has no $branch branch, run task work:init" >&2
	exit 1
fi

base="$(git -C "$work" rev-list --max-parents=0 "$branch")"

git -C "$work" log --format=%H%x20%s "$base..$branch" | while read -r sha subject; do
	if ! printf '%s\n' "$subject" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$'; then
		echo "slot-nes-snes: commit $sha has subject \"$subject\", want a lowercase patch slug like canvas or platform-nes" >&2
		exit 1
	fi
done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git -C "$work" format-patch -q --binary --no-signature --zero-commit -o "$tmp" "$base..$branch"

set -- "$tmp"/*.patch
if [ ! -f "$1" ]; then
	set -- "$root"/patches/*.patch
	if [ -f "$1" ]; then
		echo "slot-nes-snes: $branch has no commits past the base but patches/ has patches, run task work:resume instead of exporting" >&2
		exit 1
	fi
	exit 0
fi

rm -f "$root"/patches/*.patch
mv "$@" "$root/patches/"
ls "$root/patches"
