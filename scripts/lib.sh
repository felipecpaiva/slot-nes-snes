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
