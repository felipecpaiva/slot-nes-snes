#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
work="$root/work/slot"
branch="nes-snes"

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

rm -f "$root"/patches/*.patch
git -C "$work" format-patch -q --binary --no-signature --zero-commit \
	-o "$root/patches" "$base..$branch"
ls "$root/patches"
