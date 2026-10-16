#!/bin/sh
set -eu

usage() {
	echo "usage: $0 DIR" >&2
	exit 2
}

[ $# -eq 1 ] && [ -d "$1" ] || usage

log="$(mktemp)"
trap 'rm -f "$log" "$log.skips"' EXIT

# check promises real-core tests: with SLOT_REQUIRE_CORES=1 all seven host dylibs must exist inside the
# tree under test (build/slot/vendor is a symlink to the shared vendor/, -f follows it).
if [ "${SLOT_REQUIRE_CORES:-}" = 1 ]; then
	for core in mgba gpsp fceumm snes9x nestopia snes9x2005_plus genesis_plus_gx; do
		[ -f "$1/vendor/${core}_libretro.dylib" ] || {
			echo "slot-nes-snes: $1/vendor/${core}_libretro.dylib is missing, run task core:host" >&2
			exit 1
		}
	done
fi

# Shared CI runners (GitHub sets CI=true) fail upstream's real-time tests on the unpatched upstream
# tree too (emu.rs: test.yml run 38313541162; audio.rs: run 38343132049, 2026-10-13), so there they
# say nothing about the patches. Upstream's slot-gfx pipeline.rs pixel tests fail on the runner's GPU
# on the unpatched tree too (run 38348725485), and render_shelf.rs compares two renders pixel for
# pixel the same way (run 38351152364), and so does our retro_pipeline.rs (run 38407714973). Our own real-time budget tests (snes_ff.rs,
# snes_rewind.rs: run 38347334149) are treated the same way. On CI these binaries are left out of the gating run and run on their
# own afterwards as information only. Locally they still gate.
ci_timing="slot:emu slot:audio slot:snes_ff slot:snes_rewind slot-gfx:pipeline slot-gfx:retro_pipeline slot:render_shelf"
ci_skips=""
if [ "${CI:-}" = true ]; then
	for pt in $ci_timing; do
		names="$(cd "$1" && cargo test -q -p "${pt%%:*}" --test "${pt#*:}" -- --list --format terse 2>/dev/null |
			sed -n 's/: test$//p' | sed 's/^/--skip /' | tr '\n' ' ')"
		[ -n "$names" ] || {
			echo "slot-nes-snes: could not list the $pt tests to run them apart on CI" >&2
			exit 1
		}
		ci_skips="$ci_skips $names"
	done
	ci_skips="--exact $ci_skips"
fi

# Upstream's own frame-hash tests in slot-gfx layout.rs fail on the unpatched v1.7.0 tree on this
# Mac too (two tests, the GPU renders a different hash than the one Brandon pinned). They are left
# out of the gating run and run in both trees afterwards: the patched tree must fail no test the
# upstream tree passes.
both_trees="slot-gfx:layout"
up="$(dirname "$1")/slot-upstream"
[ -d "$up/crates" ] || {
	echo "slot-nes-snes: $up is missing, run task upstream:build" >&2
	exit 1
}
for pt in $both_trees; do
	names="$(cd "$1" && cargo test -q -p "${pt%%:*}" --test "${pt#*:}" -- --list --format terse 2>/dev/null |
		sed -n 's/: test$//p' | sed 's/^/--skip /' | tr '\n' ' ')"
	[ -n "$names" ] || {
		echo "slot-nes-snes: could not list the $pt tests to run them in both trees" >&2
		exit 1
	}
	[ -n "$ci_skips" ] || ci_skips="--exact"
	ci_skips="$ci_skips $names"
done

rc=0
# shellcheck disable=SC2086
(cd "$1" && cargo test --workspace -- --nocapture $ci_skips) >"$log" 2>&1 || rc=$?

grep -E '^(test result|     Running|   Doc-tests|error|failures:)|^test .* (FAILED|failed)' "$log"
if [ "$rc" -ne 0 ]; then
	tail -n 60 "$log" >&2
	echo "slot-nes-snes: cargo test failed" >&2
	exit "$rc"
fi

failed() {
	(cd "$1" && cargo test -q -p "${2%%:*}" --test "${2#*:}" 2>&1 || true) |
		sed -n 's/^test \(.*\) \.\.\. FAILED$/\1/p; s/^    \([a-z0-9_]*\)$/\1/p' | sort -u
}
for pt in $both_trees; do
	failed "$up" "$pt" >"$log.up"
	failed "$1" "$pt" >"$log.ours"
	extra="$(comm -13 "$log.up" "$log.ours")"
	echo "$pt in both trees: upstream fails $(wc -l <"$log.up" | tr -d ' '), patched fails $(wc -l <"$log.ours" | tr -d ' ')"
	rm -f "$log.up" "$log.ours"
	[ -z "$extra" ] || {
		echo "slot-nes-snes: $pt fails in the patched tree but passes upstream: $extra" >&2
		exit 1
	}
done

if [ "${CI:-}" = true ]; then
	for pt in $ci_timing; do
		t="${pt#*:}"
		echo "$pt runner-sensitive tests (information only on CI, they gate locally):"
		if (cd "$1" && cargo test -q -p "${pt%%:*}" --test "$t") >"$log.$t" 2>&1; then
			grep '^test result' "$log.$t"
		else
			grep -E '^test result|^test .* FAILED' "$log.$t"
			echo "::warning::$pt runner-sensitive tests failed on this runner (information only)"
		fi
		rm -f "$log.$t"
	done
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
[ -z "$ci_skips" ] || echo "  [runner] slot tests emu, audio, snes_ff, snes_rewind, render_shelf and slot-gfx tests pipeline and retro_pipeline (runner-sensitive, run apart as information on CI only)"
if grep -q '^  CORE MISSING ' "$log.skips"; then
	echo "slot-nes-snes: a test skipped because a core is missing, build the host cores first" >&2
	exit 1
fi
