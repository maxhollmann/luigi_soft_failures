import os

def ensure_dir(*path):
    path = os.path.join(*[str(p) for p in path])
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
