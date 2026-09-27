import importlib.util
from pathlib import Path

import imageio
import numpy as np
import pyglet

from algonim.script import ScriptExecutor, write_script
from algonim.time_utils import Timer
from algonim.window import AppWindow


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location("videoscript", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load script from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "build_script"):
        raise RuntimeError(f"{path} must define build_script()")

    return module.build_script


def exec_preview(script_exec: ScriptExecutor):
    script_exec.start()
    pyglet.app.run()


def exec_video_renderer(
    window: AppWindow,
    script_exec: ScriptExecutor,
    target_fps: int,
    output: Path,
):
    fixed_dt = 1 / target_fps
    buffer = pyglet.image.get_buffer_manager().get_color_buffer()
    # macro_block_size=8 keeps 1080p unpadded (default 16 resizes it to 1088)
    writer = imageio.get_writer(
        output, fps=target_fps, codec="libx264", quality=8, macro_block_size=8
    )

    with Timer("render_frames"):
        window.switch_to()

        while not script_exec.is_complete():
            script_exec.execute_current_action(fixed_dt)

            window.clear()
            window.dispatch_events()
            window.dispatch_event("on_draw")

            # To show preview in OS window, window without `double_buffer`
            # should use it over `flip`
            pyglet.gl.glFlush()

            # Fetch native RGBA: pyglet's own format conversion is very slow
            raw = buffer.get_image_data().get_data("RGBA", window.width * 4)
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(
                window.height, window.width, 4
            )
            # OpenGL stores image upside down
            writer.append_data(np.ascontiguousarray(frame[::-1, :, :3]))

    window.set_visible(False)
    writer.close()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser("algonim")
    parser.add_argument("script", help="Path to video script")
    parser.add_argument("--video", action="store_true", help="Render to a file")
    parser.add_argument("--headless", action="store_true", help="Don't show the window")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("output.mp4"), help="Video path"
    )
    parser.add_argument("--fps", type=int, default=60, help="Video frame rate")

    args = parser.parse_args()

    # Type ignore here is a bug in pyglet typing
    window = AppWindow(visible=not args.headless, double_buffer=not args.video)  # type: ignore[abstract]
    build_script = load_script(Path(args.script))

    script_exec = write_script(window, build_script)

    if not args.video:
        exec_preview(script_exec)
    else:
        exec_video_renderer(window, script_exec, args.fps, args.output)
