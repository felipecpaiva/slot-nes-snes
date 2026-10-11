#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"

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

build() {
	dir="$1"

	rm -f "$dir.meta"
	[ -d "$dir/.git" ] || git init -q "$dir"
	for p in "$root"/patches/*.patch; do
		[ -f "$p" ] || continue
		if ! git -C "$dir" apply --verbose "$p"; then
			echo "slot-nes-snes: $(basename "$p") does not apply to $dir" >&2
			exit 1
		fi
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
