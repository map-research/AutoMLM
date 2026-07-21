import sys
from pathlib import Path

# This is the small start file for the GUI window.
# Python 3.12 is the shared project version for this app.
# .venv312 is the matching private Python folder for this project.
# D:\Projekte\AutoMLM\.venv312\Scripts\python.exe
# It keeps the GUI libraries separate from other Python projects on the computer.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    # The project folder is added so names like "src.gui.app" can be found.
    sys.path.insert(0, str(PROJECT_ROOT))

from src.gui.app import run


if __name__ == "__main__":
    # This creates the window and starts the GUI event loop.
    run()
