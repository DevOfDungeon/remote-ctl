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