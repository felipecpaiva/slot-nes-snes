# Modular platforms: a design for upstream slot

Status: draft for discussion, nothing sent upstream yet. Decision record:
[ADR 0058](../adr/0058-propose-modular-platform-registry-upstream.md). Discussion draft:
[modular-discussion-draft.md](modular-discussion-draft.md).

Upstream citations are slot v1.7.0 (`SLOT_PIN`, 34ac380) in `build/slot-upstream/`; ours are the
patched tree `build/slot/` at 29fb26a (patches 0001 to 0029). Counts come from
[docs/UPSTREAM-TOUCHPOINTS.md](../UPSTREAM-TOUCHPOINTS.md).

## 1. Goal and non-goals

The maintainer asked for this, in his words: "open PRs to the main slot repo, not to introduce new
systems but the modular approach we are taking, so we can make it modular and extendable, so it
will be easy for the community to build modules for it as we are doing."

Goal: a short series of small upstream PRs. Once they land, a community module (our NES, SNES and
Sega, nelynes' WonderSwan and Lynx) is mostly new files, with near zero edits to files upstream
owns.

Non-goals:

- **No new systems upstream.** Brandon said so on slot#30. Every PR here adds zero platforms and
  zero cores, and each one should still be worth having if no fork ever uses it.
- **GBA, GB and GBC behaviour stays byte identical.** Same `slot.state` bytes, same files and
  folders, same menus, same frames (upstream's layout frame-hash tests, ADR 0045), same core
  options. Each PR proves this with upstream's own tests, left unedited wherever possible.
- **No runtime plugin loading and no new dependencies.** Cores already load at runtime
  (`crates/slot/src/core.rs:10-16`); platform behaviour stays compiled Rust. A distributed-slice
  crate (`linkme`, `inventory`) would give true zero-edit registration for a new dependency and
  link-time tricks on the device toolchain. Section 3.6 gets close enough without one.
- **Upstream-first fixes are a separate track** (ADR 0047): audio reopen (16 hunks), frame trace
  (6) and per-shelf memory (23) are excluded from every count below.

## 2. Today: where a new system touches upstream

Our 29 patches touch **41 upstream files in 262 hunks (1061 changed lines)**. Taking out the three
non-platform tracks leaves **217 hunks, 867 lines, in 37 files** that exist only because upstream
has no place to say "this is a platform". Each row of the touch-point map was assigned to exactly
one concern (one row, one bucket, so the buckets add up):

| Concern | Hunks | Lines | Main upstream sites (v1.7.0) |
|---|---:|---:|---|
| GBA-only gates (`!= Platform::Gba`) | 1 | 2 | `app.rs:1384`, `app.rs:3695`, `session.rs:496`, `core.rs:133` |
| Platform identity: enum, names, folders, extensions, scan | 18 | 70 | `platform.rs:4-42`, `scan.rs:20-35,65`, `root.rs:3-28`, `slot_state.rs:604-608` |
| Core enum, options, picker | 28 | 114 | `slot-store/src/core.rs:9-55`, `slot/src/core.rs:133-197`, `core_picker.rs:47-163` |
| Canvas, frame size, libretro AV env | 52 | 193 | `pipeline.rs:15-210`, `libretro.rs:212-691`, `mock.rs`, `emu.rs:154,946`, `video_mode.rs:43-55` |
| Video defaults and input policy | 19 | 75 | `gesture.rs:50-454`, `emu.rs:689`, `session.rs:473,501`, `video_mode.rs:48` |
| Cart art, labels, shells | 33 | 149 | `cart.rs:82-262`, `shell.rs:91`, `board.rs:232`, `shelf.rs:460,542`, `cart_shell.rs:12-60`, `label_cache.rs:23` |
| Shaders, Screen page, quick menu, bezels, per-system settings | 66 | 264 | `quick_menu.rs:42-404`, `slot_state.rs:210-600`, `toast.rs`, `lcd3x.rs`, `app.rs:847-982,1618-2237` |
| **Total (platform work)** | **217** | **867** | 37 files |

The worst file is `crates/slot/src/app.rs` (42 hunks, 226 lines), mostly arms in matches that
upstream writes once per platform: `(QuickRow::Shader, Platform::Gba) => QuickRow::GbaShader`
(`app.rs:847-855`), `Platform::Gba => &mut self.state.bezel_gba` (`app.rs:972-982`).

Upstream tests pin some of these literals, which is why we keep five named test sites
(ADR 0013, 0044, 0048, 0055):

- (b) `crates/slot-ui/tests/chrome.rs:42-47`, `label_band` matches every `Platform`.
- (e) `crates/slot/tests/gpsp.rs:224-227`, the colour-key match over every `Core`.
- (f) `crates/slot-store/tests/durability.rs`, the full `SlotState` literal.
- (g), (h) `crates/slot-ui/tests/quick_menu.rs:110-113,137-154`, Screen labels and opening rows.
- Not a site, a wall: `crates/slot-store/tests/platform.rs:11` pins `ALL == [Gba, Gb, Gbc]`.

What we already built: policy methods in own files (`build/slot/crates/slot-store/src/`
`platform_policy.rs:17-97`, `core_policy.rs:15-67`, `crates/slot/src/platform_video.rs:7-21`,
`core_options_policy.rs:26-55`), `Platform::SHELVES` beside an untouched `ALL`
(`platform_policy.rs:6-15`), a side struct for new libretro state (`slot-retro/src/canvas.rs:15-21`,
ADR 0009, 0015) and one payload variant per upstream enum (ADR 0027). This moves that seam upstream.

## 3. Target design

One idea: **every per-platform fact lives in one const struct, and upstream code asks the struct
instead of matching on the enum.** The struct has no `Default` and no optional "hook" methods, so
a module that forgets a field fails to compile. That keeps the guarantee our exhaustive matches
give today (patch 0001), and is the reason for a table over a trait with default methods.

### 3.1 `PlatformSpec` (slot-store)

```rust
// crates/slot-store/src/platform.rs
pub struct PlatformSpec {
    pub dir: &'static str,                    // Games/<dir>, Saves/<dir>, slot.state key (lowercased)
    pub name: &'static str,                   // "Game Boy Advance"
    pub screen_order: u8,                     // Screen page position
    pub extensions: &'static [&'static str],
    pub picture: (u32, u32),                  // native picture inside the canvas
    pub title: fn(&Path) -> Option<(String, String)>, // header title and code, None keeps the stem
    pub cores: &'static [Core],               // first is the default; two or more open the picker
    pub caps: Caps,
    pub play: PlayPolicy,
    pub screen_needs_carts: bool,             // section 3.5, false for upstream's three
}

pub struct Caps {
    pub link_cable: bool,      // session.rs:496
    pub runahead: &'static [Core], // app.rs:4457, which cores may run ahead here
    pub gb_palettes: bool,     // slot/src/core.rs:133
    pub colour_correction: bool,
    pub bezel: Bezel,          // app.rs:824, 950, 960
}

pub enum Bezel { Panel, Files, SameAs(Platform) }

pub struct PlayPolicy {
    pub shoulders_to_game: bool,      // app.rs:1384 slot_owns_the_shoulders
    pub xy_to_game: bool,             // ours: SNES, MD (platform_policy.rs:36)
    pub select_x_toggles_picture: bool, // ours: ADR 0007
    pub default_stretch: bool,        // ours: ADR 0022
    pub stretch_crops_height: bool,   // ours: ADR 0046
    pub follows_frame_width: bool,    // ours: ADR 0052
}

impl Platform {
    pub fn spec(self) -> &'static PlatformSpec {
        match self {
            Platform::Gba => &GBA,
            Platform::Gb => &GB,
            Platform::Gbc => &GBC,
        }
    }
    pub fn dir_name(self) -> &'static str { self.spec().dir }       // and so on, same API
}
```

`Platform::ALL` stays `[Gba, Gb, Gbc]`, so `tests/platform.rs:11` holds. A new
`Platform::SHELVES` (equal to `ALL` upstream) is what scan, shelves, recents parsing and folder
creation iterate. `#[default] Gba` stays. `platform_value` (`slot_state.rs:604-608`) keeps
parsing `dir_name()`, over `SHELVES`, so a card written by a fork with an unknown platform still
reads as "never said" on upstream (durability test, ADR 0012).

`root::DIRS` (`root.rs:3`, `[&str; 24]`) stays as it is: `boot.rs:254`, `dist.rs:11-26` and
`bios.rs:118-127` iterate it, and `dist.rs` pins the top-level set. `ensure()` also creates
`Games/`, `Labels/`, `Saves/` and `States/<dir>` for `SHELVES` entries outside `ALL`, all below
existing top-level folders, so upstream creates the same 24 and `dist.rs` holds for forks too.

### 3.2 Upstream's three platforms, expressed in it

```rust
const GBA: PlatformSpec = PlatformSpec {
    dir: "GBA", name: "Game Boy Advance", screen_order: 0,
    extensions: &["gba"], picture: (240, 160), title: gba::header_title_code,
    cores: &[Core::Mgba, Core::Gpsp],
    caps: Caps { link_cable: true, runahead: &[Core::Mgba], gb_palettes: false,
                 colour_correction: true, bezel: Bezel::Panel },
    play: PlayPolicy { shoulders_to_game: true, xy_to_game: false, select_x_toggles_picture: false,
                       default_stretch: false, stretch_crops_height: false, follows_frame_width: false },
    screen_needs_carts: false,
};
const GB: PlatformSpec = PlatformSpec {
    dir: "GB", name: "Game Boy", screen_order: 2,
    extensions: &["gb", "gbc"], picture: (160, 144), title: gb::title_only,
    cores: &[Core::Mgba],
    caps: Caps { link_cable: false, runahead: &[], gb_palettes: true,
                 colour_correction: true, bezel: Bezel::Files },
    play: PlayPolicy { shoulders_to_game: false, ..GBA.play }, screen_needs_carts: false,
};
const GBC: PlatformSpec = PlatformSpec { dir: "GBC", name: "Game Boy Color", screen_order: 1, ..GB };
```

Why each value is upstream's current behaviour:

| Field | Upstream today | Same result from the table |
|---|---|---|
| `cores` | `Core::runs`: mGBA everywhere, gpSP on GBA only (`slot-store/src/core.rs:44-49`); `default_for` mGBA (`:51-55`) | `runs(p) = p.spec().cores.contains(&self)`, `default_for = cores[0]` |
| picker | opens only on GBA (`app.rs:3695`) | opens when `cores.len() >= 2` |
| `link_cable` | `player.filter(\|_\| platform == Gba)` (`session.rs:496`) | `.filter(\|_\| platform.spec().caps.link_cable)` |
| `runahead` | `(Core::Mgba, Platform::Gba) => frames` (`app.rs:4457`) | `caps.runahead.contains(&core)` |
| `gb_palettes` | `platform != Gba && dmg_only(rom)` (`slot/src/core.rs:133`) | `caps.gb_palettes && dmg_only(rom)` |
| `bezel` | GBA lists no files and offers no Default (`app.rs:950,960`), hides the row when unframed (`:824`) | `Panel` versus `Files` |
| `shoulders_to_game` | slot takes L1 and R1 unless GBA (`app.rs:1384`) | `!shoulders_to_game` |
| `title` | GBA reads title and code, others `gb::title` (`scan.rs:20-35`) | a function per platform |
| `screen_order` | Screen lists GBA, GBC, GB (`quick_menu.rs:111-112`) while `ALL` is GBA, GB, GBC | explicit field; deriving from `ALL` would swap them and break `tests/quick_menu.rs:112` |

### 3.3 `CoreSpec` (slot-store)

```rust
pub struct CoreSpec {
    pub ini: &'static str,                  // selected_core.txt value, dylib stem "<ini>_libretro"
    pub text: &'static str,                 // "mGBA"
    pub option_prefix: &'static str,        // "<prefix>_frameskip"; snes9x2005_plus says "snes9x_2005"
    pub colour_key: Option<&'static str>,   // "mgba_color_correction"; None = no colour option
    pub fixed_options: &'static [(&'static str, &'static str)], // ours: core_options_policy.rs:18-24
    pub canvas: fn(Platform) -> (u32, u32), // ADR 0050: Genesis Plus GX is 240x160 on GG only
}
```

`Core::ALL` stays `[Mgba, Gpsp]` (`slot-store/tests/core.rs:203` pins its length). Our `Core::EVERY`
(`core_policy.rs:5-13`) becomes upstream's `Core::REGISTERED`. `as_str`, `text`, `parse` and
`dylib_name` read the spec. mGBA and gpSP get `canvas: |_| (240, 160)`, which is what the fixed
`SRC_W`/`SRC_H` constants say today.

### 3.4 Cart look (slot-ui)

Upstream already has the right shape inside `cart.rs`: a private `Spec { w, h, label, mask,
mould, paint }` chosen by `spec(shape_of(cart))` (`cart.rs:110-146`). Since v1.7.0 carts are
painted bitmaps with an `Overlay`, which is what our generated neutrals reuse (ADR 0054, 0056).
The proposal makes that per platform:

```rust
// crates/slot-ui/src/cart.rs
pub struct CartLook {
    pub shape: fn(&Cart) -> Spec,         // GB picks Notched or Rounded from the ROM class
    pub seated: (u32, u32),               // seated_box (cart.rs:150-156)
    pub shell: fn(&Cart) -> Shell,        // shell.rs:91-92, used when cart_shell.txt names no colour
    pub label_fit: LabelFit,              // Cover (upstream), Top (ours, NES/SNES), Contain (ours, SMS box art, ADR 0057)
    pub outlines: &'static [(&'static str, Outline)], // cart_shell.txt words this platform accepts
}
pub fn cart_look(p: Platform) -> &'static CartLook;
```

`gb_shell_of`, `seated_box`, `cart_box`, `label_size`, `cart_interior`, `shell_for`, `label_art`
(`label_cache.rs:23`) and the shelf's shadow and star (`shelf.rs:460,542`) all go through
`cart_look`. Label fetching (ScreenScraper, Cart Studio) stays outside slot.

### 3.5 Screen page, quick menu and per-system settings

The maintainer's rule: **every system gets its own Screen section, even when its shader list is
shared with another system.** Upstream already does this for GB and GBC: same `Shader::GB` list,
two pages (`quick_menu.rs:114-130`). So the Screen page is generated from `SHELVES`, sorted by
`screen_order`, one console row per platform, and each page's rows come from the platform's caps:

```rust
pub enum Setting { Shader, ColourCorrection, Palette, Bezel }

impl PlatformSpec {
    pub fn screen_settings(&self) -> &'static [Setting]; // GBA: Shader, ColourCorrection, Bezel
}                                                         // GB: Shader, ColourCorrection, Palettes, Bezel

pub enum QuickRow { /* upstream's non-platform rows unchanged */, System(Platform), Set(Platform, Setting) }

impl QuickRow {
    #[allow(non_upper_case_globals)]
    pub const ScreenGba: QuickRow = QuickRow::System(Platform::Gba);
    #[allow(non_upper_case_globals)]
    pub const GbaShader: QuickRow = QuickRow::Set(Platform::Gba, Setting::Shader);
    // ... one const per upstream variant name, so callers and tests keep compiling
}
```

`QuickRow` derives `PartialEq, Eq`, so the consts also work as match patterns. The consts need
`#[allow(non_upper_case_globals)]`, which upstream has nowhere today. So this is offered as one of
two options and Brandon picks: (a) the payload variants plus consts, as above; or (b) keep
upstream's named variants (`ScreenGba`, `GbaShader`, ...) exactly as they are and add only
`QuickRow::System(Platform)` and `QuickRow::Set(Platform, Setting)` for platforms outside the
three, with `page()` and `label()` delegating to the spec for those. Option (b) adds no `allow`
and touches fewer lines; it keeps upstream's three systems special-cased in the menu code.

Upstream's two pinned assertions need care:

- `QuickRow::SCREEN` stays a const `[QuickRow; 3]` with the same three rows, so
  `tests/quick_menu.rs:110-113` is unchanged. A new test asserts that the generated page equals
  `SCREEN` when no module is compiled in.
- `QuickRow::ALL` stays upstream's 40 rows, so the `opens` list (`:137-154`) is unchanged.
  Rows added by modules come from a separate `QuickRow::every()`, the pattern `Toast::every()`
  and `QuickValue::every()` already use in our patches (ADR 0027).

Per-system values: `SlotState` keeps its named GBA, GB and GBC fields (`slot_state.rs:210-229`),
with the same keys written in the same order (`:408-445`, including the appended
`colour_correction_gbc`), so `durability.rs` and every card on disk are untouched. A platform
outside the three stores its values in `Config/platform_settings.txt`, an `ini` file keyed
`<dir>.<setting>`. This is ADR 0051's `Config/sega_shaders.txt` made generic. App code reads all
of them through one accessor:

```rust
impl App {
    fn setting(&self, p: Platform, s: Setting) -> SettingValue; // GBA/GB/GBC: struct field; others: ini
    fn set_setting(&mut self, p: Platform, s: Setting, v: SettingValue);
}
```

That replaces the triple matches at `app.rs:847-855,972-982,1618-1636,2183-2185,2235-2237`.
Shader programs: upstream's `Shader` and `ScreenEffect` keep their variants and gain one payload
variant each, `Shader::Extra(u16)` and `ScreenEffect::Extra(u16)`, an index into a table of extra
GL programs (name, label, fragment source). Our `Retro(RetroShader)` (ADR 0027, 0028) is exactly
this already. `Shader::GBA` and `Shader::GB` stay consts.

Hiding: our rule that a system's Screen row is hidden on a card with no carts of it
(`build/slot/crates/slot/src/retro_quick.rs:79`) becomes the spec field `screen_needs_carts`,
false for upstream's three. Upstream's menus and frames stay as they are.

### 3.6 Where a module plugs in: one stub file per crate

With `Platform` an enum, a module still adds a variant and a `spec()` arm. That is one or two
lines, but they sit in upstream's `platform.rs`, and those lines are where our rebases hurt. Three
options:

| Option | Upstream edits per module | Cost |
|---|---|---|
| A. Enum variant plus table row | 1 variant and 1 arm in `platform.rs`, the same in `core.rs` and `cart.rs` | Conflicts on every rebase that touches those files |
| B. `Platform` as a newtype id over a static slice | 1 row in a slice | the three variants appear 419 times in 59 upstream files; matches lose exhaustiveness |
| C. **Extension stub:** `Platform::Ext(ExtPlatform)`, where upstream ships `pub enum ExtPlatform {}` in its own `ext.rs` | none to upstream logic; a fork edits only the stub file | Upstream carries an uninhabited enum and one `Ext(e) => e.spec()` arm per accessor |

```rust
// crates/slot-store/src/ext.rs, as upstream ships it
#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
pub enum ExtPlatform {}
impl ExtPlatform {
    pub const ALL: [ExtPlatform; 0] = [];
    pub fn spec(self) -> &'static PlatformSpec { match self {} }
}
```

An uninhabited enum costs nothing at runtime. A fork replaces `ext.rs` (and the slot-ui stub for
`cart_look`, and `ExtCore`) with its own lists; upstream never edits the stubs, so they never
conflict. Two honest limits. First, a payload variant breaks `self as usize`/`as u8` casts
(`slot-store/src/core.rs:26`, `scan.rs:103`, `app.rs:2697`, `quick_menu.rs:160`), so PRs 2, 3
and 7 replace them with a position lookup first. Second, the toolchain is Rust 1.96
(`rust-toolchain.toml`), which lets a match omit arms for an empty type, so upstream is never
forced to write `Ext(e) =>`. A new upstream match on `Platform` is then a compile error in the
fork, one arm to add at rebase: loud, and far smaller than today. The same holds for the
exhaustive matches in upstream tests (sites b and e), which only go away if upstream accepts the
rewordings offered in PRs 3 and 6. We recommend C as the last PR, dropped without harm if
Brandon would rather stop at A.

## 4. Incremental PR plan

Eight PRs, in order. Each adds no platform and no core, changes no behaviour, and is useful to
upstream on its own. "Removes" is the share of our 217 platform hunks that the PR makes
unnecessary, from a one-row-one-PR assignment of the touch-point map (straddling rows counted
once). "Residual" is what our patch set still adds to upstream files. Sizes are estimates.

| # | Title | Size | Removes (hunks / lines) | Residual for our 5 systems |
|---|---|---|---:|---|
| 1 | Name the GBA-only gates | S, ~40 lines | 1 / 2 | 0 |
| 2 | One platform table | M, ~150 | 18 / 70 | 5 variants and 5 arms (0 with PR 8) |
| 3 | One core table, picker from the platform's cores | M, ~200 | 28 / 114 | 5 variants and 5 arms (0 with PR 8) |
| 4 | Canvas and AV info from the core | L, ~350 | 52 / 193 | 0 |
| 5 | Play policy in the platform table | S, ~100 | 19 / 75 | 0 (values in our rows) |
| 6 | Cart look per platform | M, ~200 | 33 / 149 | 1 arm per platform (0 with PR 8) |
| 7 | Screen page and settings from the table | L, ~350 | 66 / 264 | 0 |
| 8 | Extension stubs | S, ~60 | the residual column above | 0 |
| | **Total** | | **217 / 867** | stubs, plus one arm per new upstream match (3.6) |

### PR 1. Name the GBA-only gates

- Scope: replace each `== Platform::Gba` or `!= Platform::Gba` that means a capability with a
  named method on `Platform`: `has_link_cable`, `opens_core_picker`, `slot_takes_shoulders`,
  `has_bezel_files`, `runs_ahead(core)`, `offers_gb_palettes`. Pure renaming, three-armed matches.
- Files: `slot-store/src/platform.rs`, `slot/src/app.rs` (5 sites), `session.rs:496`,
  `slot/src/core.rs:133`.
- Tests: none edited. Add `slot-store/tests/platform_caps.rs`, one assert per method per platform,
  written from the old conditions. `link_ui.rs`, `core_picker.rs`, `app.rs` tests prove behaviour.
- Risk: very low. Value alone: each GBA-only rule gets a name, so the reason is visible.

### PR 2. One platform table

- Scope: `PlatformSpec` with identity fields only (dir, name, screen_order, extensions, picture,
  title). `Platform::SHELVES`. `scan`, `shelves_of` (`app.rs:425`), `platform_value`
  (`slot_state.rs:604`) and `root::ensure` iterate `SHELVES`. `read_header` calls `spec().title`.
  The cart sort (`scan.rs:103`, `app.rs:2697`) uses `platform.position()` in place of `as u8`.
- Files: `platform.rs`, `scan.rs`, `slot_state.rs`, `root.rs`, `app.rs:425`.
- Tests: none edited. `tests/platform.rs` (`ALL`, dir names), `tests/scan.rs`, `durability.rs`
  hold as written. Add a table conformance test over `SHELVES`: unique dirs, no extension claimed
  by two platforms (GB and GBC share `gb`/`gbc` on purpose, listed as an allowed pair), non-empty
  names.
- Risk: low. `dir_name()` feeds persisted keys; the conformance test plus `durability.rs` cover it.
- Removes for us: 18 hunks (`platform.rs` 5, `root.rs` 5, `scan.rs` 3, store `lib.rs` 2,
  `slot_state.rs` 1, `app.rs` 1, `durability.rs` 1).

### PR 3. One core table, picker from the platform's cores

- Scope: `CoreSpec`, `Core::REGISTERED`, `index()` as a position lookup (`core.rs:25-27`),
  `runs`/`default_for` from `PlatformSpec.cores`, colour
  option keys and frameskip prefix from the spec (`slot/src/core.rs:175-197`), and `CorePicker`
  taking the two cores from the platform (`core_picker.rs:57-163`). A platform with one core never
  opens the picker, the gate N64 and PS1 also need (`docs/research/n64-feasibility.md`, item 2b).
- Files: `slot-store/src/core.rs`, `slot/src/core.rs`, `core_picker.rs`, `frontend.rs` (faces for
  every registered core), `app.rs:3695-3698`.
- Tests: `core_picker.rs`, `core_options.rs`, `slot-store/tests/core.rs` unedited. Optionally
  offer to reword `gpsp.rs:224-227` from a match into "the key of every other registered core";
  same assertion, and our site (e) disappears. If Brandon prefers the literal, it stays and it
  still compiles, since upstream adds no core.
- Risk: low to medium. `selected_core.txt` values are pinned by `ini`; the spec keeps `"mgba"`
  and `"gpsp"`.
- Removes for us: 28 hunks (`frontend.rs` 7, store `core.rs` 6, `core_picker.rs` 6, slot `core.rs`
  4, `app.rs` 2, `lib.rs` 2, `gpsp.rs` site e).

### PR 4. Canvas and AV info from the core

- Scope: the game texture, `u_src`, the libretro video buffer, the mock core and thumbnails take
  their size from `RetroCore::canvas()` (default 240x160) instead of `SRC_W`/`SRC_H`
  (`pipeline.rs:51-55,155,208`). The libretro host answers `SET_GEOMETRY` and
  `SET_SYSTEM_AV_INFO` into a side struct (our `HostExtra`, `canvas.rs:15-21`, ADR 0009: `Host`
  keeps its fields) and rebuilds the resampler on an AV change.
- Files: `slot-gfx/src/fbo.rs`, `pipeline.rs`, `slot-retro/src/core.rs`, `libretro.rs`, `mock.rs`,
  `slot/src/emu.rs`, `thumb.rs`, `video_mode.rs`, `frontend.rs`.
- Tests: none edited. The layout frame-hash tests must be byte identical (ADR 0045). Add the env
  tests we already have (`env_tests`, patch 0006) as an upstream test file.
- Risk: medium. One reviewed `unsafe` for GL texture reallocation (ADR 0019); every GBA frame
  runs through it, so `bench:compare` numbers come with the PR. Value alone: two libretro calls
  any core may make are handled, and 240x160 stops being an assumption in four crates.
- Removes for us: 52 hunks.

### PR 5. Play policy in the platform table

- Scope: add `PlayPolicy` (section 3.1). Upstream's three set `shoulders_to_game` as today and
  `false` for the rest. `Gestures` takes an "XY to game" and a "Select+X picture" flag at session
  start; both are off for upstream's three, so its chord table (`gesture.rs:454`) acts the same.
  `source_rect` and the default video mode read the policy.
- Files: `platform.rs`, `slot-input/src/gesture.rs`, `emu.rs`, `session.rs`, `video_mode.rs`.
- Tests: none edited. Add policy rows to the conformance test.
- Risk: low, every new branch is off for GBA, GB and GBC. Weakest value to upstream alone; if he
  declines it, we keep these 19 hunks. Removes for us: 19 hunks.

### PR 6. Cart look per platform

- Scope: make `Spec` public and choose it through `cart_look(platform)` (section 3.4). Shell
  colours, label fit and `cart_shell.txt` outline words come from the look.
- Files: `slot-ui/src/cart.rs`, `shell.rs`, `board.rs`, `shelf.rs`, `art.rs`,
  `slot-store/src/cart_shell.rs`, `slot/src/label_cache.rs`.
- Tests: `render_shelves.rs` and the other frame-hash tests unedited. `chrome.rs:42-47`
  (`label_band`) is an exhaustive match over `Platform`; offer to read the band from
  `cart_look(c.platform).shape(c).label` instead, same numbers, and our site (b) disappears.
- Risk: medium; shelf frames are hashed, which is the proof. Removes for us: 33 hunks.

### PR 7. Screen page and per-system settings from the table

- Scope: section 3.5. `QuickRow::System`/`Set` with named consts for every upstream variant,
  `QuickRow::index` (`quick_menu.rs:160`) as a position lookup like our `QuickValue` hunk, the
  Screen page generated from `SHELVES` by `screen_order`, `App::setting`/`set_setting`,
  `Config/platform_settings.txt` for platforms outside the three, `Shader::Extra` and
  `ScreenEffect::Extra`.
- Files: `slot-ui/src/quick_menu.rs`, `toast.rs`, `slot-store/src/slot_state.rs` (accessor only,
  no field or key changes), `slot-gfx/src/lcd3x.rs`, `pipeline.rs`, `slot/src/app.rs`,
  `frontend.rs`.
- Tests: `tests/quick_menu.rs` and `durability.rs` unedited (`SCREEN`, `ALL` and the `SlotState`
  fields keep their values). Add "generated Screen page equals `SCREEN`" and a
  `platform_settings.txt` round trip.
- Risk: highest of the series. `QuickRow` is a flat 40-variant enum used positionally. That is why
  it goes last, after the table has proved itself in PRs 2 to 6.
- Removes for us: 66 hunks, including named test sites (f), (g) and (h), which pin values this
  PR keeps.
- Our migration: NES and SNES shaders move from `slot.state` (`shader_nes`, `shader_snes`) to
  `platform_settings.txt`, read once from the old keys. Sega already lives outside (ADR 0051).

### PR 8. Extension stubs

- Scope: `ExtPlatform`, `ExtCore` and the slot-ui look stub (section 3.6), all uninhabited.
- Files: three new `ext.rs` files, one `Ext(e)` arm per accessor (casts already gone in 2, 3, 7).
- Tests: assert `ExtPlatform::ALL` is empty and `SHELVES == ALL`. Risk: very low, nothing is
  reachable. A convenience for forks, and we say so.

## 5. A community module afterwards

Our NES module after PR 8, as files we add (upstream files untouched except the stubs):

```text
crates/slot-store/src/ext.rs                 replaces the stub: ExtPlatform { Nes, Snes, Gg, Sms, Md }
crates/slot-store/src/platforms/nes.rs       PlatformSpec NES: "NES", ["nes"], 256x240, cores [Fceumm, Nestopia]
crates/slot-store/src/cores/fceumm.rs        CoreSpec: "fceumm", overscan options, canvas 360x240
crates/slot-ui/src/ext.rs                    cart_look for ExtPlatform
crates/slot-ui/src/looks/nes.rs              CartLook: neutrals, label well, Top fit, outline words "nes", "famicom"
crates/slot-gfx/src/extra_shaders.rs         Line, Pixel, Sharp, Scanlines, crt-pi, crt-1tap
crates/slot/tests/nes_*.rs                   our tests, as today
cores/fceumm/build.sh, licenses/             as today
```

The NES spec reads like this:

```rust
pub const NES: PlatformSpec = PlatformSpec {
    dir: "NES", name: "Nintendo Entertainment System", screen_order: 3,
    extensions: &["nes"], picture: (256, 240), title: |_| None,
    cores: &[Core::Ext(ExtCore::Fceumm), Core::Ext(ExtCore::Nestopia)],
    caps: Caps { link_cable: false, runahead: &[], gb_palettes: false,
                 colour_correction: false, bezel: Bezel::SameAs(Platform::Gba) },
    play: PlayPolicy { shoulders_to_game: false, xy_to_game: false, select_x_toggles_picture: false,
                       default_stretch: true, stretch_crops_height: true, follows_frame_width: false },
    screen_needs_carts: true,
};
```

Every value already exists in our policy files (`platform_policy.rs:17-97`,
`platform_video.rs:7-12`, `core_policy.rs:36-51`). The patch set would shrink from 217 platform
hunks in 37 upstream files to the three stub files and the non-platform track. Named sites
(f), (g), (h) go; (b) and (e) go only with the PR 3 and PR 6 rewordings (3.6). One gap: our Screen
row says "NES" while `name` is the full name, so PR 7 adds a `screen_label` field (upstream's
three repeat their name). A nelynes WonderSwan module looks the same, plus a rotation flag in
`PlayPolicy` by a small PR of its own.

Not covered, so a module cannot do it alone: PS1 needs `need_fullpath`, disk control and L2/R2
to the game (`docs/research/ps1-plan.md`), each a small PR into the PR 4 side struct when someone
builds it. `REWIND_BYTES` is a fixed 20 MiB (`slot/src/rewind.rs:3`); all our systems fit.

## 6. Collaboration

- **nelynes/slotPlus** (WonderSwan, Lynx, Game Gear on Gearsystem, rebased on v1.7.0) carries the
  same patch-on-upstream pain and gains the most. We share the design before posting and, if they
  agree, the post names them. Their rotation and pad remap become `PlayPolicy` fields.
- **savethefails/ezGBA-640x480** (SNES, same two cores), **bently0602** (PS1, SNES, a Cart Studio
  SNES renderer) and gmaster1998 (closed PR #76 put `Platform::Snes` straight into upstream's
  enums, the collision this design avoids): told once the shape is settled.
- **How Brandon works:** he rewrote and merged our lazy-shelf fix himself (3339c6f), credits many
  contributors in the v1.7.0 notes, and lands contributions by hand, closing the PRs. Our account
  also cannot open PRs on his repo (`CreatePullRequest` was refused). So step one is a discussion
  post ([draft](modular-discussion-draft.md), not posted) asking whether he wants this and in what
  form: PRs, a branch he rewrites, or this document alone. A no costs us nothing; our policy files
  already follow this shape.

## 7. Verification for each PR, on our side first

Each PR is first built as a patch on v1.7.0 with no NES, SNES or Sega code. It must pass
upstream's whole suite with no test edited (the PR 3 and PR 6 rewordings go as separate commits),
the layout frame-hash tests (ADR 0045), `bench:compare` on the RG34XXSP (GBA within 2%) and
`harness/downgrade.rs`. Then our 29 patches are rebased on top to measure the real removal.
