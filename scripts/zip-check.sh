#!/bin/sh
# T13: check a release zip before it ships. Fails on every missing piece it finds, not just the first.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/scripts/lib.sh"
read_pin

cores="mgba gpsp fceumm snes9x nestopia snes9x2005_plus genesis_plus_gx pcsx_rearmed"
# Games/ folders the zip may hold.
games="GBA GB GBC NES SNES GG SMS MD PS1"
# Folders that ship empty, the user's own data lives there.
empty="Config Saves States Labels BIOS Wallpapers"

usage() {
	echo "usage: $0 ZIP" >&2
	exit 2
}

[ $# -eq 1 ] && [ -n "$1" ] || usage
zip="$1"
[ -f "$zip" ] || zip="$root/build/$1"
[ -f "$zip" ] || {
	echo "zip-check: $1 not found" >&2
	exit 1
}

failed=0
seen=
# Each distinct message prints once, however many checks reach it.
bad() {
	case "$seen" in *"
$*
"*) ;; *)
		seen="$seen
$*
"
		echo "zip-check: $*" >&2
		;;
	esac
	failed=1
}

need() {
	for pattern in "$@"; do
		set -- "$lic"/$pattern
		[ -f "$1" ] || bad "System/licenses/$pattern is missing"
	done
}

aarch64() {
	is_aarch64 "$1" || bad "${1#"$d"/} is not an aarch64 ELF: $(file -b "$1")"
}

release="$(release_name)"
want="$release"
src="slot-nes-snes-src-${release#slot-nes-snes-}"
tops="$(unzip -Z1 "$zip" | cut -d/ -f1 | sort -u)"
[ "$(printf '%s\n' "$tops" | wc -l | tr -d ' ')" = 1 ] || {
	bad "expected one top folder, found: $(printf '%s' "$tops" | tr '\n' ' ')"
	exit 1
}
[ "$tops" = "$want" ] || bad "top folder is $tops, SLOT_PIN and VERSION want $want"
[ "$(basename "$zip")" = "$want-h700.zip" ] || bad "zip is named $(basename "$zip"), want $want-h700.zip"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
unzip -q "$zip" -d "$work"
d="$work/$tops"
sys="$d/System"
lic="$sys/licenses"

# A symlink in a release zip can point anywhere on the machine that unpacks it.
find "$d" -type l | while read -r l; do echo "zip-check: symlink in zip: ${l#"$d"/}" >&2; done
[ -z "$(find "$d" -type l)" ] || failed=1

for dir in System $empty $(for g in $games; do echo "Games/$g"; done); do
	[ -d "$d/$dir" ] || bad "$dir/ is missing"
done
for dir in $empty; do
	[ -z "$(find "$d/$dir" ! -type d 2>/dev/null)" ] || bad "$dir/ must hold no files: $(find "$d/$dir" ! -type d | sed "s|^$d/||" | tr '\n' ' ')"
done
for g in "$d"/Games/*; do
	[ -e "$g" ] || continue
	case " $games " in *" $(basename "$g") "*) ;; *) bad "Games/$(basename "$g") is not a folder this release ships ($games)" ;; esac
done

# System/ holds exactly this set: upstream's dist output plus our core and licence files.
req="bezels/640x480.png bootlogo.bmp coresave.sh launch_frontend.sh led.sh lid.sh repair.sh slotlink.sh slot fsck.exfat
mgba_libretro.so gpsp_libretro.so fceumm_libretro.so snes9x_libretro.so nestopia_libretro.so snes9x2005_plus_libretro.so
genesis_plus_gx_libretro.so pcsx_rearmed_libretro.so"
for f in $req; do
	[ -f "$sys/$f" ] || bad "System/$f is missing"
done
mc="$(slot_var MGBA_COMMIT)"
gc="$(slot_var GPSP_COMMIT)"
ev="$(slot_var EXFATPROGS_VERSION)"
[ -n "$mc" ] && [ -n "$gc" ] && [ -n "$ev" ] || bad "no MGBA_COMMIT, GPSP_COMMIT or EXFATPROGS_VERSION in build/slot/taskfile.yml, run task build"
ok="bezels/640x480.png bootlogo.bmp coresave.sh launch_frontend.sh led.sh lid.sh repair.sh slotlink.sh slot fsck.exfat
licenses/exfatprogs-GPL-2.0.txt licenses/exfatprogs-$ev.tar.gz
mgba_libretro.so gpsp_libretro.so fceumm_libretro.so snes9x_libretro.so nestopia_libretro.so snes9x2005_plus_libretro.so
genesis_plus_gx_libretro.so pcsx_rearmed_libretro.so
licenses/bezel-CC-BY-SA-4.0.txt licenses/shaders.txt licenses/retro-shaders.txt licenses/cores.sha256
licenses/mgba-MPL-2.0.txt licenses/mgba-$mc.meta
licenses/gpsp-GPL-2.0.txt licenses/gpsp-$gc.meta licenses/gpsp-$gc.tar.gz
licenses/fceumm_libretro.so.meta licenses/fceumm-src.meta licenses/fceumm-src.tar.gz
licenses/fceumm-GPL-2.0.txt licenses/fceumm-headerless-files.txt licenses/$src.tar.gz
licenses/snes9x_libretro.so.meta licenses/snes9x-src.meta licenses/snes9x-src.tar.gz licenses/snes9x-LICENSE.txt
licenses/nestopia_libretro.so.meta licenses/nestopia-src.meta licenses/nestopia-src.tar.gz licenses/nestopia-GPL-2.0.txt
licenses/snes9x2005_plus_libretro.so.meta licenses/snes9x2005_plus-src.meta licenses/snes9x2005_plus-src.tar.gz licenses/snes9x2005-LICENSE.txt
licenses/genesis_plus_gx_libretro.so.meta licenses/genesis_plus_gx-src.meta licenses/genesis_plus_gx-src.tar.gz licenses/genesis_plus_gx-LICENSE.txt
licenses/pcsx_rearmed_libretro.so.meta licenses/pcsx_rearmed-src.meta licenses/pcsx_rearmed-src.tar.gz licenses/pcsx_rearmed-GPL-2.0.txt"
for p in "$root"/build/slot/cores/mgba/*.patch; do ok="$ok licenses/mgba-$(basename "$p")"; done
for p in "$root"/build/slot/cores/gpsp/*.patch; do ok="$ok licenses/gpsp-$(basename "$p")"; done
for p in "$root"/patches/*.patch; do ok="$ok licenses/slot-nes-snes-$(basename "$p")"; done
find "$sys" ! -type d | sed "s|^$sys/||" | sort | while read -r f; do
	case " $(echo $ok) " in *" $f "*) ;; *) echo "zip-check: System/$f is not expected in a release" >&2 ;; esac
done 2>"$work/stray"
for f in $ok; do
	[ -f "$sys/$f" ] || bad "System/$f is missing"
done
if [ -s "$work/stray" ]; then
	cat "$work/stray" >&2
	failed=1
fi

for f in "$sys/slot" "$sys"/*_libretro.so; do
	[ ! -f "$f" ] || [ -x "$f" ] || bad "${f#"$d"/} is not executable"
done

for f in "$sys"/*.sh; do
	[ ! -f "$f" ] || ! grep -q "$(printf '\r')" "$f" || bad "System/$(basename "$f") has CRLF line endings"
done

# Each core must be the one its name says: its own library name is in its strings and in no other
# core's, and its sha256 is the one dist-device.sh recorded in licenses/cores.sha256.
# snes9x2005_plus is built from snes9x 1.43 and its option keys are snes9x_2005_*, so "snes9x" is
# legitimately in it: that one pair is skipped, and "Snes9x 2005 Plus" must stay out of snes9x.
for pair in mgba:mGBA gpsp:gpSP fceumm:FCEUmm snes9x:snes9x nestopia:Nestopia snes9x2005_plus:Snes9x.2005.Plus genesis_plus_gx:Genesis.Plus.GX pcsx_rearmed:PCSX-ReARMed; do
	for other in mgba:mGBA gpsp:gpSP fceumm:FCEUmm snes9x:snes9x nestopia:Nestopia snes9x2005_plus:Snes9x.2005.Plus genesis_plus_gx:Genesis.Plus.GX pcsx_rearmed:PCSX-ReARMed; do
		f="$sys/${pair%%:*}_libretro.so"
		[ -f "$f" ] || continue
		[ "${pair%%:*}:${other%%:*}" != snes9x2005_plus:snes9x ] || continue
		n="$(strings -a "$f" | grep -c -- "${other#*:}" || true)"
		if [ "$pair" = "$other" ]; then
			[ "$n" -gt 0 ] || bad "System/${pair%%:*}_libretro.so does not contain its own name ${pair#*:}, not that core"
		else
			[ "$n" = 0 ] || bad "System/${pair%%:*}_libretro.so contains ${other#*:}, it is the ${other%%:*} core or a mix"
		fi
	done
done
if [ -f "$lic/cores.sha256" ]; then
	for core in $cores; do
		f="$sys/${core}_libretro.so"
		[ -f "$f" ] || continue
		want="$(sed -n "s/^\([0-9a-f]*\)  ${core}_libretro.so\$/\1/p" "$lic/cores.sha256")"
		[ -n "$want" ] && [ "$(file_sha256 "$f")" = "$want" ] ||
			bad "System/${core}_libretro.so does not match the sha256 in licenses/cores.sha256"
	done
fi

# Shipped licence and source files are checked by content, not just by name: each licence file we
# keep in licenses/ and each patch must be byte-equal to the repo copy, each core's source tarball
# must be the one SLOT_PIN pins, and each .meta must name the pinned commit.
for f in "$root"/licenses/*; do
	[ -f "$f" ] || continue
	[ ! -f "$lic/$(basename "$f")" ] || cmp -s "$f" "$lic/$(basename "$f")" ||
		bad "System/licenses/$(basename "$f") differs from licenses/$(basename "$f")"
done
for p in "$root"/patches/*.patch; do
	[ ! -f "$lic/slot-nes-snes-$(basename "$p")" ] || cmp -s "$p" "$lic/slot-nes-snes-$(basename "$p")" ||
		bad "System/licenses/slot-nes-snes-$(basename "$p") differs from patches/$(basename "$p")"
done
for core in fceumm snes9x nestopia snes9x2005_plus genesis_plus_gx pcsx_rearmed; do
	eval "cc=\${${core}_commit:-}"
	[ -n "$cc" ] || bad "SLOT_PIN has no ${core}_commit"
	for m in "$core-src.meta" "${core}_libretro.so.meta"; do
		[ ! -f "$lic/$m" ] || grep -qx "commit=$cc" "$lic/$m" || bad "System/licenses/$m does not name the pinned commit $cc"
	done
done
for pair in fceumm:fceumm-src.tar.gz:fceumm_tarball_sha256 snes9x:snes9x-src.tar.gz:snes9x_tarball_sha256 nestopia:nestopia-src.tar.gz:nestopia_tarball_sha256 snes9x2005_plus:snes9x2005_plus-src.tar.gz:snes9x2005_plus_tarball_sha256 genesis_plus_gx:genesis_plus_gx-src.tar.gz:genesis_plus_gx_tarball_sha256 pcsx_rearmed:pcsx_rearmed-src.tar.gz:pcsx_rearmed_tarball_sha256 gpsp:gpsp-$gc.tar.gz:gpsp_tarball_sha256; do
	f="$lic/$(echo "$pair" | cut -d: -f2)"
	eval "want=\${$(echo "$pair" | cut -d: -f3):-}"
	[ -n "$want" ] || bad "SLOT_PIN has no $(echo "$pair" | cut -d: -f3)"
	[ ! -f "$f" ] || [ "$(file_sha256 "$f")" = "$want" ] ||
		bad "System/licenses/$(basename "$f") is not the source SLOT_PIN pins ($(echo "$pair" | cut -d: -f3))"
done

[ -x "$sys/slot" ] || bad "System/slot is missing or not executable"
[ ! -f "$sys/slot" ] || aarch64 "$sys/slot"
[ ! -f "$sys/fsck.exfat" ] || aarch64 "$sys/fsck.exfat"
es="$(slot_var EXFATPROGS_SHA256)"
f="$lic/exfatprogs-$ev.tar.gz"
[ ! -f "$f" ] || [ "$(file_sha256 "$f")" = "$es" ] ||
	bad "System/licenses/exfatprogs-$ev.tar.gz is not the source upstream pins (EXFATPROGS_SHA256)"

for f in "$sys"/*_libretro.*; do
	[ -e "$f" ] || continue
	core="$(basename "$f")"
	core="${core%%_libretro.*}"
	case " $cores " in *" $core "*) ;; *) bad "$(basename "$f") is not a core this release ships ($cores)" ;; esac
	case $f in *.so) aarch64 "$f" ;; *) bad "$(basename "$f") is not a device core (.so)" ;; esac
done

for core in $cores; do
	[ -f "$sys/${core}_libretro.so" ] || bad "System/${core}_libretro.so is missing"
	case $core in
	mgba) need 'mgba-*.meta' mgba-MPL-2.0.txt ;;
	gpsp) need 'gpsp-*.tar.gz' 'gpsp-*.meta' gpsp-GPL-2.0.txt ;;
	fceumm) need fceumm_libretro.so.meta fceumm-src.tar.gz fceumm-src.meta fceumm-GPL-2.0.txt fceumm-headerless-files.txt ;;
	snes9x) need snes9x_libretro.so.meta snes9x-src.tar.gz snes9x-src.meta snes9x-LICENSE.txt ;;
	nestopia) need nestopia_libretro.so.meta nestopia-src.tar.gz nestopia-src.meta nestopia-GPL-2.0.txt ;;
	snes9x2005_plus) need snes9x2005_plus_libretro.so.meta snes9x2005_plus-src.tar.gz snes9x2005_plus-src.meta snes9x2005-LICENSE.txt ;;
	genesis_plus_gx) need genesis_plus_gx_libretro.so.meta genesis_plus_gx-src.tar.gz genesis_plus_gx-src.meta genesis_plus_gx-LICENSE.txt ;;
	pcsx_rearmed) need pcsx_rearmed_libretro.so.meta pcsx_rearmed-src.tar.gz pcsx_rearmed-src.meta pcsx_rearmed-GPL-2.0.txt ;;
	*) bad "no file list for core $core in zip-check.sh" ;;
	esac
done

need 'slot-nes-snes-*.patch'
n="$(find "$lic" -name 'slot-nes-snes-src-*' | wc -l | tr -d ' ')"
if [ "$n" != 1 ] || [ ! -f "$lic/$src.tar.gz" ]; then
	bad "System/licenses must hold exactly one slot-nes-snes-src-*, named $src.tar.gz"
else
	list="$(tar -tzf "$lic/$src.tar.gz" | grep -v '/$')"
	own_repo "$root/work/slot" || bad "work/slot is not a git checkout, cannot compare the source tarball to it"
	if own_repo "$root/work/slot"; then
		git -C "$root/work/slot" ls-files | sed "s|^|$src/slot/|" | LC_ALL=C sort >"$work/want"
		printf '%s\n' "$list" | grep "^$src/slot/" | LC_ALL=C sort >"$work/have"
		diff "$work/want" "$work/have" >"$work/diff" ||
			bad "$src.tar.gz slot/ differs from work/slot HEAD: $(sed -n 's/^[<>] //p' "$work/diff" | head -5 | tr '\n' ' ')"
	fi
	for f in slot-nes-snes/SLOT_PIN slot-nes-snes/VERSION slot-nes-snes/taskfile.yml \
		$(for p in "$root"/patches/*.patch "$root"/scripts/*.sh; do echo "slot-nes-snes/${p#"$root"/}"; done); do
		printf '%s\n' "$list" | grep -qxF "$src/$f" || bad "$src.tar.gz does not hold $f"
	done
fi

[ "$failed" = 0 ] || exit 1
echo "zip-check: $(basename "$zip") ok"
