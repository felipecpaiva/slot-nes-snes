#!/bin/sh
# Device controls check: does every libretro joypad id a core polls get answered by some device button?
# Per game line: point slot at the game through Config/slot.state, pick the core, turn on SLOT_TRACE, restart
# slot so it boots into the game, press every device button and a set of chords one at a time, eject through
# the menu, pull slot.log with every ROM name redacted, then pair each press with the "slot: pad answered"
# lines it caused. Everything it touches on the device is backed up first and put back on exit, even on failure.
#
#   sh scripts/device-controls.sh                         all default games (see the list below)
#   GAMES=path/to/list sh scripts/device-controls.sh      one line per game: PLATDIR|core|stem, # comments
#   sh scripts/device-controls.sh selftest                local checks, no device
#   sh scripts/device-controls.sh parse <log> <presses>   reparse a saved log and presses file, no device
# Env: SD=/mnt/sdcard ADB=adb DATE=<today> GAMES (file) NODE_KEYS=/dev/input/eventN NODE_HAT=/dev/input/eventN
# Output: docs/device-controls/<date>/<id>.log and <id>.presses, <id> = PLATDIR lowercased plus the line index.
# What counts: harness/controls-reads.tsv lists, per shelf, the RetroPad ids its core reads (controls_pages.rs
# keeps it equal to the host test's lists). Many cores poll all 16 ids every frame, so only a polled id on that
# list must be answered by some press. docs/device-controls/exempt.txt ("PLATDIR id reason") can excuse more.
# Exit status 1 if any game has a polled id it reads that no press answered.
#
# Per press the device writes "press <name> <uptime>" to a presses file (uptime from /proc/uptime, kept for the
# record only: slot.log lines carry no wall time). Each press is anchored in the log on the
# "slot: GbaDown(<Btn>) in ..." line of its first button (for a chord, the next GbaDown must be its second
# button); the answered ids of a press are the OR of every "slot: pad answered" between its anchor and the next
# press's anchor. A press whose anchor never shows (taken by a slot shortcut or swallowed) is "not delivered"
# and does not shift the presses after it.
# Input injection, eject gesture and the SLOT_TRACE export are as in scripts/auto-play.sh.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
SD="${SD:-/mnt/sdcard}"
ADB="${ADB:-adb}"
DATE="${DATE:-$(date +%Y-%m-%d)}"
GAMES="${GAMES:-}"
NODE_KEYS="${NODE_KEYS:-}"
NODE_HAT="${NODE_HAT:-}"
tab="$(printf '\t')"
mt="${TMPDIR:-/tmp}"
exempt="$root/docs/device-controls/exempt.txt"
reads="$root/harness/controls-reads.tsv"

die() {
	echo "slot-nes-snes: $*" >&2
	exit 1
}
shq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
dev() { $ADB shell "$1" </dev/null 2>/dev/null | tr -d '\r'; }
dx() { $ADB shell "$1" </dev/null >/dev/null 2>&1; }

# Default games: PLATDIR|core|stem. Stems exactly as on the card. These are game titles, they never reach a
# saved log (redacted to the id) and no ROM is ever copied off the card.
games="CPS1|fbneo|knights
CPS2|fbneo|ssf2t
NEOGEO|fbneo|mslug
SNES|snes9x|Super Mario World (USA)
MD|genesis_plus_gx|Street Fighter II' - Special Champion Edition (USA)
# PS1|pcsx_rearmed|<a game using L2 and R2>
VB|mednafen_vb|Red Alarm (Japan, USA)"

# The game list as id|PLATDIR|core|stem, comments and blank lines dropped, index counted over game lines.
game_list() {
	awk -F'|' '/^[ \t]*(#|$)/ { next } { n++; print tolower($1) n "|" $0 }'
}

# Presses in order: name|first file|second file (chords). Files are the event file names below.
presses="A|a|
B|b|
X|x|
Y|y|
L1|l1|
R1|r1|
L2|l2|
R2|r2|
SELECT|select|
START|start|
UP|up|
DOWN|down|
LEFT|left|
RIGHT|right|
L1+UP|l1|up
L1+DOWN|l1|down
L1+LEFT|l1|left
L1+RIGHT|l1|right
R1+A|r1|a
R1+B|r1|b
R1+X|r1|x
R1+Y|r1|y"

# Event file name -> kind and code, as slot maps them (crates/slot/src/input/evdev.rs code_to_btn and Hat):
# X and Y are swapped against the Linux BTN_X/BTN_Y names, 0x139 is unused. Hat: X -1 left +1 right, Y -1 up +1 down.
code_of() {
	case "$1" in
	a) echo "key 304" ;; b) echo "key 305" ;; y) echo "key 306" ;; x) echo "key 307" ;;
	l1) echo "key 308" ;; r1) echo "key 309" ;; select) echo "key 310" ;; start) echo "key 311" ;;
	menu) echo "key 312" ;; l2) echo "key 314" ;; r2) echo "key 315" ;;
	up | down) echo "abs 17" ;; left | right) echo "abs 16" ;;
	*) return 1 ;;
	esac
}

# One struct input_event as a printf format string: aarch64, 16 bytes of zero timeval, u16 type, u16 code,
# i32 value, little endian, 24 bytes. ev TYPE CODE VALUE
ev() {
	v=$(($3 & 4294967295))
	printf '\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000'
	printf '\\%03o\\%03o\\%03o\\%03o' $(($1 & 255)) $(($1 >> 8 & 255)) $(($2 & 255)) $(($2 >> 8 & 255))
	printf '\\%03o\\%03o\\%03o\\%03o' $((v & 255)) $((v >> 8 & 255)) $((v >> 16 & 255)) $((v >> 24 & 255))
}
# key or hat change followed by SYN_REPORT, as one 48 byte write
key() { ev 1 "$1" "$2"; ev 0 0 0; }
abs() { ev 3 "$1" "$2"; ev 0 0 0; }

# Down and up event file contents for an event file name: dn|up NAME
frame() {
	set -- "$1" "$2" $(code_of "$2")
	case "$3" in
	key) if [ "$1" = dn ]; then key "$4" 1; else key "$4" 0; fi ;;
	abs)
		case "$1$2" in dnup | dnleft) abs "$4" -1 ;; dndown | dnright) abs "$4" 1 ;; *) abs "$4" 0 ;; esac
		;;
	esac
}

# Pair presses with answered ids. parse_controls LOG PRESSES [EXEMPT [READS]]. The presses file starts with
# "plat PLATDIR", then "press NAME UPTIME" lines. Prints one line per press, then polled, unanswered, names,
# and "result ok" or "result fail".
parse_controls() {
	awk -v ex="${3:-}" -v rd="${4:-}" '
	function hx(s,   i, c, v) { sub(/^0x/, "", s); v = 0; for (i = 1; i <= length(s); i++) { c = index("0123456789abcdef", tolower(substr(s, i, 1))) - 1; if (c < 0) break; v = v * 16 + c } return v }
	function bit(x, n) { return int(x / 2 ^ n) % 2 }
	function bor(a, b,   n, r) { r = 0; for (n = 0; n < 16; n++) if (bit(a, n) || bit(b, n)) r += 2 ^ n; return r }
	function btn(p) { return (p in bn) ? bn[p] : p }
	BEGIN {
		split("A B X Y L1 R1 L2 R2 SELECT START UP DOWN LEFT RIGHT", k, " ")
		split("A B X Y L1 R1 L2 R2 Select Start Up Down Left Right", v, " ")
		for (i in k) bn[k[i]] = v[i]
	}
	{ f = (FILENAME == ARGV[1]) ? 1 : 2 }
	f == 1 && /^slot: GbaDown\(/ { g = $2; sub(/^GbaDown\(/, "", g); sub(/\)$/, "", g); ng++; gb[ng] = g; gl[ng] = FNR; next }
	f == 1 && /^slot: pad answered 0x/ { na++; al[na] = FNR; av[na] = hx($4); next }
	f == 1 && /^slot: pad polled 0x/ { polled = bor(polled, hx($4)); next }
	f == 1 && /^slot: pad names / { if (names == "") { names = $0; sub(/^slot: pad /, "", names) } next }
	f == 2 && $1 == "plat" { plat = toupper($2); next }
	f == 2 && $1 == "press" { np++; pn[np] = $2; lead[np] = btn($2); sec[np] = ""; if (index($2, "+")) { split($2, ch, "+"); lead[np] = btn(ch[1]); sec[np] = btn(ch[2]) }; next }
	END {
		if (ex != "") while ((getline line < ex) > 0) { split(line, w, " "); if (w[1] !~ /^#/ && w[2] != "" && toupper(w[1]) == plat) exem[w[2] + 0] = 1 }
		readmask = 65535; listed = (rd == "")
		if (rd != "") while ((getline line < rd) > 0) { split(line, w, "\t"); if (w[1] !~ /^#/ && toupper(w[1]) == plat) { readmask = hx(w[2]); listed = 1 } }
		# anchor: first GbaDown at or after j of the lead, followed (for a chord) by a GbaDown of the second, and
		# before the anchor any later press would take (so a swallowed press does not steal a later one)
		j = 1
		for (p = 1; p <= np; p++) {
			c1 = find(p, j); lo = 0
			for (q = p + 1; q <= np; q++) { c = find(q, j); if (c && (!lo || c < lo)) lo = c }
			if (c1 && (!lo || c1 < lo)) { at[p] = gl[c1]; j = c1 + 1 } else at[p] = 0
		}
		all = 0; got = 0
		for (p = 1; p <= np; p++) {
			if (!at[p]) { print pn[p] " -> not delivered"; continue }
			got++
			nx = 0; for (q = p + 1; q <= np; q++) if (at[q]) { nx = at[q]; break }
			m = 0; for (i = 1; i <= na; i++) if (al[i] > at[p] && (!nx || al[i] < nx)) m = bor(m, av[i])
			all = bor(all, m)
			printf "%s -> answered 0x%04x\n", pn[p], m
		}
		printf "polled 0x%04x\n", polled
		miss = ""; fail = 0
		for (n = 0; n < 16; n++) {
			if (!bit(polled, n) || bit(all, n) || !bit(readmask, n)) continue
			if ((n == 14 || n == 15) && plat != "VB") continue
			if (n in exem) { miss = miss " " n "(exempt)"; continue }
			miss = miss " " n; fail = 1
		}
		print "unanswered" (miss == "" ? " none" : miss)
		if (names != "") print names
		# nothing polled or nothing delivered means the trace is missing (old slot, no SLOT_TRACE, no game)
		if (!listed) print "no read list for " plat " in harness/controls-reads.tsv"
		print "result " ((!polled || !got || !listed) ? "nodata" : fail ? "fail" : "ok")
	}
	function find(p, from,   i) {
		for (i = from; i <= ng; i++) if (gb[i] == lead[p] && (sec[p] == "" || (i < ng && gb[i + 1] == sec[p]))) return i
		return 0
	}' "$1" "$2"
}

selftest() {
	z16="$(printf '%032d' 0)"
	got="$(printf "$(key 304 1)" | od -An -tx1 | tr -d ' \n')"
	[ "$got" = "${z16}0100300101000000$(printf '%048d' 0)" ] || die "selftest: key 304 down is $got"
	for f in a y l2 r2 up down left right; do
		for e in dn up; do
			[ "$(printf "$(frame $e $f)" | wc -c | tr -d ' ')" = 48 ] || die "selftest: $f.$e is not 48 bytes"
		done
	done
	got="$(printf "$(frame dn up)" | od -An -tx1 | tr -d ' \n' | cut -c33-48)"
	[ "$got" = 03001100ffffffff ] || die "selftest: up.dn is $got, want HAT0Y -1"
	got="$(printf "$(frame dn y)" | od -An -tx1 | tr -d ' \n' | cut -c33-48)"
	[ "$got" = 0100320101000000 ] || die "selftest: y.dn is $got, want key 306"
	got="$(printf "$(frame up right)" | od -An -tx1 | tr -d ' \n' | cut -c33-48)"
	[ "$got" = 0300100000000000 ] || die "selftest: right.up is $got, want HAT0X 0"

	[ "$(printf '%s\n' "$games" | game_list | sed -n '6p')" = "vb6|VB|mednafen_vb|Red Alarm (Japan, USA)" ] ||
		die "selftest: the default game list does not give vb6 for VB"

	f="$mt/dc.$$"
	# A answered, B swallowed (no GbaDown, must not shift X), X answered, L1+UP chord, polled has 9 never
	# answered and 14 (ignored off VB).
	cat >"$f.log" <<'EOF'
slot: boot: start at 1.0 ms
slot: pad polled 0x0101
slot: pad answered 0x0001
slot: GbaDown(A) in Playing { cart: "snes1" }
slot: pad 0x0100
slot: pad answered 0x0100
slot: pad polled 0x4311
slot: GbaUp(A) in Playing { cart: "snes1" }
slot: pad 0x0000
slot: pad answered 0x0000
slot: GbaDown(X) in Playing { cart: "snes1" }
slot: pad 0x0200
slot: pad answered 0x0800
slot: GbaUp(X) in Playing { cart: "snes1" }
slot: pad answered 0x0000
slot: GbaDown(L1) in Playing { cart: "snes1" }
slot: pad answered 0x0400
slot: GbaDown(Up) in Playing { cart: "snes1" }
slot: pad answered 0x0410
slot: GbaUp(Up) in Playing { cart: "snes1" }
slot: GbaUp(L1) in Playing { cart: "snes1" }
slot: pad answered 0x0000
slot: pad names [(0, "B"), (8, "A")]
EOF
	printf '%s\n' 'plat SNES' 'press A 10.00' 'press B 11.00' 'press X 12.00' 'press L1+UP 13.00' 'press L1+DOWN 14.00' >"$f.pr"
	: >"$f.ex"
	got="$(parse_controls "$f.log" "$f.pr" "$f.ex" | tr '\n' ';')"
	want='A -> answered 0x0100;B -> not delivered;X -> answered 0x0800;L1+UP -> answered 0x0410;L1+DOWN -> not delivered;polled 0x4311;unanswered 0 9;names [(0, "B"), (8, "A")];result fail;'
	[ "$got" = "$want" ] || die "selftest: parse gave $got"
	# the same log on VB counts 14; an exemption for SNES 0 and 9 turns the SNES run into a pass
	sed 's/^plat SNES/plat VB/' "$f.pr" >"$f.vb"
	parse_controls "$f.log" "$f.vb" "$f.ex" | grep -qx 'unanswered 0 9 14' || die "selftest: VB does not count id 14"
	printf '%s\n' '# PLATDIR id reason' 'snes 9 not wired' 'SNES 0 answered before the first press' 'VB 9 other platform' >"$f.ex"
	got="$(parse_controls "$f.log" "$f.pr" "$f.ex" | grep -E "^(unanswered|result) " | tr '\n' ';')"
	[ "$got" = 'unanswered 0(exempt) 9(exempt);result ok;' ] || die "selftest: exemptions gave $got"
	# a read list without id 9 means the core does not read X, so only 0 is missing; a shelf off the list fails
	: >"$f.ex"
	printf '# shelf\tmask\nSNES\t0x0dfd\n' >"$f.rd"
	got="$(parse_controls "$f.log" "$f.pr" "$f.ex" "$f.rd" | grep -E "^(unanswered|result) " | tr '\n' ';')"
	[ "$got" = 'unanswered 0;result fail;' ] || die "selftest: the read list gave $got"
	got="$(parse_controls "$f.log" "$f.vb" "$f.ex" "$f.rd" | tail -n 1)"
	rm -f "$f.log" "$f.pr" "$f.ex" "$f.vb" "$f.rd"
	[ "$got" = 'result nodata' ] || die "selftest: a shelf off the read list gave $got"
	# single L1 and R1 swallowed, the chords are not: L1 must not take L1+UP's anchor and push L2 out
	printf '%s\n' 'slot: pad polled 0x1410' 'slot: GbaDown(L2) in Playing' 'slot: pad answered 0x1000' 'slot: pad answered 0x0000' \
		'slot: GbaDown(L1) in Playing' 'slot: GbaDown(Up) in Playing' 'slot: pad answered 0x0010' 'slot: pad answered 0x0000' >"$f.log"
	printf '%s\n' 'plat SNES' 'press L1 1' 'press R1 2' 'press L2 3' 'press L1+UP 4' >"$f.pr"
	got="$(parse_controls "$f.log" "$f.pr" | tr '\n' ';')"
	[ "$got" = 'L1 -> not delivered;R1 -> not delivered;L2 -> answered 0x1000;L1+UP -> answered 0x0010;polled 0x1410;unanswered 10;result fail;' ] ||
		die "selftest: swallowed L1 and R1 gave $got"
	# an empty log (old slot, no SLOT_TRACE, no game) must not pass
	: >"$f.log"
	got="$(parse_controls "$f.log" "$f.pr" | tail -n 1)"
	rm -f "$f.log" "$f.pr"
	[ "$got" = 'result nodata' ] || die "selftest: an empty log gave $got"
	echo "selftest ok"
}

case "${1:-}" in
selftest)
	selftest
	exit 0
	;;
parse)
	[ -f "${2:-}" ] && [ -f "${3:-}" ] || die "usage: $0 parse <log> <presses>"
	parse_controls "$2" "$3" "$exempt" "$reads"
	exit 0
	;;
esac

# ---------------------------------------------------------------- device run

if [ -n "$GAMES" ]; then
	[ -f "$GAMES" ] || die "no game list at $GAMES"
	sel="$(game_list <"$GAMES")"
else
	sel="$(printf '%s\n' "$games" | game_list)"
fi
[ -n "$sel" ] || die "the game list is empty"
[ "$($ADB get-state 2>/dev/null)" = device ] || die "no adb device in state device ($ADB get-state), connect the RG34XXSP"

out="$root/docs/device-controls/$DATE"
tmp="$(mktemp -d "$mt/dc.XXXXXX")"
printf '%s\n' "$sel" >"$tmp/sel"
cut -d"|" -f4 "$tmp/sel" >"$tmp/listed"
: >"$tmp/backed"
bk="$SD/controls-backup-$(date +%Y%m%d-%H%M%S)"
cfg="$SD/Config"
tf="$SD/System/launch_frontend.sh"
armed=0

slot_up() { [ -n "$(dev "sh $(shq "$bk/inj/slotctl.sh") pids")" ]; }

# Stop slot (kill -9, nothing is written on the way out), then either a supervisor brings it back or we
# start it ourselves through launch_frontend.sh. Fails if slot is not running afterwards.
restart_slot() {
	dx "sh $(shq "$bk/inj/slotctl.sh") stop"
	n=0
	while [ "$n" -lt 8 ]; do
		slot_up && break
		sleep 1
		n=$((n + 1))
	done
	slot_up || dx "sh $(shq "$bk/inj/slotctl.sh") start"
	n=0
	while [ "$n" -lt 10 ]; do
		slot_up && return 0
		sleep 1
		n=$((n + 1))
	done
	return 1
}

# Per game saves and the resume state: copied on first use, put back before the run and on exit (pressing
# every button can save or load in game). Args: PLATDIR core stem.
cart_dir() { printf '%s/c%s' "$bk" "$(printf '%s' "$1|$2|$3" | cksum | cut -d' ' -f1)"; }
backup_cart() {
	grep -qxF -- "$1|$2|$3" "$tmp/backed" && return 0
	dx "d=$(shq "$(cart_dir "$1" "$2" "$3")"); mkdir -p \"\$d/saves\"
cp -p $(shq "$SD/Saves/$1/$3").* \"\$d/saves/\" 2>/dev/null
[ -d $(shq "$SD/States/$1/$2/$3") ] && cp -rp $(shq "$SD/States/$1/$2/$3") \"\$d/states\"
true" || die "cannot back up the saves of $3"
	printf '%s\n' "$1|$2|$3" >>"$tmp/backed"
}
restore_one() {
	dx "d=$(shq "$(cart_dir "$1" "$2" "$3")"); [ -d \"\$d\" ] || exit 0
rm -f $(shq "$SD/Saves/$1/$3").*
cp -p \"\$d/saves/\"* $(shq "$SD/Saves/$1/") 2>/dev/null
rm -rf $(shq "$SD/States/$1/$2/$3")
[ -d \"\$d/states\" ] && cp -rp \"\$d/states\" $(shq "$SD/States/$1/$2/$3")
true"
}

# BAK LIVE: LIVE with the keys set_config writes (cart, cart_platform, eject_save) put back as in BAK,
# or dropped where BAK has none.
own_keys() {
	awk -F= '
	NR == FNR { if ($1 == "cart" || $1 == "cart_platform" || $1 == "eject_save") b[$1] = $0; next }
	$1 == "cart" || $1 == "cart_platform" || $1 == "eject_save" { if ($1 in b) print b[$1]; next }
	{ print }' "$1" "$2"
}

# Put the device back. Runs on every exit once the backup exists.
cleanup() {
	rc=$?
	trap - EXIT INT TERM
	set +e
	if [ "$armed" = 1 ]; then
		echo "restoring the device from $bk" >&2
		dx "
cd $(shq "$bk") || exit 1
if [ -f selected_core.txt ]; then cp -p selected_core.txt $(shq "$cfg/selected_core.txt"); else rm -f $(shq "$cfg/selected_core.txt"); fi
[ -f launch_frontend.sh ] && cp -p launch_frontend.sh $(shq "$tf")
true" || echo "slot-nes-snes: RESTORE FAILED, copy the files in $bk back by hand" >&2
		dx "sh $(shq "$bk/inj/slotctl.sh") stop"
		if $ADB pull "$cfg/slot.state" "$tmp/slot.state.live" </dev/null >/dev/null 2>&1 &&
			$ADB pull "$bk/slot.state" "$tmp/slot.state.bak" </dev/null >/dev/null 2>&1; then
			own_keys "$tmp/slot.state.bak" "$tmp/slot.state.live" >"$tmp/slot.state.back" &&
				$ADB push "$tmp/slot.state.back" "$cfg/slot.state" </dev/null >/dev/null ||
				echo "slot-nes-snes: RESTORE FAILED for slot.state, copy $bk/slot.state back by hand" >&2
		else
			dx "cp -p $(shq "$bk/slot.state") $(shq "$cfg/slot.state")" ||
				echo "slot-nes-snes: RESTORE FAILED for slot.state, copy $bk/slot.state back by hand" >&2
		fi
		while IFS='|' read -r pd co st; do restore_one "$pd" "$co" "$st"; done <"$tmp/backed"
		restart_slot || echo "slot-nes-snes: slot did not come back, power-cycle the device" >&2
		dx "rm -rf $(shq "$bk/inj")"
		echo "device restored to the shelf, backup kept in $bk (delete it when happy)" >&2
	fi
	rm -rf "$tmp"
	exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

# ---------------------------------------------------------------- preflight

dx "sleep 0.05" || die "the device sleep does not take fractions, the injection timing needs it"
dx "test -f $(shq "$cfg/slot.state")" || die "no $cfg/slot.state on the device (run slot once so it writes one)"
dx "test -f $(shq "$tf")" || die "no $tf on the device"
dx "grep -q '^export SLOT_ROOT' $(shq "$tf")" || die "$tf has no 'export SLOT_ROOT' line to hang the SLOT_TRACE export on"
cur="$(dev "grep '^cart=' $(shq "$cfg/slot.state")")"
[ "$cur" = "cart=" ] || echo "slot-nes-snes: warning: slot.state has '$cur', a game may be running. Its unsaved play is lost when slot is stopped." >&2

caps="$(dev 'for d in /sys/class/input/event*; do echo "${d##*/}|$(cat $d/device/capabilities/key 2>/dev/null)|$(cat $d/device/capabilities/abs 2>/dev/null)"; done')"
node_for() { # key|abs code -> node path
	printf '%s\n' "$caps" | awk -F'|' -v kind="$1" -v n="$2" '
	function hasbit(c, n,   k, w, i, s, t, p, v) {
		k = split(c, w, " "); s = ""
		for (i = 1; i <= k; i++) { t = w[i]; while (length(t) < 16) t = "0" t; s = s t }
		p = int(n / 4); if (s == "" || p >= length(s)) return 0
		v = index("0123456789abcdef", tolower(substr(s, length(s) - p, 1))) - 1
		return int(v / (2 ^ (n % 4))) % 2
	}
	hasbit(kind == "key" ? $2 : $3, n) { print "/dev/input/" $1; exit }'
}

mkdir -p "$tmp/inj" "$out"

# Event files, and the node each one goes to.
: >"$tmp/nodes"
for f in a b x y l1 r1 l2 r2 select start menu up down left right; do
	set -- $(code_of "$f")
	case "$1" in key) nd="${NODE_KEYS:-$(node_for key "$2")}" ;; *) nd="${NODE_HAT:-$(node_for abs "$2")}" ;; esac
	[ -n "$nd" ] || die "no input node on the device reports $1 code $2 ($f) (capabilities: $caps). Set NODE_KEYS and NODE_HAT"
	printf "$(frame dn "$f")" >"$tmp/inj/$f.dn"
	printf "$(frame up "$f")" >"$tmp/inj/$f.up"
	printf '%s %s\n' "$f" "$nd" >>"$tmp/nodes"
done
nd_of() { awk -v f="$1" '$1 == f { print $2 }' "$tmp/nodes"; }

cat >"$tmp/inj/slotctl.sh" <<EOF
#!/bin/sh
SD='$SD'
EOF
cat >>"$tmp/inj/slotctl.sh" <<'EOF'
pids() { for p in /proc/[0-9]*; do tr '\0' '\n' <"$p/cmdline" 2>/dev/null | grep -qE '/[S]ystem/slot$' && echo "${p#/proc/}"; done; }
case "$1" in
pids) pids ;;
stop)
	for p in $(pids); do kill -9 "$p"; done
	n=0
	while [ -n "$(pids)" ] && [ "$n" -lt 50 ]; do sleep 0.1; n=$((n + 1)); done
	;;
start)
	[ -n "$(pids)" ] && exit 0
	if command -v setsid >/dev/null 2>&1; then
		setsid sh "$SD/System/launch_frontend.sh" </dev/null >/dev/null 2>&1 &
	else
		nohup sh "$SD/System/launch_frontend.sh" </dev/null >/dev/null 2>&1 &
	fi
	sleep 1
	;;
esac
EOF
# Device press script: sh press.sh PLATDIR. Every press: hold 0.5 s, release, wait 0.5 s. A chord holds its
# first button 0.2 s before and after the second. Then hold MENU 1.5 s to eject (not recorded as a press).
# The presses file lives outside inj so cleanup does not take it before it is pulled.
{
	printf '#!/bin/sh\nd=%s\nP=%s\n' "$(shq "$bk/inj")" "$(shq "$bk/presses.txt")"
	cat <<'EOF'
mark() { read -r u _ </proc/uptime; echo "press $1 $u" >>"$P"; }
press() { mark "$1"; cat "$d/$3.dn" >"$2"; sleep 0.5; cat "$d/$3.up" >"$2"; sleep 0.5; }
chord() { mark "$1"; cat "$d/$3.dn" >"$2"; sleep 0.2; cat "$d/$5.dn" >"$4"; sleep 0.5; cat "$d/$5.up" >"$4"; sleep 0.2; cat "$d/$3.up" >"$2"; sleep 0.5; }
echo "plat $1" >"$P"
EOF
	printf '%s\n' "$presses" | while IFS='|' read -r name f1 f2; do
		if [ -z "$f2" ]; then
			printf 'press %s %s %s\n' "$name" "$(nd_of "$f1")" "$f1"
		else
			printf 'chord %s %s %s %s %s\n' "$name" "$(nd_of "$f1")" "$f1" "$(nd_of "$f2")" "$f2"
		fi
	done
	printf 'cat "$d/menu.dn" >%s; sleep 1.5; cat "$d/menu.up" >%s\n' "$(nd_of menu)" "$(nd_of menu)"
} >"$tmp/inj/press.sh"

# Everything below changes the device. Backup first, nothing is touched if it fails.
dx "mkdir -p $(shq "$bk/inj")" || die "cannot create $bk"
dx "cd $(shq "$bk") && cp -p $(shq "$cfg/slot.state") slot.state && { [ -f $(shq "$cfg/selected_core.txt") ] && cp -p $(shq "$cfg/selected_core.txt") selected_core.txt; true; } && cp -p $(shq "$tf") launch_frontend.sh && { cp -p $(shq "$SD/Logs/slot.log") slot.log.bak 2>/dev/null; cp -p $(shq "$SD/Logs/slot.log.1") slot.log.1.bak 2>/dev/null; true; }" ||
	die "the backup failed, nothing was changed"
for f in "$tmp"/inj/*; do $ADB push "$f" "$bk/inj/" </dev/null >/dev/null || die "adb push of ${f##*/} failed"; done
armed=1

# Redaction list: every ROM name on the card (6 characters or more).
dev "for f in $(shq "$SD/Games")/*/*; do [ -f \"\$f\" ] && echo \"\${f##*/}\"; done" | sed 's/\.[A-Za-z0-9]\{1,5\}$//' | awk 'length($0) >= 6' >"$tmp/stems"

# True once the fixed string shows up in slot.log, within the given seconds.
seen() {
	n=0
	while [ "$n" -lt "$2" ]; do
		c="$(dev "grep -cF -- $(shq "$1") $(shq "$SD/Logs/slot.log")")"
		case "$c" in '' | *[!0-9]*) c=0 ;; esac
		[ "$c" -gt 0 ] && return 0
		sleep 1
		n=$((n + 1))
	done
	return 1
}

# Originals as pulled once, edited fresh for every game.
$ADB pull "$cfg/selected_core.txt" "$tmp/sel.orig" </dev/null >/dev/null 2>&1 || : >"$tmp/sel.orig"
$ADB pull "$tf" "$tmp/launch.orig" </dev/null >/dev/null || die "cannot read launch_frontend.sh"
if grep -q 'SLOT_TRACE=' "$tmp/launch.orig"; then
	cp "$tmp/launch.orig" "$tmp/launch.new"
else
	awk '{ print } /^export SLOT_ROOT/ { print "export SLOT_TRACE=1" }' "$tmp/launch.orig" >"$tmp/launch.new"
fi

set_config() { # stem platform core
	$ADB pull "$cfg/slot.state" "$tmp/slot.state.cur" </dev/null >/dev/null || die "cannot read slot.state"
	CART="$1" CP="$2" awk '
	/^cart=/ { print "cart=" ENVIRON["CART"]; a = 1; next }
	/^cart_platform=/ { print "cart_platform=" ENVIRON["CP"]; b = 1; next }
	/^eject_save=/ { print "eject_save=0"; e = 1; next }
	{ print }
	END { if (!a) print "cart=" ENVIRON["CART"]; if (!b) print "cart_platform=" ENVIRON["CP"]; if (!e) print "eject_save=0" }' "$tmp/slot.state.cur" >"$tmp/slot.state.new"
	$ADB push "$tmp/slot.state.new" "$cfg/slot.state" </dev/null >/dev/null || die "cannot write slot.state"
	S="$1" C="$3" awk '
	{ i = index($0, "="); k = substr($0, 1, i - 1); gsub(/^[ \t]+|[ \t]+$/, "", k); if (i > 0 && k == ENVIRON["S"]) next; print }
	END { print ENVIRON["S"] " = " ENVIRON["C"] }' "$tmp/sel.orig" >"$tmp/sel.new"
	$ADB push "$tmp/sel.new" "$cfg/selected_core.txt" </dev/null >/dev/null || die "cannot write selected_core.txt"
}

failed=""
skipped=""
checked=0
while IFS='|' read -r id pd core stem; do
	pl="$(printf '%s' "$pd" | tr '[:upper:]' '[:lower:]')"
	echo "== $id ($pd $core)"
	dx "test -f $(shq "$SD/System/${core}_libretro.so")" || {
		echo "  skipped: no $core core in System/" >&2
		skipped="$skipped $id"
		continue
	}
	dx "for f in $(shq "$SD/Games/$pd/$stem").*; do [ -f \"\$f\" ] && exit 0; done; exit 1" || {
		echo "  skipped: that game is not on the card under Games/$pd (name not printed)" >&2
		skipped="$skipped $id"
		continue
	}
	checked=$((checked + 1))
	backup_cart "$pd" "$core" "$stem"
	restore_one "$pd" "$core" "$stem"
	set_config "$stem" "$pl" "$core"
	$ADB push "$tmp/launch.new" "$tf" </dev/null >/dev/null || die "cannot write launch_frontend.sh"
	dx "chmod 755 $(shq "$tf"); rm -f $(shq "$SD/Logs/slot.log") $(shq "$bk/presses.txt"); touch $(shq "$bk/mark")"
	restart_slot || die "slot did not start"
	if seen "launch: first frame shown" 120; then
		sleep 3
		dx "sh $(shq "$bk/inj/press.sh") $(shq "$pd")" || echo "  the press script failed" >&2
		seen "samples dropped" 40 || echo "  no session summary line, the eject did not take" >&2
	else
		echo "  no first game frame within 120 s, logging what exists" >&2
	fi
	$ADB pull "$bk/presses.txt" "$out/$id.presses" </dev/null >/dev/null 2>&1 || printf 'plat %s\n' "$pd" >"$out/$id.presses"
	raw="$tmp/slot.raw"
	$ADB pull "$SD/Logs/slot.log" "$raw" </dev/null >/dev/null 2>&1 || : >"$raw"
	if dx "test $(shq "$SD/Logs/slot.log.1") -nt $(shq "$bk/mark")"; then
		$ADB pull "$SD/Logs/slot.log.1" "$tmp/slot.raw1" </dev/null >/dev/null 2>&1 && cat "$tmp/slot.raw1" "$raw" >"$tmp/slot.raw2" && mv "$tmp/slot.raw2" "$raw"
	fi
	# keep only the last slot session
	last="$(grep -n 'slot: boot: start at' "$raw" | tail -n 1 | cut -d: -f1)"
	if [ -n "$last" ]; then tail -n "+$last" "$raw" >"$raw.last" && mv "$raw.last" "$raw"; fi
	# longest names first, so a short title inside a long one cannot leave half a name behind; every listed
	# stem too, whatever its length (short arcade names sit below the 6 character floor of the card list)
	{
		printf '%s\t%s\n' "$stem" "$id"
		awk -v s="$stem" -v t="$tab" '$0 != s { print $0 t "other-rom" }' "$tmp/stems" "$tmp/listed"
	} | awk -F'\t' '{ print length($1) "\t" $0 }' | sort -t "$tab" -k1,1nr | cut -f2- >"$tmp/map"
	awk -F'\t' 'NR == FNR { s[NR] = $1; r[NR] = $2; m = NR; next }
	{ for (i = 1; i <= m; i++) while ((j = index($0, s[i])) > 0) $0 = substr($0, 1, j - 1) r[i] substr($0, j + length(s[i])); print }' "$tmp/map" "$raw" >"$out/$id.log"
	if grep -qF -- "$stem" "$out/$id.log"; then
		rm -f "$out/$id.log"
		die "redaction left a ROM name in the log for $id, nothing saved"
	fi
	parse_controls "$out/$id.log" "$out/$id.presses" "$exempt" "$reads" | sed 's/^/  /' | tee "$tmp/res"
	grep -qx '  result ok' "$tmp/res" || failed="$failed $id"
done <"$tmp/sel"

echo "checked $checked game(s), skipped:${skipped:- none}"
if [ -n "$failed" ]; then
	echo "polled ids no press answered (or no trace data) in:$failed" >&2
	exit 1
fi
[ "$checked" -gt 0 ] || die "no game was checked"
echo "every polled id was answered"
