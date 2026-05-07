import json
import os
import fcntl
from datetime import datetime
from typing import Dict, Any

AUDIT_LOG_FILE = os.getenv("AUDIT_LOG_FILE", "/app/data/audit_ledger.jsonl")

def log_audit_event(user: str, action: str, filename: str, status: str, details: Dict[str, Any]):
    """
    Appends an audit event to the JSON Lines log file.
    Uses file locking to act as a thread-safe mock immutable ledger.
    """
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user,
        "action": action,
        "filename": filename,
        "status": status,
        "details": details
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)
    
    try:
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            # Acquire exclusive lock
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(event) + "\n")
                f.flush()
            finally:
                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        print(f"Failed to write to audit log: {str(e)}")
        # Fallback for Windows if fcntl isn't available (during local non-Docker dev)
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as fallback_e:
            print(f"Fallback failed: {str(fallback_e)}")
