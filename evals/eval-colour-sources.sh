#!/bin/sh
# Every row of NES_TITLES and SNES_TITLES (crates/slot-ui/src/retro_shell.rs) names the VARIANTS.md row that
# cites it in its `source` field (the Sega plastics, which have no title rows, are sampled in docs/cart-art/SEGA.md, the PS1 jewel tray in docs/cart-art/PS1.md); that row must exist in docs/cart-art/VARIANTS.md, carry a URL, and begin with
# the row's own title. The hex of the row's plastic (RETRO_BLACK is DUAL_MODE_SHELL in shell.rs) must appear in
# VARIANTS.md section 7 on a line that names the row's title. Every plastic colour must have a sampling record.
# Any orphan or mismatch fails the run.
# SLOT_TREE picks the tree to read, default build/slot.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
tree="${SLOT_TREE:-$root/build/slot}"
src="$tree/crates/slot-ui/src/retro_shell.rs"
doc="$root/docs/cart-art/VARIANTS.md"
sega="$root/docs/cart-art/SEGA.md"
ps1="$root/docs/cart-art/PS1.md"

[ -f "$src" ] || {
	echo "slot-nes-snes: $src is missing, run task build or set SLOT_TREE" >&2
	exit 1
}
[ -f "$doc" ] || {
	echo "slot-nes-snes: $doc is missing" >&2
	exit 1
}

fail=0
rows=0

shellrs="$tree/crates/slot-ui/src/shell.rs"
[ -f "$shellrs" ] || {
	echo "slot-nes-snes: $shellrs is missing" >&2
	exit 1
}

hex_of() {
	sed -n "s/^pub const $1: Shell = solid(\[\(0x[0-9a-f]*\), \(0x[0-9a-f]*\), \(0x[0-9a-f]*\)\]);\$/\1\2\3/p" "$src" | sed 's/0x//g'
}

black_hex="$(sed -n 's/^pub const DUAL_MODE_SHELL: Shell = shell(\[\(0x[0-9a-f]*\), \(0x[0-9a-f]*\), \(0x[0-9a-f]*\)\].*/\1\2\3/p' "$shellrs" | sed 's/0x//g')"
[ -n "$black_hex" ] || {
	echo "slot-nes-snes: DUAL_MODE_SHELL has no colour in $shellrs" >&2
	exit 1
}
sampled="$(sed -n '/^## 7\./,$p' "$doc")"

squash() {
	printf '%s' "$1" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9'
}

records="$(awk '
	/^ *title: "/ { t = $0; sub(/^ *title: "/, "", t); sub(/",$/, "", t) }
	/^ *plastic: / { p = $0; sub(/^ *plastic: /, "", p); sub(/,$/, "", p) }
	/^ *source: "/ { s = $0; sub(/^ *source: "/, "", s); sub(/",$/, "", s); print t "|" p "|" s }
' "$src")"
n_titles="$(grep -c '^ *title: "' "$src" || true)"
n_sources="$(grep -c '^ *source: "' "$src" || true)"
[ "$n_titles" -eq "$n_sources" ] && [ "$n_titles" -eq "$(printf '%s\n' "$records" | grep -c .)" ] || {
	echo "slot-nes-snes: retro_shell.rs has a row without a source or a source without a row" >&2
	exit 1
}

while IFS='|' read -r title plastic source; do
	rows=$((rows + 1))
	line="$(grep -F -- "| $source |" "$doc" | head -n 1 || true)"
	if [ -z "$line" ]; then
		echo "ORPHAN: no VARIANTS.md row named \"$source\""
		fail=1
		continue
	elif ! printf '%s\n' "$line" | grep -q 'https\{0,1\}://'; then
		echo "ORPHAN: the VARIANTS.md row \"$source\" has no URL"
		fail=1
		continue
	fi
	case "$(squash "$source")" in
	"$(squash "$title")"*) ;;
	*)
		echo "MISMATCH: title \"$title\" does not belong to the source row \"$source\""
		fail=1
		continue
		;;
	esac
	if [ "$plastic" = RETRO_BLACK ]; then
		hex="$black_hex"
	else
		hex="$(hex_of "$plastic")"
	fi
	key="${title%% - *}"
	if [ -z "$hex" ]; then
		echo "ORPHAN: the plastic $plastic of \"$title\" has no colour in retro_shell.rs"
		fail=1
	elif printf '%s\n' "$sampled" | grep -iF -- "$key" | grep -qi "#$hex"; then
		echo "ok: $title -> $plastic #$hex, source row \"$source\""
	else
		echo "MISMATCH: section 7 has no line naming \"$key\" with #$hex, the colour its plastic $plastic uses"
		fail=1
	fi
done <<EOF2
$records
EOF2

for hex in $(sed -n 's/.*solid(\[\(0x[0-9a-f]*\), \(0x[0-9a-f]*\), \(0x[0-9a-f]*\)\]).*/\1\2\3/p' "$src" | sed 's/0x//g') $black_hex; do
	if grep -qi "#$hex" "$doc" "$sega" "$ps1"; then
		echo "ok: #$hex is recorded in VARIANTS.md, SEGA.md or PS1.md"
	else
		echo "ORPHAN: colour #$hex has no sampling record in VARIANTS.md, SEGA.md or PS1.md"
		fail=1
	fi
done

[ "$rows" -gt 0 ] || {
	echo "slot-nes-snes: no table rows found in $src" >&2
	exit 1
}
if [ "$fail" -ne 0 ]; then
	echo "eval-colour-sources: FAIL"
	exit 1
fi
echo "eval-colour-sources: PASS ($rows rows)"
