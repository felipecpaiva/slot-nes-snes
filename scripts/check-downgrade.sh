#!/bin/sh
# T30b: an unpatched slot, with a slot.state that says cart_platform=nes (written by a patched slot),
# boots to the shelf and does not panic. Runs the example harness/downgrade.rs in build/slot-upstream.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
up="$root/build/slot-upstream"

[ -d "$up/crates" ] && [ -e "$up/vendor/mgba_libretro.dylib" ] || {
	echo "slot-nes-snes: run task upstream:build and task core:host first" >&2
	exit 1
}

mkdir -p "$up/crates/slot/examples"
cmp -s "$root/harness/downgrade.rs" "$up/crates/slot/examples/downgrade.rs" ||
	cp "$root/harness/downgrade.rs" "$up/crates/slot/examples/downgrade.rs"
(cd "$up" && cargo run --quiet --example downgrade -p slot)
