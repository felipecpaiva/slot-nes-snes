#!/bin/sh
set -eu

usage() {
	echo "usage: $0 DIR" >&2
	exit 2
}

[ $# -eq 1 ] && [ -d "$1" ] || usage

log="$(mktemp)"
trap 'rm -f "$log" "$log.skips"' EXIT

rc=0
(cd "$1" && cargo test --workspace -- --nocapture) >"$log" 2>&1 || rc=$?

grep -E '^(test result|     Running|   Doc-tests|error|failures:)|^test .* (FAILED|failed)' "$log"
if [ "$rc" -ne 0 ]; then
	tail -n 60 "$log" >&2
	echo "slot-nes-snes: cargo test failed" >&2
	exit "$rc"
fi

echo "skip report (tests that printed a skip message, with the reason):"
# A skip that names a missing core fails the run: the host cores are built before the tests, so
# a skipped core test means the suite did not test what check promises. A message that also names
# a cart, ROM, card or BIOS ("no vendored core or no Game Boy cart") cannot tell which is missing,
# so it is listed as an asset skip; check asserts both dylibs exist before the tests run.
awk '
	/^     Running / { bin = $0; sub(/^ *Running /, "", bin); sub(/ \(.*$/, "", bin); next }
	/^   Doc-tests / { bin = "doc-tests " $2; next }
	/^test .* \.\.\. (ok|FAILED|ignored)$/ { next }
	{ line = $0; sub(/^test .* \.\.\. /, "", line); sub(/^slot: [a-z]*: /, "", line) }
	line ~ /skipp?(ed|ing)/ { n[bin ": " line]++ }
	END {
		for (k in n) {
			l = tolower(k)
			bad = l ~ /core/ && l ~ /not found|missing|vendored/ && l !~ /cart|rom|card|bios/
			printf "  %s%s (x%d)\n", bad ? "CORE MISSING " : "", k, n[k]
		}
	}
' "$log" | sort >"$log.skips"
cat "$log.skips"
if grep -q '^  CORE MISSING ' "$log.skips"; then
	echo "slot-nes-snes: a test skipped because a core is missing, build the host cores first" >&2
	exit 1
fi
