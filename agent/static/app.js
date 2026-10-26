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
let last = null;

function centroid(touches) {
  let x = 0, y = 0;
  for (const t of touches) { x += t.clientX; y += t.clientY; }
  return { x: x / touches.length, y: y / touches.length };
}

pad.addEventListener("touchstart", (ev) => {
  ev.preventDefault();
  last = centroid(ev.touches);
}, { passive: false });

pad.addEventListener("touchmove", (ev) => {
  ev.preventDefault();
  const c = centroid(ev.touches);
  send({ t: "move", dx: Math.round((c.x - last.x) * SENS), dy: Math.round((c.y - last.y) * SENS) });
  last = c;
}, { passive: false });

pad.addEventListener("touchend", (ev) => {
  ev.preventDefault();
  if (ev.touches.length > 0) last = centroid(ev.touches); // a finger lifted, others remain
}, { passive: false });