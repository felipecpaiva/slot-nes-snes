#!/bin/sh
# Print the path of the linux arm64 task binary for the Task version mise.toml pins (the
# docker device build runs slot's own tasks with it). The release tarball is checked against
# task_linux_arm64_sha256 in SLOT_PIN before anything is extracted or run. The cache directory
# is keyed on version and sha, so a bump of either downloads again.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
. "$root/SLOT_PIN"
: "${task_linux_arm64_sha256:?SLOT_PIN lacks task_linux_arm64_sha256}"

version="$(sed -n 's/^task = "\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)"$/\1/p' "$root/mise.toml")"
[ -n "$version" ] || {
	echo "slot-nes-snes: mise.toml needs an exact task version (task = \"X.Y.Z\")" >&2
	exit 1
}

sha256() { file_sha256 "$1"; }

dir="$root/build/task-linux/v$version-$task_linux_arm64_sha256"
tgz="$dir/task_linux_arm64.tar.gz"
if [ ! -f "$tgz" ] || [ "$(sha256 "$tgz")" != "$task_linux_arm64_sha256" ]; then
	rm -rf "$dir"
	mkdir -p "$dir"
	curl -fsSL -o "$tgz.part" "https://github.com/go-task/task/releases/download/v$version/task_linux_arm64.tar.gz"
	got="$(sha256 "$tgz.part")"
	[ "$got" = "$task_linux_arm64_sha256" ] || {
		rm -rf "$dir"
		echo "slot-nes-snes: task v$version linux arm64 tarball sha256 is $got, SLOT_PIN wants $task_linux_arm64_sha256" >&2
		exit 1
	}
	mv "$tgz.part" "$tgz"
fi
tar -xzf "$tgz" -C "$dir" task
echo "$dir/task"
