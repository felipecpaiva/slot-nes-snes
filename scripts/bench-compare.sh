#!/bin/sh
# core_bench on the harness carts in both trees, the same flags in each, five repeats. The median is
# read from the frames/s figure (core_bench prints ms/frame to 3 places, too coarse for a 0.05 ms
# frame). Each case gets up to three interleaved attempts and passes when any one has the patched
# median within 2% of upstream's, so scheduler noise cannot fail it but a real 2% loss fails all
# three. Both medians of every attempt are printed.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
up="$root/build/slot-upstream"
ours="$root/build/slot"
roms="$root/harness/roms"
limit=102
attempts=3

for tree in "$up" "$ours"; do
	[ -d "$tree/crates" ] && [ -e "$tree/vendor/mgba_libretro.dylib" ] && [ -e "$tree/vendor/gpsp_libretro.dylib" ] || {
		echo "slot-nes-snes: $tree is not ready, run task upstream:build, task build and task core:host" >&2
		exit 1
	}
	(cd "$tree" && cargo build --release --quiet -p slot-retro --example core_bench)
done

median_ms() {
	"$1/target/release/examples/core_bench" "$1/vendor/$2_libretro.dylib" "$roms/$3" \
		--frames 3000 --warmup 300 --repeats 5 |
		sed -n 's/^median .*), \([0-9.]*\) frames\/s.*/\1/p' |
		awk '{ printf "%.5f", 1000 / $1 }'
}

bad=0
for case in mgba:240pee_mb.gba mgba:gb240p.gb mgba:cgb-acid2.gbc gpsp:240pee_mb.gba; do
	core="${case%%:*}"
	rom="${case#*:}"
	pass=0
	n=1
	while [ "$n" -le "$attempts" ] && [ "$pass" = 0 ]; do
		a="$(median_ms "$up" "$core" "$rom")"
		b="$(median_ms "$ours" "$core" "$rom")"
		[ -n "$a" ] && [ -n "$b" ] || {
			echo "slot-nes-snes: core_bench printed no median for $core $rom" >&2
			exit 1
		}
		verdict="$(awk -v a="$a" -v b="$b" -v l="$limit" 'BEGIN { printf "%.1f%% of upstream %s", b / a * 100, (b * 100 > a * l) ? "over" : "ok" }')"
		echo "bench $core $rom attempt $n: upstream median $a ms/frame, patched median $b ms/frame, $verdict"
		case "$verdict" in *ok) pass=1 ;; esac
		n=$((n + 1))
	done
	[ "$pass" = 1 ] || bad=1
done
[ "$bad" = 0 ] || {
	echo "slot-nes-snes: a patched median was more than 2% above upstream's in every attempt" >&2
	exit 1
}
echo "bench: patched medians within 2% of upstream"
