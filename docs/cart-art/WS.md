# WonderSwan carts (WonderSwan and WonderSwan Color)

Two shells on one `Games/WS` shelf, drawn by the retro bitmap renderer (ADR 0054), patch 0069
(issue 98). Same rules as [VARIANTS.md](VARIANTS.md): every value cites a source; nothing is guessed.

| Value | Used | Source |
|---|---|---|
| Shell size | 66 x 41 mm, seated box 240 x 149 (cart box 360 x 224) | nelynes/slotPlus [77fd357](https://github.com/nelynes/slotPlus/commit/77fd357) `cart.rs` ("a 66 x 41 mm shell"). ConsoleMods' dimensions page sits behind a bot check and could not be read on 2026-10-19 |
| WonderSwan plastic | `1e1e21`, solid (black) | nelynes/slotPlus [21cc4b0](https://github.com/nelynes/slotPlus/commit/21cc4b0) `WS_MONO_SHELL` |
| WonderSwan Color plastic | `3a3a40`, translucent (frosted smoke-clear, the board shows through) | nelynes/slotPlus 21cc4b0 `WS_SHELL` |
| Which shell | The footer colour flag (16 bytes from the end, byte 7); the extension (`.wsc` clear, `.ws` black) when the footer cannot be read | Footer layout: Beetle Cygne `4b01295` and docs/research/wswan-plan.md section 2; extension rule: nelynes 21cc4b0 |
| Outline and nameplate | `crates/slot-ui/assets/ws_cart.svg` and `ws_cart_detail.svg`: a wide body with an oval nameplate on top and the connector step below | Our own drawing, with nelynes 77fd357's `ws_cart.svg` as the reference for the proportions (GPL-3.0, credited in the patch) |
| Labels | ScreenScraper `support-texture`, system id 45 (WonderSwan) or 46 (Color) by the footer flag; dats `Bandai - WonderSwan` and `Bandai - WonderSwan Color` | Skyscraper `platforms_idmap.csv` at ccd49ae; libretro-database `metadat/no-intro` |

Not done: no per-title plastic (WonderSwan Color games also came in coloured shells; no cited list
yet), no `Config/cart_shell.txt` outline word for the two shells (a colour line still applies).
