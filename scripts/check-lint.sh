#!/bin/sh
# Lint must add zero warnings compared with upstream. Upstream-file warnings match on
# "path: message" (a patch shifts line numbers); any warning in a file upstream lacks fails.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
up="$root/build/slot-upstream"
ours="$root/build/slot"

[ -d "$up/crates" ] && [ -d "$ours/crates" ] || {
	echo "slot-nes-snes: run task upstream:build and task build first" >&2
	exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

warnings() {
	log="$tmp/log"
	for args in "--workspace --all-targets" "-p slot --no-default-features --features device"; do
		# shellcheck disable=SC2086
		(cd "$1" && cargo clippy $args --message-format short) >"$log" 2>&1 || {
			tail -n 40 "$log" >&2
			echo "slot-nes-snes: cargo clippy failed in $1 ($args)" >&2
			exit 1
		}
		grep -E '^[^ ]+\.rs:[0-9]+:[0-9]+: (warning|error)' "$log" || true
	done | sed "s|^$1/||" | sort -u
}

warnings "$up" >"$tmp/up"
warnings "$ours" >"$tmp/ours"

echo "lint: upstream has $(wc -l <"$tmp/up" | tr -d ' ') warning lines, build/slot has $(wc -l <"$tmp/ours" | tr -d ' ')"

sed -E 's/^([^:]+):[0-9]+:[0-9]+: /\1: /' "$tmp/up" | sort -u >"$tmp/up.keys"
new="$tmp/new"
: >"$new"
while IFS= read -r line; do
	file="${line%%:*}"
	key="$(echo "$line" | sed -E 's/^([^:]+):[0-9]+:[0-9]+: /\1: /')"
	if [ ! -f "$up/$file" ] || ! grep -qxF -- "$key" "$tmp/up.keys"; then
		echo "$line" >>"$new"
	fi
done <"$tmp/ours"

if [ -s "$new" ]; then
	echo "slot-nes-snes: warnings not in upstream:" >&2
	cat "$new" >&2
	exit 1
fi
echo "lint: 0 new warnings compared with upstream"
