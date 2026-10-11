#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
up="$root/build/slot-upstream"
ours="$root/build/slot"

[ -d "$up/crates" ] && [ -d "$ours/crates" ] || {
	echo "slot-nes-snes: run task upstream:build and task build first" >&2
	exit 1
}

edition="$(sed -n 's/^edition = "\(.*\)"/\1/p' "$up/Cargo.toml" | head -n 1)"
: "${edition:?upstream Cargo.toml lacks an edition}"

files="$(cd "$ours" && find crates -name '*.rs' | sort | while read -r f; do
	[ -f "$up/$f" ] && cmp -s "$up/$f" "$ours/$f" || echo "$f"
done)"

if [ -z "$files" ]; then
	echo "format: no new or changed .rs files, nothing to check"
	exit 0
fi

echo "format: checking files we add or change (edition $edition):"
echo "$files" | sed 's/^/  /'
cd "$ours"
echo "$files" | tr '\n' '\0' | xargs -0 rustfmt --check --edition "$edition" || {
	echo "slot-nes-snes: files we add or change are not rustfmt clean" >&2
	exit 1
}
echo "format: ok"
