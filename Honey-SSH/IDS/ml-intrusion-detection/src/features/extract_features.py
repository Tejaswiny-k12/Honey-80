from typing import Dict, Any
import math
import re
from collections import Counter

SUSPICIOUS_KEYWORDS = [
    'curl', 'wget', 'bash', 'sh', 'exec', 'eval', 'base64', 'python', 'perl', 'php',
    'nc', 'ncat', 'socat', 'rm', 'chmod', 'chown', 'sudo', 'passwd', 'ssh', '$(', '`', '&&', '||'
]

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    return -sum((cnt/length) * math.log2(cnt/length) for cnt in counts.values())

def count_special_chars(s: str) -> int:
    return len(re.findall(r'[^A-Za-z0-9\s]', s))

def extract_features_from_text(s: str) -> dict:
    s = s or ""
    s_lower = s.lower()
    features = {}
    features['text_len'] = float(len(s))
    features['num_words'] = float(len(s.split()))
    features['num_digits'] = float(len(re.findall(r'\d', s)))
    features['num_special'] = float(count_special_chars(s))
    # suspicious keyword count
    features['suspicious_kw_count'] = float(sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in s_lower))
    # token / shell-symbol presence flags (as float)
    features['has_backtick'] = 1.0 if '`' in s else 0.0
    features['has_subshell'] = 1.0 if '$(' in s else 0.0
    features['has_pipe_logic'] = 1.0 if '&&' in s or '||' in s else 0.0
    features['entropy'] = float(shannon_entropy(s))
    # heuristic: many slashes likely URL/payload
    features['slash_count'] = float(s.count('/'))
    return features

def extract_features_from_log(log: Dict[str, Any]) -> Dict[str, float]:
    """
    Convert a single honeypot/log event into the numeric feature dict expected by model.
    Customize to match your processed training features.
    Example fields: request_size, num_commands, unique_ips_count, time_since_last, error_count
    """
    return {
        "request_size": float(log.get("request_size", 0)),
        "num_commands": float(log.get("num_commands", 0)),
        "unique_ips_count": float(log.get("unique_ips_count", 0)),
        "time_since_last": float(log.get("time_since_last", 0)),
        "error_count": float(log.get("error_count", 0))
        # add/modify keys to match columns.json
    }