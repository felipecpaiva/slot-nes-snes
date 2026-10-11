use std::path::Path;
use std::process::exit;
use std::time::{Duration, Instant};

use slot::app::{App, Phase};
use slot::audio::{AudioSink, StubSink, GBA_HZ};
use slot::frontend::Frontend;
use slot::label_cache;
use slot::session::Session;
use slot_gfx::{Compositor, HeadlessSurface};
use slot_input::{Btn, InputSource, Millis, RawEvent};
use slot_power::{Power, SimPlatform};

const FPS: f64 = 60.0;
const CLOCK: i64 = 1_790_784_000;
const SETTLE: u32 = 120;
const STEP_TIMEOUT: Duration = Duration::from_secs(2);
const CORE_TIMEOUT: Duration = Duration::from_secs(5);
const LABEL_TIMEOUT: Duration = Duration::from_secs(60);
const LOCK_AFTER: Duration = Duration::from_millis(23);
const LOCK_BEFORE: Duration = Duration::from_micros(24500);
const TICK_GAP: Duration = Duration::from_millis(15);

fn die(why: &str) -> ! {
    eprintln!("frame_dump: {why}");
    exit(1)
}

fn late(why: &str) -> ! {
    eprintln!("frame_dump: late: {why}, rerun on an idle machine");
    exit(3)
}

struct Sha256 {
    k: Vec<u32>,
    h: [u32; 8],
}

impl Sha256 {
    fn new() -> Self {
        let primes: Vec<u64> = (2u64..)
            .filter(|n| (2..*n).take_while(|d| d * d <= *n).all(|d| n % d != 0))
            .take(64)
            .collect();
        let part = |x: f64| (x.fract() * 4_294_967_296.0) as u32;
        let mut h = [0u32; 8];
        for (slot, p) in h.iter_mut().zip(&primes) {
            *slot = part((*p as f64).sqrt());
        }
        Sha256 {
            k: primes.iter().map(|p| part((*p as f64).cbrt())).collect(),
            h,
        }
    }

    fn block(&mut self, chunk: &[u8]) {
        let mut w = [0u32; 64];
        for (i, word) in chunk.chunks_exact(4).enumerate() {
            w[i] = u32::from_be_bytes([word[0], word[1], word[2], word[3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let mut v = self.h;
        for (k, wi) in self.k.iter().zip(w) {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7]
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(*k)
                .wrapping_add(wi);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(maj);
            v = [
                t1.wrapping_add(t2),
                v[0],
                v[1],
                v[2],
                v[3].wrapping_add(t1),
                v[4],
                v[5],
                v[6],
            ];
        }
        for (h, v) in self.h.iter_mut().zip(v) {
            *h = h.wrapping_add(v);
        }
    }

    fn hex(mut self, data: &[u8]) -> String {
        let mut whole = data.chunks_exact(64);
        for chunk in &mut whole {
            self.block(chunk);
        }
        let mut tail = whole.remainder().to_vec();
        tail.push(0x80);
        while tail.len() % 64 != 56 {
            tail.push(0);
        }
        tail.extend_from_slice(&((data.len() as u64) * 8).to_be_bytes());
        for chunk in tail.chunks_exact(64) {
            self.block(chunk);
        }
        self.h.iter().map(|h| format!("{h:08x}")).collect()
    }
}

fn sha256(data: &[u8]) -> String {
    Sha256::new().hex(data)
}

#[derive(Default)]
struct Scripted(Vec<RawEvent>);

impl InputSource for Scripted {
    fn poll(&mut self, _now: Millis) -> Vec<RawEvent> {
        std::mem::take(&mut self.0)
    }
}

trait Rig {
    fn settling(&self) -> bool;
    fn advance(&mut self, input: &mut Scripted, now: Millis);
    fn step(&self) -> bool;
    fn app(&self) -> &App;
    fn after(&mut self, leg: &str, frame: u64, running: bool);
    fn mark(&mut self, leg: &str, frame: u64);
}

const DT: f32 = (1.0 / FPS) as f32;

fn present() -> Duration {
    Duration::from_secs_f64(1.0 / FPS)
}

fn sink() -> Box<dyn AudioSink> {
    let mut sink = StubSink::draining();
    if let Err(e) = sink.open(GBA_HZ) {
        die(&format!("audio: {e}"));
    }
    Box::new(sink)
}

fn platform(root: &Path) -> Box<SimPlatform> {
    Box::new(SimPlatform::at(root.into()).stopped_at(CLOCK))
}

struct CoreRig {
    session: Session,
    seen: u64,
}

impl CoreRig {
    fn boot(root: &Path) -> Self {
        let mut session = Session::boot_with(root.into(), sink());
        session
            .app_mut()
            .set_power(Power::new(platform(root), Duration::from_secs(180)));
        session.set_driven(true);
        CoreRig { session, seen: 0 }
    }
}

impl Rig for CoreRig {
    fn settling(&self) -> bool {
        self.session.core_settling()
    }

    fn advance(&mut self, input: &mut Scripted, now: Millis) {
        let events = input.poll(now);
        self.session.feed(events, now);
        self.session.update(DT);
    }

    fn step(&self) -> bool {
        self.session.step_emulator(present(), STEP_TIMEOUT)
    }

    fn app(&self) -> &App {
        self.session.app()
    }

    fn after(&mut self, leg: &str, frame: u64, running: bool) {
        let published = self.session.frames_published();
        let fresh = published.saturating_sub(self.seen);
        self.seen = published;
        if fresh != u64::from(running) {
            late(&format!(
                "{fresh} core frames published at frame {frame}, expected {}",
                u64::from(running)
            ));
        }
        if running {
            let Some(pixels) = self.session.frame() else {
                late(&format!("no core frame to hash at frame {frame}"));
            };
            println!("{leg} {frame} core {}", sha256(&pixels));
        }
    }

    fn mark(&mut self, _leg: &str, _frame: u64) {}
}

struct CompositeRig {
    frontend: Frontend,
    compositor: Compositor,
    _surface: HeadlessSurface,
}

impl CompositeRig {
    fn boot(root: &Path) -> Self {
        let surface =
            HeadlessSurface::new().unwrap_or_else(|e| die(&format!("headless GL: {e:?}")));
        let mut compositor =
            Compositor::new(&surface).unwrap_or_else(|e| die(&format!("compositor: {e:?}")));
        let mut frontend = Frontend::boot_with(platform(root), sink());
        frontend.upload_faces(&mut compositor);
        frontend.drive_emulator();
        let mut rig = CompositeRig {
            frontend,
            compositor,
            _surface: surface,
        };
        rig.wait_for_labels(root);
        rig
    }

    fn wait_for_labels(&mut self, root: &Path) {
        let stale = label_cache::stale(root, self.frontend.app().carts()).len();
        if stale == 0 {
            return;
        }
        eprintln!("frame_dump: label cache is cold, {stale} labels to wait for");
        let began = Instant::now();
        while !self.frontend.rebuilding_labels() {
            if began.elapsed() > LABEL_TIMEOUT {
                die("the label rebuild never started");
            }
            self.frontend.compose(&mut self.compositor);
            std::thread::sleep(Duration::from_millis(2));
        }
        while self.frontend.rebuilding_labels() {
            if began.elapsed() > LABEL_TIMEOUT {
                die("the label rebuild never finished");
            }
            self.frontend.compose(&mut self.compositor);
            std::thread::sleep(Duration::from_millis(2));
        }
    }
}

impl Rig for CompositeRig {
    fn settling(&self) -> bool {
        self.frontend.core_settling()
    }

    fn advance(&mut self, input: &mut Scripted, now: Millis) {
        self.frontend.advance_at(input, now, DT);
    }

    fn step(&self) -> bool {
        self.frontend.step_emulator(present(), STEP_TIMEOUT)
    }

    fn app(&self) -> &App {
        self.frontend.app()
    }

    fn after(&mut self, _leg: &str, _frame: u64, _running: bool) {
        self.frontend.compose(&mut self.compositor);
    }

    fn mark(&mut self, leg: &str, frame: u64) {
        println!(
            "{leg} {frame} composite {}",
            sha256(&self.compositor.read_frame())
        );
    }
}

fn running(app: &App) -> bool {
    matches!(app.phase(), Phase::Playing { .. })
        && app.power_menu().is_none()
        && !app.game_menu_open()
        && !app.shutting_down()
}

fn playing(app: &App) -> bool {
    matches!(app.phase(), Phase::Playing { .. })
}

fn on_shelf(app: &App) -> bool {
    matches!(app.phase(), Phase::Shelf)
}

struct Run<R: Rig> {
    rig: R,
    leg: &'static str,
    input: Scripted,
    frame: u64,
    stepped: Option<Instant>,
}

impl<R: Rig> Run<R> {
    fn frame(&mut self) {
        let began = Instant::now();
        while self.rig.settling() {
            if began.elapsed() > CORE_TIMEOUT {
                die("the core never finished loading");
            }
            std::thread::sleep(Duration::from_millis(1));
        }
        let began = Instant::now();
        self.frame += 1;
        let now = (self.frame as f64 * 1000.0 / FPS) as Millis;
        self.rig.advance(&mut self.input, now);
        let running = running(self.rig.app());
        if running {
            match self.stepped {
                Some(last) if last.elapsed() > TICK_GAP => late(&format!(
                    "{} ms between emulator ticks at frame {}",
                    last.elapsed().as_millis(),
                    self.frame
                )),
                Some(_) => {}
                None => {
                    while began.elapsed() < LOCK_AFTER {
                        std::thread::sleep(Duration::from_micros(500));
                    }
                    if began.elapsed() > LOCK_BEFORE {
                        late(&format!("slept too long to lock at frame {}", self.frame));
                    }
                }
            }
            if !self.rig.step() {
                late(&format!(
                    "the emulator was not locked {} ms after the update at frame {}",
                    began.elapsed().as_millis(),
                    self.frame
                ));
            }
            self.stepped = Some(Instant::now());
        } else {
            self.stepped = None;
        }
        self.rig.after(self.leg, self.frame, running);
    }

    fn wait(&mut self, frames: u32) {
        for _ in 0..frames {
            self.frame();
        }
    }

    fn tap(&mut self, button: Btn, hold: u32) {
        self.input.0.push(RawEvent::Down(button));
        self.wait(hold);
        self.input.0.push(RawEvent::Up(button));
    }

    fn until(&mut self, what: &str, done: fn(&App) -> bool) {
        for _ in 0..1200 {
            if done(self.rig.app()) {
                return;
            }
            self.frame();
        }
        die(&format!("gave up waiting for {what}"));
    }

    fn mark(&mut self, what: &str) {
        eprintln!("frame_dump: {} {} {what}", self.leg, self.frame);
        self.rig.mark(self.leg, self.frame);
    }

    fn drive(&mut self, frames: u32) {
        for i in 0..frames {
            match i % 100 {
                10 => self.input.0.push(RawEvent::Down(Btn::Down)),
                40 => self.input.0.push(RawEvent::Down(Btn::A)),
                70 => self.input.0.push(RawEvent::Down(Btn::B)),
                90 => self.input.0.push(RawEvent::Down(Btn::Right)),
                14 => self.input.0.push(RawEvent::Up(Btn::Down)),
                44 => self.input.0.push(RawEvent::Up(Btn::A)),
                74 => self.input.0.push(RawEvent::Up(Btn::B)),
                94 => self.input.0.push(RawEvent::Up(Btn::Right)),
                _ => {}
            }
            if i == frames / 2 {
                self.mark("in game moving");
            }
            self.frame();
        }
    }

    fn visit(&mut self, frames: u32) {
        self.tap(Btn::A, 6);
        self.until("the game to play", playing);
        self.wait(SETTLE);
        self.mark("in game steady");
        self.drive(frames);
        self.mark("in game after input");
        self.tap(Btn::Menu, 70);
        self.until("the shelf after the eject", on_shelf);
        self.wait(SETTLE);
        self.mark("after eject");
    }

    fn leg(&mut self) {
        self.wait(SETTLE);
        self.mark("shelf idle");
        match self.leg {
            "H1" => {
                self.tap(Btn::Menu, 6);
                self.wait(60);
                self.mark("quick menu steady");
                self.tap(Btn::Menu, 6);
                self.wait(30);
                self.visit(600);
            }
            _ => {
                self.tap(Btn::R1, 6);
                self.wait(SETTLE);
                self.mark("gb shelf idle");
                self.visit(300);
                self.tap(Btn::R1, 6);
                self.wait(SETTLE);
                self.mark("gbc shelf idle");
                self.visit(300);
            }
        }
    }
}

fn run<R: Rig>(rig: R, leg: &'static str) {
    let mut run = Run {
        rig,
        leg,
        input: Scripted::default(),
        frame: 0,
        stepped: None,
    };
    run.leg();
}

fn warm(root: &Path) {
    let app = App::boot(root);
    let carts: Vec<_> = app.carts().cloned().collect();
    let cold = label_cache::stale(root, carts.iter()).len();
    for cart in &carts {
        let _ = label_cache::label_art(root, cart);
    }
    if !label_cache::stale(root, carts.iter()).is_empty() {
        die("the label cache is still cold after warming");
    }
    eprintln!("frame_dump: warmed {cold} of {} labels", carts.len());
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let args: Vec<&str> = args.iter().map(String::as_str).collect();
    match args.as_slice() {
        ["warm", root] => warm(Path::new(root)),
        ["core", "H1", root] => run(CoreRig::boot(Path::new(root)), "H1"),
        ["core", "H2", root] => run(CoreRig::boot(Path::new(root)), "H2"),
        ["composite", "H1", root] => run(CompositeRig::boot(Path::new(root)), "H1"),
        ["composite", "H2", root] => run(CompositeRig::boot(Path::new(root)), "H2"),
        _ => {
            eprintln!("usage: frame_dump (core|composite) (H1|H2) ROOT | frame_dump warm ROOT");
            exit(2)
        }
    }
    exit(0)
}
