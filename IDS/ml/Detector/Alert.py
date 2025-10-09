import json
import logging
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(r'c:\Users\teju\Desktop\Honey-SSH\IDS\ml-intrusion-detection\logs\ids.log')
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=str(LOG_FILE), level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def send_alert(payload: dict):
    """
    Minimal alert: log to file and print. Extend to send email/slack/webhook.
    """
    try:
        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "alert": payload
        }
        logging.warning(json.dumps(entry))
        # also append to honeypot log for correlation
        with open(Path(r'c:\Users\teju\Desktop\Honey-SSH\logs\honeypot.log'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
        print("ALERT:", json.dumps(entry))
    except Exception as e:
        logging.error(f"Failed to send alert: {e}")