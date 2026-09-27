import pyglet

from algonim.script import Script


class Var:
    def __init__(self, script: Script, x, y, varname: str, value: str):
        res = script.resolution
        self.label = pyglet.text.Label(
            f"{varname} = {value}",
            res.pixel(x),
            res.pixel(y),
            font_size=res.length(27),
        )
        self.varname = varname
        script.register(self)

    def update_val(self, value):
        def update(delta):
            self.label.text = f"{self.varname} = {value}"
            return True

        return update

    def draw(self):
        self.label.draw()
