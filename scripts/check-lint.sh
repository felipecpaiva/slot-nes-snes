#!/bin/sh
# Lint must add nothing compared with upstream. Per tree, diagnostics are de-duplicated on
# "path:line:col: message" (cargo replays them across targets), then line:col is dropped and each
# "path: message" is counted. Span-less warnings (manifest, build.rs) are counted by message.
# A clippy failure fails the run; ours having more of any key than upstream fails it.
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

# clippy TREE NAME: both runs go to $tmp/NAME.log; the exit status is checked right here, never
# inside a pipeline, where an exit would only leave a subshell.
clippy() {
	: >"$tmp/$2.log"
	for args in "--workspace --all-targets" "-p slot --no-default-features --features device"; do
		# shellcheck disable=SC2086
		(cd "$1" && cargo clippy $args --message-format short) >"$tmp/run.log" 2>&1 || {
			tail -n 40 "$tmp/run.log" >&2
			echo "slot-nes-snes: cargo clippy failed in $1 ($args)" >&2
			exit 1
		}
		cat "$tmp/run.log" >>"$tmp/$2.log"
	done
}

# keys NAME TREE: one "path: message" or span-less "warning: message" per line, sorted.
keys() {
	{
		grep -E '^[^ ]+\.rs:[0-9]+:[0-9]+: (warning|error)' "$tmp/$1.log" | sed "s|^$2/||" | sort -u |
			sed -E 's/^([^:]+):[0-9]+:[0-9]+: /\1: /' || true
		grep -E '^(warning|error)(\[[^]]*\])?: ' "$tmp/$1.log" | grep -vE 'generated [0-9]+ warning' | sed "s|$2/||g" | sort -u || true
	} | sort
}

clippy "$up" up
clippy "$ours" ours
keys up "$up" >"$tmp/up.keys"
keys ours "$ours" >"$tmp/ours.keys"

echo "lint: upstream has $(wc -l <"$tmp/up.keys" | tr -d ' ') distinct warnings, build/slot has $(wc -l <"$tmp/ours.keys" | tr -d ' ')"

awk '
	FILENAME == ARGV[1] { u[$0]++; next }
	{ o[$0]++ }
	END { for (k in o) if (o[k] > u[k]) printf "  %s (build/slot %d, upstream %d)\n", k, o[k], u[k] }
' "$tmp/up.keys" "$tmp/ours.keys" | sort >"$tmp/new"

if [ -s "$tmp/new" ]; then
	echo "slot-nes-snes: warnings not in upstream:" >&2
	cat "$tmp/new" >&2
	exit 1
fi
echo "lint: 0 new warnings compared with upstream"
