#!/bin/sh
# Run a shell command line on the box the device build wants: natively on Linux aarch64, else in
# rust:1-bullseye (glibc 2.31, the same as slot's release) with the repo mounted at /src.
# Copy of slot's internal device:sh task, which cannot be called from outside slot.
# DEVICE_ROOT=1 runs as root (slot's own tasks apt-get cmake) and hands /src/vendor and /src/build
# back to the calling user on exit.
set -eu

[ $# -eq 1 ] && [ -n "$1" ] || {
	echo "usage: $0 'COMMAND LINE'" >&2
	exit 2
}

if [ "$(uname -s)-$(uname -m)" = "Linux-aarch64" ]; then
	sh -c "$1"
else
	root="$(cd "$(dirname "$0")/.." && pwd)"
	if [ -n "${DEVICE_ROOT:-}" ]; then
		docker run --rm -e HOME=/root -e DEVICE_CMD="$1" -e OWNER="$(id -u):$(id -g)" \
			-v "$root":/src -w /src rust:1-bullseye sh -c '
			test -f /src/scripts/device-sh.sh || {
				echo "repo path not visible inside docker; under colima keep the repo under your home directory" >&2
				exit 1
			}
			git config --global --add safe.directory "*"
			trap '"'"'chown -R "$OWNER" /src/vendor /src/build'"'"' EXIT
			sh -c "$DEVICE_CMD"
			'
		exit
	fi
	docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e FCEUMM_BUILDER \
		-v "$root":/src -w /src rust:1-bullseye sh -c '
		test -f /src/scripts/device-sh.sh || {
			echo "repo path not visible inside docker; under colima keep the repo under your home directory" >&2
			exit 1
		}
		git config --global --add safe.directory /src
		'"$1"
fi
