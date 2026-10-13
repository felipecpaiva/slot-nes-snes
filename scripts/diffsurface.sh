#!/bin/sh
# Per upstream file changed by patches/, the net changed lines (added + removed) between the pinned
# slot release and the release with every patch applied, and the touch-point map with one row per
# changed hunk (docs/UPSTREAM-TOUCHPOINTS.md, rendered by scripts/touchpoints.py). There is no line
# limit; every touch point must be in the map with a reason (CONTRIBUTING.md, docs/DECISIONS.md).
#   sh scripts/diffsurface.sh          print the counts and rewrite docs/UPSTREAM-TOUCHPOINTS.md
#   sh scripts/diffsurface.sh --check  fail if the committed map is stale or a row has no reason
# Env: SLOT_TARBALL (pinned release tarball, default build/slot-<commit>.tar.gz or a download),
#      PATCHES_DIR (default patches/).
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

check=0
[ "${1:-}" = --check ] && check=1
map="$root/docs/UPSTREAM-TOUCHPOINTS.md"
patches="${PATCHES_DIR:-$root/patches}"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/slot-nes-snes.XXXXXX")"
trap 'rm -rf "$tmp" 2>/dev/null || true' EXIT
# no background git gc in the scratch repo: it can still be writing when the trap removes it
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=gc.auto GIT_CONFIG_VALUE_0=0

tarball="${SLOT_TARBALL:-$root/build/slot-$commit.tar.gz}"
if [ -n "${SLOT_TARBALL:-}" ] && [ ! -f "$tarball" ]; then
	echo "slot-nes-snes: SLOT_TARBALL $tarball does not exist" >&2
	exit 1
fi
if [ ! -f "$tarball" ]; then
	tarball="$tmp/slot.tar.gz"
	curl -fsSL -o "$tarball" "https://github.com/BrandonKowalski/slot/archive/$commit.tar.gz"
fi
got="$(file_sha256 "$tarball")"
[ "$got" = "$tarball_sha256" ] || {
	echo "slot-nes-snes: $tarball has sha256 $got, SLOT_PIN wants $tarball_sha256" >&2
	exit 1
}

base_repo "$tarball" "$tmp/t"
applied=0
for p in "$patches"/*.patch; do
	[ -f "$p" ] || continue
	applied=$((applied + 1))
	git -C "$tmp/t" apply --numstat "$p" | awk -F'\t' -v n="$(basename "$p" .patch)" '{ print n "\t" $3 }' >>"$tmp/patchfiles"
	git -C "$tmp/t" apply --whitespace=nowarn "$p" || {
		echo "slot-nes-snes: $(basename "$p") does not apply to the pinned release" >&2
		exit 1
	}
done
[ "$applied" -gt 0 ] || {
	echo "slot-nes-snes: no *.patch found in $patches" >&2
	exit 1
}
git -C "$tmp/t" add -A -f -- . ':!vendor'

# Net diff against upstream, files upstream has (modified or deleted); files we add are ours and not counted.
git -C "$tmp/t" diff --cached --numstat --no-renames --diff-filter=MD HEAD |
	awk -F'\t' '$1 != "-" { print $1 + $2 "\t" $3 }' | sort -t'	' -k1,1nr -k2 >"$tmp/out"

[ -s "$tmp/out" ] || {
	echo "slot-nes-snes: patches applied but no upstream file changed, refusing to report a pass" >&2
	exit 1
}
awk -F'\t' '{ printf "%6d  %s\n", $1, $2 }' "$tmp/out"

git -C "$tmp/t" diff --cached -U0 --no-renames --diff-filter=MD HEAD >"$tmp/diff"
old="$map"
[ -f "$old" ] || old="$tmp/none"
python3 "$root/scripts/touchpoints.py" "$tmp/diff" "$tmp/patchfiles" "$old" "$tmp/map.md"
rows="$(grep -c '^| `' "$tmp/map.md" || true)"
todo="$(grep -c 'TODO: explain' "$tmp/map.md" || true)"
if [ "$check" = 1 ]; then
	[ -f "$map" ] || {
		echo "slot-nes-snes: docs/UPSTREAM-TOUCHPOINTS.md is missing, run task diffsurface" >&2
		exit 1
	}
	cmp -s "$tmp/map.md" "$map" || {
		echo "slot-nes-snes: docs/UPSTREAM-TOUCHPOINTS.md is stale, run task diffsurface and review the changed rows" >&2
		diff "$map" "$tmp/map.md" | head -40 >&2
		exit 1
	}
	[ "$todo" = 0 ] || {
		echo "slot-nes-snes: $todo touch points in docs/UPSTREAM-TOUCHPOINTS.md have no reason (TODO: explain)" >&2
		exit 1
	}
	echo "touchpoints: map is current, every row has a reason"
	exit 0
fi
cp "$tmp/map.md" "$map"
echo "touchpoints: wrote docs/UPSTREAM-TOUCHPOINTS.md ($rows rows, $todo without a reason)"
