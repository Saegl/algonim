import importlib.util
from pathlib import Path

import imageio
import numpy as np
import pyglet
from pyglet import gl
from pyglet.math import Mat4

from algonim.resolution import RESOLUTIONS, Resolution
from algonim.script import Player, Script, frame_count, write_script
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


def exec_preview(script: Script):
    Player(script).start()
    pyglet.app.run()


def exec_video_renderer(
    window: AppWindow,
    script: Script,
    target_fps: int,
    output: Path,
):
    width, height = window.resolution.width, window.resolution.height
    # macro_block_size=8 keeps 1080p unpadded (default 16 resizes it to 1088)
    writer = imageio.get_writer(
        output, fps=target_fps, codec="libx264", quality=8, macro_block_size=8
    )

    window.switch_to()
    # Frames render offscreen, so the video doesn't depend on the window
    # being visible or fitting on the screen
    framebuffer = pyglet.image.buffer.Framebuffer()
    framebuffer.attach_texture(pyglet.image.Texture.create(width, height))
    window.projection = Mat4.orthogonal_projection(0, width, 0, height, -255, 255)
    frame = np.empty((height, width, 4), dtype=np.uint8)

    with Timer("render_frames"):
        for i in range(frame_count(script.duration, target_fps)):
            script.seek(i / target_fps)

            window.dispatch_events()
            framebuffer.bind()
            gl.glViewport(0, 0, width, height)
            window.on_draw()
            gl.glReadPixels(
                0, 0, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, frame.ctypes.data
            )
            # OpenGL stores image upside down
            writer.append_data(np.ascontiguousarray(frame[::-1, :, :3]))

            if window.visible:
                show_frame(window, width, height)
            framebuffer.unbind()

    window.set_visible(False)
    writer.close()


def show_frame(window: AppWindow, width: int, height: int):
    """Blit the offscreen frame, still bound for reading, to the window"""
    gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)
    gl.glBlitFramebuffer(
        0,
        0,
        width,
        height,
        0,
        0,
        *window.get_framebuffer_size(),
        gl.GL_COLOR_BUFFER_BIT,
        gl.GL_LINEAR,
    )
    window.flip()


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
    parser.add_argument(
        "-r",
        "--resolution",
        choices=RESOLUTIONS,
        default="1080p",
        help="Output resolution, scripts use 1600x900 coordinates at any of them",
    )

    args = parser.parse_args()

    resolution = Resolution.preset(args.resolution)
    # Type ignore here is a bug in pyglet typing
    window = AppWindow(resolution, visible=not args.headless)  # type: ignore[abstract]
    build_script = load_script(Path(args.script))

    script = write_script(window, build_script)

    if not args.video:
        exec_preview(script)
    else:
        exec_video_renderer(window, script, args.fps, args.output)
