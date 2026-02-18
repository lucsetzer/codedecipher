# shared/file_queue.py
import json
import os
from pathlib import Path

# Use a persistent directory for queue files
QUEUE_DIR = Path("/tmp/docudecipher_queue")
QUEUE_DIR.mkdir(exist_ok=True)

def save_analysis(analysis_id: str, data: dict):
    """Save analysis data to a file"""
    file_path = QUEUE_DIR / f"{analysis_id}.json"
    with open(file_path, 'w') as f:
        json.dump(data, f)
    print(f"💾 Saved to file: {analysis_id}")

def load_analysis(analysis_id: str):
    """Load analysis data from file"""
    file_path = QUEUE_DIR / f"{analysis_id}.json"
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

def get_all_ids():
    """Get all analysis IDs"""
    return [f.stem for f in QUEUE_DIR.glob("*.json")]

def delete_analysis(analysis_id: str):
    """Delete analysis file"""
    file_path = QUEUE_DIR / f"{analysis_id}.json"
    if file_path.exists():
        file_path.unlink()