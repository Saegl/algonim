# Algonim

Algonim is script-first animation engine for creating educational programming
videos.

Videos are defined using plain Python scripts and rendered
deterministically.

The long-term goal is to use Algonim to create short, clear YouTube videos
explaining algorithms and code execution step by step.

# Key Ideas

- Script-first: animations are written as Python code, no editor, no GUI
- Deterministic rendering: same script -> same video
- Programming-focused: variables, arrays, code lines, execution tracing
- Separation of concerns:
    algonim/ → engine
    videoscripts/ → video content

# Usage

Run a video script in preview mode (press `Q` to quit):

```bash
python -m algonim videoscripts/bubble_sort.py
```

Render a video to a file:

```bash
python -m algonim videoscripts/max_elem.py --video --headless -o max_elem.mp4
```

Options: `--video` renders to a file, `--headless` hides the window,
`-o/--output` sets the path (default `output.mp4`), `--fps` sets the frame
rate (default 60), `-r/--resolution` picks a 16:9 preset: `720p`, `900p`,
`1080p` (default), `1440p`, `4k`.

Each video script must define a function that fills the given `Script`.
Scripts always use a virtual 1600x900 canvas, `(0, 0)` is the bottom left
corner. Positions, sizes and font sizes are scaled to the chosen resolution,
so the same script renders crisp and with identical layout at any preset.

```python
from algonim.script import Script, fade_in
from algonim.primitives.text import Text


def build_script(script: Script):
    title = Text(script, 800, 450, "Hello")
    script.play(fade_in(title))
```

# Development

```bash
uv sync
pytest  # needs a display: scripts are built against a hidden window
mypy
ruff check . && ruff format .
```

# TODO

- Scene abstraction (window-independent scripts)
- Pause / resume in preview mode
- Array index highlighting
- Variable update animations
- Code line highlighting improvements
- First video: How to find max element in an array
- Upload first YouTube video
