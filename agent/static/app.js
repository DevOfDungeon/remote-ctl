"use strict";
const pad = document.getElementById("pad");
const statusEl = document.getElementById("status");
let ws = null;
let ready = false;

function setStatus(text) { statusEl.textContent = text; }

function connect() {
  const token = localStorage.getItem("rc_token") || prompt("Token");
  if (!token) { setStatus("no token"); return; }
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/input`);
  ws.onopen = () => ws.send(token);
  ws.onmessage = (ev) => {
    if (ev.data === "ok") {
      localStorage.setItem("rc_token", token); // only remember it once it worked
      ready = true;
      setStatus("connected");
    }
  };
  ws.onclose = (ev) => {
    ready = false;
    if (ev.code === 4401) localStorage.removeItem("rc_token");
    setStatus("disconnected");
    setTimeout(connect, 1500);
  };
}

function send(msg) { if (ready) ws.send(JSON.stringify(msg)); }

connect();

// ---------- trackpad ----------
const SENS = 1.6;
const SCROLL_PX = 18;   // finger px per wheel notch
const TAP_MS = 350;
const TAP_SLOP = 15;
let last = null, startT = 0, startPos = null, moved = false, maxFingers = 0;

function centroid(touches) {
  let x = 0, y = 0;
  for (const t of touches) { x += t.clientX; y += t.clientY; }
  return { x: x / touches.length, y: y / touches.length };
}

pad.addEventListener("touchstart", (ev) => {
  ev.preventDefault();
  if (ev.touches.length === 1) { startT = Date.now(); moved = false; maxFingers = 0; }
  maxFingers = Math.max(maxFingers, ev.touches.length);
  last = startPos = centroid(ev.touches);
}, { passive: false });

pad.addEventListener("touchmove", (ev) => {
  ev.preventDefault();
  const c = centroid(ev.touches);
  if (Math.hypot(c.x - startPos.x, c.y - startPos.y) > TAP_SLOP) moved = true;
  const dx = c.x - last.x, dy = c.y - last.y;
  if (ev.touches.length >= 2) {
    send({ t: "scroll", dx: Math.round(dx / SCROLL_PX), dy: Math.round(dy / SCROLL_PX) });
  } else {
    send({ t: "move", dx: Math.round(dx * SENS), dy: Math.round(dy * SENS) });
  }
  last = c;
}, { passive: false });

pad.addEventListener("touchend", (ev) => {
  ev.preventDefault();
  if (ev.touches.length > 0) { last = centroid(ev.touches); return; }
  if (!moved && Date.now() - startT < TAP_MS) {
    send({ t: "click", b: maxFingers >= 2 ? "right" : "left" });
  }
}, { passive: false });

// ---------- key buttons (slides + keys panels) ----------
document.querySelectorAll("[data-key]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const mods = (btn.dataset.mods || "").split(",").filter(Boolean);
    send({ t: "key", k: btn.dataset.key, mods });
  });
});

// ---------- panel toggling ----------
document.querySelectorAll("[data-panel]").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".panel").forEach((p) => {
      p.hidden = p.id === btn.dataset.panel ? !p.hidden : true;
    });
  });
});

// ---------- text box ----------
const txt = document.getElementById("txt");
function sendText() {
  if (txt.value) send({ t: "text", s: txt.value });
  txt.value = "";
}
document.getElementById("sendtxt").addEventListener("click", sendText);
txt.addEventListener("keydown", (ev) => { if (ev.key === "Enter") sendText(); });