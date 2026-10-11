#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
up="$root/build/slot-upstream"
ours="$root/build/slot"
allowed_file=crates/slot-retro/src/libretro.rs
allowed_block='#[cfg(test)] mod env_tests;'

[ -d "$up/crates" ] && [ -d "$ours/crates" ] || {
	echo "slot-nes-snes: run task upstream:build and task build first" >&2
	exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
bad=0

fail() {
	echo "slot-nes-snes: upstream test code changed: $1" >&2
	bad=1
}

# Writes each #[cfg(test)] block of FILE to DIR/NNNN, from the attribute line to the matching
# close brace (or the semicolon of a bodiless mod). Braces inside strings and chars count like
# any other brace: upstream's blocks balance either way, and a miscount only makes the guard
# stricter, never looser.
split_blocks() {
	mkdir -p "$2"
	awk -v dir="$2" '
		!n && /^[ \t]*#\[cfg\(test\)\]/ { n = 1; depth = 0; seen = 0; out = sprintf("%s/%04d", dir, ++i); printf "" > out }
		n {
			print > out
			line = $0
			o = gsub(/\{/, "", line); c = gsub(/\}/, "", line)
			depth += o - c
			if (o) seen = 1
			if ((seen && depth <= 0) || (!seen && $0 ~ /;[ \t]*$/)) { close(out); n = 0 }
		}
	' "$1"
}

sum() { cksum <"$1" | cut -d' ' -f1,2; }

# Every file under crates/*/tests/ in upstream: unchanged and present. New files are ours.
for f in $(cd "$up" && find crates -path 'crates/*/tests/*' -type f | sort); do
	[ -f "$ours/$f" ] || { fail "$f removed"; continue; }
	cmp -s "$up/$f" "$ours/$f" || fail "$f differs"
done

# Every in-source test block of a src file that differs.
n=0
for f in $(cd "$up" && find crates -path 'crates/*/src/*' -name '*.rs' | sort); do
	if [ ! -f "$ours/$f" ]; then
		grep -q '^[[:space:]]*#\[cfg(test)\]' "$up/$f" && fail "$f removed"
		continue
	fi
	cmp -s "$up/$f" "$ours/$f" && continue
	n=$((n + 1))
	split_blocks "$up/$f" "$tmp/$n/u"
	split_blocks "$ours/$f" "$tmp/$n/o"
	for b in "$tmp/$n"/u/*; do
		[ -f "$b" ] || continue
		found=0
		for o in "$tmp/$n"/o/*; do
			[ -f "$o" ] && [ "$(sum "$b")" = "$(sum "$o")" ] && { found=1; break; }
		done
		[ "$found" = 1 ] || fail "$f, block starting '$(head -n 2 "$b" | tr '\n' ' ')' changed or removed"
	done
	for o in "$tmp/$n"/o/*; do
		[ -f "$o" ] || continue
		found=0
		for b in "$tmp/$n"/u/*; do
			[ -f "$b" ] && [ "$(sum "$b")" = "$(sum "$o")" ] && { found=1; break; }
		done
		[ "$found" = 1 ] && continue
		[ "$f" = "$allowed_file" ] && [ "$(cat "$o")" = "$allowed_block" ] && continue
		fail "$f, new block '$(head -n 2 "$o" | tr '\n' ' ')' not allowed"
	done
done

[ "$bad" = 0 ] || exit 1
echo "upstream test code: 0 blocks changed"
