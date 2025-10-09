import os
import sqlite3
import random
from datetime import datetime
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'  # change for production

BASE_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, '../logs/honeypot.log'))
SIGN_LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, '../logs/sign.log'))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, 'users.db'))
PRED_URL = "http://127.0.0.1:8000/predict_text"

responses = {
    "hello": ["Hi there!", "Hello!", "Hey!"],
    "how are you": ["I'm just a bot, but I'm doing great!", "I'm fine, thank you!"],
    "what is your name": ["You can call me hiGPT.", "I'm hiGPT, your friendly chatbot."],
    "bye": ["Goodbye!", "See you later!"],
    "default": ["Sorry, I didn't understand that.", "Could you please rephrase that?"]
}

def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or BASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def add_user(email, password):
    """Return True on success, False if email exists or error."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
                    (email.lower(), generate_password_hash(password), datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE email = ?", (email.lower(),))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return check_password_hash(row[0], password)

def log_command(ip, command):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        # honeypot.log entries WITHOUT timestamp (per request)
        f.write(f"IP: {ip} | Command: {command}\n")

def log_sign_event(user, message):
    os.makedirs(os.path.dirname(SIGN_LOG_PATH), exist_ok=True)
    with open(SIGN_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.utcnow().isoformat()} | User: {user} | {message}\n")

@app.route('/')
def index():
    if not session.get('user'):
        return redirect(url_for('auth'))
    return render_template('index.html', user=session.get('user'))

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        if session.get('user'):
            return redirect(url_for('index'))
        return render_template('login.html')
    data = request.get_json(silent=True) or request.form
    form_type = (data.get('form_type') or '').lower()
    email = (data.get('email') or '').strip()
    ip = request.remote_addr
    if form_type == 'signup':
        password = data.get('password', '')
        confirm = data.get('confirm', '')
        if not email or not password or password != confirm:
            return jsonify({'success': False, 'message': 'Invalid signup data'}), 400
        ok = add_user(email, password)
        if ok:
            log_sign_event(email, f'Signed up from {ip}')
            return jsonify({'success': True, 'message': 'Signup successful'})
        else:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400

    elif form_type == 'login':
        password = data.get('password', '')
        if not email or not password:
            return jsonify({'success': False, 'message': 'Invalid login data'}), 400
        if verify_user(email, password):
            session['user'] = email.lower()
            log_sign_event(email, f'Logged in from {ip}')
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            log_sign_event(email or 'UNKNOWN', f'Failed login attempt from {ip}')
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    else:
        return jsonify({'success': False, 'message': 'Unknown form type'}), 400

@app.route('/logout')
def logout():
    user = session.pop('user', None)
    ip = request.remote_addr
    if user:
        log_sign_event(user, f'Logged out from {ip}')
    return redirect(url_for('auth'))

@app.route("/chat", methods=["POST"])
def chat():
    if not session.get('user'):
        return jsonify({'response': 'Not authenticated'}), 401
    message = None
    if request.is_json:
        message = request.get_json().get('message')
    else:
        message = request.form.get('message')
    if message is None:
        return jsonify({'response': 'No message provided'}), 400
    user_ip = request.remote_addr
    log_command(user_ip, message)

    msg_lower = message.lower()
    for key in responses:
        if key in msg_lower:
            return jsonify({'response': random.choice(responses[key])})

    data = request.json or {}
    user_msg = data.get("message", "")
    # call ML-IDS
    try:
        resp = requests.post(PRED_URL, json={"text": user_msg, "meta": {"remote_addr": request.remote_addr}}, timeout=1.0)
        det = resp.json()
        if det.get("malicious_probability", 0) >= 0.7 or det.get("prediction") == 1:
            # show alert to operator in response
            return jsonify({"reply": "I'm sorry, I cannot process that request.", "alert": det}), 200
    except Exception:
        # on failure, fail-safe: continue normal chatbot
        pass

    reply = "This is a safe chatbot reply."  # replace with existing logic
    return jsonify({"reply": reply})

if __name__ == '__main__':
    os.makedirs(os.path.abspath(os.path.join(BASE_DIR, '../logs')), exist_ok=True)
    init_db()
    open(SIGN_LOG_PATH, 'a', encoding='utf-8').close()
    app.run(host='0.0.0.0', port=5000)