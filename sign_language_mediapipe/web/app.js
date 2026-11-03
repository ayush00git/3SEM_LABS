// Phone version: MediaPipe hand tracking, the classifier from /model.json, word building
// and speech, all in the browser. serve.py on the laptop only serves the files.
//
// handFeatures() must stay identical to common.py hand_features(), Classifier to
// common.py Classifier, and WordBuilder to live.py WordBuilder.

export const MP_VERSION = "1.1.1";
export const MP_URL = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${MP_VERSION}/vision_bundle.mjs`;
export const MP_WASM = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${MP_VERSION}/wasm`;
export const FEATURE_VERSION = "world_v1";
export const SMOOTH_FRAMES = 5;     // average the probabilities of the last 5 frames with a hand
export const NO_HAND_GAP = 0.8;     // seconds without a hand that finish the word
export const SENTENCE_WORDS = 8;    // keep the last 8 words
export const HAND_CONNECTIONS = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12], [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [0, 17], [17, 18], [18, 19], [19, 20]];

// ---------------------------------------------------------------- pure parts (tested)

/** 63 numbers describing the hand's shape (same as common.py hand_features): wrist at the
 * origin, left hands mirrored (x negated), scaled so the farthest point is 1 from the
 * wrist, flattened (x, y, z) x 21. `world` is 21 {x, y, z} points or 21 [x, y, z]. */
export function handFeatures(world, handedness) {
  if (!world || world.length !== 21) throw new Error("handFeatures needs 21 points");
  const p = world.map(q => Array.isArray(q) ? q : [q.x, q.y, q.z]);
  const out = new Float32Array(63);
  const [wx, wy, wz] = p[0];
  const flip = handedness === "Left" ? -1 : 1;
  let scale = 0;
  for (let i = 0; i < 21; i++) {
    const x = (p[i][0] - wx) * flip, y = p[i][1] - wy, z = p[i][2] - wz;
    out[3 * i] = x; out[3 * i + 1] = y; out[3 * i + 2] = z;
    scale = Math.max(scale, Math.hypot(x, y, z));
  }
  if (scale > 0) for (let i = 0; i < 63; i++) out[i] /= scale;
  return out;
}

/** MediaPipe sometimes flips Left/Right for a frame or two, which mirrors the features.
 * Score-weighted vote over the last 15 frames while the hand stays in view (same as
 * common.py HandTracker in video mode). add(name, score) returns the voted handedness;
 * reset() when no hand is detected. */
export class HandednessVote {
  constructor(n = 15) { this.n = n; this.votes = []; }
  add(name, score) {
    this.votes.push([name, score]);
    if (this.votes.length > this.n) this.votes.shift();
    let right = 0, left = 0;
    for (const [h, s] of this.votes) { if (h === "Right") right += s; else if (h === "Left") left += s; }
    return right >= left ? "Right" : "Left";
  }
  reset() { this.votes = []; }
}

/** The small network exported by train.py: standardise -> dense+ReLU ... -> dense+softmax. */
export class Classifier {
  constructor(m) {
    if (!m || m.feature_version !== FEATURE_VERSION)
      throw new Error("model.json was made with different features. Run train.py again on the laptop.");
    this.labels = m.labels;
    this.mean = Float32Array.from(m.mean);
    this.std = Float32Array.from(m.std);
    this.layers = m.layers.map(l => ({
      nIn: l.W.length, nOut: l.W[0].length,
      W: Float32Array.from(l.W.flat()),   // row-major (nIn x nOut), x @ W
      b: Float32Array.from(l.b),
    }));
    if (this.mean.length !== 63 || this.layers[0].nIn !== 63 ||
        this.layers[this.layers.length - 1].nOut !== this.labels.length)
      throw new Error("model.json has unexpected sizes. Run train.py again on the laptop.");
  }

  predictProba(features) {
    let x = new Float32Array(63);
    for (let i = 0; i < 63; i++) x[i] = (features[i] - this.mean[i]) / this.std[i];
    this.layers.forEach((L, k) => {
      const y = new Float32Array(L.nOut);
      for (let j = 0; j < L.nOut; j++) {
        let s = L.b[j];
        for (let i = 0; i < L.nIn; i++) s += x[i] * L.W[i * L.nOut + j];
        y[j] = (k < this.layers.length - 1 && s < 0) ? 0 : s;
      }
      x = y;
    });
    let max = -Infinity;
    for (const v of x) max = Math.max(max, v);
    let sum = 0;
    const e = x.map(v => Math.exp(v - max));
    for (const v of e) sum += v;
    return e.map(v => v / sum);
  }
}

/** Turns per-frame probabilities into letters, words and a sentence (same rules as
 * live.py WordBuilder). update(probs | null, nowSeconds) returns events:
 * ["add", label] when a sign is appended, ["word", word] when a word is finished. */
export class WordBuilder {
  constructor(labels, threshold = 0.7, hold = 1.0) {
    this.labels = labels.slice();
    this.threshold = threshold;
    this.hold = hold;
    this.buffer = [];
    this.word = "";
    this.sentence = [];
    this.avg = null;
    this.label = null; this.conf = 0;
    this.candidate = null;
    this.holdStart = null;
    this.lastHand = null;
  }

  update(probs, now) {
    const events = [];
    let candidate;
    if (probs == null) {
      this.buffer = [];
      this.avg = null; this.label = null; this.conf = 0;
      candidate = null;
      if (this.lastHand !== null && now - this.lastHand >= NO_HAND_GAP && this.word) {
        const w = this.word.trim();
        events.push(["word", w]);
        this.sentence.push(w);
        this.sentence = this.sentence.slice(-SENTENCE_WORDS);
        this.word = "";
      }
    } else {
      this.lastHand = now;
      this.buffer.push(Float32Array.from(probs));
      if (this.buffer.length > SMOOTH_FRAMES) this.buffer.shift();
      const n = this.labels.length, avg = new Float32Array(n);
      for (const b of this.buffer) for (let i = 0; i < n; i++) avg[i] += b[i];
      for (let i = 0; i < n; i++) avg[i] /= this.buffer.length;
      this.avg = avg;
      let best = 0;
      for (let i = 1; i < n; i++) if (avg[i] > avg[best]) best = i;
      this.label = this.labels[best]; this.conf = avg[best];
      candidate = this.conf >= this.threshold ? this.label : null;
    }
    if (candidate !== this.candidate) {           // candidate changed: restart its hold timer
      this.candidate = candidate;
      this.holdStart = candidate !== null ? now : null;
    } else if (candidate !== null && now - this.holdStart >= this.hold) {
      this.append(candidate);
      events.push(["add", candidate]);
      this.holdStart = now;                        // holding longer repeats it
    }
    return events;
  }

  append(label) {
    if (label.length === 1) this.word += label;
    else this.word += (this.word === "" || this.word.endsWith(" ") ? "" : " ") + label + " ";
  }

  progress(now) {
    if (this.candidate === null) return 0;
    return this.hold > 0 ? Math.min(1, (now - this.holdStart) / this.hold) : 1;
  }

  top(n = 3) {
    if (!this.avg) return [];
    return [...this.avg].map((p, i) => [this.labels[i], p]).sort((a, b) => b[1] - a[1]).slice(0, n);
  }

  backspace() { this.word = this.word.slice(0, -1); }
  clear() { this.word = ""; this.sentence = []; }
}

// ---------------------------------------------------------------- loading

export async function loadMediaPipe() {
  try {
    return await import(MP_URL);
  } catch (e) {
    throw new Error("MediaPipe failed to load. The phone needs internet access (cdn.jsdelivr.net). " +
                    "Check the connection and reload. (" + (e.message || e) + ")");
  }
}

/** True when WebGL is a software renderer (SwiftShader/llvmpipe): the GPU delegate is then
 * much slower than the CPU one. */
export function softwareWebGL() {
  try {
    const gl = document.createElement("canvas").getContext("webgl2") || document.createElement("canvas").getContext("webgl");
    if (!gl) return true;
    const ext = gl.getExtension("WEBGL_debug_renderer_info");
    const r = String(ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER));
    return /swiftshader|llvmpipe|software|basic render/i.test(r);
  } catch (e) { return true; }
}

/** HandLandmarker from /hand_landmarker.task; tries the GPU and falls back to the CPU. */
export async function createLandmarker(mp, runningMode = "VIDEO", delegates = ["GPU", "CPU"]) {
  let fileset;
  try {
    fileset = await mp.FilesetResolver.forVisionTasks(MP_WASM);
  } catch (e) {
    throw new Error("MediaPipe failed to load its WebAssembly files. Check the internet connection and reload.");
  }
  let lastErr;
  for (const delegate of delegates) {
    try {
      const landmarker = await mp.HandLandmarker.createFromOptions(fileset, {
        baseOptions: { modelAssetPath: "/hand_landmarker.task", delegate },
        runningMode, numHands: 1,
        minHandDetectionConfidence: 0.5, minHandPresenceConfidence: 0.5, minTrackingConfidence: 0.5,
      });
      return { landmarker, delegate };
    } catch (e) {
      lastErr = e;
      console.warn("HandLandmarker with " + delegate + " failed:", e);
    }
  }
  throw new Error("MediaPipe hand tracker could not start: " + (lastErr && lastErr.message || lastErr));
}

export async function loadClassifier(url = "/model.json") {
  let r;
  try {
    r = await fetch(url, { cache: "no-store" });
  } catch (e) {
    throw new Error("Cannot reach the laptop. Is serve.py still running?");
  }
  if (r.status === 404) throw new Error("Train first: run train.py on the laptop, then reload this page.");
  if (!r.ok) throw new Error("Could not load model.json (HTTP " + r.status + ").");
  return new Classifier(await r.json());
}

// ---------------------------------------------------------------- the page

function main() {
  const $ = id => document.getElementById(id);
  const ui = {
    start: $("start"), startScreen: $("start-screen"), status: $("status"), error: $("error"),
    video: $("video"), canvas: $("view"), fps: $("fps"), pred: $("pred"), conf: $("conf"),
    bar: $("hold-bar"), top: $("top3"), word: $("word"), said: $("said"),
    voice: $("btn-voice"), flip: $("btn-flip"), back: $("btn-back"), clear: $("btn-clear"),
    delegate: $("delegate"), appError: $("app-error"),
  };
  const params = new URLSearchParams(location.search);
  const ctx = ui.canvas.getContext("2d");
  const state = { facing: "user", voice: true, fps: 0, frames: 0, delegate: null, running: false };
  window.__slr = state;   // for debugging / tests
  const vote = new HandednessVote();
  let stream = null, landmarker = null, clf = null, wb = null, wakeLock = null;
  let lastVideoTime = -1, lastTs = 0, lastTick = 0;

  // Before Start (or after tracking stops) errors show on the start screen; while running
  // they show as a banner over the app.
  const showError = msg => {
    const box = state.running ? ui.appError : ui.error;
    box.textContent = msg;
    box.hidden = false;
    if (!state.running) { ui.status.textContent = ""; ui.startScreen.hidden = false; }
    state.error = msg;
  };
  const setStatus = msg => { ui.status.textContent = msg; };

  // Start loading the heavy parts right away; Start only waits for them.
  const forced = params.get("delegate");
  const ready = Promise.allSettled([
    loadClassifier(),
    loadMediaPipe().then(mp => createLandmarker(mp, "VIDEO",
      forced ? [forced.toUpperCase()] : softwareWebGL() ? ["CPU"] : ["GPU", "CPU"])),
  ]);
  // Report every problem (train first + MediaPipe) at once, the model one first.
  const readyAll = ready.then(rs => {
    const bad = rs.filter(r => r.status === "rejected").map(r => r.reason.message || String(r.reason));
    if (bad.length) throw new Error(bad.join("\n\n"));
    return rs.map(r => r.value);
  });
  readyAll.then(([c, lm]) => {
    clf = c; landmarker = lm.landmarker; state.delegate = lm.delegate;
    ui.delegate.textContent = lm.delegate;
    wb = new WordBuilder(clf.labels);
    state.labels = clf.labels;
    if (!state.running) setStatus("Ready. Signs: " + clf.labels.join(", "));
  }).catch(e => showError(e.message));

  // ---- speech
  function say(text) {
    if (!state.voice || !text || !("speechSynthesis" in window)) return;
    try {
      const u = new SpeechSynthesisUtterance(text.toLowerCase().length > 1 ? text.toLowerCase() : text);
      u.rate = 1.0;
      speechSynthesis.speak(u);
    } catch (e) { /* no voice: keep going */ }
  }
  function unlockSpeech() {
    // iOS only speaks after speak() was called inside a tap.
    try {
      if ("speechSynthesis" in window) {
        const u = new SpeechSynthesisUtterance(" ");
        u.volume = 0;
        speechSynthesis.speak(u);
      }
    } catch (e) { /* ignore */ }
  }

  // ---- wake lock
  async function keepAwake() {
    try {
      if ("wakeLock" in navigator && document.visibilityState === "visible")
        wakeLock = await navigator.wakeLock.request("screen");
    } catch (e) { /* not allowed (e.g. battery saver): fine */ }
  }
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && state.running) keepAwake();
  });

  // ---- camera
  async function startCamera() {
    if (stream) stream.getTracks().forEach(t => t.stop());
    stream = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: state.facing, width: { ideal: 640 }, height: { ideal: 480 } },
      });
    } catch (e) {
      if (e.name === "NotAllowedError" || e.name === "SecurityError")
        throw new Error("Camera access was denied. Allow the camera for this site in the browser's " +
                        "site settings (the icon next to the address), then reload.");
      if (e.name === "NotFoundError" || e.name === "OverconstrainedError")
        throw new Error("No camera found" + (state.facing === "environment" ? " on the back." : "."));
      if (e.name === "NotReadableError")
        throw new Error("The camera is busy. Close other apps that use it, then reload.");
      throw new Error("Could not open the camera: " + (e.message || e.name));
    }
    ui.video.srcObject = stream;
    await ui.video.play();
    lastVideoTime = -1;
    vote.reset();
  }

  // ---- per frame
  function drawHand(lm, w, h, mirror) {
    const pts = lm.map(p => [(mirror ? 1 - p.x : p.x) * w, p.y * h]);
    ctx.lineWidth = Math.max(2, w / 160);
    ctx.strokeStyle = "#3ddc84";
    ctx.beginPath();
    for (const [a, b] of HAND_CONNECTIONS) { ctx.moveTo(...pts[a]); ctx.lineTo(...pts[b]); }
    ctx.stroke();
    ctx.fillStyle = "#ffffff";
    const r = Math.max(3, w / 130);
    for (const [x, y] of pts) { ctx.beginPath(); ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.fill(); }
  }

  function render(now) {
    const p = wb.progress(now);
    ui.bar.style.width = (p * 100).toFixed(0) + "%";
    if (wb.label === null) {
      ui.pred.textContent = "show your hand"; ui.pred.className = "pred dim"; ui.conf.textContent = "";
    } else if (wb.candidate === null) {
      ui.pred.textContent = "unsure"; ui.pred.className = "pred dim";
      ui.conf.textContent = wb.label + " " + Math.round(wb.conf * 100) + "%";
    } else {
      ui.pred.textContent = wb.label; ui.pred.className = "pred";
      ui.conf.textContent = Math.round(wb.conf * 100) + "%";
    }
    const top = wb.top(3);
    ui.top.innerHTML = "";
    for (const [label, prob] of top) {
      const row = document.createElement("div");
      row.className = "row";
      const name = document.createElement("span"); name.className = "name"; name.textContent = label;
      const track = document.createElement("span"); track.className = "track";
      const fill = document.createElement("span"); fill.className = "fill"; fill.style.width = (prob * 100).toFixed(1) + "%";
      track.appendChild(fill);
      const pct = document.createElement("span"); pct.className = "pct"; pct.textContent = Math.round(prob * 100) + "%";
      row.append(name, track, pct);
      ui.top.appendChild(row);
    }
    renderWord();
    ui.fps.textContent = state.fps.toFixed(0) + " FPS";
  }

  function renderWord() {
    ui.word.textContent = wb.word || " ";
    ui.word.classList.toggle("empty", !wb.word);
    const items = wb.sentence.slice().reverse();
    if (ui.said.dataset.v !== items.join("|")) {
      ui.said.dataset.v = items.join("|");
      ui.said.innerHTML = "";
      for (const w of items) {
        const li = document.createElement("li"); li.textContent = w; ui.said.appendChild(li);
      }
    }
    state.word = wb.word; state.said = wb.sentence.slice();
  }

  function processFrame() {
    const v = ui.video;
    if (!v.videoWidth || v.readyState < 2) return;
    if (v.currentTime === lastVideoTime) return;     // no new frame
    lastVideoTime = v.currentTime;
    const w = v.videoWidth, h = v.videoHeight;
    if (ui.canvas.width !== w || ui.canvas.height !== h) { ui.canvas.width = w; ui.canvas.height = h; }
    const mirror = state.facing === "user";
    ctx.save();
    if (mirror) { ctx.translate(w, 0); ctx.scale(-1, 1); }
    ctx.drawImage(v, 0, 0, w, h);
    ctx.restore();

    let ts = performance.now();
    if (ts <= lastTs) ts = lastTs + 1;               // timestamps must strictly increase
    lastTs = ts;
    // The unmirrored video goes to MediaPipe; only the display is mirrored.
    const result = landmarker.detectForVideo(v, ts);
    const now = ts / 1000;
    let probs = null;
    if (result.worldLandmarks && result.worldLandmarks.length) {
      const cat = result.handedness[0][0];
      const handed = vote.add(cat.categoryName, cat.score);
      state.handedness = handed;
      probs = clf.predictProba(handFeatures(result.worldLandmarks[0], handed));
      drawHand(result.landmarks[0], w, h, mirror);
    } else {
      vote.reset();
    }
    for (const [kind, text] of wb.update(probs, now)) say(text);

    const dt = (ts - lastTick) / 1000;
    if (lastTick && dt > 0) state.fps = state.fps === 0 ? 1 / dt : 0.9 * state.fps + 0.1 / dt;
    lastTick = ts;
    state.frames++;
    state.pred = wb.label; state.conf = wb.conf;
    render(now);
  }

  let loopGen = 0;
  function startLoop() {
    const gen = ++loopGen;
    const step = () => {
      if (!state.running || gen !== loopGen) return;   // stopped, or replaced after a camera flip
      try {
        processFrame();
      } catch (e) {
        state.running = false;
        showError("Tracking stopped: " + (e.message || e) + ". Reload the page.");
        return;
      }
      if ("requestVideoFrameCallback" in HTMLVideoElement.prototype) ui.video.requestVideoFrameCallback(step);
      else requestAnimationFrame(step);
    };
    step();
  }

  // ---- buttons
  ui.start.addEventListener("click", async () => {
    unlockSpeech();
    ui.error.hidden = true;
    if (!window.isSecureContext || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showError("The camera only works over HTTPS. Open the https://... address that serve.py printed " +
                "on the laptop (not http://).");
      return;
    }
    ui.start.disabled = true;
    setStatus("Starting camera...");
    try {
      await startCamera();
      setStatus("Loading hand tracker...");
      await readyAll;
    } catch (e) {
      ui.start.disabled = false;
      showError(e.message);
      return;
    }
    ui.startScreen.hidden = true;
    state.running = true;
    keepAwake();
    startLoop();
  });

  ui.voice.addEventListener("click", () => {
    state.voice = !state.voice;
    ui.voice.textContent = state.voice ? "🔊 Voice" : "🔇 Muted";
    ui.voice.setAttribute("aria-pressed", String(state.voice));
    if (!state.voice && "speechSynthesis" in window) speechSynthesis.cancel();
  });
  ui.flip.addEventListener("click", async () => {
    if (!state.running) return;
    const old = state.facing;
    state.facing = old === "user" ? "environment" : "user";
    try {
      await startCamera();
      startLoop();
    } catch (e) {
      state.facing = old;
      try { await startCamera(); startLoop(); } catch (e2) { /* keep the error below */ }
      showError(e.message);
      setTimeout(() => { ui.appError.hidden = true; }, 4000);
    }
  });
  ui.back.addEventListener("click", () => { if (wb) { wb.backspace(); renderWord(); } });
  ui.clear.addEventListener("click", () => { if (wb) { wb.clear(); renderWord(); } });
}

if (typeof document !== "undefined" && document.getElementById("start")) main();
