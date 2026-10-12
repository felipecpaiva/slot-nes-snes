use std::error::Error;
use std::path::PathBuf;
use std::process::ExitCode;
use std::time::Instant;

use slot::frames::Frames;
use slot_gfx::{Compositor, HeadlessSurface};
use slot_retro::{ButtonMask, LibretroCore, RetroCore};
use slot_store::Core;

const USAGE: &str =
    "usage: frontend_cost CORE DYLIB ROM [--frames N] [--repeats R] [--warmup W], CORE is mgba, gpsp, fceumm or snes9x";

struct Args {
    core: Core,
    dylib: PathBuf,
    rom: PathBuf,
    frames: u32,
    repeats: u32,
    warmup: u32,
}

fn number(it: &mut impl Iterator<Item = String>, flag: &str) -> Result<u32, String> {
    match it.next().map(|v| v.parse()) {
        Some(Ok(n)) if n > 0 => Ok(n),
        _ => Err(format!("{flag} takes a whole number above 0\n{USAGE}")),
    }
}

fn parse(mut it: impl Iterator<Item = String>) -> Result<Args, String> {
    let mut positional = Vec::new();
    let (mut frames, mut repeats, mut warmup) = (600, 5, 300);
    while let Some(arg) = it.next() {
        match arg.as_str() {
            "--frames" => frames = number(&mut it, &arg)?,
            "--repeats" => repeats = number(&mut it, &arg)?,
            "--warmup" => warmup = number(&mut it, &arg)?,
            s if s.starts_with('-') => return Err(USAGE.to_string()),
            _ => positional.push(arg),
        }
    }
    let [name, dylib, rom] = <[String; 3]>::try_from(positional).map_err(|_| USAGE.to_string())?;
    let core = Core::parse(&name).ok_or_else(|| format!("no core named {name}\n{USAGE}"))?;
    Ok(Args {
        core,
        dylib: dylib.into(),
        rom: rom.into(),
        frames,
        repeats,
        warmup,
    })
}

fn micros(began: Instant, frames: u32) -> f64 {
    began.elapsed().as_secs_f64() * 1e6 / f64::from(frames)
}

fn run_frames(core: &mut LibretroCore, frames: u32) -> f64 {
    let idle = ButtonMask::default();
    let began = Instant::now();
    for _ in 0..frames {
        core.run_frame(idle);
        core.take_audio();
    }
    micros(began, frames)
}

fn run(a: &Args) -> Result<(), Box<dyn Error>> {
    let (w, h) = a.core.canvas();
    let system = a.dylib.parent().map(PathBuf::from).unwrap_or_default();
    let mut core = LibretroCore::open_with(&a.dylib, &system, &std::env::temp_dir())?;
    core.set_canvas(w, h);
    core.load(&a.rom)?;
    let idle = ButtonMask::default();
    for _ in 0..a.warmup {
        core.run_frame(idle);
    }
    let start = core.serialize()?;

    let surface = HeadlessSurface::new().map_err(|e| format!("headless GL: {e:?}"))?;
    let mut compositor = Compositor::new(&surface).map_err(|e| format!("compositor: {e:?}"))?;
    compositor.set_game_canvas(w, h);
    let frames = Frames::new(w as usize * h as usize * 4);

    let (mut full_best, mut bare_best) = (f64::MAX, f64::MAX);
    let (mut publish, mut upload) = (f64::MAX, f64::MAX);
    for _ in 0..a.repeats {
        core.unserialize(&start)?;
        let full = run_frames(&mut core, a.frames);
        core.unserialize(&start)?;
        core.set_canvas(1, 1);
        let bare = run_frames(&mut core, a.frames);
        core.set_canvas(w, h);
        full_best = full_best.min(full);
        bare_best = bare_best.min(bare);

        core.unserialize(&start)?;
        let (mut published, mut uploaded) = (0.0, 0.0);
        for _ in 0..a.frames {
            core.run_frame(idle);
            core.take_audio();
            let began = Instant::now();
            let mut buf = frames.take_write();
            buf.clear();
            buf.extend_from_slice(core.video_xrgb8888());
            frames.publish(buf);
            published += began.elapsed().as_secs_f64();
            let began = Instant::now();
            let frame = frames.latest().ok_or("no frame was published")?;
            compositor.upload_game(&frame);
            uploaded += began.elapsed().as_secs_f64();
        }
        publish = publish.min(published * 1e6 / f64::from(a.frames));
        upload = upload.min(uploaded * 1e6 / f64::from(a.frames));
    }
    let convert = (full_best - bare_best).max(0.0);
    println!(
        "frontend_cost {} convert {convert:.3} publish {publish:.3} upload {upload:.3} total {:.3} canvas {w}x{h}",
        a.core.as_str(),
        convert + publish + upload
    );
    Ok(())
}

fn main() -> ExitCode {
    let args = match parse(std::env::args().skip(1)) {
        Ok(a) => a,
        Err(e) => {
            eprintln!("{e}");
            return ExitCode::from(2);
        }
    };
    match run(&args) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("frontend_cost: {e}");
            ExitCode::FAILURE
        }
    }
}
