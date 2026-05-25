"""Central, OS-independent resolution of on-disk resources.

Every module that needs a model, image or other bundled asset imports the
relevant constant from here instead of hard-coding a (often Windows-style)
relative path. Paths are derived from this file's location, so the project
runs regardless of the current working directory.
"""

from pathlib import Path

# paths.py lives at <root>/src/chess_ai/paths.py
# parents[0] = chess_ai, parents[1] = src, parents[2] = project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Piece sprites for the from-scratch engine (descriptive names, e.g. rook_black.png)
ENGINE_IMAGES = ASSETS_DIR / "engine"
# Piece sprites for the Maia GUI (short codes, e.g. bb.png, wk.png)
GUI_IMAGES = ASSETS_DIR / "gui"

# Vendored Maia (Leela Chess Zero) weights used for AI move selection.
MAIA_MODEL = MODELS_DIR / "mymodel2.h5"
# CNN trained by chess_ai.ml.model on Lichess games.
TRAINED_MODEL = MODELS_DIR / "my_chess_model.h5"

BACKGROUND = ASSETS_DIR / "bg.png"
