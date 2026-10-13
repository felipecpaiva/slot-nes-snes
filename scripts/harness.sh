#!/bin/sh
# The GBA, GB and GBC frame-hash harness. warm builds frame_dump in both trees, pre-builds the label
# cache once into build/harness/root and adds a generated DMG-only cart (the palettes need one), a
# generated 640x480 bezel and a copy of the root that selects gpSP for the GBA cart; control runs each
# tree twice and demands identical hashes; compare runs each tree twice again and demands all four runs
# identical, and refuses until control passed for these inputs; inject proves the harness can fail: a
# cold cache of 403 large generated labels hashed from frame 1 must report at least 20 diffs.
# Legs: H1 (GBA on mGBA), H1G (the same script on gpSP, with colour correction), H2 (GB and GBC) and
# B1 (4:3 window with a bezel, composite only). Each composite leg also hashes the output pass (blue
# light gain and bezel), the polaroid view and the written state thumbnails. H3 runs in the patched
# tree only, in a copy of the root that adds a generated NES cart: it inserts and ejects the NES cart
# (rows tagged H3N), then plays the H1 script again (rows tagged H3), and the H3 rows must equal the
# patched H1 rows, so a GBA cart after a NES one draws as if no NES cart had been played.
#
# Retry rule: frame_dump exits 3 when the machine was too busy to keep the emulator in lockstep and
# the run is repeated (3 tries, 6 when CI is set). Every retry is logged as "tree leg" and counted per
# leg and tree, printed as "retries: upstream N, patched M, H3 (patched only) K; per leg upstream/patched:
# H1 u/p ...". The run fails when, in the patched tree, a leg needed at least 2 retries and more than
# upstream's retries of that leg (p > max(1, u)), or the legs together needed more than upstream's total
# + 2, or one H3 run needed more than 2. So it catches lateness concentrated on one leg (2 or more beyond
# upstream) or well above upstream's in total. It does NOT catch spread-out lateness: 1 retry per leg
# passes, and the patched total may exceed upstream's by up to 2 without a failure. One retry on one
# leg is noise.
# Measured on an idle M5 Max (2026-10-12), 30 control runs each:
#   before the lock wait in frame_dump: 28 passed, 2 failed on the old "patched <= upstream + 1" and
#   "H3 at most 1" rules, on noise alone. Per leg and tree never more than 1 retry (232 samples),
#   upstream total at most 1, patched total at most 2 (H2 and B1 in one run), H3 0, 1 or 2 per run,
#   29 late lines. Most over upstream in total: +2.
#   after the lock wait: 30 passed. Upstream total 0 in 23 runs, 1 in 6, 2 in 1; patched total 0 in 25
#   runs and 1 in 5; H3 needed 1 once, 0 otherwise; 13 late lines. Most over upstream: +1.
# Both sets of 30 runs pass the current rule (checked from the logged counts). 60 runs with 0 false
# failures bound the false-failure rate at about 5% (95% confidence, 3/60), not at 0.
# Late frames before: 296 x8 (H2), 338 x5 (H3), 1921 x3 (H1G), 170 x2 (B1), 2281, 2725 ("not locked
# 23 ms after the update": the emulator thread locks a variable time after the core is ready; frame_dump
# now waits for the lock in the core part), 1564 x4 ("1 core frames published, expected 0": the polaroid
# frame outlasts the emulator's 25 ms stall and it runs a frame alone, only slot could avoid that), and
# ticks 22-37 ms apart (869 x2, 2153, 2235, 2854): scheduler.
# Late frames after (13): "not locked 23 ms" at 296 x6, 1921 x2, 338 x1, then 1564 x2 and 2 tick gaps
# (2854, 1431). The wait removed 11 of the 20 "not locked" lines. The remaining 9 are the composite
# part: only its rig has no lock accessor (it never waits for the lock), while the core part now waits
# for the lock and ticks at once. The marks printed before a late line are the same in both parts, so
# this is by elimination, not read off the log. A patched-only Frontend::emu accessor would remove
# them; it is left out because frame_dump is built in the upstream tree too.
# HARNESS_FAKE_LATE="H2 2" makes the first 2 patched H2 dumps exit 3 as if late (the faked "patched needs
# 2 more retries" case): control must then fail on H2.
# The gate needs a mostly idle machine: a loaded one fails closed, it never passes a bad frame.
# On CI (CI is set) a shared runner is never idle, so lateness is information only and hashes still gate:
# 10 tries per run; a leg that stays late (exit 3) in either tree after them is warned about with
# "::warning::" and not compared (all its comparisons are skipped, the other legs go on); the retry rule
# above warns instead of failing; hash diffs between legs that completed in both trees, and inject's
# race check, still fail; inject warns and stops if its own runs stay late. A CI run prints "legs
# compared, legs skipped as late". On GitHub's macos-14 runner every leg stayed late in both trees
# (run 38351790206), so a run that compared nothing only warns there; the harness gates locally. HARNESS_FAKE_LATE="H2 99"
# fakes a leg that stays late for all tries, "ALL 999" every patched leg (CI only, locally it just fails).
# Local behaviour (CI unset) is unchanged.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
up="$root/build/slot-upstream"
ours="$root/build/slot"
work="$root/build/harness"
retry_log="$work/out/retries.txt"
legs="H1 H1G H2 B1"
modes="core composite"
tries=3
ci="${CI:-}"
[ -z "$ci" ] || tries=10
late_log="$work/out/late.txt"
label_px=6000
extra_labels=400
min_diffs=20
h3_max=2
fake_late="${HARNESS_FAKE_LATE:-}"

usage() {
	echo "usage: $0 warm | control | compare | inject" >&2
	exit 2
}

fail() {
	echo "slot-nes-snes: $*" >&2
	exit 1
}

sha256() {
	if command -v sha256sum >/dev/null 2>&1; then sha256sum; else shasum -a 256; fi | cut -d' ' -f1
}

tree_ready() {
	[ -d "$1/crates" ] && [ -e "$1/vendor/mgba_libretro.dylib" ] && [ -e "$1/vendor/gpsp_libretro.dylib" ] ||
		fail "$1 is not ready, run task upstream:build, task build and task core:host"
}

install() {
	tree_ready "$1"
	mkdir -p "$1/crates/slot/examples"
	cmp -s "$root/harness/frame_dump.rs" "$1/crates/slot/examples/frame_dump.rs" ||
		cp "$root/harness/frame_dump.rs" "$1/crates/slot/examples/frame_dump.rs"
	(cd "$1" && cargo build --release --quiet --example frame_dump -p slot)
}

dumper() {
	echo "$1/target/release/examples/frame_dump"
}

warm() {
	install "$up"
	install "$ours"
	rm -rf "$work/root"
	mkdir -p "$work"
	cp -RLp "$root/harness/root-template" "$work/root"
	python3 "$root/harness/make_assets.py" dmg "$root/harness/roms/gb240p.gb" "$work/root/Games/GB/zdmg-blank.gb"
	"$(dumper "$up")" warm "$work/root" 2>&1 | grep '^frame_dump:'
	mkdir -p "$work/root/System/bezels"
	python3 "$root/harness/make_assets.py" bezel 640 480 "$work/root/System/bezels/640x480.png"
	rm -rf "$work/root-gpsp"
	cp -Rp "$work/root" "$work/root-gpsp"
	echo "240pee_mb=gpsp" >"$work/root-gpsp/Config/selected_core.txt"
	rm -rf "$work/root-nes"
	cp -Rp "$work/root" "$work/root-nes"
	python3 "$root/harness/make_assets.py" nes "$work/root-nes/Games/NES/znes-backdrop.nes"
	"$(dumper "$ours")" warm "$work/root-nes" 2>&1 | grep '^frame_dump:'
}

# run_dump TREE OUT SRC ARG...: a fresh copy of SRC per attempt, frame_dump ARG... ROOT appended to OUT,
# a clean retry when frame_dump says the machine was too busy (exit 3), anything else is final. Each
# retry is appended to retry_log as "up|ours LEG" (LEG is the second argument). Returns 3 only on CI, when
# the tries ran out late: logged in late_log as "upstream|patched LEG" after a warning.
run_dump() {
	dir="$1"
	out="$2"
	src="$3"
	shift 3
	try=1
	while :; do
		tmp="$(mktemp -d)"
		cp -Rp "$src" "$tmp/root"
		rc=0
		SLOT_ROOT="$tmp/root" "$(dumper "$dir")" "$@" "$tmp/root" >"$tmp/out" 2>"$tmp/err" || rc=$?
		if [ "$rc" = 0 ] && [ "$dir" != "$up" ] && [ -n "$fake_late" ] && { [ "${fake_late%% *}" = "${2:-}" ] || [ "${fake_late%% *}" = ALL ]; } &&
			[ "${fake_late#* }" -gt 0 ]; then
			fake_late="${fake_late%% *} $((${fake_late#* } - 1))"
			rc=3
		fi
		if grep -q 'mock test pattern' "$tmp/err"; then
			rm -rf "$tmp"
			fail "frame_dump $* in $dir ran the mock core, a real core was not found"
		fi
		if [ "$rc" = 0 ]; then
			cat "$tmp/out" >>"$out"
			notes="$(grep -E 'rebuild took|cold boot hashed|label cache is cold|stale labels at' "$tmp/err" | sed 's/^frame_dump: //' || true)"
			rm -rf "$tmp"
			return
		fi
		grep -v '^slot:' "$tmp/err" >&2 || true
		rm -rf "$tmp"
		if [ -n "$ci" ] && [ "$rc" = 3 ] && [ "$try" -ge "$tries" ]; then
			name=patched
			[ "$dir" != "$up" ] || name=upstream
			echo "::warning::harness $name ${2:-} stayed late after $tries tries on this runner (information only)"
			echo "$name ${2:-}" >>"$late_log"
			return 3
		fi
		[ "$rc" = 3 ] && [ "$try" -lt "$tries" ] || fail "frame_dump $* failed in $dir (exit $rc)"
		if [ "$dir" = "$up" ]; then echo "up ${2:-}" >>"$retry_log"; else echo "ours ${2:-}" >>"$retry_log"; fi
		try=$((try + 1))
	done
}

# one_run TREE LEG OUT: the core and composite hashes of one leg. H1G is H1 on gpSP, chosen for the
# cart through Config/selected_core.txt in its own root. B1 runs in a 4:3 window and has no core part.
one_run() {
	: >"$3"
	src="$work/root"
	[ "$2" != H1G ] || src="$work/root-gpsp"
	[ "$2" != H3 ] || src="$work/root-nes"
	for mode in $modes; do
		[ "$2" != B1 ] || [ "$mode" = composite ] || continue
		run_dump "$1" "$3" "$src" "$mode" "$2" || return 3
	done
	[ -s "$3" ] || fail "frame_dump printed nothing for $2 in $1"
}

# h3_run OUT: one H3 run in the patched tree. Upstream has no H3 to set its retries against (the first
# emulator step after a core loads is often late), so one H3 run has its own bound, h3_max retries.
h3_run() {
	kept="$(grep -c '^ours H3$' "$retry_log" || true)"
	one_run "$ours" H3 "$1" || return 3
	used=$(($(grep -c '^ours H3$' "$retry_log" || true) - kept))
	[ "$used" -le "$h3_max" ] && return 0
	[ -z "$ci" ] || { echo "::warning::harness H3 needed $used retries in one run, the most allowed is $h3_max (information only)"; return 0; }
	fail "H3 needed $used retries in one run, the most allowed is $h3_max"
}

# skipped LEG: true when LEG stayed late in some tree (CI only, late_log is empty otherwise).
skipped() {
	grep -q " $1\$" "$late_log"
}

# ci_summary: on CI, print how many legs were compared and fail when none was.
ci_summary() {
	[ -n "$ci" ] || return 0
	total=0
	late=0
	for leg in $legs; do
		total=$((total + 1))
		if skipped "$leg"; then late=$((late + 1)); fi
	done
	echo "harness: $((total - late)) legs compared, $late legs skipped as late (of $total)"
	[ "$late" -lt "$total" ] ||
		echo "::warning::harness: no leg completed in both trees on this runner, nothing was compared (information only; the harness gates locally in task check)"
}

# verdict_retries: print the retry counts and fail on a leg that needed at least 2 retries and more than
# upstream's for that leg, or on patched needing more than upstream's total + 2 (H3 has its own bound).
verdict_retries() {
	out="$(awk -v legs="$legs" '
		{ c[$1 " " $2]++; if ($2 == "H3") h3++; else t[$1]++ }
		END {
			n = split(legs, l, " ")
			for (i = 1; i <= n; i++) {
				u = c["up " l[i]] + 0
				p = c["ours " l[i]] + 0
				per = per " " l[i] " " u "/" p
				if (p > 1 && p > u) print "FAIL " l[i] " needed " p " retries in the patched tree against upstream" "\047" "s " u
			}
			printf "retries: upstream %d, patched %d, H3 (patched only) %d; per leg upstream/patched:%s\n", t["up"], t["ours"], h3, per
			if (t["ours"] > t["up"] + 2) print "FAIL patched needed " t["ours"] " retries in all against upstream" "\047" "s " (t["up"] + 0)
		}' "$retry_log")"
	echo "$out" | grep -v '^FAIL'
	failed="$(echo "$out" | grep '^FAIL' | sed 's/^FAIL //' || true)"
	[ -z "$failed" ] && return 0
	[ -z "$ci" ] || { echo "::warning::harness retries: $failed, an intermittent regression (information only)"; return 0; }
	fail "$failed, an intermittent regression"
}

# report LABEL A B [LEG_A LEG_B]: print the differing frames of two runs and add them to bad.
report() {
	found="$(differ "$2" "$3" "${4:-}" "${5:-}")"
	if [ -n "$found" ]; then
		echo "$found" | sed "s/^/$1: /" | head -n 20
		bad=$((bad + $(echo "$found" | wc -l)))
	fi
}

# differ A B [LEG_A LEG_B]: one line per frame whose hash differs or that only one run has. With two
# leg names only those legs' rows are compared, as one leg, so a leg can be held against another
# (the H3 GBA part against H1 in issue 09).
differ() {
	awk -v la="${3:-}" -v lb="${4:-}" '
		NR == FNR { if (la == "" || $1 == la) a[(la == "" ? $1 " " : "") $2 " " $3] = $4; next }
		{
			if (lb != "" && $1 != lb) next
			k = (lb == "" ? $1 " " : "") $2 " " $3
			seen[k] = 1
			if (!(k in a)) print "only in the second run: " k
			else if (a[k] != $4) print "differs: " k
		}
		END { for (k in a) if (!(k in seen)) print "only in the first run: " k }
	' "$1" "$2" | sort -u
}

stamp() {
	{
		cat "$root/scripts/harness.sh" "$root/harness/frame_dump.rs" "$up.meta" "$ours.meta"
		(cd "$root" && find harness patches -type f -o -type l | sort | while read -r f; do
			echo "$f"
			cat "$f"
		done)
		cat "$root/vendor/mgba_libretro.dylib" "$root/vendor/gpsp_libretro.dylib" "$root/vendor/fceumm_libretro.dylib"
	} | sha256
}

control() {
	warm >/dev/null
	mkdir -p "$work/out"
	rm -f "$work/control.ok"
	: >"$retry_log"
	: >"$late_log"
	bad=0
	for tree in up ours; do
		eval "dir=\$$tree"
		for leg in $legs; do
			one_run "$dir" "$leg" "$work/out/control-$tree-$leg-1.txt" || continue
			one_run "$dir" "$leg" "$work/out/control-$tree-$leg-2.txt" || continue
			report "control $tree $leg" "$work/out/control-$tree-$leg-1.txt" "$work/out/control-$tree-$leg-2.txt"
		done
	done
	if h3_run "$work/out/control-ours-H3-1.txt" && h3_run "$work/out/control-ours-H3-2.txt"; then
		report "control ours H3" "$work/out/control-ours-H3-1.txt" "$work/out/control-ours-H3-2.txt"
	fi
	echo "control: $bad diffs"
	verdict_retries
	ci_summary
	[ "$bad" = 0 ] || exit 1
	stamp >"$work/control.ok"
}

compare() {
	[ -f "$work/control.ok" ] && [ "$(cat "$work/control.ok")" = "$(stamp)" ] ||
		fail "refusing to compare, task harness:control has not passed for these inputs"
	warm >/dev/null
	: >"$retry_log"
	: >"$late_log"
	bad=0
	for leg in $legs; do
		o="$work/out/compare-$leg"
		one_run "$up" "$leg" "$o-up-1.txt" || continue
		one_run "$up" "$leg" "$o-up-2.txt" || continue
		one_run "$ours" "$leg" "$o-ours-1.txt" || continue
		one_run "$ours" "$leg" "$o-ours-2.txt" || continue
		report "compare $leg upstream runs" "$o-up-1.txt" "$o-up-2.txt"
		report "compare $leg patched runs" "$o-ours-1.txt" "$o-ours-2.txt"
		report "compare $leg trees" "$o-up-1.txt" "$o-ours-1.txt"
	done
	o="$work/out/compare-H3"
	if h3_run "$o-ours-1.txt" && h3_run "$o-ours-2.txt"; then
		report "compare H3 patched runs" "$o-ours-1.txt" "$o-ours-2.txt"
		skipped H1 || report "compare H3 against H1" "$work/out/compare-H1-ours-1.txt" "$o-ours-1.txt" H1 H3
	fi
	echo "compare: $bad diffs ($(echo $legs | sed 's/ /, /g'), H3 patched only, held against H1)"
	verdict_retries
	ci_summary
	[ "$bad" = 0 ] || exit 1
}

# inject: a cold label cache of large labels generated at run time (never committed), hashed from
# frame 1 without the wait, twice. Every generated cart and label is a real file (a symlink would be
# followed, but a copy cannot be mistaken for one), their stems match, and the cache directory does not
# exist, so label_cache::stale lists every one of them and the rebuild decodes every one. The rebuild
# keeps the screen busy for many frames and moves its progress count at different frames in each run,
# so the two runs must differ in at least min_diffs frames: one frame of drift is scheduler noise, 20
# is a third of a second of picture, far more than a handful of labels finishing a frame apart, and
# well under the length of the rebuild (extra_labels is sized so the lowest of five runs was over 200).
# Fewer means the harness cannot see the very race its wait
# exists for. The same root with the wait, running the same cold script, must then give 0 diffs.
# inject_late: CI only, an inject run stayed late (run_dump already warned), so nothing can be concluded.
inject_late() {
	echo "inject: skipped, a run stayed late on this runner (information only)"
}

inject() {
	warm >/dev/null
	mkdir -p "$work/out"
	heavy="$work/heavy-root"
	rm -rf "$heavy"
	cp -RLp "$root/harness/root-template" "$heavy"
	rm -rf "$heavy/System"
	python3 "$root/harness/make_assets.py" png "$label_px" "$heavy/Labels/GBA/240pee_mb.png"
	n=1
	while [ "$n" -le "$extra_labels" ]; do
		cp "$root/harness/roms/240pee_mb.gba" "$heavy/Games/GBA/extra-$n.gba"
		cp "$heavy/Labels/GBA/240pee_mb.png" "$heavy/Labels/GBA/extra-$n.png"
		n=$((n + 1))
	done
	cp "$heavy/Labels/GBA/240pee_mb.png" "$heavy/Labels/GB/gb240p.png"
	cp "$heavy/Labels/GBA/240pee_mb.png" "$heavy/Labels/GBC/cgb-acid2.png"
	echo "inject: $((extra_labels + 3)) labels of ${label_px}x${label_px} generated, the stale count below is a few lower because the rebuild has begun by the first frame"
	: >"$retry_log"
	: >"$late_log"
	o="$work/out/inject"
	: >"$o-nowait-1.txt"
	: >"$o-nowait-2.txt"
	: >"$o-wait-1.txt"
	: >"$o-wait-2.txt"
	: >"$o-warm-1.txt"
	: >"$o-warm-2.txt"
	run_dump "$up" "$o-warm-1.txt" "$work/root" composite --no-wait || { inject_late; return 0; }
	run_dump "$up" "$o-warm-2.txt" "$work/root" composite --no-wait || { inject_late; return 0; }
	bad=0
	report "inject warm" "$o-warm-1.txt" "$o-warm-2.txt"
	echo "inject: no wait, warm cache (control for the injection): $bad diffs, $(wc -l <"$o-warm-1.txt" | tr -d ' ') frames hashed"
	[ "$bad" = 0 ] || fail "inject: hashing from frame 1 differs even with a warm cache, so a diff would not prove the race"
	run_dump "$up" "$o-nowait-1.txt" "$heavy" composite --no-wait || { inject_late; return 0; }
	run_dump "$up" "$o-nowait-2.txt" "$heavy" composite --no-wait || { inject_late; return 0; }
	bad=0
	found="$(differ "$o-nowait-1.txt" "$o-nowait-2.txt")"
	[ -z "$found" ] || bad="$(echo "$found" | wc -l | tr -d ' ')"
	echo "inject: no wait, $(echo "$notes" | tr '\n' ' '): $bad diffs of $(wc -l <"$o-nowait-1.txt" | tr -d ' ') frames hashed (at least $min_diffs needed)"
	[ "$bad" -ge "$min_diffs" ] || fail "inject: the cold-cache run without the label wait differed in only $bad frames, the harness cannot see the race"
	run_dump "$up" "$o-wait-1.txt" "$heavy" composite --wait || { inject_late; return 0; }
	run_dump "$up" "$o-wait-2.txt" "$heavy" composite --wait || { inject_late; return 0; }
	bad=0
	report "inject wait" "$o-wait-1.txt" "$o-wait-2.txt"
	echo "inject: with the wait, same cold labels and script ($(echo "$notes" | tr '\n' ' ')): $bad diffs"
	[ "$bad" = 0 ] || fail "inject: the label wait did not make the cold-cache run deterministic"
	echo "inject: ok, the harness reports the race without the wait and 0 diffs with it"
}

[ $# -eq 1 ] || usage
case "$1" in
warm) warm ;;
control) control ;;
compare) compare ;;
inject) inject ;;
*) usage ;;
esac
