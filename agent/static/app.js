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

const SENS = 1.6;
const TAP_MS = 250;
const TAP_SLOP = 8; // px of travel still counted as a tap
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
  last = startPos = centroid(ev.touches)
}, { passive: false });

pad.addEventListener("touchmove", (ev) => {
  ev.preventDefault();
  const c = centroid(ev.touches);
  if (Math.hypot(c.x - startPos.x, c.y - startPos.y) > TAP_SLOP) moved = true;
  const SCROLL_PX = 18;
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
  const dur = Date.now() - startT;
  if (!moved && dur < TAP_MS) {
    send({ t: "click", b: maxFingers >= 2 ? "right" : "left" });
  }
}, { passive: false });