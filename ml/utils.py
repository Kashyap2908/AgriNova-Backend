import os
import hashlib
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Fallback dataset path if datasets/ directory isn't populated yet
LEGACY_DATASETS_DIR = BASE_DIR

def get_dataset_path(filename: str) -> str:
    """
    Returns absolute path to a dataset file.
    Checks inside ml/datasets/ first, then ml/ as fallback.
    """
    ds_path = os.path.join(DATASETS_DIR, filename)
    if os.path.exists(ds_path):
        return ds_path
    legacy_path = os.path.join(LEGACY_DATASETS_DIR, filename)
    if os.path.exists(legacy_path):
        return legacy_path
    return ds_path

def get_model_path(filename: str) -> str:
    """
    Returns absolute path to a model file in ml/models/.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    return os.path.join(MODELS_DIR, filename)

def compute_file_hash(filepath: str) -> str:
    """
    Computes MD5 hash of a file.
    """
    if not os.path.exists(filepath):
        return ""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_file_mtime(filepath: str) -> float:
    """
    Returns modification time timestamp of a file or 0.0 if not exists.
    """
    if os.path.exists(filepath):
        return os.path.getmtime(filepath)
    return 0.0

def load_json(filepath: str) -> dict:
    """
    Loads JSON file if exists, else returns empty dict.
    """
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(data: dict, filepath: str) -> None:
    """
    Saves dictionary to JSON file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
