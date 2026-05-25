# Vendored: Leela Chess Zero / Maia

This directory contains **third-party code that is not original to this
project**. It is kept here, isolated under `third_party/`, to make its
provenance and license explicit.

## Source

The files under `tf2/` are vendored from
[Leela Chess Zero (LCZero)](https://github.com/LeelaChessZero/lc0):

- **`tf2/lc0_az_policy_map.py`** — maps the AlphaZero-style policy output
  (80×8×8 = 5120 planes) to LCZero's flat 1858-move policy vector.
- **`tf2/policy_index.py`** — the canonical list of 1858 legal moves in UCI
  notation used by the policy head.
- **`tf2/net.ipynb`** — notebook documenting how the Maia network was converted
  to the Keras `.h5` weights this project loads.

## License

```
This file is part of Leela Chess Zero.
Copyright (C) 2019 The LCZero Authors

Leela Chess Zero is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.
```

See the project-root [`LICENSE`](../../LICENSE) (GPL-3.0) and
[`NOTICE`](../../NOTICE).

## Model weights

The Maia network weights used by the GUI live in `models/mymodel2.h5` (kept
outside this directory because they are data, not source). Maia builds
human-like chess engines on top of LCZero — see https://maiachess.com.
