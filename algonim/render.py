import importlib.util
from pathlib import Path

import imageio
import numpy as np
import pyglet
from pyglet import gl
from pyglet.math import Mat4

from algonim.resolution import Resolution
from algonim.script import FPS, Player, write_script
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


def preview(script_path: Path, resolution: Resolution):
    """Play the script in a window with pause and dev tools"""
    window = AppWindow(resolution, visible=True)  # type: ignore[abstract]
    script = write_script(window, load_script(script_path))
    player = Player(script)
    window.attach_player(player)
    player.start()
    pyglet.app.run()


def render_video(script_path: Path, resolution: Resolution, output: Path):
    """Render the script to a video file without showing a window"""
    window = AppWindow(resolution, visible=False)  # type: ignore[abstract]
    script = write_script(window, load_script(script_path))
    width, height = window.resolution.width, window.resolution.height
    # macro_block_size=8 keeps 1080p unpadded (default 16 resizes it to 1088)
    writer = imageio.get_writer(
        output, fps=FPS, codec="libx264", quality=8, macro_block_size=8
    )

    window.switch_to()
    # Drawing goes to an offscreen multisampled buffer, which is resolved
    # into a plain one that can be read
    msaa = pyglet.image.buffer.Framebuffer()
    msaa.attach_renderbuffer(
        pyglet.image.buffer.Renderbuffer(width, height, gl.GL_RGBA8, samples=4)
    )
    framebuffer = pyglet.image.buffer.Framebuffer()
    framebuffer.attach_texture(pyglet.image.Texture.create(width, height))
    window.projection = Mat4.orthogonal_projection(0, width, 0, height, -255, 255)
    frame = np.empty((height, width, 4), dtype=np.uint8)

    with Timer("render_frames"):
        for i in range(script.frame + 1):
            script.seek(i)

            window.dispatch_events()
            msaa.bind()
            gl.glViewport(0, 0, width, height)
            window.on_draw()
            gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, framebuffer.id)
            gl.glBlitFramebuffer(
                0,
                0,
                width,
                height,
                0,
                0,
                width,
                height,
                gl.GL_COLOR_BUFFER_BIT,
                gl.GL_NEAREST,
            )
            framebuffer.bind()
            gl.glReadPixels(
                0, 0, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, frame.ctypes.data
            )
            # OpenGL stores image upside down
            writer.append_data(np.ascontiguousarray(frame[::-1, :, :3]))
            framebuffer.unbind()

    writer.close()
    window.close()
