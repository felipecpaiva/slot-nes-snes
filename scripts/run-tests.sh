#!/bin/sh
set -eu

usage() {
	echo "usage: $0 DIR" >&2
	exit 2
}

[ $# -eq 1 ] && [ -d "$1" ] || usage

log="$(mktemp)"
trap 'rm -f "$log" "$log.skips"' EXIT

# check promises real-core tests: with SLOT_REQUIRE_CORES=1 all four host dylibs must exist inside the
# tree under test (build/slot/vendor is a symlink to the shared vendor/, -f follows it).
if [ "${SLOT_REQUIRE_CORES:-}" = 1 ]; then
	for core in mgba gpsp fceumm snes9x; do
		[ -f "$1/vendor/${core}_libretro.dylib" ] || {
			echo "slot-nes-snes: $1/vendor/${core}_libretro.dylib is missing, run task core:host" >&2
			exit 1
		}
	done
fi

rc=0
(cd "$1" && cargo test --workspace -- --nocapture) >"$log" 2>&1 || rc=$?

grep -E '^(test result|     Running|   Doc-tests|error|failures:)|^test .* (FAILED|failed)' "$log"
if [ "$rc" -ne 0 ]; then
	tail -n 60 "$log" >&2
	echo "slot-nes-snes: cargo test failed" >&2
	exit "$rc"
fi

echo "skip report (tests that printed a skip message, with the reason):"
# A skip message that mentions a dylib, libretro or core fails the run as CORE MISSING: the host
# cores are built before the tests, so such a skip means the suite did not test what check
# promises. The exception is a message that also names a cart, ROM, card or BIOS ("no vendored
# core or no Game Boy cart"), which cannot tell which is missing; it is listed as a ROM skip.
# Non-ROM skips are labelled [tool] (zbarimg) or [asset] (bootlogo) so they do not mix in.
awk '
	/^     Running / { bin = $0; sub(/^ *Running /, "", bin); sub(/ \(.*$/, "", bin); next }
	/^   Doc-tests / { bin = "doc-tests " $2; next }
	{ line = $0; gsub(/test [^ ]+ \.\.\. (ok|FAILED|ignored)/, "", line); sub(/^test .* \.\.\. /, "", line); sub(/^slot: [a-z]*: /, "", line) }
	line ~ /skipp?(ed|ing)/ {
		l = tolower(line)
		rom = l ~ /(^|[^a-z])(carts?|roms?|cards?|bios)([^a-z]|$)/
		tag = ""
		if (!rom && l ~ /(^|[^a-z])(dylib|libretro|cores?)([^a-z]|$)/) tag = "CORE MISSING "
		else if (l ~ /zbarimg/) tag = "[tool] "
		else if (tolower($0) ~ /bootlogo/) tag = "[asset] "
		n[tag bin ": " line]++
	}
	END { for (k in n) printf "  %s (x%d)\n", k, n[k] }
' "$log" | sort >"$log.skips"
cat "$log.skips"
if grep -q '^  CORE MISSING ' "$log.skips"; then
	echo "slot-nes-snes: a test skipped because a core is missing, build the host cores first" >&2
	exit 1
fi
