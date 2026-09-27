import pyglet

from algonim.script import Anim, Script, set_to


class Var:
    def __init__(self, script: Script, x, y, varname: str, value: str):
        res = script.resolution
        self.label = pyglet.text.Label(
            f"{varname} = {value}",
            res.length(x),
            res.length(y),
            font_size=res.length(27),
        )
        self.varname = varname
        self.value = script.prop(value, self.set_value)
        script.register(self)

    def set_value(self, value):
        self.label.text = f"{self.varname} = {value}"

    def update_val(self, value) -> Anim:
        return set_to(self.value, value)

    def draw(self):
        self.label.draw()
