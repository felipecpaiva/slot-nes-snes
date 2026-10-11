#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"

. "$root/SLOT_PIN"

source_url="https://github.com/BrandonKowalski/slot/archive/$commit.tar.gz"
tarball="$root/build/slot-$commit.tar.gz"

usage() {
	echo "usage: $0 stamp | fetch DIR" >&2
	exit 2
}

sha256() {
	if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi |
		cut -d' ' -f1
}

stamp() {
	echo "slot_commit=$commit"
	echo "source=$source_url"
}

fetch() {
	dir="$1"

	if [ ! -f "$tarball" ]; then
		mkdir -p "$(dirname "$tarball")"
		curl -fsSL -o "$tarball.part" "$source_url"
		mv "$tarball.part" "$tarball"
	fi
	got="$(sha256 "$tarball")"
	if [ "$got" != "$tarball_sha256" ]; then
		rm -f "$tarball"
		echo "slot-nes-snes: $source_url has sha256 $got, SLOT_PIN wants $tarball_sha256" >&2
		exit 1
	fi

	rm -rf "$dir" "$dir.meta"
	mkdir -p "$dir" "$root/vendor"
	tar -xzf "$tarball" -C "$dir" --strip-components=1
	ln -s "$root/vendor" "$dir/vendor"
	stamp >"$dir.meta"
}

case "${1:-}" in
stamp)
	[ $# -eq 1 ] || usage
	stamp
	;;
fetch)
	[ $# -eq 2 ] && [ -n "$2" ] || usage
	fetch "$2"
	;;
*)
	usage
	;;
esac
