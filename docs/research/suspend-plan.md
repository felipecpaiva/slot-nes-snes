# Suspend-to-RAM on lid close: probe, design and upstream draft (plan only, no code)

Date: 2026-10-18. Status: **stopped. The read-only probe failed on the RG34XXSP on 2026-10-18 (P4: no
power-key wake source), so ADR 0033 stands.** See section 3, "Result". The rest is kept as the design
if a later BaseOS exposes lid wake. Nothing here is implemented. If it goes ahead it needs a new ADR that supersedes
[ADR 0033](../adr/0033-keep-upstream-lid-timeout.md) (and amends [ADR 0078](../adr/0078-rest-while-dozing.md)),
and an upstream discussion first (ADR 0047), because Brandon is reworking lid power-off right now.

Sources: [fork-suprsomething.md](fork-suprsomething.md) section 1 and 9 (slot.advance c9e5697, dbbadae,
d7cb474, read at `~/.cache/forks/suprsomething` 3525f86, `crates/slot-power/src/sleep.rs`),
[fork-jgraving.md](fork-jgraving.md) row "Deep sleep on lid close" (jgraving/slot f2aa20d, 5958250, read
at `~/.cache/forks/jgraving` 3b5fec5, `crates/slot-power/src/device.rs` `suspend()`), upstream main
2c82294 (Lid Off row, `lid_off_min`) and ad5ce8a (`card/System/lid.sh`), read at
`~/.cache/forks/upstream-slot` 1b20432.

## 1. What exists

### Today (v1.7.0, our pin)

Lid shut: `doze()` flushes the resume state and `.sav`, turns the backlight off and pauses the core.
After 3 minutes (`DOZE_TIMEOUT`) slot powers off; the next boot resumes the game. Our patch 0051 stops
drawing while dozing. Coming back after 3 minutes costs a boot and a state load (4.4 MB on PS1).

### Upstream main (1.8.0, unreleased)

- 2c82294: `lid_off_min` in slot.state, `LID_OFF_MIN = [1, 3, 5, 10, 15, 30]`, a **Lid Power Off** row
  on General (just above Date & Time). Unset means the platform's 3 minutes. `doze_expired()` compares
  `self.now() - dozed_at` with it; `self.now()` is slot's own clock, which advances by the frame `dt`
  (`Instant`, which on Linux does **not** count time suspended).
- ad5ce8a (#117): `card/System/lid.sh`, started by `launch_frontend.sh`. Every 5 s it reads
  `/sys/class/power_supply/axp2202-battery/hallkey` (0 = shut), stamps the first shut reading with
  `/proc/uptime` (which **does** count time suspended) into `/run/slot-lid.closed`, and once the lid has
  been shut for `lid_off_min * 60 + 60` s it runs `rmmod 8821cs; sync; poweroff` behind slot's back.
  `minutes()` accepts only `1|3|5|10|15|30` and reads anything else as 3. It exists because slot could
  hang on a black screen with the lid shut.
- 0ba5370: holding POWER powers off.

### The two forks

| | suprsomething/slot.advance (RG SP 2026, BaseOS 1.3.0) | jgraving/slot (RG SP, RG35XXSP) |
|---|---|---|
| Wake sources | lid and RTC alarm (and POWER) | POWER and RTC alarm only (lid does not wake) |
| Lid wake | writes `0` to `axp2202-battery/os_sleep` (BaseOS writes `16` at boot, "Super Standby"), then checks `.../axp2101-pek.0/power/wakeup` reads `enabled` | writes `16` to `os_sleep` for the sleep, restores the old value after |
| RTC | the rtc whose `name` is `sunxi-rtc` (found by name, never by number), relative alarm `+secs` written to `wakealarm`, read back until it is a number, cleared with `0` after | `class/rtc/rtc0/wakealarm`, absolute epoch seconds, old alarm restored after |
| Suspend | `mem` to `/sys/power/state` (refuses unless `mem` is listed), blocks until wake | same |
| Time asleep | `/proc/uptime` minus `Instant`, plus `success:` in `/sys/kernel/debug/suspend_stats` | `now() >= deadline` after wake means the alarm fired: power off |
| Audio | nothing new (ALSA write path already calls `snd_pcm_recover`) | `alsactl -f /run/slot-sleep-mixer.state store` before, `restore` after |
| Lid after wake | `hallkey` can stay `0` (the driver writes 0 then 1 and the second write is sometimes missed); cross-checked with the `hall switch` line in debugfs `/sys/kernel/debug/gpio` | n/a |
| Wake handling | lid open: resume; deadline: clean shutdown; anything else: back to sleep after 1 s; two failed suspends or 20 stray wakes fall back to software doze; POWER ignored with the lid shut and for 3 s after a wake; deadline pulled in to leave 10% battery | a 750 ms guard eats the waking POWER press |
| Measured (their device, gauge only) | about 70 mA asleep, 2 to 3.2 %/h overnight, wake to first frame 0.81 s median; 9 of 20 rapid lid flicks left the screen dark | none published |

Neither fork ran on an RG34XXSP. Every node above is unverified on ours.

## 2. Goal and the one design rule

Open the lid hours later and the game is there in about a second, at a few percent battery per hour,
on every system (PS1 gains most: no boot, no 4.4 MB state load). Speed and battery trades are user
options and factory defaults stay, so suspend is **opt-in** and the current behaviour stays the default.

## 3. Probe steps (read-only, maintainer runs them)

Every command only reads (`cat`, `ls`, `grep`, `find`, `dmesg`). None writes to sysfs, none suspends.
Run them on the charger, slot on the shelf, lid open unless the step says otherwise. Save the output.

```sh
# P1. Battery node: os_sleep, hallkey and the gauge fields the forks used
adb shell 'P=/sys/class/power_supply/axp2202-battery; ls $P; for f in type os_sleep hallkey capacity voltage_now current_now status charge_full_design; do printf "%s=" $f; cat $P/$f 2>&1; done'

# P2. Sleep states the kernel offers (need "mem"); mem_sleep says whether mem is deep or s2idle
adb shell 'cat /sys/power/state; cat /sys/power/mem_sleep 2>&1; cat /sys/power/wakeup_count 2>&1'

# P3. RTCs: which one is sunxi-rtc, does it have wakealarm, is it a wake source, does it keep time
adb shell 'date +%s; for r in /sys/class/rtc/rtc*; do echo "$r name=$(cat $r/name) since_epoch=$(cat $r/since_epoch 2>&1) wakealarm=[$(cat $r/wakealarm 2>&1)] wakeup=$(cat $r/device/power/wakeup 2>&1)"; done'

# P4. Power key device that owns the lid interrupt, and whether it is a wake source today
adb shell 'find /sys/devices -maxdepth 10 -name "axp2101-pek*" 2>/dev/null; for w in $(find /sys/devices -maxdepth 11 -path "*axp2101-pek*/power/wakeup" 2>/dev/null); do echo "$w=$(cat $w)"; done'

# P5. Raw hall switch line (for the stale-lid check) and the kernel's suspend counters
adb shell 'mount | grep debugfs; grep -i -e hall -e lid /sys/kernel/debug/gpio; cat /sys/kernel/debug/suspend_stats 2>&1; head -30 /sys/kernel/debug/wakeup_sources 2>&1'

# P6. Interrupt lines for the PMIC, power key and RTC
adb shell 'grep -i -E "axp|pek|rtc|hall|gpio" /proc/interrupts'

# P7. Kernel, BaseOS and modules (Wi-Fi driver name for the SDIO stall risk)
adb shell 'cat /proc/version; cat /etc/baseos-release 2>/dev/null; lsmod; ls /sys/class/misc/sunxi-wlan/rf-ctrl/ 2>&1'

# P8. Has this kernel ever suspended, and how does it log it
adb shell 'dmesg | grep -i -E "PM:|suspend|resume|sunxi-rtc|axp2101|wakeup" | tail -40'

# P9. hallkey and the raw line with the lid open, then shut, then open (close the lid during the loop;
#     slot will doze, which is harmless; adb keeps working)
adb shell 'P=/sys/class/power_supply/axp2202-battery; for i in 1 2 3 4 5 6 7 8 9 10; do echo "$(cut -d" " -f1 /proc/uptime) hallkey=$(cat $P/hallkey) $(grep -i hall /sys/kernel/debug/gpio 2>/dev/null)"; sleep 2; done'

# P10. lid.sh state, only on a build with upstream 1.8.0 (after the rebase)
adb shell 'cat /run/slot-lid.pid /run/slot-lid.closed 2>&1; tail -5 /mnt/sdcard/Logs/ags-shutdown-trace.log 2>&1'
```

What decides it:

- **Go to the write tests** only if P1 shows `os_sleep` and `hallkey`, P2 lists `mem` (and P2's
  `mem_sleep`, if present, offers `deep`), P3 shows a `sunxi-rtc` with a `wakealarm` file, and P4 finds
  `axp2101-pek.0` with a `power/wakeup` node.
- Record: the `os_sleep` value (the forks expect `16`), whether `current_now` is live (it makes awake
  segments measurable without 1% ticks), which rtc number `sunxi-rtc` is (jgraving's hardcoded `rtc0`
  may be the wrong one here), whether P9 shows `hallkey` flipping 1 to 0 to 1 and a matching raw line,
  and whether P7 shows `8821cs` (the fork's 1.1 s `mmc2: error -110` wake stall came from its SDIO card).
- If any required node is missing: stop. Suspend is not possible on this BaseOS; ADR 0033 stands.

### Result on the RG34XXSP, 2026-10-18

| Probe | Read | Verdict |
|---|---|---|
| P1 `os_sleep` | exists, empty | present, but not the `16` the forks expect |
| P1 `hallkey` | `1` (lid open) | present |
| P1 `current_now` | absent | no live current; battery work needs 1% ticks |
| P2 `/sys/power/state` | `freeze mem`, no `mem_sleep` file | `mem` offered |
| P3 rtc | `rtc1` = `sunxi-rtc`, has `wakealarm` | present (jgraving's hardcoded `rtc0` would be the wrong rtc here) |
| P4 `*pek*/power/wakeup` | nothing found | **fail**: no power-key wake source, so the lid cannot be armed as a wake source the way suprsomething does |

Per the stop rule above: **the probe failed on P4, `current_now` is absent, and ADR 0033 stands.** No
write test is to be run. Revisit only if a BaseOS update exposes a lid or power-key wake source (rerun
P1 to P4 first). A POWER-only, RTC-timed suspend in the style of jgraving would not need P4, but it was
never in scope (it loses lid wake, the point of this plan) and would need its own decision.

The write tests (manual suspend by RTC alarm, lid wake, wake time, current per segment, our systems,
stress, lid.sh conflict) are already written as steps 1 to 7 of fork-suprsomething.md section 9. They
write `os_sleep`, an rtc alarm and `mem`, so they are not part of this read-only probe; run them only
after the maintainer decides to continue.

## 4. Design: extend upstream's Lid Power Off row

Built on top of the 1.8.0 rebase (it needs `lid_off_min`, the row and `lid.sh`). No new SlotState key,
no new row, no change for anyone who does not pick a long value.

### The row

- `LID_OFF_MIN` gains long values, shown only when the probe passes at start: `[1, 3, 5, 10, 15, 30,
  60, 120, 480]`, shown as `1 h`, `2 h`, `8 h`. A value of 60 or more means "sleep, then power off at
  that time". Values up to 30 keep today's light doze exactly. Unset stays the platform's 3 minutes.
- On a device or kernel where the probe fails, the long values are hidden and a stored long value reads
  as 30 with a `slot: sleep:` log line (no silent fallback).
- Open question for the maintainer: a separate choice "Lid Close: Doze / Sleep" would also let short
  timeouts sleep. It costs a new key and a new row, which suprsomething had and fork-suprsomething.md
  advised against. The long-values-only design keeps one row and one key.

### What slot does

1. Lid shut: `doze()` as today (flush the resume state and `.sav`, backlight off, core paused, link
   ended). Our 0051 rest loop starts.
2. If `lid_off_min >= 60` and the lid is still shut after a 2 s settle (a quick close and open stays a
   light doze), slot suspends: `sync`, write `/run/slot-sleep.until` (the `/proc/uptime` second at which
   power-off is due), arm lid wake (`os_sleep=0`, check `pek` `power/wakeup` is `enabled`), set the
   `sunxi-rtc` alarm (found by name) to the remaining time and read it back, write `mem` to
   `/sys/power/state`. Refuse and stay in light doze, with a log line, if any step fails.
3. On wake, classify by `hallkey` (cross-checked with the raw `hall switch` line, P9) and the clock:
   - lid open: clear the alarm, delete `/run/slot-sleep.until`, restore `os_sleep` to the value read
     at start, `wake()` as today (backlight on, core resumes);
   - deadline reached: power off through slot's own path (the save is already flushed);
   - anything else (POWER with the lid shut, charger, stray): back to sleep for the remaining time after
     1 s; two failed suspends or 20 stray wakes fall back to light doze for the rest of the timeout.
4. Time: slot's clock (`self.now()`) advances by frame `dt` from `Instant`, which does not count
   suspend. Doze expiry for sleep must use `/proc/uptime` (boot time, counts suspend), the same clock
   `lid.sh` and the forks use. The first frame after a wake must not see the whole sleep as one `dt`.
5. Battery: pull the deadline in so at least 10% is left (suprsomething's rule), never below 3 minutes.
6. POWER while asleep with the lid shut: wakes the kernel; slot goes back to sleep (step 3). A held POWER
   still powers off (0ba5370). POWER with the lid open after a wake behaves as today.

### How lid.sh must learn about suspend

Today, after a stray wake, `lid.sh` sees `/proc/uptime` far past its shut stamp and powers off at once,
with no save from slot's side of the clock and before slot classifies the wake. It must:

1. Accept the long values: `1 | 3 | 5 | 10 | 15 | 30 | 60 | 120 | 480` in `minutes()`.
2. Respect slot's deadline: if `/run/slot-sleep.until` exists, power off only when `uptime >= until +
   GRACE` (still a minute after slot should have powered off), instead of `closed + minutes*60 + GRACE`.
   That keeps the watcher's purpose (#117: slot hung with the lid shut) and stops it from killing a
   sleeping device on a stray wake.
3. Nothing else: it already stops counting when the lid opens (`hallkey != 0` removes the stamp).
   `card/test-lid.sh` gains cases for the marker file and the long values.

`launch_frontend.sh` is unchanged. Upstream's held-POWER power-off is unchanged.

## 5. Risks

- **Interfaces unverified on the RG34XXSP**: every node in section 1 was found on an RG SP or RG35XXSP.
  The probe decides; a failed probe ends the plan.
- **Dark screen after rapid lid flicks** (suprsomething: 9 to 10 of 20). Needs the stress step and a
  rule that a lid opened during the 2 s settle never suspends.
- **Stale `hallkey=0` after a wake**: needs the debugfs cross-check, so debugfs must be mounted (P5).
- **lid.sh powering off a sleeping device** (section 4); must ship in the same change, and upstream owns
  `lid.sh`.
- **Clock**: `Instant` skips suspend; using it for the timeout means the device never powers off on
  time. Use boot time.
- **Resume of what slot holds open**: the GL context on fbdev, ALSA (recover path exists; jgraving also
  stores and restores the mixer), pcsx_rearmed's threaded GPU and dynarec threads (ADR 0064), CHD reads,
  the input event nodes, Wi-Fi SDIO (`mmc2: error -110`, about 1.1 s per wake on the fork's device).
- **Stray wakes drain battery** (charger, POWER in a bag): bounded by the fall-back rule and the 10%
  floor.
- **RTC games** (GBA, Pokemon Emerald): the game clock reads the host clock, so it jumps forward by the
  time asleep, which is correct; check it once.
- **SlotLink**: doze already ends the link; a peer sees a disconnect, as today.
- **Gauge**: 1% steps and nonlinear above 80%, so battery claims need the fork's tick method (section 9
  step 4 of fork-suprsomething.md).
- **Scope**: device-wide and touching `doze`, the device loop (patch 0015, 0051), `lid.sh` and
  `slot-power`. A large patch to carry; much better upstream.

## 6. Upstream discussion draft (not sent)

> **Title:** Suspend-to-RAM while the lid is shut, as longer steps of Lid Power Off
>
> Hi Brandon. With Lid Power Off (2c82294) and the lid watcher (ad5ce8a) in main, I would like to ask
> whether you would take hardware sleep for the lid, and if so in what shape.
>
> Two forks have done it. slot.advance (suprsomething, RG SP 2026) arms the lid as a wake source with
> `os_sleep=0`, sets the `sunxi-rtc` alarm (found by name) for the power-off time and writes `mem` to
> `/sys/power/state`. They measured about 70 mA asleep, 2 to 3 %/h, and 0.8 s from lid open to the first
> frame. jgraving's fork does the same with POWER as the only wake source. Neither has run on an
> RG34XXSP; I have a read-only probe list for the nodes and will post the results from mine.
>
> The shape I have in mind, so nothing changes for anyone who does not opt in:
>
> - Lid Power Off gains `1 h`, `2 h`, `8 h`, shown only when the kernel offers `mem`, the rtc has a
>   `wakealarm` and lid wake arms. Up to 30 min stays the doze you have today.
> - With a long value, slot dozes exactly as now (resume state and save flushed first), then suspends
>   after 2 s with the lid still shut. Lid open resumes; the alarm powers off through slot's own path;
>   any other wake goes back to sleep, and repeated failures fall back to the doze.
> - The timeout uses boot time (`/proc/uptime`), since `Instant` skips suspend.
> - `lid.sh` accepts the long values and, while slot has written a `/run/slot-sleep.until` deadline,
>   powers off a minute after that deadline instead of a minute after the lid timer, so a stray wake
>   does not cut power before slot has looked at it. It still covers the hang it was written for.
>
> Known risks from the forks: a dark screen after rapid lid flicks, a stale `hallkey=0` after a wake,
> and a 1 s Wi-Fi SDIO stall on wake. I would bring device numbers for each before a PR.
>
> Would you want this in slot at all? If yes, is extending Lid Power Off the right place, or would you
> rather keep sleep separate from power off?
