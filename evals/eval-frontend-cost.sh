#!/bin/sh
# Success criterion 3: per-frame pixel conversion, publish and upload on NES and SNES stay within 5% of the
# larger GBA figure (mgba, gpsp) on the same host. evals/frontend_cost.rs is copied into build/slot as an
# example (it needs the patched tree, set_canvas does not exist upstream) and run once per core, each in its
# own process because slot-retro allows one open core. It times, per frame, at the core's real canvas:
# convert (run_frame at the real canvas minus the same frames at a 1x1 canvas, so emulation cancels and only
# video_refresh's copy or RGB565 conversion is left), publish (slot's Frames take_write, copy, publish) and
# upload (Frames latest, Compositor::upload_game). SLOT_TRACE only logs actions, it has no per-frame timing.
# Each process takes the min of its repeat means per stage; this script runs ATTEMPTS passes over all four cores
# (interleaved, like bench-compare) and keeps each core's lowest total, so scheduler noise only ever pushes up.
# A generated NES cart and SNES cart are used (harness/make_assets.py), override with NES_ROM and SNES_ROM.
# The generated SNES cart is 256 wide: the 512 wide hires halving path in copy_centred is not measured.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
ours="$root/build/slot"
roms="$root/harness/roms"
work="$root/build/harness/eval"
limit=105
attempts=3

for core in mgba gpsp fceumm snes9x; do
	[ -d "$ours/crates" ] && [ -e "$ours/vendor/${core}_libretro.dylib" ] || {
		echo "slot-nes-snes: $ours is not ready or lacks ${core}_libretro.dylib, run task build and task core:host" >&2
		exit 1
	}
done

mkdir -p "$ours/crates/slot/examples" "$work"
cmp -s "$root/evals/frontend_cost.rs" "$ours/crates/slot/examples/frontend_cost.rs" ||
	cp "$root/evals/frontend_cost.rs" "$ours/crates/slot/examples/frontend_cost.rs"
(cd "$ours" && cargo build --release --quiet --example frontend_cost -p slot)
bin="$ours/target/release/examples/frontend_cost"

nes="${NES_ROM:-$work/nes.nes}"
snes="${SNES_ROM:-$work/snes.sfc}"
[ -n "${NES_ROM:-}" ] || python3 "$root/harness/make_assets.py" nes "$nes"
[ -n "${SNES_ROM:-}" ] || python3 "$root/harness/make_assets.py" snes "$snes"

rom_of() {
	case "$1" in
	mgba | gpsp) echo "$roms/240pee_mb.gba" ;;
	fceumm) echo "$nes" ;;
	snes9x) echo "$snes" ;;
	esac
}

best_total() {
	awk -v a="$1" -v b="$2" 'BEGIN { print (b < a) ? b : a }'
}

for core in mgba gpsp fceumm snes9x; do
	: >"$work/$core.best"
	echo 999999 >"$work/$core.total"
done

n=1
while [ "$n" -le "$attempts" ]; do
	for core in mgba gpsp fceumm snes9x; do
		line="$(SLOT_ROOT="$work" "$bin" "$core" "$ours/vendor/${core}_libretro.dylib" "$(rom_of "$core")" | grep '^frontend_cost ')" || true
		total="$(echo "$line" | sed -n 's/.* total \([0-9][0-9]*\.[0-9]*\) .*/\1/p')"
		[ -n "$total" ] && awk -v t="$total" 'BEGIN { exit !(t > 0) }' || {
			echo "slot-nes-snes: frontend_cost printed no total for $core: $line" >&2
			exit 1
		}
		echo "attempt $n: $line"
		if [ "$(best_total "$(cat "$work/$core.total")" "$total")" = "$total" ]; then
			echo "$total" >"$work/$core.total"
			echo "$line" >"$work/$core.best"
		fi
	done
	n=$((n + 1))
done

for core in mgba gpsp fceumm snes9x; do
	echo "eval-frontend-cost $core: $(sed 's/^frontend_cost [a-z0-9]* //' "$work/$core.best") us/frame (min of $attempts)"
done

gba="$(awk -v a="$(cat "$work/mgba.total")" -v b="$(cat "$work/gpsp.total")" 'BEGIN { print (a > b) ? a : b }')"
bad=0
for core in fceumm snes9x; do
	verdict="$(awk -v t="$(cat "$work/$core.total")" -v g="$gba" -v l="$limit" 'BEGIN { printf "%.1f%% of max(GBA) %s", t / g * 100, (t * 100 > g * l) ? "over" : "ok" }')"
	echo "eval-frontend-cost $core: $(cat "$work/$core.total") us/frame against max(GBA) $gba us/frame, $verdict"
	case "$verdict" in *over) bad=1 ;; esac
done
if [ "$bad" = 0 ]; then
	echo "eval-frontend-cost: ok, NES and SNES within 5% of max(GBA)"
else
	echo "eval-frontend-cost: fail, NES or SNES is more than 5% above max(GBA)"
	exit 1
fi
