use std::path::Path;
use std::process::exit;

use slot::app::{App, Phase};
use slot::root::DIRS;
use slot_store::{read_slot_state, write_slot_state, Platform, SlotState};

const STEM: &str = "Mario";
const OURS: [&str; 5] = ["nes", "snes", "gg", "sms", "md"];

fn fail(dir: &Path, why: &str) -> ! {
    let _ = std::fs::remove_dir_all(dir);
    eprintln!("downgrade: {why}");
    exit(1);
}

fn gba_cart(root: &Path, stem: &str) {
    let mut rom = vec![0u8; 0x100];
    rom[0xa0..0xa0 + stem.len()].copy_from_slice(stem.to_uppercase().as_bytes());
    std::fs::write(root.join("Games/GBA").join(format!("{stem}.gba")), rom).expect("write cart");
}

fn main() {
    let dir = std::env::temp_dir().join(format!("slot-downgrade-{}", std::process::id()));
    std::fs::create_dir_all(&dir).expect("create root");
    for sub in DIRS {
        std::fs::create_dir_all(dir.join(sub)).expect("create content dir");
    }
    gba_cart(&dir, "Emerald");
    gba_cart(&dir, "Fusion");
    let mut rom = vec![0u8; 16 + 0x4000 + 0x2000];
    rom[..4].copy_from_slice(b"NES\x1a");
    std::fs::create_dir_all(dir.join("Games/NES")).expect("create NES dir");
    std::fs::write(dir.join("Games/NES/Mario.nes"), rom).expect("write nes cart");
    for ours in OURS {
        let state = SlotState {
            cart: Some(STEM.into()),
            cart_platform: Some(Platform::Gba),
            clock_set: true,
            ..Default::default()
        };
        write_slot_state(&dir, &state).expect("write slot.state");
        let file = dir.join("Config/slot.state");
        let text = std::fs::read_to_string(&file).expect("read slot.state");
        let patched = text.replace("cart_platform=gba", &format!("cart_platform={ours}"));
        if patched == text {
            fail(&dir, "slot.state has no cart_platform=gba line to rewrite");
        }
        std::fs::write(&file, patched).expect("write slot.state");
        if read_slot_state(&dir).cart_platform.is_some() {
            fail(
                &dir,
                &format!("upstream read cart_platform={ours} as a platform"),
            );
        }
        let app = App::boot(&dir);
        if !matches!(app.phase(), Phase::Shelf) {
            fail(
                &dir,
                &format!(
                    "cart_platform={ours}: the phase is {:?}, not the shelf",
                    app.phase()
                ),
            );
        }
        if app.seated_cart().is_some() {
            fail(&dir, &format!("cart_platform={ours}: a cart is seated"));
        }
        println!("downgrade: ok, cart_platform={ours} boots to the shelf with no panic");
    }
    let _ = std::fs::remove_dir_all(&dir);
}
