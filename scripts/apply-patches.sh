#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"

usage() {
	echo "usage: $0 stamp | build DIR" >&2
	exit 2
}

sha256() {
	if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi |
		cut -d' ' -f1
}

stamp() {
	sh "$root/scripts/fetch-slot.sh" stamp
	for p in "$root"/patches/*.patch; do
		[ -f "$p" ] || continue
		echo "patch=$(basename "$p") sha256:$(sha256 "$p")"
	done
}

show_hunks() {
	printf '%s\n' "$3" | sed -n 's/^error: patch failed: \(.*\):\([0-9][0-9]*\)$/\1 \2/p' |
		while read -r file line; do
			echo "rejected hunk in $file at line $line:" >&2
			awk -v f="$file" -v l="$line" '
				/^diff --git /{ infile = ($3 == "a/" f); show = 0 }
				infile && /^@@ /{ show = (index($0, "@@ -" l ",") == 1 || index($0, "@@ -" l " ") == 1) }
				infile && show { print }' "$1" >&2
		done
}

fail() {
	echo "slot-nes-snes: $(basename "$1") does not apply to $dir" >&2
	exit 1
}

build() {
	dir="$1"

	rm -f "$dir.meta"
	if [ -e "$dir/.git" ]; then
		echo "slot-nes-snes: $dir is not a fresh extraction, run task build" >&2
		exit 1
	fi
	git init -q "$dir"
	own_repo "$dir" || { echo "slot-nes-snes: git init did not make $dir its own repo" >&2; exit 1; }
	for p in "$root"/patches/*.patch; do
		[ -f "$p" ] || continue
		want="$(grep -c '^diff --git ' "$p" || true)"
		got="$(git -C "$dir" apply --numstat "$p" 2>/dev/null | wc -l | tr -d ' ')"
		if [ "$want" != "$got" ]; then
			echo "slot-nes-snes: $(basename "$p") lists $want files but git apply sees $got" >&2
			fail "$p"
		fi
		bad=0
		out="$(git -C "$dir" apply --whitespace=nowarn --verbose "$p" 2>&1)" || bad=1
		case $out in *error:*) bad=1 ;; esac
		if [ "$bad" = 1 ]; then
			printf '%s\n' "$out" >&2
			show_hunks "$p" "$dir" "$out"
			fail "$p"
		fi
		printf '%s\n' "$out"
	done
	stamp >"$dir.meta"
}

case "${1:-}" in
stamp)
	[ $# -eq 1 ] || usage
	stamp
	;;
build)
	[ $# -eq 2 ] && [ -n "$2" ] || usage
	build "$2"
	;;
*)
	usage
	;;
esac
