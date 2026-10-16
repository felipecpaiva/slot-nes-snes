use std::ffi::c_void;
use std::path::{Path, PathBuf};
use std::process::exit;
use std::time::{Duration, Instant};

use slot::app::{App, Phase};
use slot::audio::{AudioSink, StubSink, GBA_HZ};
use slot::frontend::Frontend;
use slot::label_cache;
use slot::session::Session;
use slot_gfx::{Compositor, HeadlessSurface, Surface, OUT_H, OUT_W};
use slot_input::{Btn, InputSource, Millis, RawEvent};
use slot_power::{Power, SimPlatform};
use slot_store::{Core, Platform, Shader};

const LEGS: [&str; 5] = ["H1", "H1G", "H2", "B1", "H3"];
const BEZEL_WINDOW: (u32, u32) = (640, 480);
const FRAMEBUFFERS: u32 = 512;
const GL_FRAMEBUFFER: u32 = 0x8D40;
const GL_PACK_ALIGNMENT: u32 = 0x0D05;
const GL_RGBA: u32 = 0x1908;
const GL_UNSIGNED_BYTE: u32 = 0x1401;
const FPS: f64 = 60.0;
const CLOCK: i64 = 1_790_784_000;
const SETTLE: u32 = 120;
const STEP_TIMEOUT: Duration = Duration::from_secs(2);
const CORE_TIMEOUT: Duration = Duration::from_secs(5);
const LABEL_TIMEOUT: Duration = Duration::from_secs(60);
const LOCK_AFTER: Duration = Duration::from_millis(23);
const LOCK_BEFORE: Duration = Duration::from_micros(24500);
const TICK_GAP: Duration = Duration::from_millis(22);

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
    fn locked(&self) -> bool {
        true
    }
    fn app(&self) -> &App;
    fn after(&mut self, leg: &str, frame: u64, running: bool);
    fn mark(&mut self, leg: &str, frame: u64);
    fn output(&mut self, _leg: &str, _frame: u64) {}
    fn rebuilding(&self) -> bool {
        false
    }
    fn flush(&mut self) {}
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

    fn locked(&self) -> bool {
        self.session.emu().is_some_and(|emu| emu.locked())
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

type IsFramebuffer = unsafe extern "C" fn(u32) -> u8;
type BindFramebuffer = unsafe extern "C" fn(u32, u32);
type PixelStorei = unsafe extern "C" fn(u32, i32);
type ReadPixels = unsafe extern "C" fn(i32, i32, i32, i32, u32, u32, *mut u8);

fn gl_fn<T: Copy>(surface: &HeadlessSurface, name: &str) -> T {
    let address = surface.proc_address(name);
    if address.is_null() {
        die(&format!("the GL loader has no {name}"));
    }
    // SAFETY: the address is the CGL OpenGL framework's own symbol for this name and T is its C signature.
    unsafe { std::mem::transmute_copy::<*const c_void, T>(&address) }
}

fn framebuffers(surface: &HeadlessSurface) -> Vec<u32> {
    let is_framebuffer: IsFramebuffer = gl_fn(surface, "glIsFramebuffer");
    // SAFETY: glIsFramebuffer takes any integer name and only reads GL state on the current context.
    (1..FRAMEBUFFERS)
        .filter(|id| unsafe { is_framebuffer(*id) } != 0)
        .collect()
}

struct CompositeRig {
    pending: Vec<(String, &'static str, Vec<u8>)>,
    frontend: Frontend,
    compositor: Compositor,
    surface: HeadlessSurface,
    window: (u32, u32),
    output_fbo: u32,
}

impl CompositeRig {
    fn boot(root: &Path, wait: bool, window: (u32, u32)) -> Self {
        let surface =
            HeadlessSurface::new().unwrap_or_else(|e| die(&format!("headless GL: {e:?}")));
        let mut compositor =
            Compositor::new(&surface).unwrap_or_else(|e| die(&format!("compositor: {e:?}")));
        if let Err(e) = compositor.set_panel_turn((window.1, window.0), false) {
            die(&format!("panel turn: {e:?}"));
        }
        let mut frontend = Frontend::boot_with(platform(root), sink());
        frontend.upload_faces(&mut compositor);
        frontend.upload_bezel(&mut compositor, window);
        frontend.drive_emulator();
        let before = framebuffers(&surface);
        compositor.fit(window);
        compositor.begin_frame(slot_gfx::Layout::Framed);
        compositor.end_frame(window);
        let made: Vec<u32> = framebuffers(&surface)
            .into_iter()
            .filter(|id| !before.contains(id))
            .collect();
        let [output_fbo] = made[..] else {
            die(&format!("expected one output framebuffer, found {made:?}"));
        };
        let mut rig = CompositeRig {
            pending: Vec::new(),
            frontend,
            compositor,
            surface,
            window,
            output_fbo,
        };
        if wait {
            rig.wait_for_labels(root);
        }
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
        eprintln!(
            "frame_dump: label rebuild took {} ms",
            began.elapsed().as_millis()
        );
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
        self.frontend.render(&mut self.compositor, self.window);
    }

    fn mark(&mut self, leg: &str, frame: u64) {
        let pixels = self.compositor.read_frame();
        self.pending
            .push((format!("{leg} {frame}"), "composite", pixels));
    }

    fn output(&mut self, leg: &str, frame: u64) {
        let (w, h) = self.window;
        let bind: BindFramebuffer = gl_fn(&self.surface, "glBindFramebuffer");
        let pack: PixelStorei = gl_fn(&self.surface, "glPixelStorei");
        let read: ReadPixels = gl_fn(&self.surface, "glReadPixels");
        let mut pixels = vec![0u8; w as usize * h as usize * 4];
        // SAFETY: the buffer holds w * h RGBA bytes, the GL context is current on this thread, and the output framebuffer is complete.
        unsafe {
            bind(GL_FRAMEBUFFER, self.output_fbo);
            pack(GL_PACK_ALIGNMENT, 1);
            read(
                0,
                0,
                w as i32,
                h as i32,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                pixels.as_mut_ptr(),
            );
        }
        self.pending
            .push((format!("{leg} {frame}"), "output", pixels));
    }

    fn flush(&mut self) {
        for (key, kind, pixels) in self.pending.drain(..) {
            println!("{key} {kind} {}", sha256(&pixels));
        }
    }

    fn rebuilding(&self) -> bool {
        self.frontend.rebuilding_labels()
    }
}

fn running(app: &App) -> bool {
    matches!(app.phase(), Phase::Playing { .. })
        && app.power_menu().is_none()
        && !app.game_menu_open()
        && app.in_game_menu().is_none()
        && !app.shutting_down()
}

fn playing(app: &App) -> bool {
    matches!(app.phase(), Phase::Playing { .. })
}

fn inserting(app: &App) -> bool {
    matches!(app.phase(), Phase::Inserting { .. })
}

fn ejecting(app: &App) -> bool {
    matches!(app.phase(), Phase::Ejecting { .. })
}

fn polaroids_open(app: &App) -> bool {
    matches!(app.phase(), Phase::Polaroids { .. })
}

fn palette_live(app: &App) -> bool {
    app.palette_live()
}

fn on_shelf(app: &App) -> bool {
    matches!(app.phase(), Phase::Shelf)
}

struct Run<R: Rig> {
    rig: R,
    root: PathBuf,
    leg: &'static str,
    core: Core,
    input: Scripted,
    frame: u64,
    base: u64,
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
                    if !self.rig.locked() {
                        // The emulator thread locks a variable time after the core is ready, and its
                        // 25 ms stall clock starts with the lock, so a late lock is ticked at once.
                        while !self.rig.locked() {
                            if began.elapsed() > CORE_TIMEOUT {
                                die("the emulator never locked after the core loaded");
                            }
                            std::thread::sleep(Duration::from_micros(500));
                        }
                    } else if began.elapsed() > LOCK_BEFORE {
                        late(&format!("slept too long to lock at frame {}", self.frame));
                    }
                }
            }
            let mut stepped = self.rig.step();
            // The composite rig cannot see the lock (frame_dump builds in the upstream tree, which
            // has no Frontend accessor for it). Since v1.7.0 the worker locks later after an
            // insert, so the first tick of a run is retried until it lands; a tick that misses the
            // lock is dropped by the worker's rate restart, so no extra frame runs.
            while !stepped && self.stepped.is_none() && began.elapsed() < CORE_TIMEOUT {
                std::thread::sleep(Duration::from_micros(500));
                stepped = self.rig.step();
            }
            if !stepped {
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
        self.rig.after(self.leg, self.frame - self.base, running);
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
        eprintln!("frame_dump: {} {} {what}", self.leg, self.frame - self.base);
        self.rig.mark(self.leg, self.frame - self.base);
    }

    fn output(&mut self) {
        self.rig.output(self.leg, self.frame - self.base);
    }

    fn must(&self, what: &str, holds: fn(&App) -> bool) {
        if !holds(self.rig.app()) {
            die(&format!("{} {}: expected {what}", self.leg, self.frame));
        }
    }

    fn chord(&mut self, held: Btn, pressed: Btn) {
        self.input.0.push(RawEvent::Down(held));
        self.wait(2);
        self.input.0.push(RawEvent::Down(pressed));
        self.wait(2);
        self.input.0.push(RawEvent::Up(pressed));
        self.input.0.push(RawEvent::Up(held));
        self.wait(6);
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

    fn enter(&mut self) {
        self.tap(Btn::A, 6);
        self.until("the insert to start", inserting);
        self.wait(8);
        self.must("the insert to be under way", inserting);
        self.mark("mid insert");
        self.until("the game to play", playing);
        if self.rig.app().core() != self.core {
            die(&format!(
                "{} {}: expected the {} core",
                self.leg,
                self.frame,
                self.core.as_str()
            ));
        }
        self.wait(SETTLE);
        self.mark("in game steady");
    }

    fn leave(&mut self) {
        self.input.0.push(RawEvent::Down(Btn::Menu));
        self.until("the eject to start", ejecting);
        self.wait(12);
        self.must("the eject to be under way", ejecting);
        self.mark("mid eject");
        self.input.0.push(RawEvent::Up(Btn::Menu));
        self.until("the shelf after the eject", on_shelf);
        self.wait(SETTLE);
        self.mark("after eject");
    }

    fn shaders(&mut self, count: usize) {
        let first = self.rig.app().screen_shader();
        let mut last = first;
        for _ in 0..count {
            self.chord(Btn::Select, Btn::A);
            let now = self.rig.app().screen_shader();
            if now == last {
                die(&format!(
                    "{} {}: the shader did not change",
                    self.leg, self.frame
                ));
            }
            last = now;
            self.mark("shader");
        }
        if last != first {
            die(&format!(
                "{} {}: the shaders did not cycle round",
                self.leg, self.frame
            ));
        }
    }

    fn picture(&mut self, owned: bool) {
        let start = self.rig.app().source_rect();
        self.tap(Btn::L1, 6);
        self.wait(6);
        let stretched = self.rig.app().source_rect();
        self.mark("l1 picture");
        self.tap(Btn::R1, 6);
        self.wait(6);
        let actual = self.rig.app().source_rect();
        self.mark("r1 picture");
        if owned && (stretched == actual || actual != start) {
            die(&format!(
                "{} {}: L1 and R1 did not change the picture",
                self.leg, self.frame
            ));
        }
    }

    fn adjustments(&mut self) {
        for _ in 0..3 {
            self.chord(Btn::Select, Btn::Right);
        }
        self.mark("blue light up");
        self.output();
        for _ in 0..3 {
            self.chord(Btn::Select, Btn::Left);
        }
    }

    fn buttons(&mut self) {
        self.tap(Btn::Start, 6);
        self.wait(10);
        self.mark("start");
        self.tap(Btn::Select, 6);
        self.wait(12);
        self.mark("select");
    }

    fn states(&mut self) {
        self.wait(2);
        self.chord(Btn::Select, Btn::R1);
        self.wait(10);
        self.mark("state saved");
        self.tap(Btn::Down, 6);
        self.tap(Btn::A, 6);
        self.wait(30);
        self.mark("after more input");
        self.chord(Btn::Select, Btn::L1);
        self.wait(10);
        self.mark("state loaded");
        self.chord(Btn::Select, Btn::R1);
        self.wait(10);
        self.mark("second state saved");
        self.thumbs();
        self.polaroids();
    }

    fn thumbs(&mut self) {
        let mut found = Vec::new();
        let mut dirs = vec![self.root.join("States")];
        while let Some(dir) = dirs.pop() {
            for entry in std::fs::read_dir(&dir).into_iter().flatten().flatten() {
                let path = entry.path();
                if path.is_dir() {
                    dirs.push(path);
                } else if path.extension().is_some_and(|e| e == "png") {
                    found.push(path);
                }
            }
        }
        found.sort();
        if found.is_empty() {
            die(&format!(
                "{} {}: no state thumbnail written",
                self.leg, self.frame
            ));
        }
        for (n, path) in found.iter().enumerate() {
            let bytes = std::fs::read(path).unwrap_or_default();
            if bytes.is_empty() {
                die(&format!(
                    "{} {}: empty thumbnail {}",
                    self.leg,
                    self.frame,
                    path.display()
                ));
            }
            println!(
                "{} {} thumb{n} {}",
                self.leg,
                self.frame - self.base,
                sha256(&bytes)
            );
        }
    }

    fn polaroids(&mut self) {
        self.tap(Btn::Menu, 3);
        self.wait(3);
        self.tap(Btn::Menu, 3);
        self.until("the polaroids to open", polaroids_open);
        self.wait(30);
        self.mark("polaroids");
        self.tap(Btn::B, 6);
        self.until("the polaroids to close", playing);
        self.wait(10);
    }

    fn in_game(&mut self, shaders: usize, owned: bool, frames: u32) {
        self.shaders(shaders);
        self.adjustments();
        self.picture(owned);
        self.buttons();
        self.drive(frames);
        self.mark("in game after input");
        self.states();
    }

    fn quick_menu(&mut self) {
        self.tap(Btn::Menu, 6);
        self.wait(60);
        self.mark("quick menu steady");
        self.open_screen(0);
        self.wait(20);
        self.mark("quick screen rows");
        self.tap(Btn::Right, 6);
        self.wait(10);
        self.mark("quick shader stepped");
        self.tap(Btn::Left, 6);
        self.wait(10);
        self.close_screen();
    }

    // v1.7.0 opens the quick menu on General; Screen is the next row and lists the platforms
    // (Game Boy Advance, Game Boy Color, Game Boy), each with its own page.
    fn open_screen(&mut self, platform: u32) {
        self.tap(Btn::Down, 6);
        self.wait(4);
        self.tap(Btn::A, 6);
        self.wait(10);
        for _ in 0..platform {
            self.tap(Btn::Down, 6);
            self.wait(4);
        }
        self.tap(Btn::A, 6);
        self.wait(10);
    }

    fn close_screen(&mut self) {
        self.tap(Btn::B, 6);
        self.tap(Btn::B, 6);
        self.tap(Btn::Menu, 6);
        self.wait(30);
    }

    fn screen_row(&mut self, platform: u32, downs: u32, what: &str) {
        self.tap(Btn::Menu, 6);
        self.wait(30);
        self.open_screen(platform);
        for _ in 0..downs {
            self.tap(Btn::Down, 6);
            self.wait(4);
        }
        self.tap(Btn::Right, 6);
        self.wait(10);
        self.mark(what);
        self.close_screen();
    }

    fn colour_visit(&mut self) {
        self.screen_row(0, 1, "colour correction on");
        self.must("GBA colour correction to be on", |a| a.colour_correction_for(Platform::Gba));
        self.enter();
        self.drive(60);
        self.mark("colour correction in game");
        self.leave();
    }

    fn palette_visit(&mut self) {
        self.tap(Btn::Right, 6);
        self.wait(SETTLE);
        self.mark("dmg cart selected");
        self.enter();
        self.must("the palette to be live", palette_live);
        for _ in 0..2 {
            self.chord(Btn::Select, Btn::R2);
            self.wait(10);
            self.mark("palette");
        }
        self.leave();
    }

    fn gba(&mut self) {
        self.wait(SETTLE);
        self.mark("shelf idle");
        self.gba_script();
    }

    fn gba_script(&mut self) {
        self.wait(SETTLE);
        self.mark("shelf settled");
        self.quick_menu();
        self.enter();
        self.in_game(Shader::GBA.len(), false, 600);
        self.leave();
        self.output();
        self.colour_visit();
    }

    fn shelves(&mut self, button: Btn, count: u32) {
        for _ in 0..count {
            self.tap(button, 6);
            self.wait(10);
        }
    }

    fn nes_then_gba(&mut self) {
        self.wait(SETTLE);
        self.mark("shelf idle");
        self.leg = "H3N";
        self.shelves(Btn::R1, 3);
        self.wait(SETTLE);
        self.mark("nes shelf idle");
        self.enter();
        self.drive(60);
        self.output();
        self.leave();
        self.shelves(Btn::L1, 3);
        self.wait(SETTLE);
        self.leg = "H3";
        self.core = core_of("H1");
        self.base = self.frame - u64::from(SETTLE);
        self.gba_script();
    }

    fn leg(&mut self) {
        match self.leg {
            "H1" | "H1G" => self.gba(),
            "H3" => self.nes_then_gba(),
            _ => self.gb_and_bezel(),
        }
    }

    fn gb_and_bezel(&mut self) {
        self.wait(SETTLE);
        self.mark("shelf idle");
        match self.leg {
            "H2" => {
                self.tap(Btn::R1, 6);
                self.wait(SETTLE);
                self.mark("gb shelf idle");
                self.enter();
                self.in_game(Shader::GB.len(), true, 300);
                self.leave();
                self.screen_row(2, 2, "gb palettes on");
                self.palette_visit();
                self.tap(Btn::R1, 6);
                self.wait(SETTLE);
                self.mark("gbc shelf idle");
                self.screen_row(1, 1, "colour correction on");
                self.must("GBC colour correction to be on", |a| a.colour_correction_for(Platform::Gbc));
                self.enter();
                self.in_game(Shader::GB.len(), true, 300);
                self.leave();
                self.output();
            }
            "B1" => {
                self.output();
                self.enter();
                self.adjustments();
                self.output();
                self.leave();
            }
            other => die(&format!("no script for leg {other}")),
        }
    }
}

fn run<R: Rig>(rig: R, root: &Path, leg: &'static str) {
    let mut run = Run {
        rig,
        root: root.into(),
        leg,
        core: core_of(leg),
        input: Scripted::default(),
        frame: 0,
        base: 0,
        stepped: None,
    };
    run.leg();
    run.rig.flush();
}

fn core_of(leg: &str) -> Core {
    match leg {
        "H1G" => Core::Gpsp,
        "H3" => Core::parse("fceumm")
            .unwrap_or_else(|| die("this tree has no fceumm core, H3 runs on the patched tree only")),
        _ => Core::Mgba,
    }
}

fn window_of(leg: &str) -> (u32, u32) {
    if leg == "B1" {
        BEZEL_WINDOW
    } else {
        (OUT_W, OUT_H)
    }
}

fn cold(root: &Path, wait: bool) {
    let mut run = Run {
        rig: CompositeRig::boot(root, wait, (OUT_W, OUT_H)),
        root: root.into(),
        leg: "COLD",
        core: Core::Mgba,
        input: Scripted::default(),
        frame: 0,
        base: 0,
        stepped: None,
    };
    let stale = label_cache::stale(root, run.rig.frontend.app().carts()).len();
    eprintln!("frame_dump: {stale} stale labels at the first frame");
    let began = Instant::now();
    let (mut rebuilt, mut settled) = (stale == 0, 0);
    while settled < SETTLE {
        if began.elapsed() > LABEL_TIMEOUT {
            die("the label rebuild never finished");
        }
        run.frame();
        run.rig.mark(run.leg, run.frame);
        run.rig.flush();
        rebuilt |= run.rig.rebuilding();
        if rebuilt && !run.rig.rebuilding() {
            settled += 1;
        }
    }
    eprintln!(
        "frame_dump: cold boot hashed {} frames in {} ms",
        run.frame,
        began.elapsed().as_millis()
    );
}

fn known(leg: &str) -> &'static str {
    match LEGS.iter().find(|known| **known == leg) {
        Some(known) => known,
        None => die(&format!(
            "unknown leg {leg}, the legs are {}",
            LEGS.join(" ")
        )),
    }
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
        ["core", leg, root] => run(CoreRig::boot(Path::new(root)), Path::new(root), known(leg)),
        ["composite", "--no-wait", root] => cold(Path::new(root), false),
        ["composite", "--wait", root] => cold(Path::new(root), true),
        ["composite", leg, root] => {
            let leg = known(leg);
            let rig = CompositeRig::boot(Path::new(root), true, window_of(leg));
            run(rig, Path::new(root), leg)
        }
        _ => {
            eprintln!(
                "usage: frame_dump (core|composite) LEG ROOT | frame_dump composite (--no-wait|--wait) ROOT | frame_dump warm ROOT"
            );
            exit(2)
        }
    }
    exit(0)
}
