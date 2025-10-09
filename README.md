# Honeypot Ubuntu Project

## Overview
This project is a honeypot system designed to simulate a vulnerable chatbot running on HTTP. When a user interacts with the chatbot, a Python client connects to a server running inside an isolated Ubuntu Docker container, providing shell access and logging attacker commands and IP addresses.

## Structure
```
client/
    client.py
Docker/
    Dockerfile
    server.py
Database/
    inspect_db.py
Detector/
    Alert.py
IDS/
    alerts_api.py
web/
    app.py
logs/
    honeypot.log
```

## Features
- Fake chatbot web interface (Flask)
- Vulnerable input field triggers shell access
- Python socket server in Docker container
- Logs attacker commands and IP addresses

## Setup
1. **Create Python virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```
2. **Install dependencies**
   ```powershell
   pip install flask
   ```
3. **Build and run Docker container**
   ```powershell
   cd Docker
   docker build -t honeypot-ubuntu .
   docker run -it --rm -p 4444:4444 honeypot-ubuntu
   ```
4. **Run the web server**
   ```powershell
   cd web
   python app.py
   ```

## Usage
- Access the chatbot via your browser at `http://localhost:5000` (or the port you set).
- Interact with the chatbot; each message triggers the client connection and logs activity in `logs/honeypot.log`.

## Logging
All commands, IP addresses and users ID are logged in `logs/honeypot.log & sign.log`.

## License
MIT
