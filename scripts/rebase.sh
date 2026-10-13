#!/bin/sh
# Move the patch set onto a new slot release.
#   rebase.sh NEW_TAG --dry-run   try it in a temp clone, report "all patches apply" or the first failing patch
#   rebase.sh NEW_TAG             do it in work/slot, re-export patches/, run task check, bump SLOT_PIN
# NEW_TAG may be a branch such as main for --dry-run only. Never edits a .patch by hand: patches/ is
# always re-exported from work/slot by scripts/export-patches.sh.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
work="$root/work/slot"
repo=https://github.com/BrandonKowalski/slot
. "$root/scripts/lib.sh"
read_pin

usage() {
	echo "usage: $0 NEW_TAG [--dry-run]" >&2
	exit 2
}
fail() {
	echo "slot-nes-snes: $*" >&2
	exit 1
}

[ $# -ge 1 ] && [ $# -le 2 ] || usage
new="$1"
dry=0
case "${2:-}" in "") ;; --dry-run) dry=1 ;; *) usage ;; esac

tmp="$(mktemp -d "${TMPDIR:-/tmp}/slot-nes-snes.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

# Resolve NEW_TAG to a commit by exact ref name: a tag (annotated target first), then a branch.
case "$new" in "" | *[!A-Za-z0-9._-]*) fail "invalid release name '$new', want [A-Za-z0-9._-]+" ;; esac
refs="$(git ls-remote --refs "$repo")" || fail "cannot reach $repo"
peeled="$(git ls-remote "$repo" "refs/tags/$new^{}" | awk -v r="refs/tags/$new^{}" '$2==r{print $1}')"
istag=1
newcommit="$(printf '%s\n' "$refs" | awk -v r="refs/tags/$new" '$2==r{print $1}')"
[ -n "$newcommit" ] || { istag=0; newcommit="$(printf '%s\n' "$refs" | awk -v r="refs/heads/$new" '$2==r{print $1}')"; }
[ -z "$peeled" ] || newcommit="$peeled"
[ -n "$newcommit" ] || fail "$new is neither a tag nor a branch of $repo"
[ "$(printf '%s\n' "$newcommit" | wc -l)" -eq 1 ] || fail "$new matches more than one ref of $repo"
[ "$istag" = 1 ] || [ "$dry" = 1 ] || fail "$new is a branch, a real rebase needs a release tag"

# Fetch and verify the new tarball: the commit named in its top directory must be the one asked for.
mkdir -p "$root/build"
newtar="$root/build/slot-$newcommit.tar.gz"
if [ ! -f "$newtar" ]; then
	curl -fsSL -o "$newtar.part" "$repo/archive/$newcommit.tar.gz"
	mv "$newtar.part" "$newtar"
fi
top="$(tar -tzf "$newtar" | head -1 | cut -d/ -f1)"
[ "$top" = "slot-$newcommit" ] || fail "$newtar unpacks to $top, want slot-$newcommit"
newsha="$(file_sha256 "$newtar")"
echo "new release $new = $newcommit, tarball sha256 $newsha"

# slug of the patch file for a commit subject
patch_for() { ls "$root"/patches/ | grep -F -- "-$1.patch" | head -1; }

# $1 = repo on branch nes-snes, $2 = new base commit ref inside it. Rebases, reports, returns 0 or 1.
try_rebase() {
	old="$(git -C "$1" rev-list --max-parents=0 nes-snes)"
	if git -C "$1" -c commit.gpgsign=false -c user.name=slot-nes-snes -c user.email=slot-nes-snes@users.noreply.github.com \
		rebase -q --onto "$2" "$old" nes-snes >"$tmp/rebase.log" 2>&1; then
		return 0
	fi
	sha="$(git -C "$1" rev-parse -q --verify REBASE_HEAD || true)"
	subj="$(git -C "$1" log -1 --format=%s "$sha" 2>/dev/null || echo unknown)"
	echo "patch $(patch_for "$subj") ($subj) does not apply to $new" >&2
	echo "conflicting files:" >&2
	git -C "$1" diff --name-only --diff-filter=U | sed 's/^/  /' >&2
	return 1
}

if [ "$dry" = 1 ]; then
	t="$tmp/work"
	if own_repo "$work" && [ "$(git -C "$work" symbolic-ref -q HEAD)" = refs/heads/nes-snes ]; then
		git clone -q --no-hardlinks -b nes-snes "$work" "$t"
	else
		# No work/slot on this machine: replay patches/ onto the pinned release, as task work:resume does.
		oldtar="$root/build/slot-$commit.tar.gz"
		[ -f "$oldtar" ] || curl -fsSL -o "$oldtar" "$repo/archive/$commit.tar.gz"
		[ "$(file_sha256 "$oldtar")" = "$tarball_sha256" ] || fail "$oldtar does not match tarball_sha256 in SLOT_PIN"
		base_repo "$oldtar" "$t"
		for p in "$root"/patches/*.patch; do
			[ -f "$p" ] || continue
			GIT_COMMITTER_NAME=slot-nes-snes GIT_COMMITTER_EMAIL=slot-nes-snes@users.noreply.github.com \
				git -C "$t" -c commit.gpgsign=false am -q --whitespace=nowarn "$p" ||
				fail "$(basename "$p") does not apply to the pinned $tag, fix that first"
		done
	fi
	base_repo "$newtar" "$tmp/new"
	git -C "$t" fetch -q "$tmp/new" HEAD
	if try_rebase "$t" FETCH_HEAD; then
		echo "all patches apply to $new"
		exit 0
	fi
	exit 1
fi

# Real rebase, in work/slot.
own_repo "$work" || fail "$work is not a git checkout, run task work:init or task work:resume"
[ "$(git -C "$work" symbolic-ref -q HEAD || true)" = refs/heads/nes-snes ] || fail "$work is not on branch nes-snes"
[ -z "$(git -C "$work" status --porcelain)" ] || fail "$work has uncommitted changes"
base_repo "$newtar" "$tmp/new"
git -C "$work" fetch -q "$tmp/new" HEAD
git -C "$work" tag -f "slot-$new" FETCH_HEAD >/dev/null
if ! try_rebase "$work" FETCH_HEAD; then
	echo "resolve in $work (git rebase --continue), then: sh scripts/export-patches.sh, edit SLOT_PIN, task check" >&2
	echo "or abandon with: git -C work/slot rebase --abort" >&2
	exit 1
fi
sh "$root/scripts/export-patches.sh" >/dev/null

oldpin="$(cat "$root/SLOT_PIN")"
sed -i.bak -e "s/^tag=.*/tag=$new/" -e "s/^commit=.*/commit=$newcommit/" -e "s/^tarball_sha256=.*/tarball_sha256=$newsha/" "$root/SLOT_PIN"
rm -f "$root/SLOT_PIN.bak"
echo "SLOT_PIN changed:"
printf '%s\n' "$oldpin" | diff - "$root/SLOT_PIN" | grep '^[<>]' || true
echo "review by hand: gpsp_* and the core commits in SLOT_PIN follow upstream's taskfile pins, VERSION wants ns.1"

(cd "$root" && task check)
echo "rebased onto $new, patches/ re-exported, task check green. Next: device smoke, set VERSION to ns.1, tag $new-ns.1 (docs/REBASE.md)"
