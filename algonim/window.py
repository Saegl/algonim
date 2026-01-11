import pyglet
from PIL import Image
from pyglet.window import key


class AppWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(
            width=1600,
            height=900,
            resizable=False,
            fullscreen=False,
            visible=True,
        )
        self.objects = []
        self.frames = []

    def update(self, delta: float):
        print(delta)

    def on_draw(self):
        self.clear()
        for object in self.objects:
            object.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            self.close()

    def capture_frame(self, delta):
        import numpy as np

        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        image_data = buffer.get_image_data()
        data = image_data.get_data("RGBA", image_data.width * 4)
        img = Image.frombytes("RGBA", (image_data.width, image_data.height), data)
        img = img.transpose(
            Image.Transpose.FLIP_TOP_BOTTOM
        )  # Flip the image (OpenGL stores it upside down)

        frame = np.array(img)
        self.frames.append(frame)
