# Sourced by the other scripts (POSIX sh). Needs $root.

# True only when DIR has its own .git and git resolves to DIR itself, so a plain
# extraction inside an outer repo never lets git fall through to the outer repo.
own_repo() { [ -d "$1/.git" ] && [ "$(git -C "$1" rev-parse --show-toplevel 2>/dev/null)" = "$(cd "$1" && pwd -P)" ]; }

# Load SLOT_PIN and fail loudly if a key is missing.
read_pin() {
	. "$root/SLOT_PIN"
	: "${tag:?SLOT_PIN lacks tag}"
	: "${commit:?SLOT_PIN lacks commit}"
	: "${tarball_sha256:?SLOT_PIN lacks tarball_sha256}"
}

same_identity() {
	for key in user.name user.email; do
		value="$(git -C "$2" config "$key" || true)"
		[ -z "$value" ] || git -C "$1" config "$key" "$value"
	done
}

# slot-nes-snes-v1.6.0-ns.0: slot's tag from SLOT_PIN plus the release counter in VERSION.
release_name() {
	v="$(cat "$root/VERSION")"
	printf '%s\n' "$v" | grep -Eq '^ns\.[0-9]+$' || {
		echo "slot-nes-snes: VERSION is '$v', want ns.<number>" >&2
		return 1
	}
	echo "slot-nes-snes-$tag-$v"
}

# True for an aarch64 ELF. The ", ARM aarch64," machine field is what file reads from e_machine;
# matching "aarch64" anywhere also passes an x86-64 ELF whose interpreter path says aarch64.
is_aarch64() { file "$1" | grep -q ', ARM aarch64,'; }

# The value of NAME in build/slot's taskfile vars, the one place upstream pins MGBA_COMMIT and GPSP_COMMIT.
slot_var() { sed -n "s/^  $1: *//p" "$root/build/slot/taskfile.yml"; }

# Print the sha256 of FILE.
file_sha256() {
	if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi |
		cut -d' ' -f1
}

# Extract TARBALL (a github archive, one top directory) into DIR as a fresh repo with a single base commit,
# dated like task work:init so the same input gives the same commit.
base_repo() {
	rm -rf "$2"
	mkdir -p "$2"
	tar -xzf "$1" -C "$2" --strip-components=1
	git -C "$2" init -q -b nes-snes
	git -C "$2" add -A -f -- . ':!vendor'
	GIT_AUTHOR_NAME=slot-nes-snes GIT_COMMITTER_NAME=slot-nes-snes \
		GIT_AUTHOR_EMAIL=slot-nes-snes@users.noreply.github.com \
		GIT_COMMITTER_EMAIL=slot-nes-snes@users.noreply.github.com \
		GIT_AUTHOR_DATE="2000-01-01T00:00:00Z" GIT_COMMITTER_DATE="2000-01-01T00:00:00Z" \
		git -C "$2" -c commit.gpgsign=false commit -q -m "base"
}
