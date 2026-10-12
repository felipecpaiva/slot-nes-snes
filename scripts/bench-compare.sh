#!/bin/sh
# core_bench on the harness carts in both trees, the same flags in each: 6000 frames, 300 warmup, five
# repeats. What core_bench times: retro_run through LibretroCore::run_frame, which runs the core and,
# inside retro_run, slot's own video_refresh (copy or RGB565 to XRGB8888 into Host.video) and audio
# callbacks (extend Host.audio), then take_audio per present. It does not time the emulator thread,
# Session, the compositor or the GL upload, and it feeds no input (--steps only batches presents), so
# the scene is whatever the cart shows idle after warmup. The median is read from the frames/s figure
# (the ms/frame figure is only 3 places, too coarse for a 0.05 ms frame). Each case runs three
# interleaved attempts per tree; the gate compares the minimum repeat median of each tree across the
# attempts (min of N, the least noisy estimate of the real cost) and fails when the patched minimum is
# over 2% above the upstream minimum. Every attempt is printed. The output also says whether the
# slot-retro crate and the vendored cores are byte-identical between the trees: when they are, the
# only difference left is noise and a number near 100% is not a measured signal.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
up="$root/build/slot-upstream"
ours="$root/build/slot"
roms="$root/harness/roms"
limit=102
attempts=3
frames=6000

for tree in "$up" "$ours"; do
	[ -d "$tree/crates" ] && [ -e "$tree/vendor/mgba_libretro.dylib" ] && [ -e "$tree/vendor/gpsp_libretro.dylib" ] || {
		echo "slot-nes-snes: $tree is not ready, run task upstream:build, task build and task core:host" >&2
		exit 1
	}
	(cd "$tree" && cargo build --release --quiet -p slot-retro --example core_bench)
done

same=yes
for f in $(cd "$up" && find crates/slot-retro -type f -name '*.rs' -o -type f -name Cargo.toml | sort); do
	cmp -s "$up/$f" "$ours/$f" || same="no ($f differs)"
done
for core in mgba gpsp; do
	cmp -s "$up/vendor/${core}_libretro.dylib" "$ours/vendor/${core}_libretro.dylib" || same="no (${core} core differs)"
done
echo "bench: slot-retro sources and vendored cores identical between the trees: $same"

median_ms() {
	"$1/target/release/examples/core_bench" "$1/vendor/$2_libretro.dylib" "$roms/$3" \
		--frames "$frames" --warmup 300 --repeats 5 |
		sed -n 's/^median .*), \([0-9.]*\) frames\/s.*/\1/p' |
		awk '{ printf "%.5f", 1000 / $1 }'
}

lower() {
	awk -v a="$1" -v b="$2" 'BEGIN { print (b < a) ? b : a }'
}

bad=0
for case in mgba:240pee_mb.gba mgba:gb240p.gb mgba:cgb-acid2.gbc gpsp:240pee_mb.gba; do
	core="${case%%:*}"
	rom="${case#*:}"
	best_up=999
	best_ours=999
	n=1
	while [ "$n" -le "$attempts" ]; do
		a="$(median_ms "$up" "$core" "$rom")"
		b="$(median_ms "$ours" "$core" "$rom")"
		[ -n "$a" ] && [ -n "$b" ] || {
			echo "slot-nes-snes: core_bench printed no median for $core $rom" >&2
			exit 1
		}
		echo "bench $core $rom attempt $n: upstream median $a ms/frame, patched median $b ms/frame"
		best_up="$(lower "$best_up" "$a")"
		best_ours="$(lower "$best_ours" "$b")"
		n=$((n + 1))
	done
	verdict="$(awk -v a="$best_up" -v b="$best_ours" -v l="$limit" 'BEGIN { printf "%.1f%% of upstream %s", b / a * 100, (b * 100 > a * l) ? "over" : "ok" }')"
	echo "bench $core $rom min of $attempts: upstream $best_up ms/frame, patched $best_ours ms/frame, $verdict"
	case "$verdict" in *over) bad=1 ;; esac
done
[ "$bad" = 0 ] || {
	echo "slot-nes-snes: a patched minimum was more than 2% above upstream's" >&2
	exit 1
}
echo "bench: patched minimum medians within 2% of upstream (slot-retro identical: $same)"
