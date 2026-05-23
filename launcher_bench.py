from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent
MAPS_DIR = BASE_DIR / "maps/"

for path in MAPS_DIR.rglob("*.txt"):
    relative_path = path.relative_to(MAPS_DIR)
    if path.is_file():
        print(f"{relative_path}", end="", flush=True)
        subprocess.run(["uv", "run", "main.py", str(path), "--bench"])
