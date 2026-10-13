#!/bin/sh
# Non-interactive part of the cross-platform performance evaluation (issue 39 / #45).
# For every platform and core pair it can run without a person pressing buttons, runs core_bench on the
# connected device RUNS times per mode, records governor and SoC temperature per run, discards runs that
# start hot, keeps the raw logs under docs/perf/<date>/ and writes a markdown table (median and worst over
# runs per metric, GBA mGBA side by side) to docs/perf/<date>/perf-eval.md.
#
# Modes: normal; serialize (rewind cost); ff (--steps 4, four frames per present, every core);
# ffskip (--steps 4 --frameskip, mgba and gpsp only: core_bench sets only the mgba_ and gpsp_ options).
#
# Idle temperature: the first SoC reading of the session plus MARGIN (default 10 C: the RG34XXSP idles near 54 C with slot on screen after a cool 47 C first reading). Run it on a rested
# device on the charger. A run that would start above that waits COOL seconds and re-checks, up to TRIES
# times, then is discarded (logged in discards.log) and that pair is reported as missing.
# Card carts are found by listing Games/<PLATFORM> on the device (first file with a known extension), or
# set ROM_GBA ROM_GB ROM_GBC ROM_NES ROM_SNES to a device path. No ROM name is ever printed or kept.
#   DATE=YYYY-MM-DD  RUNS=3  TRIES=4  COOL=30  MARGIN=10  SD=/mnt/sdcard  ADB=adb
#   NORMAL_ARGS SER_ARGS FF_ARGS override the core_bench arguments.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

SD="${SD:-/mnt/sdcard}"
ADB="${ADB:-adb}"
DATE="${DATE:-$(date +%Y-%m-%d)}"
RUNS="${RUNS:-3}"
TRIES="${TRIES:-4}"
COOL="${COOL:-30}"
MARGIN="${MARGIN:-10}"
NORMAL_ARGS="${NORMAL_ARGS:---frames 1800 --warmup 300 --repeats 3}"
SER_ARGS="${SER_ARGS:---serialize --frames 300 --warmup 300}"
FF_ARGS="${FF_ARGS:---steps 4 --frames 1800 --warmup 300 --repeats 3}"
out="$root/docs/perf/$DATE"
tab="$(printf '\t')"

die() {
	echo "slot-nes-snes: $*" >&2
	exit 1
}
shq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
dev() { $ADB shell "$1" </dev/null 2>/dev/null | tr -d '\r'; }

[ "$($ADB get-state 2>/dev/null)" = device ] || die "no adb device in state device ($ADB get-state), connect the RG34XXSP"

# Build once, the per-run calls reuse it.
task_bin="$(sh "$root/scripts/fetch-task.sh")"
DEVICE_ROOT=1 sh "$root/scripts/device-sh.sh" "'${task_bin#"$root"/}' -d build/slot bench:device"

# SoC thermal zone: the first zone whose type says cpu or soc, else the first readable one. Read only.
zone="$(dev 'for z in /sys/class/thermal/thermal_zone*; do [ -r "$z/temp" ] && echo "$z $(cat "$z/type" 2>/dev/null)"; done' |
	awk 'tolower($0) ~ /cpu|soc/ { print $1; found = 1; exit } NR == 1 { first = $1 } END { if (!found) print first }')"
[ -n "$zone" ] || die "no readable thermal zone under /sys/class/thermal on the device"
ztype="$(dev "cat '$zone/type'")"
temp() {
	raw="$(dev "cat '$zone/temp'")"
	awk -v r="$raw" 'BEGIN { if (r !~ /^-?[0-9]+$/) exit 1; printf "%.1f\n", (r > 1000 || r < -1000) ? r / 1000 : r }' ||
		die "cannot read $zone/temp"
}
gov() { dev 'cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'; }

idle="$(temp)"
limit="$(awk -v i="$idle" -v m="$MARGIN" 'BEGIN { printf "%.1f\n", i + m }')"
mkdir -p "$out"
rm -f "$out/runs.tsv" "$out/status.tsv" "$out/discards.log"
: >"$out/runs.tsv"
: >"$out/status.tsv"
{
	echo "date $DATE"
	echo "device $(dev 'uname -srm')"
	echo "zone $zone ($ztype)"
	echo "governor $(gov)"
	echo "idle_temp_c $idle (first reading), run limit $limit (idle + $MARGIN)"
	echo "power $(dev 'cat /sys/class/power_supply/*/status' | tr '\n' ' ')"
	echo "slot $tag, VERSION $(cat "$root/VERSION")"
	echo "runs $RUNS, tries $TRIES, cool ${COOL}s"
	echo "normal: $NORMAL_ARGS"
	echo "serialize: $SER_ARGS"
	echo "ff: $FF_ARGS"
} >"$out/meta.txt"
cat "$out/meta.txt"

# Pairs: id platform core source. card:<DIR>:<ext list> or harness:<file>.
pairs="gba-mgba GBA mgba card:GBA:gba
gba-gpsp GBA gpsp card:GBA:gba
gba-mgba-harness GBA mgba harness:240pee_mb.gba
gba-gpsp-harness GBA gpsp harness:240pee_mb.gba
gb-mgba-card GB mgba card:GB:gb
gbc-mgba-card GBC mgba card:GBC:gbc
gb-mgba-harness GB mgba harness:gb240p.gb
gbc-mgba-harness GBC mgba harness:cgb-acid2.gbc
nes-fceumm NES fceumm card:NES:nes
nes-nestopia NES nestopia card:NES:nes
snes-snes9x SNES snes9x card:SNES:sfc.smc
snes-snes9x2005_plus SNES snes9x2005_plus card:SNES:sfc.smc"
printf '%s\n' "$pairs" >"$out/pairs.txt"

# First card file in Games/DIR whose extension is in EXTS (dot separated), or nothing.
find_card() {
	override="$(eval "printf '%s' \"\${ROM_$1:-}\"")"
	if [ -n "$override" ]; then
		printf '%s\n' "$override"
		return 0
	fi
	dev "for f in $(shq "$SD/Games/$1")/*; do [ -f \"\$f\" ] && echo \"\${f##*/}\"; done" | tr -d '\r' | sort | while IFS= read -r f; do
		e="$(printf '%s' "${f##*.}" | tr '[:upper:]' '[:lower:]')"
		case ".$2." in *".$e."*)
			printf '%s\n' "$SD/Games/$1/$f"
			break
			;;
		esac
	done
}

parse() { # log mode: "metric value" lines
	case "$2" in
	serialize)
		sed -nE 's/^ *(run|save|load): median ([0-9.]+) +p95 ([0-9.]+) +max ([0-9.]+) ms.*/\1 \2 \4/p' "$1" |
			awk '{ print $1 "_med", $2; print $1 "_max", $3 }'
		;;
	*)
		sed -nE 's/^median ([0-9.]+) ms\/frame \(min [0-9.]+, max ([0-9.]+), spread.*, ([0-9.]+) frames\/s.*/\1 \2 \3/p' "$1" |
			awk '{ print "ms_med", $1; print "ms_max", $2; print "fps", $3; print "rt", $3 / 60 }'
		;;
	esac
}

# Wait until the SoC is at or under the limit. Returns 1 after TRIES checks.
cool_down() {
	try=1
	while :; do
		t="$(temp)"
		awk -v t="$t" -v l="$limit" 'BEGIN { exit !(t <= l) }' && return 0
		echo "  start temp $t C above limit $limit C (try $try/$TRIES)" | tee -a "$out/discards.log" >&2
		[ "$try" -ge "$TRIES" ] && return 1
		try=$((try + 1))
		sleep "$COOL"
	done
}

# pair mode core romkind rom args -> runs RUNS times, appends kept runs to runs.tsv. Returns 1 if a run is missing.
bench_mode() {
	pair="$1"
	mode="$2"
	core="$3"
	romkind="$4"
	rom="$5"
	args="$6"
	n=1
	while [ "$n" -le "$RUNS" ]; do
		log="$out/$pair.$mode.$n.log"
		cool_down || {
			echo "# discarded: start temperature stayed above $limit C" >"$log"
			return 1
		}
		t0="$(temp)"
		{
			echo "# pair $pair core $core mode $mode run $n"
			echo "# governor $(gov)"
			echo "# temp_start_c $t0 (limit $limit)"
		} >"$log"
		rc=0
		if [ "$romkind" = card ]; then
			env "ROM_ON_DEVICE=$rom" "ROM=" "CORE=$core" "SD=$SD" "ARGS=$args" "ADB=$ADB" BENCH_NO_BUILD=1 \
				sh "$root/scripts/bench-device.sh" </dev/null >>"$log" 2>&1 || rc=$?
		else
			env "ROM=$rom" "ROM_ON_DEVICE=" "CORE=$core" "SD=$SD" "ARGS=$args" "ADB=$ADB" BENCH_NO_BUILD=1 \
				sh "$root/scripts/bench-device.sh" </dev/null >>"$log" 2>&1 || rc=$?
		fi
		{
			echo "# temp_end_c $(temp)"
			echo "# exit $rc"
		} >>"$log"
		[ "$rc" -eq 0 ] || return 1
		parse "$log" "$mode" >"$log.parsed"
		[ -s "$log.parsed" ] || return 1
		while read -r m v; do
			printf '%s\t%s\t%s\t%s\t%s\n' "$pair" "$mode" "$n" "$m" "$v" >>"$out/runs.tsv"
		done <"$log.parsed"
		rm -f "$log.parsed"
		n=$((n + 1))
	done
}

printf '%s\n' "$pairs" | while read -r pair plat core src; do
	echo "== $pair ($plat $core)"
	kind="${src%%:*}"
	rest="${src#*:}"
	if [ "$kind" = card ]; then
		rom="$(find_card "${rest%%:*}" "${rest#*:}")"
		if [ -z "$rom" ]; then
			printf '%s\tno workload (no %s cart on the card)\n' "$pair" "$plat" >>"$out/status.tsv"
			echo "  no workload"
			continue
		fi
	else
		kind=harness
		rom="$root/harness/roms/$rest"
		[ -f "$rom" ] || {
			printf '%s\tmissing (harness cart %s absent)\n' "$pair" "$rest" >>"$out/status.tsv"
			continue
		}
	fi
	[ "$kind" = card ] || kind=local
	why=""
	modes="normal serialize ff"
	case "$core" in mgba | gpsp) modes="$modes ffskip" ;; esac
	for mode in $modes; do
		case "$mode" in
		normal) a="$NORMAL_ARGS" ;;
		serialize) a="$SER_ARGS" ;;
		ff) a="$FF_ARGS" ;;
		ffskip) a="$FF_ARGS --frameskip" ;;
		esac
		echo "  $mode"
		bench_mode "$pair" "$mode" "$core" "$kind" "$rom" "$a" || why="$why $mode"
	done
	if [ -n "$why" ]; then
		printf '%s\tmissing (runs failed or discarded:%s)\n' "$pair" "$why" >>"$out/status.tsv"
	else
		printf '%s\tok\n' "$pair" >>"$out/status.tsv"
	fi
done

# Tables. runs.tsv rows: pair mode run metric value. Worst is the max for times and the min for rates.
metrics="$out/metrics.tsv"
{
	printf '%s\t' normal ms_med 1 "Frame cost, median over repeats (ms per frame, lower is better)"; echo
	printf '%s\t' normal ms_max 1 "Frame cost, worst repeat (ms per frame, lower is better)"; echo
	printf '%s\t' normal rt 0 "Speed headroom in normal play (x real time, higher is better)"; echo
	printf '%s\t' ff ms_med 1 "Fast-forward, 4 frames per present, no frameskip (ms per emulated frame, lower is better)"; echo
	printf '%s\t' ff rt 0 "Fast-forward speed reached, no frameskip (x real time, higher is better)"; echo
	printf '%s\t' ffskip rt 0 "Fast-forward speed reached, frameskip on, mgba and gpsp only (x real time, higher is better)"; echo
	printf '%s\t' serialize run_med 1 "Rewind: frame cost while serializing every frame, median (ms)"; echo
	printf '%s\t' serialize save_med 1 "Rewind: serialize per frame, median (ms)"; echo
	printf '%s\t' serialize save_max 1 "Rewind: serialize per frame, worst (ms)"; echo
	printf '%s\t' serialize load_med 1 "Rewind: unserialize per frame, median (ms)"; echo
	printf '%s\t' serialize load_max 1 "Rewind: unserialize per frame, worst (ms)"; echo
} | sed 's/\t$//' >"$metrics"

awk -F'\t' -v meta="$out/meta.txt" -v base="gba-mgba" '
function med(k,   n, i, j, t, a) {
	n = c[k]
	for (i = 1; i <= n; i++) a[i] = v[k, i] + 0
	for (i = 2; i <= n; i++) { t = a[i]; for (j = i - 1; j >= 1 && a[j] > t; j--) a[j + 1] = a[j]; a[j + 1] = t }
	return (n % 2) ? a[(n + 1) / 2] : (a[n / 2] + a[n / 2 + 1]) / 2
}
function worst(k, hi,   n, i, w) {
	n = c[k]; w = v[k, 1] + 0
	for (i = 2; i <= n; i++) if (hi ? v[k, i] + 0 > w : v[k, i] + 0 < w) w = v[k, i] + 0
	return w
}
FILENAME ~ /pairs.txt$/ { split($0, f, " "); np++; pid[np] = f[1]; plat[f[1]] = f[2]; core[f[1]] = f[3]; next }
FILENAME ~ /status.tsv$/ { st[$1] = $2; next }
FILENAME ~ /metrics.tsv$/ { nm++; mo[nm] = $1; me[nm] = $2; hi[nm] = $3; ti[nm] = $4; next }
{ k = $1 SUBSEP $2 SUBSEP $4; c[k]++; v[k, c[k]] = $5 }
END {
	print "# Performance evaluation, raw core_bench on the device\n"
	while ((getline line < meta) > 0) print "    " line
	print "\nEach cell is median and worst over runs. The last column is the median against " base " (GBA mGBA, card cart) in the same session. Frame cost is the core plus slot copy and audio callbacks, not the GL upload."
	for (m = 1; m <= nm; m++) {
		print "\n## " ti[m] "\n"
		print "| Pair | Platform | Core | Median | Worst | vs " base " |"
		print "|---|---|---|---|---|---|"
		bk = base SUBSEP mo[m] SUBSEP me[m]
		for (p = 1; p <= np; p++) {
			id = pid[p]; k = id SUBSEP mo[m] SUBSEP me[m]
			if (mo[m] == "ffskip" && core[id] != "mgba" && core[id] != "gpsp") continue
			if (st[id] != "ok" && !(k in c)) { print "| " id " | " plat[id] " | " core[id] " | " st[id] " | | |"; continue }
			if (!(k in c)) { print "| " id " | " plat[id] " | " core[id] " | " (st[id] == "ok" ? "n/a" : "missing") " | | |"; continue }
			md = med(k); wr = worst(k, hi[m])
			d = ((bk in c) && med(bk) != 0) ? sprintf("%+.1f%%", (md - med(bk)) / med(bk) * 100) : "n/a"
			printf "| %s | %s | %s | %.3f | %.3f | %s |\n", id, plat[id], core[id], md, wr, d
		}
	}
	print "\n## Pair status\n"
	print "| Pair | Status |\n|---|---|"
	for (p = 1; p <= np; p++) print "| " pid[p] " | " st[pid[p]] " |"
}' "$out/pairs.txt" "$out/status.tsv" "$metrics" "$out/runs.tsv" >"$out/perf-eval.md"
rm -f "$metrics"
echo "wrote $out/perf-eval.md"
if grep -q "${tab}missing" "$out/status.tsv"; then
	echo "slot-nes-snes: some pairs are missing runs, see $out/status.tsv and discards.log" >&2
	exit 1
fi
