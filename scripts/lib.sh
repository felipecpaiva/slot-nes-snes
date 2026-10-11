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
