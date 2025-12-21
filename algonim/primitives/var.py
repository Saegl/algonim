import pyglet


class Var:
    def __init__(self, x, y, varname: str, value: str):
        self.label = pyglet.text.Label(f"{varname} = {value}", x, y, font_size=32)
        self.varname = varname

    def update_val(self, value):
        def update(delta):
            self.label.text = f"{self.varname} = {value}"
            return True

        return update

    def draw(self):
        self.label.draw()
