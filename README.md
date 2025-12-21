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

Run a video script in preview mode:

```bash
python -m algonim videoscripts/bubble_sort.py
```

Render a video (work in progress):

```bash
python -m algonim render videoscripts/example.py
```

Each video script must define:

```python
def build_script(window):
    ...
```

# TODO

- Headless rendering (algonim render …)
- Resolution presets (native, fullhd, 4k)
- Scene abstraction (window-independent scripts)
- Pause / resume in preview mode
- Array index highlighting
- Variable update animations
- Code line highlighting improvements
- First video: How to find max element in an array
- Upload first YouTube video
