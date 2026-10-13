#!/bin/sh
# Cart likeness, success criterion for issue 26. Two steps:
#   sh evals/eval-cart-likeness.sh            renders the four variants (nes famicom snes sfc) through the
#                                             render_nes_shelves test into build/cart-art/<variant>.png, pairs each
#                                             with docs/cart-art/refs/<variant>.jpg, and prepares the blind set in
#                                             build/cart-art/blind/: renders and photos copied under shuffled
#                                             neutral names (R1.., P1..), labels stripped, plus
#                                             build/cart-art/answer-key.txt. Give the reviewer only build/cart-art/blind/, never the key or the
#                                             unshuffled <variant>.png files one level up.
#   sh evals/eval-cart-likeness.sh score FILE scores a reviewer's answers. FILE has one line per render, "R1 P3"
#                                             to match it to a photo or "R1 unrecognisable". Pass is 4 of 4 matched
#                                             and none unrecognisable.
# Prepare mode exits 3 (pending): only score mode exits 0, and only on a 4 of 4 match.
# refs/snes.jpg is an oblique view of two stacked carts, a weak partner for a flat front render. The generated
# label text on a render is not stripped: the reviewer is asked to judge the shell, not the label.
# SLOT_TREE picks the tree that holds the patched slot-ui, default build/slot.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
tree="${SLOT_TREE:-$root/build/slot}"
out="$root/build/cart-art"
refs="$root/docs/cart-art/refs"
blind="$out/blind"
variants="nes famicom snes sfc"

if [ "${1:-}" = score ]; then
	answers="${2:?usage: eval-cart-likeness.sh score FILE}"
	[ -f "$out/answer-key.txt" ] || {
		echo "slot-nes-snes: no answer key, run the eval without arguments first" >&2
		exit 1
	}
	matched=0
	bad=0
	for v in $variants; do
		r="$(awk -v v="$v" '$2 == v { print $1 }' "$out/answer-key.txt" | grep '^R')"
		p="$(awk -v v="$v" '$2 == v { print $1 }' "$out/answer-key.txt" | grep '^P')"
		given="$(awk -v r="$r" '$1 == r { print $2 }' "$answers")"
		if [ "$given" = "$p" ]; then
			matched=$((matched + 1))
			echo "matched: $v ($r is $p)"
		elif [ "$given" = unrecognisable ]; then
			bad=$((bad + 1))
			echo "UNRECOGNISABLE: $v ($r)"
		else
			echo "MISMATCH: $v ($r answered \"$given\", key says $p)"
		fi
	done
	if [ "$matched" -eq 4 ] && [ "$bad" -eq 0 ]; then
		echo "eval-cart-likeness: PASS (4/4 matched)"
		exit 0
	fi
	echo "eval-cart-likeness: FAIL ($matched/4 matched, $bad unrecognisable)"
	exit 1
fi

[ -d "$tree/crates/slot-ui" ] || {
	echo "slot-nes-snes: $tree has no slot-ui, run task build or set SLOT_TREE" >&2
	exit 1
}
for v in $variants; do
	[ -f "$refs/$v.jpg" ] || {
		echo "slot-nes-snes: $refs/$v.jpg is missing" >&2
		exit 1
	}
done

mkdir -p "$out"
rm -rf "$blind"
mkdir -p "$blind/renders" "$blind/photos"
for v in $variants; do
	rm -f "$out/$v.png"
done
if ! log="$(cd "$tree" && CART_ART_DIR="$out" cargo test -p slot-ui --test render_nes_shelves a_shadow_falls_under_every_variant -- --nocapture 2>&1)"; then
	printf '%s\n' "$log" >&2
	echo "slot-nes-snes: the render test failed" >&2
	exit 1
fi
printf '%s\n' "$log" | grep -E '^(wrote|test result)'
printf '%s\n' "$log" | grep -Eq '^test result: ok\. [1-9][0-9]* passed' || {
	echo "slot-nes-snes: the render test ran no tests" >&2
	exit 1
}
for v in $variants; do
	[ -f "$out/$v.png" ] || {
		echo "slot-nes-snes: the render test wrote no $out/$v.png" >&2
		exit 1
	}
done

shuffled() {
	awk -v seed="$1" 'BEGIN { srand(seed) } { print rand() "\t" $0 }' | sort -n | cut -f2-
}

seed="${SEED:-$(date +%s)}"
order="$(printf '%s\n' $variants | shuffled "$seed")"
# photos get a different order from the renders at every position, so "R1 P1" is never right
try=1
printf '%s\n' "$order" >"$blind/.a"
while :; do
	photos="$(printf '%s\n' $variants | shuffled "$((seed + try))")"
	printf '%s\n' "$photos" >"$blind/.b"
	[ -z "$(paste -d' ' "$blind/.a" "$blind/.b" | awk '$1 == $2')" ] && break
	try=$((try + 1))
done
rm -f "$blind/.a" "$blind/.b"

: >"$out/answer-key.txt"
n=1
for v in $order; do
	cp "$out/$v.png" "$blind/renders/R$n.png"
	echo "R$n $v" >>"$out/answer-key.txt"
	n=$((n + 1))
done
n=1
for v in $photos; do
	cp "$refs/$v.jpg" "$blind/photos/P$n.jpg"
	echo "P$n $v" >>"$out/answer-key.txt"
	n=$((n + 1))
done
cat >"$blind/INSTRUCTIONS.txt" <<'EOT'
Four rendered game cartridges (renders/R1.png to R4.png) and four photographs of real cartridges
(photos/P1.jpg to P4.jpg). Each render matches exactly one photo, in a different order. For every render
write one line "R<n> P<m>" for the photo it depicts, or "R<n> unrecognisable" if it does not read as a
cartridge of any of the four kinds. Judge the shell: outline, ridges, grooves, label position and shape,
proportions. Ignore the label text and the colour of the printed label. Some photos are oblique or show two
cartridges stacked, so match on the kind of cartridge, not the camera angle.
EOT
echo "eval-cart-likeness: renders in $out, blind set in $blind (answer key: $out/answer-key.txt, keep it from the reviewer)"
echo "eval-cart-likeness: PENDING, blind judgement not done (exit 3)"
exit 3
