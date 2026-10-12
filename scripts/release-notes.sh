#!/bin/sh
# Release notes for a tag on stdout: .github/release-notes.md with the snes9x notice quoted from
# LICENSING.md (the one source of that text) and the asset names filled in.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -eq 1 ] && [ -n "$1" ] || {
	echo "usage: $0 TAG" >&2
	exit 2
}
tag="$1"
notice="$(sed -n '/^Notice text/,/^## /{/^>/p;}' "$root/LICENSING.md")"
case $notice in *snes9x2005_plus*non-commercial* | *non-commercial*snes9x2005_plus*) ;; *)
	echo "release-notes: no snes9x notice found in LICENSING.md" >&2
	exit 1
	;;
esac
NOTICE="$notice" awk -v tag="$tag" '
	$0 == "@NOTICE@" { print ENVIRON["NOTICE"]; next }
	{ gsub(/@TAG@/, tag); print }
' "$root/.github/release-notes.md"
