import pyglet

from algonim.resolution import Resolution
from algonim.script import FPS, Player

HEIGHT = 40
MARGIN = 16
LABEL_WIDTH = 160
ICON_SIZE = 14


class Timeline:
    """Dev overlay at the bottom of the window: playback progress and time,
    click or drag on it to seek"""

    def __init__(self, player: Player, resolution: Resolution):
        self.player = player
        s = resolution.scale
        self.height = HEIGHT * s
        self.x0 = (2 * MARGIN + ICON_SIZE) * s
        self.x1 = resolution.width - LABEL_WIDTH * s
        bar_y = self.height / 2
        bar_h = 6 * s

        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.shapes.Rectangle(
            0, 0, resolution.width, self.height, (20, 20, 20, 200), batch=self.batch
        )
        self.track = pyglet.shapes.Rectangle(
            self.x0,
            bar_y - bar_h / 2,
            self.x1 - self.x0,
            bar_h,
            (80, 80, 80, 255),
            batch=self.batch,
        )
        self.progress = pyglet.shapes.Rectangle(
            self.x0, bar_y - bar_h / 2, 0, bar_h, (90, 160, 255, 255), batch=self.batch
        )
        self.playhead = pyglet.shapes.Circle(
            self.x0, bar_y, 7 * s, color=(255, 255, 255, 255), batch=self.batch
        )
        self.label = pyglet.text.Label(
            "",
            x=resolution.width - MARGIN * s,
            y=bar_y,
            anchor_x="right",
            anchor_y="center",
            font_size=12 * s,
            batch=self.batch,
        )

        icon = ICON_SIZE * s
        left = MARGIN * s
        bottom = bar_y - icon / 2
        self.play_icon = pyglet.shapes.Triangle(
            left, bottom, left, bottom + icon, left + icon, bar_y, batch=self.batch
        )
        bar_w = icon / 3
        self.pause_icon = [
            pyglet.shapes.Rectangle(left + dx, bottom, bar_w, icon, batch=self.batch)
            for dx in (0, icon - bar_w)
        ]

    def draw(self):
        last = self.player.script.frame
        u = self.player.frame / last if last else 1.0
        x = self.x0 + u * (self.x1 - self.x0)
        self.progress.width = x - self.x0
        self.playhead.x = x
        playing = not self.player.paused and not self.player.finished
        self.play_icon.visible = not playing
        for bar in self.pause_icon:
            bar.visible = playing
        self.label.text = f"{self.player.frame / FPS:.2f} / {last / FPS:.2f}s"
        self.batch.draw()

    def hit(self, y: float) -> bool:
        return y <= self.height

    def seek_to(self, x: float):
        u = (x - self.x0) / (self.x1 - self.x0)
        self.player.seek(round(u * self.player.script.frame))
