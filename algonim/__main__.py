import importlib.util
from pathlib import Path

import pyglet

from algonim.script import run_script
from algonim.window import AppWindow


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location("videoscript", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load script from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "build_script"):
        raise RuntimeError(f"{path} must define build_script(window)")

    return module.build_script


if __name__ == "__main__":
    from argparse import ArgumentParser

    import moviepy.editor as mpy

    parser = ArgumentParser("algonim")
    parser.add_argument("script", help="Path to video script")
    parser.add_argument("--video", action="store_true")

    args = parser.parse_args()

    # Type ignore here is a bug in pyglet typing
    window = AppWindow()  # type: ignore[abstract]
    build_script = load_script(Path(args.script))

    run_script(window, build_script)

    if args.video:
        pyglet.clock.schedule(window.capture_frame)

    # pyglet.gl.glClearColor(1, 1, 1, 1)
    pyglet.app.run()

    if args.video:
        video = mpy.ImageSequenceClip(window.frames, fps=165)
        video.write_videofile("output.mp4", codec="libx264")
