#!/bin/sh
# The GBA, GB and GBC frame-hash harness. warm builds frame_dump in both trees and pre-builds the
# label cache once into build/harness/root; control runs each tree twice and demands identical
# hashes; compare runs upstream against patched, and refuses until control passed for these inputs.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
up="$root/build/slot-upstream"
ours="$root/build/slot"
work="$root/build/harness"
legs="H1 H2"
modes="core composite"
tries=3

usage() {
	echo "usage: $0 warm | control | compare" >&2
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
	"$(dumper "$up")" warm "$work/root" 2>&1 | grep '^frame_dump:'
}

# one_run TREE LEG OUT: fresh copy of the warmed root per mode, a clean retry when frame_dump says
# the machine was too busy to keep the emulator in lockstep (exit 3), anything else is final.
one_run() {
	: >"$3"
	for mode in $modes; do
		try=1
		while :; do
			tmp="$(mktemp -d)"
			cp -Rp "$work/root" "$tmp/root"
			rc=0
			SLOT_ROOT="$tmp/root" "$(dumper "$1")" "$mode" "$2" "$tmp/root" >"$tmp/out" 2>"$tmp/err" || rc=$?
			if [ "$rc" = 0 ]; then
				cat "$tmp/out" >>"$3"
				rm -rf "$tmp"
				break
			fi
			grep -v '^slot:' "$tmp/err" >&2 || true
			rm -rf "$tmp"
			[ "$rc" = 3 ] && [ "$try" -lt "$tries" ] || fail "frame_dump $mode $2 failed in $1 (exit $rc)"
			try=$((try + 1))
		done
	done
	[ -s "$3" ] || fail "frame_dump printed nothing for $2 in $1"
}

# differ A B: one line per frame whose hash differs or that only one run has.
differ() {
	awk '
		NR == FNR { a[$1 " " $2 " " $3] = $4; next }
		{
			k = $1 " " $2 " " $3
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
	bad=0
	for tree in up ours; do
		eval "dir=\$$tree"
		for leg in $legs; do
			one_run "$dir" "$leg" "$work/out/control-$tree-$leg-1.txt"
			one_run "$dir" "$leg" "$work/out/control-$tree-$leg-2.txt"
			found="$(differ "$work/out/control-$tree-$leg-1.txt" "$work/out/control-$tree-$leg-2.txt")"
			if [ -n "$found" ]; then
				echo "$found" | sed "s/^/control $tree $leg: /" | head -n 20
				bad=$((bad + $(echo "$found" | wc -l)))
			fi
		done
	done
	echo "control: $bad diffs"
	[ "$bad" = 0 ] || exit 1
	stamp >"$work/control.ok"
}

compare() {
	[ -f "$work/control.ok" ] && [ "$(cat "$work/control.ok")" = "$(stamp)" ] ||
		fail "refusing to compare, task harness:control has not passed for these inputs"
	warm >/dev/null
	bad=0
	for leg in $legs; do
		one_run "$up" "$leg" "$work/out/compare-up-$leg.txt"
		one_run "$ours" "$leg" "$work/out/compare-ours-$leg.txt"
		found="$(differ "$work/out/compare-up-$leg.txt" "$work/out/compare-ours-$leg.txt")"
		if [ -n "$found" ]; then
			echo "$found" | sed "s/^/compare $leg: /" | head -n 20
			bad=$((bad + $(echo "$found" | wc -l)))
		fi
	done
	echo "compare: $bad diffs (H1, H2)"
	[ "$bad" = 0 ] || exit 1
}

[ $# -eq 1 ] || usage
case "$1" in
warm) warm ;;
control) control ;;
compare) compare ;;
*) usage ;;
esac
