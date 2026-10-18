#!/bin/sh
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
up="$root/build/slot-upstream"
ours="$root/build/slot"
allowed_file=crates/slot-retro/src/libretro.rs
allowed_block='#[cfg(test)] mod env_tests;'

[ -d "$up/crates" ] && [ -d "$ours/crates" ] || {
	echo "slot-nes-snes: run task upstream:build and task build first" >&2
	exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
bad=0

fail() {
	echo "slot-nes-snes: upstream test code changed: $1" >&2
	bad=1
}

# Test block rule: a one-line attribute #[cfg(..test..)] (any whitespace, any all/any/not nesting)
# starts a block when it is exactly #[cfg(test)], or the next item is a mod, or a #[test] follows
# it; production code that merely compiles under test, like upstream's
# #[cfg(any(feature = "device", test))] fn, is not a block. Blocks are compared as a multiset
# (a deleted copy of two identical blocks fails). The one allowance is a single
# "#[cfg(test)] mod env_tests;" in libretro.rs, compared after collapsing whitespace so rustfmt's
# two-line form passes.

# Writes each test block of FILE to stdout, one per line (newlines joined with \034), sorted.
# A block runs from the attribute to the matching close brace (or the semicolon of a bodiless
# item). Braces inside strings and chars count like any other brace: upstream's blocks balance
# either way, and a miscount only makes the guard stricter, never looser.
list_blocks() {
	awk '
		function squash(s) { gsub(/[ \t]+/, "", s); return s }
		{ L[NR] = $0 }
		END {
			for (i = 1; i <= NR; i++) {
				if (L[i] !~ /^[ \t]*#\[[ \t]*cfg[ \t]*\(/) continue
				pred = L[i]; sub(/^[ \t]*#\[[ \t]*cfg[ \t]*\(/, "", pred)
				if (pred !~ /(^|[^A-Za-z0-9_])test([^A-Za-z0-9_]|$)/) continue
				rest = L[i]; sub(/^[ \t]*#\[[^]]*\][ \t]*/, "", rest)
				ok = (squash(substr(L[i], 1, length(L[i]) - length(rest))) == "#[cfg(test)]")
				if (rest ~ /^(pub(\([a-z]+\))?[ \t]+)?mod[ \t]/) ok = 1
				for (j = i + 1; j <= NR && L[j] ~ /^[ \t]*(#\[|$)/; j++) if (squash(L[j]) == "#[test]") ok = 1
				if (L[j] ~ /^[ \t]*(pub(\([a-z]+\))?[ \t]+)?mod[ \t]/) ok = 1
				if (!ok) continue
				depth = 0; seen = 0; out = ""
				for (k = i; k <= NR; k++) {
					out = out (k > i ? "\034" : "") L[k]
					line = L[k]
					o = gsub(/\{/, "", line); c = gsub(/\}/, "", line)
					depth += o - c
					if (o) seen = 1
					if ((seen && depth <= 0) || (!seen && L[k] ~ /;[ \t]*$/)) break
				}
				print out
				i = k
			}
		}
	' "$1" | sort
}

# Writes the attribute text of every cfg line that mentions test but is not an exact #[cfg(test)]
# (those start blocks, compared above), whitespace-squashed, sorted. Production items that compile
# under test, like #[cfg(any(feature = "device", test))] fn, have no block to compare, so their
# attribute lines are compared as a multiset instead: a new or removed one fails, a body edit does not.
list_attrs() {
	awk '
		function squash(s) { gsub(/[ \t]+/, "", s); return s }
		/^[ \t]*#\[[ \t]*cfg[ \t]*\(/ {
			pred = $0; sub(/^[ \t]*#\[[ \t]*cfg[ \t]*\(/, "", pred)
			if (pred !~ /(^|[^A-Za-z0-9_])test([^A-Za-z0-9_]|$)/) next
			rest = $0; sub(/^[ \t]*#\[[^]]*\][ \t]*/, "", rest)
			attr = squash(substr($0, 1, length($0) - length(rest)))
			if (attr != "#[cfg(test)]") print attr
		}
	' "$1" | sort
}

shown() { tr '\034' ' ' | cut -c1-90; }
normal() { tr '\034\n\t' '   ' | sed -E 's/ +/ /g; s/^ //; s/ $//'; }

# Every file under crates/*/tests/ in upstream: unchanged and present. New files are ours.
for f in $(cd "$up" && find crates -path 'crates/*/tests/*' -type f | sort); do
	[ -f "$ours/$f" ] || { fail "$f removed"; continue; }
	cmp -s "$up/$f" "$ours/$f" && continue
	case "$f" in
	crates/slot-ui/tests/chrome.rs) prefix=Platform ;;
	crates/slot-store/tests/durability.rs)
		pce='^[[:space:]]*\("cart_platform=pce\\n", None\),$'
		shaders='^[[:space:]]+shader_(nes|snes): Shader::Off,$'
		if [ "$(grep -c 'cart_platform=pce' "$ours/$f")" = 1 ] && [ "$(grep -cE "$pce" "$ours/$f")" = 1 ] &&
			[ "$(grep -cE "$shaders" "$ours/$f")" = 2 ] &&
			perl -0pe 's/(cart_platform=)pce(\\n", None\),\n)/$1nes$2/; s/(\n([ \t]+)shader_gb: Shader::Simpletex,\n)\2shader_nes: Shader::Off,\n\2shader_snes: Shader::Off,\n/$1/' "$ours/$f" >"$tmp/x" &&
			cmp -s "$up/$f" "$tmp/x"; then
			echo "upstream test code: $f uses the named exceptions (cart_platform=pce for cart_platform=nes, shader_nes and shader_snes in the full SlotState literal)"
		else
			fail "$f differs beyond the cart_platform=pce line and the two shader lines"
		fi
		continue ;;
	crates/slot/tests/gpsp.rs)
		mgba='^[ \t]*Core::Mgba( \| Core::Fceumm)?( \| Core::Nestopia)?( \| Core::Snes9x)?( \| Core::Snes9x2005Plus)?( \| Core::GenesisPlusGx)?( \| Core::PcsxRearmed)? => "gpsp_color_correction",$'
		if [ "$(grep -cE "$mgba" "$ours/$f")" = 1 ] &&
			perl -pe "s/^([ \\t]*Core::Mgba)( \\| Core::Fceumm)?( \\| Core::Nestopia)?( \\| Core::Snes9x)?( \\| Core::Snes9x2005Plus)?( \\| Core::GenesisPlusGx)?( \\| Core::PcsxRearmed)? => \"gpsp_color_correction\",\$/\$1 => \"gpsp_color_correction\",/" "$ours/$f" >"$tmp/x" &&
			cmp -s "$up/$f" "$tmp/x"; then
			echo "upstream test code: $f uses the named exception (new cores on the Core::Mgba colour-correction arm)"
		else
			fail "$f differs beyond the Core::Mgba arm's new core tokens"
		fi
		continue ;;
	crates/slot-ui/tests/quick_menu.rs)
		labels='^        \["Game Boy Advance", "Game Boy Color", "Game Boy", "NES", "SNES"(, "Game Gear", "Master System", "Mega Drive"(, "PlayStation")?)?\]$'
		opens='^            QuickRow::ControlsInGame, QuickRow::ScreenNes, QuickRow::ScreenSnes(, QuickRow::ScreenGg, QuickRow::ScreenSms, QuickRow::ScreenMd(, QuickRow::ScreenPs1)?)?$'
		if [ "$(grep -cE "$labels" "$ours/$f")" = 1 ] && [ "$(grep -cE "$opens" "$ours/$f")" = 1 ] &&
			[ "$(grep -cE '^            "CPU",$' "$ours/$f")" -le 1 ] &&
			perl -pe 's/^(        \["Game Boy Advance", "Game Boy Color", "Game Boy"), "NES", "SNES"(, "Game Gear", "Master System", "Mega Drive"(, "PlayStation")?)?(\])$/$1$4/; s/^(            QuickRow::ControlsInGame), QuickRow::ScreenNes, QuickRow::ScreenSnes(, QuickRow::ScreenGg, QuickRow::ScreenSms, QuickRow::ScreenMd(, QuickRow::ScreenPs1)?)?$/$1/' "$ours/$f" |
			perl -0pe 's/(\n            "Lid Power Off",\n)            "CPU",\n(            "Date & Time"\n)/$1$2/' >"$tmp/x" &&
			cmp -s "$up/$f" "$tmp/x"; then
			echo "upstream test code: $f uses the named exceptions (NES, SNES, the Sega systems and PlayStation after Game Boy in the Screen labels and the rows that open pages, CPU before Date & Time in the General labels)"
		else
			fail "$f differs beyond the NES, SNES, Sega and PlayStation tokens in the Screen labels and the rows that open pages, and the CPU line in the General labels"
		fi
		continue ;;
	*) fail "$f differs"; continue ;;
	esac
	# Exact rule: exactly one Game Boy arm line may carry | $prefix::Nes, then optionally
	# | $prefix::Snes, | $prefix::Gg, | $prefix::Sms, | $prefix::Md and | $prefix::Ps1 in that order; everything
	# else, whitespace and final newline included, must be byte-identical. A reflowed arm fails
	# here on purpose: that is a decision for a human.
	tail="( \\| $prefix::Snes( \\| $prefix::Gg( \\| $prefix::Sms( \\| $prefix::Md( \\| $prefix::Ps1)?)?)?)?)?"
	arm="^[[:space:]]*$prefix::Gb \\| $prefix::Gbc \\| $prefix::Nes$tail =>"
	if [ "$(grep -cE "$arm" "$ours/$f")" = 1 ] &&
		perl -pe "s/^([ \\t]*$prefix::Gb \\| $prefix::Gbc) \\| $prefix::Nes$tail =>/\$1 =>/" "$ours/$f" >"$tmp/x" &&
		cmp -s "$up/$f" "$tmp/x"; then
		echo "upstream test code: $f uses the named exception (| $prefix::Nes, | $prefix::Snes, the Sega platforms and | $prefix::Ps1 in the Game Boy arm)"
	else
		fail "$f differs beyond the Game Boy arm's | $prefix::Nes, | $prefix::Snes, Sega and PlayStation platform tokens"
	fi
done

# Every in-source test block of a src file that differs.
allowed_seen=0
for f in $(cd "$up" && find crates -path 'crates/*/src/*' -name '*.rs' | sort); do
	if [ ! -f "$ours/$f" ]; then
		grep -qE '^[[:space:]]*#\[[[:space:]]*cfg[[:space:]]*\(.*test' "$up/$f" && fail "$f removed"
		continue
	fi
	cmp -s "$up/$f" "$ours/$f" && continue
	list_blocks "$up/$f" >"$tmp/u"
	list_blocks "$ours/$f" >"$tmp/o"
	comm -23 "$tmp/u" "$tmp/o" >"$tmp/missing"
	comm -13 "$tmp/u" "$tmp/o" >"$tmp/extra"
	list_attrs "$up/$f" >"$tmp/ua"
	list_attrs "$ours/$f" >"$tmp/oa"
	comm -23 "$tmp/ua" "$tmp/oa" >"$tmp/amissing"
	comm -13 "$tmp/ua" "$tmp/oa" >"$tmp/aextra"
	while IFS= read -r a; do
		fail "$f, cfg(test) attribute '$a' removed"
	done <"$tmp/amissing"
	while IFS= read -r a; do
		fail "$f, cfg(test) attribute '$a' added"
	done <"$tmp/aextra"
	while IFS= read -r b; do
		fail "$f, block '$(printf "%s\n" "$b" | shown)' changed or removed"
	done <"$tmp/missing"
	while IFS= read -r b; do
		if [ "$f" = "$allowed_file" ] && [ "$(printf "%s\n" "$b" | normal)" = "$allowed_block" ]; then
			allowed_seen=$((allowed_seen + 1))
		else
			fail "$f, new block '$(printf "%s\n" "$b" | shown)' not allowed"
		fi
	done <"$tmp/extra"
done
[ "$allowed_seen" -le 1 ] || fail "$allowed_file has $allowed_seen copies of '$allowed_block', at most one is allowed"

[ "$bad" = 0 ] || exit 1
echo "upstream test code: 0 blocks changed"
