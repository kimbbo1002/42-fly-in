from pathlib import Path
from tkinter import Tk, filedialog
import subprocess


root = Tk()
root.withdraw()

BASE_DIR = Path(__file__).resolve().parent
MAPS_DIR = BASE_DIR / "maps/"

path = filedialog.askopenfilename(
    initialdir=str(MAPS_DIR)
)
if path:
    subprocess.run(["uv", "run", "main.py", path])
