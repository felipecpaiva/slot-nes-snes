#!/bin/sh
# The GBA, GB and GBC frame-hash harness. warm builds frame_dump in both trees, pre-builds the label
# cache once into build/harness/root and adds a generated DMG-only cart (the palettes need one), a
# generated 640x480 bezel and a copy of the root that selects gpSP for the GBA cart; control runs each
# tree twice and demands identical hashes; compare runs each tree twice again and demands all four runs
# identical, and refuses until control passed for these inputs; inject proves the harness can fail: a
# cold cache of ninety-nine large generated labels hashed from frame 1 must report at least 20 diffs.
# Legs: H1 (GBA on mGBA), H1G (the same script on gpSP, with colour correction), H2 (GB and GBC) and
# B1 (4:3 window with a bezel, composite only). Each composite leg also hashes the output pass (blue
# light gain and bezel), the polaroid view and the written state thumbnails.
#
# Retry rule: frame_dump exits 3 when the machine was too busy to keep the emulator in lockstep and
# the run is repeated (3 tries, 6 when CI is set). Retries are counted per tree and printed as
# "retries: upstream N, patched M". The run fails when patched needed more than upstream + 1 retries,
# so a regression that only shows up as intermittent lateness cannot hide behind the retry loop.
# The gate needs a mostly idle machine: a loaded one fails closed, it never passes a bad frame.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
up="$root/build/slot-upstream"
ours="$root/build/slot"
work="$root/build/harness"
legs="H1 H1G H2 B1"
modes="core composite"
tries=3
[ -z "${CI:-}" ] || tries=6
label_px=6000
extra_labels=99
min_diffs=20
retries_up=0
retries_ours=0

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
}

# run_dump TREE OUT SRC ARG...: a fresh copy of SRC per attempt, frame_dump ARG... ROOT appended to OUT,
# a clean retry when frame_dump says the machine was too busy (exit 3), anything else is final.
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
		if grep -q 'mock test pattern' "$tmp/err"; then
			rm -rf "$tmp"
			fail "frame_dump $* in $dir ran the mock core, a real core was not found"
		fi
		if [ "$rc" = 0 ]; then
			cat "$tmp/out" >>"$out"
			notes="$(grep -E 'rebuild took|cold boot hashed|label cache is cold|stale labels at' "$tmp/err" || true)"
			rm -rf "$tmp"
			return
		fi
		grep -v '^slot:' "$tmp/err" >&2 || true
		rm -rf "$tmp"
		[ "$rc" = 3 ] && [ "$try" -lt "$tries" ] || fail "frame_dump $* failed in $dir (exit $rc)"
		if [ "$dir" = "$up" ]; then retries_up=$((retries_up + 1)); else retries_ours=$((retries_ours + 1)); fi
		try=$((try + 1))
	done
}

# one_run TREE LEG OUT: the core and composite hashes of one leg. H1G is H1 on gpSP, chosen for the
# cart through Config/selected_core.txt in its own root. B1 runs in a 4:3 window and has no core part.
one_run() {
	: >"$3"
	src="$work/root"
	[ "$2" != H1G ] || src="$work/root-gpsp"
	for mode in $modes; do
		[ "$2" != B1 ] || [ "$mode" = composite ] || continue
		run_dump "$1" "$3" "$src" "$mode" "$2"
	done
	[ -s "$3" ] || fail "frame_dump printed nothing for $2 in $1"
}

# verdict_retries: print the retry counts and fail when patched needed more than upstream + 1.
verdict_retries() {
	echo "retries: upstream $retries_up, patched $retries_ours"
	[ "$retries_ours" -le $((retries_up + 1)) ] ||
		fail "patched needed $retries_ours retries against upstream's $retries_up, an intermittent regression"
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
	' "$1" "$2" | sort
}

stamp() {
	{
		cat "$root/scripts/harness.sh" "$root/harness/frame_dump.rs" "$up.meta" "$ours.meta"
		(cd "$root" && find harness patches -type f -o -type l | sort | while read -r f; do
			echo "$f"
			cat "$f"
		done)
		cat "$root/vendor/mgba_libretro.dylib" "$root/vendor/gpsp_libretro.dylib"
	} | sha256
}

control() {
	warm >/dev/null
	mkdir -p "$work/out"
	rm -f "$work/control.ok"
	retries_up=0
	retries_ours=0
	bad=0
	for tree in up ours; do
		eval "dir=\$$tree"
		for leg in $legs; do
			one_run "$dir" "$leg" "$work/out/control-$tree-$leg-1.txt"
			one_run "$dir" "$leg" "$work/out/control-$tree-$leg-2.txt"
			report "control $tree $leg" "$work/out/control-$tree-$leg-1.txt" "$work/out/control-$tree-$leg-2.txt"
		done
	done
	echo "control: $bad diffs"
	verdict_retries
	[ "$bad" = 0 ] || exit 1
	stamp >"$work/control.ok"
}

compare() {
	[ -f "$work/control.ok" ] && [ "$(cat "$work/control.ok")" = "$(stamp)" ] ||
		fail "refusing to compare, task harness:control has not passed for these inputs"
	warm >/dev/null
	retries_up=0
	retries_ours=0
	bad=0
	for leg in $legs; do
		o="$work/out/compare-$leg"
		one_run "$up" "$leg" "$o-up-1.txt"
		one_run "$up" "$leg" "$o-up-2.txt"
		one_run "$ours" "$leg" "$o-ours-1.txt"
		one_run "$ours" "$leg" "$o-ours-2.txt"
		report "compare $leg upstream runs" "$o-up-1.txt" "$o-up-2.txt"
		report "compare $leg patched runs" "$o-ours-1.txt" "$o-ours-2.txt"
		report "compare $leg trees" "$o-up-1.txt" "$o-ours-1.txt"
	done
	echo "compare: $bad diffs ($(echo $legs | sed 's/ /, /g'))"
	verdict_retries
	[ "$bad" = 0 ] || exit 1
}

# inject: a cold label cache of large labels generated at run time (never committed), hashed from
# frame 1 without the wait, twice. Every generated cart and label is a real file (a symlink would be
# followed, but a copy cannot be mistaken for one), their stems match, and the cache directory does not
# exist, so label_cache::stale lists every one of them and the rebuild decodes every one. The rebuild
# keeps the screen busy for many frames and moves its progress count at different frames in each run,
# so the two runs must differ in at least min_diffs frames: one frame of drift is scheduler noise, 20
# is a third of a second of picture, far more than a handful of labels finishing a frame apart, and
# well under the length of the rebuild. Fewer means the harness cannot see the very race its wait
# exists for. The same root with the wait, running the same cold script, must then give 0 diffs.
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
	retries_up=0
	retries_ours=0
	o="$work/out/inject"
	: >"$o-nowait-1.txt"
	: >"$o-nowait-2.txt"
	: >"$o-wait-1.txt"
	: >"$o-wait-2.txt"
	: >"$o-warm-1.txt"
	: >"$o-warm-2.txt"
	run_dump "$up" "$o-warm-1.txt" "$work/root" composite --no-wait
	run_dump "$up" "$o-warm-2.txt" "$work/root" composite --no-wait
	bad=0
	report "inject warm" "$o-warm-1.txt" "$o-warm-2.txt"
	echo "inject: no wait, warm cache (control for the injection): $bad diffs, $(wc -l <"$o-warm-1.txt" | tr -d ' ') frames hashed"
	[ "$bad" = 0 ] || fail "inject: hashing from frame 1 differs even with a warm cache, so a diff would not prove the race"
	run_dump "$up" "$o-nowait-1.txt" "$heavy" composite --no-wait
	run_dump "$up" "$o-nowait-2.txt" "$heavy" composite --no-wait
	bad=0
	found="$(differ "$o-nowait-1.txt" "$o-nowait-2.txt")"
	[ -z "$found" ] || bad="$(echo "$found" | wc -l | tr -d ' ')"
	echo "inject: no wait, $(echo "$notes" | tr '\n' ' '): $bad diffs of $(wc -l <"$o-nowait-1.txt" | tr -d ' ') frames hashed (at least $min_diffs needed)"
	[ "$bad" -ge "$min_diffs" ] || fail "inject: the cold-cache run without the label wait differed in only $bad frames, the harness cannot see the race"
	run_dump "$up" "$o-wait-1.txt" "$heavy" composite --wait
	run_dump "$up" "$o-wait-2.txt" "$heavy" composite --wait
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
