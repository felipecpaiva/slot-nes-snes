#!/bin/sh
# Per upstream file changed by patches/, the net changed lines (added + removed) between the pinned
# slot release and the release with every patch applied. Exits 1 when app.rs is over its budget.
# Env: SLOT_TARBALL (pinned release tarball, default build/slot-<commit>.tar.gz or a download),
#      PATCHES_DIR (default patches/).
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

budget=25
appfile="crates/slot/src/app.rs"
patches="${PATCHES_DIR:-$root/patches}"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/slot-nes-snes.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

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
n="$(awk -F'\t' -v f="$appfile" '$2 == f { print $1 }' "$tmp/out")"
n="${n:-0}"
if [ "$n" -gt "$budget" ]; then
	echo "app.rs: $n changed lines, over the budget of $budget" >&2
	exit 1
fi
echo "app.rs: $n changed lines, within the budget of $budget"
