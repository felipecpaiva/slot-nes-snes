#!/bin/sh
# Run a shell command line on the box the device build wants: natively on Linux aarch64, else in
# rust:1-bullseye (glibc 2.31, the same as slot's release) with the repo mounted at /src.
# Copy of slot's internal device:sh task, which cannot be called from outside slot.
set -eu

[ $# -eq 1 ] && [ -n "$1" ] || {
	echo "usage: $0 'COMMAND LINE'" >&2
	exit 2
}

if [ "$(uname -s)-$(uname -m)" = "Linux-aarch64" ]; then
	sh -c "$1"
else
	root="$(cd "$(dirname "$0")/.." && pwd)"
	docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e FCEUMM_BUILDER \
		-v "$root":/src -w /src rust:1-bullseye sh -c '
		test -f /src/scripts/device-sh.sh || {
			echo "repo path not visible inside docker; under colima keep the repo under your home directory" >&2
			exit 1
		}
		'"$1"
fi
