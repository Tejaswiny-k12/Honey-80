import os
import random
from datetime import datetime
import requests
import socket
import threading
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, '../logs/honeypot.log'))
PRED_URL = "http://127.0.0.1:8000/predict_text"

responses = {
    "hello": ["Hi there!", "Hello!", "Hey!"],
    "how are you": ["I'm just a bot, but I'm doing great!", "I'm fine, thank you!"],
    "what is your name": ["You can call me hiGPT.", "I'm hiGPT, your friendly chatbot."],
    "bye": ["Goodbye!", "See you later!"],
    "default": ["Sorry, I didn't understand that.", "Could you please rephrase that?"]
}

def log_command(ip, command):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"IP: {ip} | Command: {command}\n")

def execute_in_docker_terminal(command, user_ip):
    """Connect to Docker container and execute command"""
    HOST = "127.0.0.1"  # Docker container mapped to localhost
    PORT = 4444
    
    try:
        # Create socket connection to Docker container
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.settimeout(10)  # 10 second timeout
        soc.connect((HOST, PORT))
        
        # Send command to Docker container
        command_with_newline = command + "\n"
        soc.sendall(command_with_newline.encode())
        
        # Wait a bit for command execution
        time.sleep(1)
        
        # Try to read response
        response = ""
        soc.settimeout(2)  # Short timeout for reading
        try:
            while True:
                data = soc.recv(4096)
                if not data:
                    break
                response += data.decode('utf-8', errors='ignore')
                # Break if we get a reasonable amount of data
                if len(response) > 1024:
                    break
        except socket.timeout:
            pass  # Expected - command might still be running
        
        soc.close()
        
        # Log the terminal access attempt
        log_command(user_ip, f"TERMINAL_ACCESS: {command}")
        
        # Clean up the response - remove bash warnings, prompts, and unwanted messages
        cleaned_response = response
        if cleaned_response:
            # Remove common bash warnings and shell prompts
            lines_to_remove = [
                "bash: cannot set terminal process group",
                "bash: no job control in this shell",
                "Inappropriate ioctl for device"
            ]
            
            lines = cleaned_response.split('\n')
            cleaned_lines = []
            for line in lines:
                # Skip lines containing unwanted messages
                if not any(unwanted in line for unwanted in lines_to_remove):
                    # Remove shell prompts (anything that looks like root@container:/path#)
                    import re
                    # Remove lines that are just prompts
                    if re.match(r'^root@[a-zA-Z0-9]+:[^#]*#\s*$', line.strip()):
                        continue
                    # Remove prompt from beginning of lines that have content after the prompt
                    line = re.sub(r'^root@[a-zA-Z0-9]+:[^#]*#\s*', '', line)
                    # Skip empty lines
                    if line.strip():
                        cleaned_lines.append(line.strip())
            
            cleaned_response = '\n'.join(cleaned_lines).strip()
        
        return {
            "success": True,
            "output": cleaned_response if cleaned_response else "Command executed (no output)",
            "message": f"Executed in Docker terminal: {command}"
        }
        
    except Exception as e:
        # Log failed connection attempt
        log_command(user_ip, f"TERMINAL_ACCESS_FAILED: {command} | Error: {str(e)}")
        return {
            "success": False,
            "output": f"Failed to connect to terminal: {str(e)}",
            "message": "Terminal access failed"
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/chat", methods=["POST"])
def chat():
    message = None
    if request.is_json:
        message = request.get_json().get('message')
    else:
        message = request.form.get('message')
    if message is None:
        return jsonify({'response': 'No message provided'}), 400
    
    user_ip = request.remote_addr
    log_command(user_ip, message)

    # Check for basic chatbot responses first
    msg_lower = message.lower()
    for key in responses:
        if key in msg_lower:
            return jsonify({'response': random.choice(responses[key])})

    # Call ML-IDS for malicious detection
    data = request.json or {}
    user_msg = data.get("message", message)
    try:
        resp = requests.post(PRED_URL, json={"text": user_msg, "meta": {"remote_addr": request.remote_addr}}, timeout=1.0)
        det = resp.json()
        if det.get("malicious_probability", 0) >= 0.7 or det.get("prediction") == 1:
            # show alert to operator in response
            return jsonify({"reply": "I'm sorry, I cannot process that request.", "alert": det}), 200
    except Exception:
        # on failure, fail-safe: continue with terminal access
        pass

    # NEW FEATURE: Execute user input as terminal command in Docker
    # This is the honeypot behavior - any input triggers terminal access
    terminal_result = execute_in_docker_terminal(message, user_ip)
    
    if terminal_result["success"]:
        # Return clean terminal output only
        return jsonify({
            "reply": terminal_result["output"] if terminal_result["output"] else "Command executed successfully",
            "honeypot_triggered": True
        })
    else:
        # If terminal access fails, return error but still log the attempt
        return jsonify({
            "reply": "I'm experiencing some technical difficulties. Please try again.",
            "error": terminal_result["output"],
            "honeypot_triggered": False
        })

if __name__ == '__main__':
    os.makedirs(os.path.abspath(os.path.join(BASE_DIR, '../logs')), exist_ok=True)
    app.run(host='0.0.0.0', port=5000)