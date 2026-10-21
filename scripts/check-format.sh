#!/bin/sh
# rustfmt --check on every .rs file under build/slot that we add or change compared with upstream
# (not target, target-device, vendor, .git). Upstream test files are skipped: they are held
# byte for byte by check-upstream-tests.sh, so rustfmt must never reflow them.
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

files="$(cd "$ours" && find . \( -name target -o -name target-device -o -name vendor -o -name .git \) -prune -o -name '*.rs' -print |
	sed 's|^\./||' | sort | while read -r f; do
	case "$f" in (crates/*/tests/*) [ -f "$up/$f" ] && continue ;; esac
	[ -f "$up/$f" ] && cmp -s "$up/$f" "$ours/$f" || echo "$f"
done)"

if [ -z "$files" ]; then
	echo "format: no new or changed .rs files, nothing to check"
	exit 0
fi

echo "format: checking files we add or change (edition $edition):"
echo "$files" | sed 's/^/  /'
cd "$ours"
# rustfmt also walks the modules a file declares, so a changed lib.rs reaches upstream files we never
# touch; upstream v1.8.0's sticker.rs is not rustfmt clean (ADR 0104). Only our files fail the check.
out="$(echo "$files" | tr '\n' '\0' | xargs -0 rustfmt --check --edition "$edition" 2>&1 || true)"
bad="$(printf '%s\n' "$out" | sed -n "s|^Diff in $ours/\(.*\):[0-9]*:\$|\1|p" | sort -u | while read -r f; do
	printf '%s\n' "$files" | grep -Fx -- "$f" || true
done)"
printf '%s\n' "$out" | grep -q . && printf '%s\n' "$out"
if [ -n "$bad" ]; then
	echo "slot-nes-snes: files we add or change are not rustfmt clean: $(echo $bad)" >&2
	exit 1
fi
echo "format: ok"
