#!/bin/sh
# Automated device play for the interactive part of the performance evaluation (issue 39 / #45).
# Per pair and run: point slot at a cart through Config/slot.state, pick the core, turn on SLOT_TRACE and the
# latency trace, restart slot so it boots into the cart, inject the same scripted input for MINUTES, eject
# through the menu so the session summary is written, pull slot.log with every ROM name redacted, then parse
# it. Everything it touches on the device is backed up first and put back on exit, even on failure.
#
#   task perf:play                                   all default pairs (see the table below)
#   task perf:play CORE=snes9x2005_plus              only the pairs on that core
#   task perf:play PLATFORM=nes                      only that platform
#   task perf:play CORE=mgba PLATFORM=gba STEM='<name on the card>' MINUTES=1 RUNS=1    one custom pair
#   sh scripts/auto-play.sh selftest                 local checks, no device
#   sh scripts/auto-play.sh eval [YYYY-MM-DD]        rebuild play-eval.md from saved logs, no device
# Env: CORE PLATFORM(gba|gb|gbc|nes|snes|gg|sms|md) STEM (card file name, extension optional) PAIR (id for a custom pair)
#   MINUTES=10 RUNS=3 SD=/mnt/sdcard ADB=adb DATE=<today> NODE_KEYS=/dev/input/eventN NODE_HAT=/dev/input/eventN
#
# How the input gets in: slot reads every /dev/input/event* node that has buttons (no EVIOCGRAB). Writing a
# struct input_event to such a node injects it (the kernel drops codes the node does not support), so the
# script finds, from /sys/class/input/eventN/device/capabilities, the node that supports each code and
# writes there. Event files are built here with printf and pushed; the device only needs cat and sleep.
# Eject gesture: hold MENU for 1.5 s (slot ejects at 1.0 s, a tap opens the quick menu instead).
# SLOT_TRACE has to be in slot's environment and BaseOS starts slot, so the script puts one export line after
# "export SLOT_ROOT" in System/launch_frontend.sh for the run and puts the original file back afterwards.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
SD="${SD:-/mnt/sdcard}"
ADB="${ADB:-adb}"
DATE="${DATE:-$(date +%Y-%m-%d)}"
MINUTES="${MINUTES:-10}"
RUNS="${RUNS:-3}"
CORE="${CORE:-}"
PLATFORM="${PLATFORM:-}"
STEM="${STEM:-}"
PAIR="${PAIR:-}"
NODE_KEYS="${NODE_KEYS:-}"
NODE_HAT="${NODE_HAT:-}"
tab="$(printf '\t')"
mt="${TMPDIR:-/tmp}"

die() {
	echo "slot-nes-snes: $*" >&2
	exit 1
}
shq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
dev() { $ADB shell "$1" </dev/null 2>/dev/null | tr -d '\r'; }
dx() { $ADB shell "$1" </dev/null >/dev/null 2>&1; }

# Default pairs: id|platform|core|stem. Stems exactly as on the card. These are game titles, they never reach
# a saved log (redacted to the id) and no ROM is ever copied off the card.
pairs="snes-snes9x-heavy|snes|snes9x|Super Mario World 2 - Yoshi's Island (USA)
snes-snes9x-light|snes|snes9x|Super Mario World (USA)
snes-snes9x2005_plus-heavy|snes|snes9x2005_plus|Super Mario World 2 - Yoshi's Island (USA)
snes-snes9x2005_plus-light|snes|snes9x2005_plus|Super Mario World (USA)
nes-fceumm-heavy|nes|fceumm|Kirby's Adventure (USA)
nes-fceumm-light|nes|fceumm|Super Mario Bros. (World)
nes-nestopia-heavy|nes|nestopia|Kirby's Adventure (USA)
nes-nestopia-light|nes|nestopia|Super Mario Bros. (World)
gba-mgba-heavy|gba|mgba|Golden Sun (UE) [!]
gba-mgba-light|gba|mgba|Legend of Zelda, The - The Minish Cap (U)
gba-gpsp-heavy|gba|gpsp|Golden Sun (UE) [!]
gba-gpsp-light|gba|gpsp|Legend of Zelda, The - The Minish Cap (U)
gbc-mgba-card|gbc|mgba|Legend of Zelda, The - Link's Awakening DX (U) (V1.2) [C][!]
md-genesis_plus_gx-heavy|md|genesis_plus_gx|Virtua Racing (USA)
md-genesis_plus_gx-light|md|genesis_plus_gx|Sonic The Hedgehog (USA, Europe)
sms-genesis_plus_gx-light|sms|genesis_plus_gx|Alex Kidd in Miracle World (USA, Europe, Brazil) (Rev 1)
gg-genesis_plus_gx-light|gg|genesis_plus_gx|Sonic Chaos (USA, Europe)"

# One struct input_event as a printf format string: aarch64, 16 bytes of zero timeval, u16 type, u16 code,
# i32 value, little endian, 24 bytes. ev TYPE CODE VALUE
ev() {
	v=$(($3 & 4294967295))
	printf '\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000'
	printf '\\%03o\\%03o\\%03o\\%03o' $(($1 & 255)) $(($1 >> 8 & 255)) $(($2 & 255)) $(($2 >> 8 & 255))
	printf '\\%03o\\%03o\\%03o\\%03o' $((v & 255)) $((v >> 8 & 255)) $((v >> 16 & 255)) $((v >> 24 & 255))
}
# key press or release followed by SYN_REPORT, as one 48 byte write
key() { ev 1 "$1" "$2"; ev 0 0 0; }
hat() { ev 3 16 "$1"; ev 0 0 0; } # ABS_HAT0X: 1 right, 0 centred

# Metrics of one saved log: "name value" lines, only for what the log holds.
parse_log() {
	awk '
	function num(s) { sub(/,$/, "", s); return s + 0 }
	function sorted(a, n,   i, j, t) { for (i = 2; i <= n; i++) { t = a[i]; for (j = i - 1; j >= 1 && a[j] > t; j--) a[j + 1] = a[j]; a[j + 1] = t } }
	function pick(a, n, q,   i) { i = int(n * q); if (i < n * q) i++; if (i < 1) i = 1; return a[i] }
	/^slot: boot: first frame at / { if (bf == "") bf = $(NF - 1) }
	/^slot: launch: opening / { if (op == "") op = $(NF - 1) }
	/^slot: launch: first frame shown at / { if (ff == "") ff = $(NF - 1) }
	/^slot: audio: [0-9]+ samples dropped/ { sd = num($3); ss = num($6); sum = 1 }
	/^slot: audio: [0-9]+\/[0-9]+ queued/ { d = num($5); s = num($7); if (d > td) td = d; if (s > ts) ts = s; tc++ }
	/^slot: Volume(Up|Down) / { vol = 1 }
	/^slot: latency: .* total [0-9.]+ ms/ { if (vol) vol = 0; else lat[++nl] = $(NF - 1) + 0 }
	/^slot: pace: 600 frames/ { np++; pmv[np] = num($5); pev[np] = num($9); wv[np] = num($13); pv[np] = num($16) }
	/^slot: frametime: 600 presents/ { nf++; f50[nf] = $6 + 0; f99[nf] = $8 + 0; fmx[nf] = $10 + 0 }
	/^slot: crash:/ { crash++ }
	END {
		if (bf != "") print "boot_ms", bf
		if (op != "" && ff != "") print "insert_ms", ff - op
		print "summary", sum + 0
		if (sum) { print "starved", ss; print "dropped", sd }
		if (tc) { print "trace_starved_max", ts + 0; print "trace_dropped_max", td + 0 }
		if (nl) { sorted(lat, nl); print "lat_med", lat[int((nl + 1) / 2)]; print "lat_p99", pick(lat, nl, 0.99); print "lat_max", lat[nl]; print "lat_n", nl }
		np--; nf--
		for (i = 1; i <= np; i++) { pm += pmv[i]; pe += pev[i]; w[i] = wv[i]; p[i] = pv[i] }
		if (np > 0) { sorted(w, np); sorted(p, np); print "pace_missed", pm; print "pace_early", pe; print "pace_work_med", w[int((np + 1) / 2)]; print "pace_work_max", w[np]; print "pace_period_med", p[int((np + 1) / 2)] }
		if (nf > 0) { sorted(f50, nf); mx = fmx[1]; w99 = f99[1]; for (i = 2; i <= nf; i++) { if (fmx[i] > mx) mx = fmx[i]; if (f99[i] > w99) w99 = f99[i] } print "ft_p50_med", f50[int((nf + 1) / 2)]; print "ft_p99_worst", w99; print "ft_max", mx }
		print "crash", crash + 0
	}' "$1"
}

# play-eval.md from the saved logs in $1 (docs/perf/<date>/play). Rows: pair run metric value.
eval_play() {
	rows="$(mktemp "$mt/ap.XXXXXX")"
	md="${1%/play}/play-eval.md"
	for f in "$1"/*.log; do
		[ -f "$f" ] || continue
		b="${f##*/}"
		b="${b%.log}"
		parse_log "$f" | while read -r m v; do printf '%s\t%s\t%s\t%s\n' "${b%.*}" "${b##*.}" "$m" "$v"; done
	done >"$rows"
	[ -s "$rows" ] || {
		rm -f "$rows"
		die "no parsable logs in $1"
	}
	awk -F'\t' -v meta="$1/meta.txt" '
	function med(k,   n, i, j, t, a) {
		n = c[k]; for (i = 1; i <= n; i++) a[i] = v[k, i] + 0
		for (i = 2; i <= n; i++) { t = a[i]; for (j = i - 1; j >= 1 && a[j] > t; j--) a[j + 1] = a[j]; a[j + 1] = t }
		return (n % 2) ? a[(n + 1) / 2] : (a[n / 2] + a[n / 2 + 1]) / 2
	}
	function worst(k,   n, i, w) { n = c[k]; w = v[k, 1] + 0; for (i = 2; i <= n; i++) if (v[k, i] + 0 > w) w = v[k, i] + 0; return w }
	function cell(k) { return (k in c) ? sprintf("%.3g / %.3g", med(k), worst(k)) : "n/a" }
	{ if (!($1 in seen)) { seen[$1] = 1; ids[++ni] = $1 } k = $1 SUBSEP $3; c[k]++; v[k, c[k]] = $4 }
	END {
		# order: the two GBA mGBA baselines first, then the rest by name
		o[++no] = "gba-mgba-heavy"; o[++no] = "gba-mgba-light"
		for (i = 1; i <= ni; i++) if (ids[i] != o[1] && ids[i] != o[2]) rest[++nr] = ids[i]
		for (i = 2; i <= nr; i++) { x = rest[i]; for (j = i - 1; j >= 1 && rest[j] > x; j--) rest[j + 1] = rest[j]; rest[j + 1] = x }
		for (i = 1; i <= nr; i++) o[++no] = rest[i]
		nm = split("boot_ms insert_ms starved dropped trace_starved_max trace_dropped_max lat_med lat_p99 lat_max pace_missed pace_early pace_work_med pace_work_max pace_period_med ft_p50_med ft_p99_worst ft_max crash", mm, " ")
		split("Boot to first frame (ms)|Insert or resume to first game frame (ms)|Audio starved samples, session total|Audio dropped samples, session total|Audio starved, trace maximum (per 300 frames, cumulative)|Audio dropped, trace maximum|Input latency median (ms)|Input latency p99 (ms)|Input latency max (ms)|Presents that missed a latch (total over the session)|Presents drawn early (total)|Work per frame, median over 600 frame windows (ms)|Work per frame, worst 600 frame window (ms)|Present period, median (ms)|Present interval p50, median over windows (ms)|Present interval p99, worst window (ms)|Present interval, longest (ms)|Crash lines", ti, "|")
		print "# Performance evaluation, automated play on the device\n"
		while ((getline line < meta) > 0) print "    " line
		print "\nEach cell is median / worst over runs. Every run plays the same script on every core: START x3, then right held with A every 700 ms and B every 2.3 s, then eject. Latency is input to screen swap. Slot logs no per-frame wall time: the pace lines (work per frame, missed latches) are the nearest frame-time figure, and only exist with the latency trace on. Starved and dropped count samples, not events. A run without a session summary line did not end cleanly.\n"
		print "## GBA mGBA baseline, heavy and light side by side\n"
		print "| Metric | gba-mgba-heavy | gba-mgba-light |\n|---|---|---|"
		for (i = 1; i <= nm; i++) print "| " ti[i] " | " cell(o[1] SUBSEP mm[i]) " | " cell(o[2] SUBSEP mm[i]) " |"
		for (i = 1; i <= nm; i++) {
			print "\n## " ti[i] "\n"
			print "| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |\n|---|---|---|---|---|"
			for (p = 1; p <= no; p++) {
				id = o[p]; k = id SUBSEP mm[i]
				if (!(k in c)) { if ((id SUBSEP "summary") in c) print "| " id " | " (c[id SUBSEP "summary"] + 0) " | n/a | | |"; continue }
				b = (id ~ /-light$/) ? o[2] : o[1]; bk = b SUBSEP mm[i]
				d = (id != o[1] && id != o[2] && (bk in c) && med(bk) != 0) ? sprintf("%+.1f%%", (med(k) - med(bk)) / med(bk) * 100) : "n/a"
				printf "| %s | %d | %.3f | %.3f | %s |\n", id, c[k], med(k), worst(k), d
			}
		}
		print "\n## Sessions that ended cleanly (summary line present)\n"
		print "| Pair | Runs | Clean |\n|---|---|---|"
		for (p = 1; p <= no; p++) {
			id = o[p]; k = id SUBSEP "summary"; if (!(k in c)) continue
			cl = 0; for (r = 1; r <= c[k]; r++) cl += v[k, r]
			print "| " id " | " c[k] " | " cl " |"
		}
	}' "$rows" >"$md"
	rm -f "$rows"
	echo "wrote $md"
}

selftest() {
	z16="$(printf '%032d' 0)"
	got="$(printf "$(key 304 1)" | od -An -tx1 | tr -d ' \n')"
	want="${z16}0100300101000000$(printf '%048d' 0)"
	[ "$got" = "$want" ] || die "selftest: key 304 down is $got, want $want"
	[ "$(printf "$(key 304 1)" | wc -c | tr -d ' ')" = 48 ] || die "selftest: key frame is not 48 bytes"
	got="$(printf "$(ev 3 16 -1)" | od -An -tx1 | tr -d ' \n')"
	want="${z16}03001000ffffffff"
	[ "$got" = "$want" ] || die "selftest: hat -1 is $got, want $want"
	f="$mt/ap.$$"
	printf '%s\n' 'slot: boot: first frame at 900.0 ms' 'slot: launch: opening X on mgba at 1000.0 ms' \
		'slot: launch: first frame shown at 1600.5 ms' 'slot: audio: 5/10 queued, 0 dropped, 12 starved, locked true at 1.0' \
		'slot: audio: 3 samples dropped, 40 starved' 'slot: latency: read>pad 1 total 20.0 ms' 'slot: latency: read>pad 1 total 30.0 ms' \
		'slot: pace: 600 frames, 2 missed a latch, 1 drawn early, work 9.5 ms, period 16.70 ms' \
		'slot: frametime: 600 presents, p50 16.78 p99 17.10 max 20.00 ms' 'slot: VolumeUp in Playing' 'slot: latency: read>pad 400 total 405.0 ms' \
		'slot: pace: 600 frames, 7 missed a latch, 0 drawn early, work 99.0 ms, period 99.00 ms' 'slot: frametime: 600 presents, p50 50.00 p99 60.00 max 70.00 ms' >"$f"
	got="$(parse_log "$f" | tr '\n' ';')"
	rm -f "$f"
	want="boot_ms 900.0;insert_ms 600.5;summary 1;starved 40;dropped 3;trace_starved_max 12;trace_dropped_max 0;lat_med 20;lat_p99 30;lat_max 30;lat_n 2;pace_missed 2;pace_early 1;pace_work_med 9.5;pace_work_max 9.5;pace_period_med 16.7;ft_p50_med 16.78;ft_p99_worst 17.1;ft_max 20;crash 0;"
	[ "$got" = "$want" ] || die "selftest: parse_log gave $got"
	echo "selftest ok"
}

case "${1:-}" in
selftest)
	selftest
	exit 0
	;;
eval)
	eval_play "$root/docs/perf/${2:-$DATE}/play"
	exit 0
	;;
esac

# ---------------------------------------------------------------- device run

case "$MINUTES$RUNS" in *[!0-9]* | "") die "MINUTES and RUNS must be whole numbers" ;; esac
[ "$($ADB get-state 2>/dev/null)" = device ] || die "no adb device in state device ($ADB get-state), connect the RG34XXSP"

# Choose the pairs.
if [ -n "$STEM" ]; then
	[ -n "$CORE" ] && [ -n "$PLATFORM" ] || die "a custom STEM needs CORE and PLATFORM"
	case "$STEM" in
	*.[gG][bB][aA] | *.[gG][bB][cC] | *.[nN][eE][sS] | *.[sS][fF][cC] | *.[sS][mM][cC] | *.[zZ][iI][pP] | *.[gG][gG] | *.[sS][mM][sS] | *.[mM][dD] | *.[gG][eE][nN] | *.[bB][iI][nN]) STEM="${STEM%.*}" ;;
	esac
	pl="$(printf '%s' "$PLATFORM" | tr '[:upper:]' '[:lower:]')"
	sel="${PAIR:-$pl-$CORE-custom}|$pl|$CORE|$STEM"
else
	sel="$(printf '%s\n' "$pairs" | awk -F'|' -v c="$CORE" -v p="$(printf '%s' "$PLATFORM" | tr '[:upper:]' '[:lower:]')" '(c == "" || $3 == c) && (p == "" || $2 == p)')"
	[ -n "$sel" ] || die "no default pair matches CORE='$CORE' PLATFORM='$PLATFORM'"
fi

out="$root/docs/perf/$DATE/play"
tmp="$(mktemp -d "$mt/ap.XXXXXX")"
printf '%s\n' "$sel" >"$tmp/sel"
: >"$tmp/backed"
bk="$SD/play-backup-$(date +%Y%m%d-%H%M%S)"
cfg="$SD/Config"
tf="$SD/System/launch_frontend.sh"
flag="$SD/System/trace-latency.on"
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

# Per cart saves and the resume state: copied on first use, put back before every run (so every run starts the
# same) and on exit (so the maintainer's saves are never changed by a perf run). Args: PLATDIR core stem.
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
[ -f had-latency-flag ] || rm -f $(shq "$flag")
true" || echo "slot-nes-snes: RESTORE FAILED, copy the files in $bk back by hand" >&2
		dx "sh $(shq "$bk/inj/slotctl.sh") stop"
		# Only the keys this script wrote go back to the backup's values; the rest (volume, brightness...)
		# stays as the player left it during the runs.
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
nA="${NODE_KEYS:-$(node_for key 304)}"
nB="${NODE_KEYS:-$(node_for key 305)}"
nS="${NODE_KEYS:-$(node_for key 311)}"
nM="${NODE_KEYS:-$(node_for key 312)}"
nH="${NODE_HAT:-$(node_for abs 16)}"
for v in "$nA" "$nB" "$nS" "$nM" "$nH"; do
	[ -n "$v" ] || die "no input node on the device reports one of A, B, START, MENU or ABS_HAT0X (capabilities: $caps). Set NODE_KEYS and NODE_HAT"
done

mkdir -p "$tmp/inj" "$out"

# Event files and helper scripts, built here and pushed.
mk() { printf "$2" >"$tmp/inj/$1"; }
mk a.dn "$(key 304 1)"
mk a.up "$(key 304 0)"
mk b.dn "$(key 305 1)"
mk b.up "$(key 305 0)"
mk start.dn "$(key 311 1)"
mk start.up "$(key 311 0)"
mk menu.dn "$(key 312 1)"
mk menu.up "$(key 312 0)"
mk right.dn "$(hat 1)"
mk right.up "$(hat 0)"
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
# Device play script: START x3 two seconds apart, hold RIGHT, A every 700 ms, B every 2.3 s for MINUTES, then
# hold MENU to eject. Times come from /proc/uptime (centiseconds) so tap costs do not drift the schedule.
cat >"$tmp/inj/play.sh" <<EOF
#!/bin/sh
d='$bk/inj'
NA='$nA'; NB='$nB'; NS='$nS'; NM='$nM'; NH='$nH'
END_CS=$((MINUTES * 6000))
EOF
cat >>"$tmp/inj/play.sh" <<'EOF'
now() { read -r u _ </proc/uptime; echo "${u%.*}${u#*.}"; }
tap() { cat "$d/$1.dn" >"$2"; sleep 0.05; cat "$d/$1.up" >"$2"; }
tap start "$NS"; sleep 2; tap start "$NS"; sleep 2; tap start "$NS"; sleep 2
cat "$d/right.dn" >"$NH"
t0=$(now); end=$((t0 + END_CS)); na=$t0; nb=$t0
while [ "$(now)" -lt "$end" ]; do
	n=$(now)
	[ "$n" -ge "$na" ] && { tap a "$NA"; na=$((na + 70)); }
	[ "$n" -ge "$nb" ] && { tap b "$NB"; nb=$((nb + 230)); }
	sleep 0.02
done
cat "$d/right.up" >"$NH"
sleep 0.5
cat "$d/menu.dn" >"$NM"; sleep 1.5; cat "$d/menu.up" >"$NM"
EOF

# Everything below changes the device. Backup first, nothing is touched if it fails.
dx "mkdir -p $(shq "$bk/inj")" || die "cannot create $bk"
dx "cd $(shq "$bk") && cp -p $(shq "$cfg/slot.state") slot.state && { [ -f $(shq "$cfg/selected_core.txt") ] && cp -p $(shq "$cfg/selected_core.txt") selected_core.txt; true; } && cp -p $(shq "$tf") launch_frontend.sh && { [ -f $(shq "$flag") ] && touch had-latency-flag; true; } && { cp -p $(shq "$SD/Logs/slot.log") slot.log.bak 2>/dev/null; cp -p $(shq "$SD/Logs/slot.log.1") slot.log.1.bak 2>/dev/null; true; }" ||
	die "the backup failed, nothing was changed"
for f in "$tmp"/inj/*; do $ADB push "$f" "$bk/inj/" </dev/null >/dev/null || die "adb push of ${f##*/} failed"; done
armed=1

# Redaction list: every ROM name on the card (6 characters or more).
dev "for f in $(shq "$SD/Games")/*/*; do [ -f \"\$f\" ] && echo \"\${f##*/}\"; done" | sed 's/\.[A-Za-z0-9]\{1,5\}$//' | awk 'length($0) >= 6' >"$tmp/stems"

{
	echo "date $DATE"
	echo "device $(dev 'uname -srm')"
	echo "governor $(dev 'cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor')"
	echo "power $(dev 'cat /sys/class/power_supply/*/status' | tr '\n' ' ')"
	echo "input nodes: A $nA, B $nB, START $nS, MENU $nM, hat $nH"
	echo "play $MINUTES minutes per run, $RUNS runs per pair"
} >"$out/meta.txt"
cat "$out/meta.txt"

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

# Originals as pulled once, edited fresh for every run.
$ADB pull "$cfg/selected_core.txt" "$tmp/sel.orig" </dev/null >/dev/null 2>&1 || : >"$tmp/sel.orig"
$ADB pull "$tf" "$tmp/launch.orig" </dev/null >/dev/null || die "cannot read launch_frontend.sh"
if grep -q 'SLOT_TRACE=' "$tmp/launch.orig"; then
	cp "$tmp/launch.orig" "$tmp/launch.new"
else
	awk '{ print } /^export SLOT_ROOT/ { print "export SLOT_TRACE=1" }' "$tmp/launch.orig" >"$tmp/launch.new"
fi

set_config() { # stem platform core
	# The live state, so a volume or brightness change the player made during the last run carries over.
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

while IFS='|' read -r id pl core stem; do
	pd="$(printf '%s' "$pl" | tr '[:lower:]' '[:upper:]')"
	echo "== $id ($pl $core)"
	dx "test -f $(shq "$SD/System/${core}_libretro.so")" || {
		echo "  skipped: no $core core in System/" >&2
		continue
	}
	dx "for f in $(shq "$SD/Games/$pd/$stem").*; do [ -f \"\$f\" ] && exit 0; done; exit 1" || {
		echo "  skipped: that cart is not on the card under Games/$pd (name not printed)" >&2
		continue
	}
	backup_cart "$pd" "$core" "$stem"
	n=1
	while [ "$n" -le "$RUNS" ]; do
		echo "  run $n"
		restore_one "$pd" "$core" "$stem"
		set_config "$stem" "$pl" "$core"
		$ADB push "$tmp/launch.new" "$tf" </dev/null >/dev/null || die "cannot write launch_frontend.sh"
		dx "chmod 755 $(shq "$tf"); touch $(shq "$flag"); rm -f $(shq "$SD/Logs/slot.log"); touch $(shq "$bk/mark")"
		restart_slot || die "slot did not start"
		if seen "launch: first frame shown" 120; then
			sleep 2
			dx "sh $(shq "$bk/inj/play.sh")" || echo "  the input script failed" >&2
			seen "samples dropped" 40 || echo "  no session summary line, the eject did not take" >&2
		else
			echo "  no first game frame within 120 s, logging what exists" >&2
		fi
		raw="$tmp/slot.raw"
		$ADB pull "$SD/Logs/slot.log" "$raw" </dev/null >/dev/null 2>&1 || : >"$raw"
		# slot.log.1 only counts if this run's launches rotated it (a second start inside one run)
		if dx "test $(shq "$SD/Logs/slot.log.1") -nt $(shq "$bk/mark")"; then
			$ADB pull "$SD/Logs/slot.log.1" "$tmp/slot.raw1" </dev/null >/dev/null 2>&1 && cat "$tmp/slot.raw1" "$raw" >"$tmp/slot.raw2" && mv "$tmp/slot.raw2" "$raw"
		fi
		# keep only the last slot session: a restart can rotate an older session into slot.log.1 just
		# after the mark, and its lines would otherwise be parsed as this run's (seen 2026-10-13)
		last="$(grep -n 'slot: boot: start at' "$raw" | tail -n 1 | cut -d: -f1)"
		if [ -n "$last" ]; then tail -n "+$last" "$raw" >"$raw.last" && mv "$raw.last" "$raw"; fi
		# longest names first, so a short title inside a long one cannot leave half a name behind
		{
			printf '%s\t%s\n' "$stem" "$id"
			awk -v s="$stem" -v t="$tab" '$0 != s { print $0 t "other-rom" }' "$tmp/stems"
		} | awk -F'\t' '{ print length($1) "\t" $0 }' | sort -t "$tab" -k1,1nr | cut -f2- >"$tmp/map"
		awk -F'\t' 'NR == FNR { s[NR] = $1; r[NR] = $2; m = NR; next }
		{ for (i = 1; i <= m; i++) while ((j = index($0, s[i])) > 0) $0 = substr($0, 1, j - 1) r[i] substr($0, j + length(s[i])); print }' "$tmp/map" "$raw" >"$out/$id.$n.log"
		if grep -qF -- "$stem" "$out/$id.$n.log"; then
			rm -f "$out/$id.$n.log"
			die "redaction left a ROM name in the log for $id, nothing saved"
		fi
		parse_log "$out/$id.$n.log" | tr '\n' ' '
		echo
		n=$((n + 1))
	done
done <"$tmp/sel"
eval_play "$out"
