#!/bin/sh
# Run upstream's card tests (its test:card list) in build/slot. A test that fails twice there is run in
# build/slot-upstream: it gates only when the unpatched tree passes it. v1.8.0's test-coresave.sh fails
# in both trees on macOS, where sh keeps CMDLINE set by an earlier `CMDLINE=... run`, whenever its two
# crash logs land in different seconds (ADR 0106); so upstream gets two tries as well.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
ours="$root/build/slot"
up="$root/build/slot-upstream"

tests="$(sed -n '/^  test:card:/,/^  [a-z]/s/^ *- sh \(card\/test-[a-z-]*\.sh\)$/\1/p' "$ours/taskfile.yml")"
[ -n "$tests" ] || {
	echo "slot-nes-snes: no card tests listed under test:card in $ours/taskfile.yml" >&2
	exit 1
}
for t in $tests; do
	(cd "$ours" && sh "$t" </dev/null) && continue
	echo "$t failed, retrying once (upstream card tests are timing sensitive)" >&2
	(cd "$ours" && sh "$t" </dev/null) && continue
	if (cd "$up" && sh "$t" </dev/null) >/dev/null 2>&1 && (cd "$up" && sh "$t" </dev/null) >/dev/null 2>&1; then
		echo "slot-nes-snes: $t fails twice in the patched tree but passes twice upstream" >&2
		exit 1
	fi
	echo "$t fails in the unpatched tree too, not gating"
done
