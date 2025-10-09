import json
from flask import Flask, jsonify, send_from_directory, request
from pathlib import Path
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

# Path to the log where Alert.send_alert writes JSON entries (adjust if different)
LOG_FILE = Path(r'c:\Users\teju\Desktop\Honey-SSH\IDS\ml-intrusion-detection\logs\ids.log')

def read_alerts(limit=50):
    alerts = []
    if not LOG_FILE.exists():
        return alerts
    # read file lines (each line expected to be a JSON object or log that contains JSON)
    with LOG_FILE.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # attempt to extract a JSON substring
            try:
                # many alert writers output raw JSON per line; try direct parse
                obj = json.loads(line)
                # if outer log wrapper exists, try to unwrap
                if isinstance(obj, dict) and 'alert' in obj:
                    alerts.append(obj)
                else:
                    alerts.append({'ts': obj.get('ts') if isinstance(obj, dict) else None, 'alert': obj})
            except Exception:
                # try to find JSON inside line
                try:
                    start = line.index('{')
                    obj = json.loads(line[start:])
                    if isinstance(obj, dict):
                        alerts.append(obj)
                except Exception:
                    continue
    # normalize and sort by timestamp descending
    normalized = []
    for a in alerts:
        if 'alert' in a and isinstance(a['alert'], dict):
            entry = a['alert']
            ts = a.get('ts') or entry.get('ts') or entry.get('timestamp')
        elif isinstance(a, dict) and 'ts' in a:
            entry = a.get('alert', a)
            ts = a.get('ts')
        else:
            entry = a
            ts = a.get('ts') if isinstance(a, dict) else None
        # attempt parse timestamp
        try:
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else datetime.min
        except Exception:
            parsed = datetime.min
        normalized.append({'ts': ts, 'parsed_ts': parsed, 'alert': entry})
    normalized.sort(key=lambda x: x['parsed_ts'], reverse=True)
    return normalized[:limit]

@app.get('/api/alerts')
def api_alerts():
    # optional query param 'limit'
    limit = int(request.args.get('limit', 50))
    items = read_alerts(limit)
    # map to simple dict for frontend
    out = []
    for it in items:
        entry = it['alert'] if 'alert' in it else it
        out.append({
            'ts': it['ts'],
            'source_ip': entry.get('source_ip') or (entry.get('alert', {}).get('source') if isinstance(entry.get('alert'), dict) else None) or entry.get('meta', {}).get('remote_addr'),
            'destination_ip': entry.get('destination_ip') or entry.get('dst') or entry.get('alert', {}).get('destination'),
            'summary': entry.get('summary') or entry.get('message') or entry.get('alert', {}).get('summary') or entry.get('alert', {}).get('text'),
            'severity': entry.get('severity') or entry.get('alert', {}).get('severity') or 'High' if entry.get('prediction') == 1 else 'Medium',
            'raw': entry
        })
    return jsonify(out)

@app.get('/')
def index():
    # serve local dashboars.html placed in same folder
    return send_from_directory('.', 'dashboars.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)