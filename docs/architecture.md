# Architecture

The codebase is a single installable package, `chess_ai`, plus a vendored
third-party package, `maia`. It contains **two independent applications** that
share assets but not control flow.

## Module map

```
src/chess_ai/
├── paths.py        Single source of truth for on-disk resources (models,
│                   sprites, background). Paths are derived from the file's
│                   location, so the apps run from any working directory.
│
├── engine/         Application 1 — the from-scratch engine.
│   └── app.py      A self-contained `Chess` class implementing the rules
│                   (move generation, castling, en passant, promotion,
│                   check/checkmate) and its own Pygame board. Depends only on
│                   the standard library, Pygame, and `paths.py`.
│
├── gui/            Application 2 — the Maia AI opponent.
│   └── game.py     A Pygame GUI that uses python-chess for the rules and the
│                   Maia network for move selection. The model is loaded lazily
│                   (`get_ai_model`) so importing the module does not require
│                   TensorFlow or the weights file.
│
├── ml/             Machine-learning building blocks.
│   ├── tensor.py        Board → tensor encoders (see ml-pipeline.md).
│   ├── maia_model.py    Loads the Maia Keras model with its custom LCZero
│   │                    layers (ApplySqueezeExcitation, ApplyPolicyMap).
│   ├── model.py         Experimental CNN trainer (imitate a player).
│   └── print_tensor.py  Debug helper that labels each tensor plane.
│
└── data/           Data acquisition.
    ├── lichess_api.py   Fetches games from the Lichess API and turns them into
    │                    stacked board sets for training.
    └── prep_data.py     Alternative download + PGN-parsing utilities.
```

```
third_party/maia/   Vendored Leela Chess Zero code (GPL-3.0). Kept importable
                    as a top-level `maia` package; see its own README for
                    provenance and license.
```

## The two applications

| | `chess-engine` (`engine/app.py`) | `chess-gui` (`gui/game.py`) |
|---|---|---|
| **Rules** | Implemented from scratch | python-chess |
| **Opponent** | None (local hot-seat) | Maia neural network |
| **Heavy deps** | Pygame only | + TensorFlow (`--extra ml`) |
| **Sprites** | `assets/engine/` (descriptive names) | `assets/gui/` (short codes) |

They were built at different stages of the project: the engine to learn the
rules by hand, the GUI to experiment with a learned, human-like opponent. They
are intentionally kept separate rather than merged.

## Resource resolution

Every model/asset path lives in `paths.py` as a `pathlib.Path` derived from
`PROJECT_ROOT`. Call sites pass `str(...)` to Pygame / Keras. This replaced the
previous hard-coded, Windows-style relative paths (e.g. `'maia\\tf2\\...'`) and
lets both apps run regardless of the current directory.
