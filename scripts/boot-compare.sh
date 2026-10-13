#!/bin/sh
# Boot-time comparison on a connected device over adb: run one or more slot binaries against the card's
# real SLOT_ROOT, one after the other and interleaved, and print the boot marks that matter.
#
#   sh scripts/boot-compare.sh ours=build/dist/<release>/System/slot upstream=build/slot-upstream/target-device/device/slot
#   sh scripts/boot-compare.sh ours=<path>                      only ours
#   sh scripts/boot-compare.sh selftest                         local checks, no device
# Env: SD=/mnt/sdcard ADB=adb RUNS=3 WAIT=60 COLD=1 (drop the page cache before every run, needs root)
#
# Each binary is pushed to $SD/boottest/slot-<label>, run the way launch_frontend.sh runs slot (ld.so,
# SLOT_ROOT=$SD) with its output in $SD/boottest/<label>.<run>.log, killed once "boot: ui faces" shows up,
# and its boot lines are pulled. The normal slot is stopped first and brought back at the end, on every
# exit. Config/slot.state and slot.log(.1) are backed up and put back (a binary that does not know NES or
# SNES may rewrite the state). Nothing is written to slot.log and no ROM name is printed (boot lines hold none).
# The upstream binary shows the cost of GB/GBC/GBA alone (it ignores Games/NES and Games/SNES), ours adds
# the NES/SNES carts. Build upstream for the device without touching ours:
#   DEVICE_ROOT=1 sh scripts/device-sh.sh 'cargo build --profile device --target-dir build/slot-upstream/target-device --manifest-path build/slot-upstream/Cargo.toml -p slot --no-default-features --features device && file build/slot-upstream/target-device/device/slot'
set -eu

SD="${SD:-/mnt/sdcard}"
ADB="${ADB:-adb}"
RUNS="${RUNS:-3}"
WAIT="${WAIT:-60}"
COLD="${COLD:-1}"
tab="$(printf '\t')"
mt="${TMPDIR:-/tmp}"

die() {
	echo "slot-nes-snes: $*" >&2
	exit 1
}
shq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
dev() { $ADB shell "$1" </dev/null 2>/dev/null | tr -d '\r'; }
dx() { $ADB shell "$1" </dev/null >/dev/null 2>&1; }

# Marks of one log as "name<TAB>ms" lines, in the order they were printed.
marks() { sed -n "s/^slot: boot: \(.*\) at \([0-9.]*\) ms\$/\1${tab}\2/p" "$1"; }

# Each mark with its time and the step since the one before.
table() {
	marks "$1" | awk -F'\t' '{ printf "  %-16s %8.1f  (+%.1f)\n", $1, $2, $2 - prev; prev = $2 }'
}

# The time of one mark, or nothing.
at() { marks "$1" | awk -F'\t' -v k="$2" '$1 == k { print $2; exit }'; }

if [ "${1:-}" = selftest ]; then
	t="$(mktemp "$mt/bc.XXXXXX")"
	printf 'slot: boot: start at 0.0 ms\nslot: boot: scan at 1589.0 ms\nnoise\nslot: boot: session at 4672.4 ms\nslot: boot: ui faces at 4901.0 ms\n' >"$t"
	[ "$(at "$t" session)" = 4672.4 ] || die "selftest: session"
	[ "$(at "$t" 'ui faces')" = 4901.0 ] || die "selftest: ui faces"
	[ -z "$(at "$t" nothing)" ] || die "selftest: missing mark"
	table "$t" | grep -q 'session  *4672.4  (+3083.4)' || die "selftest: table"
	rm -f "$t"
	echo "boot-compare selftest ok"
	exit 0
fi

[ $# -ge 1 ] || die "usage: $0 label=path/to/aarch64/slot [label=path ...] | selftest"
for a in "$@"; do
	case "$a" in
	*=*) ;;
	*) die "'$a' is not label=path" ;;
	esac
	l="${a%%=*}"
	p="${a#*=}"
	case "$l" in *[!A-Za-z0-9_-]* | '') die "label '$l' must be letters, digits, - or _" ;; esac
	[ -f "$p" ] || die "$p is not a file"
	file "$p" | grep -q 'aarch64' || die "$p is not an aarch64 ELF (build it with device-sh.sh, see the header)"
done

bt="$SD/boottest"
cfg="$SD/Config"
tf="$SD/System/launch_frontend.sh"
tmp="$(mktemp -d "$mt/bc.XXXXXX")"
armed=0

dx "test -f $(shq "$cfg/slot.state")" || die "no $cfg/slot.state on the device"
dx "test -f $(shq "$tf")" || die "no $tf on the device"
cur="$(dev "grep '^cart=' $(shq "$cfg/slot.state")")"
[ "$cur" = "cart=" ] || echo "slot-nes-snes: warning: slot.state has '$cur', a game may be running. Its unsaved play is lost when slot is stopped, and every run resumes into that cart." >&2

# Device helper. stop: kill -9 every slot, the shelf one (.../System/slot) or a test one (.../boottest/slot-<label>).
# bg CMD...: start detached, with setsid when the device has it.
ctl="$tmp/slotctl.sh"
cat >"$ctl" <<'EOF'
#!/bin/sh
pids() { for p in /proc/[0-9]*; do tr '\0' '\n' <"$p/cmdline" 2>/dev/null | grep -qE '/(System/slot|boottest/slot-[A-Za-z0-9_-]+)$' && echo "${p#/proc/}"; done; }
case "$1" in
pids) pids ;;
stop)
	for p in $(pids); do kill -9 "$p"; done
	n=0
	while [ -n "$(pids)" ] && [ "$n" -lt 50 ]; do sleep 0.1; n=$((n + 1)); done
	;;
bg)
	shift
	if command -v setsid >/dev/null 2>&1; then
		setsid "$@" </dev/null >/dev/null 2>&1 &
	else
		nohup "$@" </dev/null >/dev/null 2>&1 &
	fi
	sleep 1
	;;
esac
EOF
$ADB shell "mkdir -p $(shq "$bt")" </dev/null
$ADB push "$ctl" "$bt/slotctl.sh" </dev/null >/dev/null || die "cannot push slotctl.sh"
sc="sh $(shq "$bt/slotctl.sh")"

# Put the device back on every exit once anything was changed: state and logs, then the normal slot.
cleanup() {
	rc=$?
	trap - EXIT INT TERM
	set +e
	if [ "$armed" = 1 ]; then
		dx "$sc stop"
		dx "cd $(shq "$bt") && cp -p slot.state $(shq "$cfg/slot.state") && { [ -f slot.log.bak ] && cp -p slot.log.bak $(shq "$SD/slot.log"); [ -f slot.log.1.bak ] && cp -p slot.log.1.bak $(shq "$SD/slot.log.1"); true; }"
		dx "$sc bg sh $(shq "$tf")"
		n=0
		while [ "$n" -lt 10 ] && [ -z "$(dev "$sc pids")" ]; do
			sleep 1
			n=$((n + 1))
		done
		[ -n "$(dev "$sc pids")" ] || echo "slot-nes-snes: slot did not come back, power-cycle the device" >&2
		dx "rm -rf $(shq "$bt")"
		echo "device restored, normal slot restarted" >&2
	fi
	rm -rf "$tmp"
	exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

dx "cd $(shq "$bt") && cp -p $(shq "$cfg/slot.state") slot.state && { cp -p $(shq "$SD/slot.log") slot.log.bak 2>/dev/null; cp -p $(shq "$SD/slot.log.1") slot.log.1.bak 2>/dev/null; true; }" ||
	die "the backup failed, nothing was changed"
armed=1

for a in "$@"; do
	$ADB push "${a#*=}" "$bt/slot-${a%%=*}" </dev/null >/dev/null || die "cannot push ${a#*=}"
done
dx "chmod 755 $(shq "$bt")/slot-*"

: >"$tmp/summary"
run=1
while [ "$run" -le "$RUNS" ]; do
	for a in "$@"; do
		l="${a%%=*}"
		log="$bt/$l.$run.log"
		dx "$sc stop"
		dx "cp -p $(shq "$bt/slot.state") $(shq "$cfg/slot.state")"
		[ "$COLD" = 1 ] && dx "sync; echo 3 > /proc/sys/vm/drop_caches"
		dx "cd $(shq "$SD") && SLOT_ROOT=$(shq "$SD") $sc bg sh -c $(shq "exec /lib/ld-linux-aarch64.so.1 $bt/slot-$l >$log 2>&1")"
		n=0
		while [ "$n" -lt "$WAIT" ]; do
			c="$(dev "grep -c 'boot: ui faces at' $(shq "$log")")"
			case "$c" in '' | *[!0-9]*) c=0 ;; esac
			[ "$c" -gt 0 ] && break
			sleep 1
			n=$((n + 1))
		done
		dx "$sc stop"
		$ADB pull "$log" "$tmp/$l.$run.log" </dev/null >/dev/null 2>&1 || : >"$tmp/$l.$run.log"
		echo "== $l run $run (COLD=$COLD)"
		table "$tmp/$l.$run.log"
		a1="$(at "$tmp/$l.$run.log" scan)"
		a2="$(at "$tmp/$l.$run.log" session)"
		a3="$(at "$tmp/$l.$run.log" 'ui faces')"
		printf '%s\t%s\t%s\t%s\t%s\n' "$l" "$run" "${a1:-?}" "${a2:-?}" "${a3:-?}" >>"$tmp/summary"
	done
	run=$((run + 1))
done

echo
printf 'label\trun\tscan\tsession\tui faces\tscan to session\n'
awk -F'\t' '{ d = ($3 == "?" || $4 == "?") ? "?" : sprintf("%.1f", $4 - $3); printf "%s\t%s\t%s\t%s\t%s\t%s\n", $1, $2, $3, $4, $5, d }' "$tmp/summary"
