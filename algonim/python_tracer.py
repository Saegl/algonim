import sys
import runpy
import linecache
import pathlib
from copy import deepcopy
from typing import Any
from dataclasses import dataclass


@dataclass
class Changed:
    from_: str
    to: str


@dataclass
class Snapshot:
    vars: dict[str, Any]
    line: str
    lineno: int

    def __init__(self, vars, line, lineno):
        self.vars = vars
        self.line = line
        self.lineno = lineno

    def diff(self, other) -> tuple[set[str], dict[str, Changed]]:
        new_vars = set(self.vars.keys()).difference(other.vars.keys())

        changed = {}
        common_vars = set(self.vars.keys()).intersection(other.vars.keys())
        for varname in common_vars:
            newval = self.vars[varname]
            oldval = other.vars[varname]

            if newval != oldval:
                changed[varname] = Changed(oldval, newval)

        return new_vars, changed


class Tracer:
    def __init__(self, filepath: pathlib.Path, watched_vars: set[str]):
        self.filepath = filepath
        self.watched_file = filepath.name
        self.watched_vars = watched_vars
        self.result = []

    def tracer(self, frame, event, arg=None):
        if event != "line":
            return self.tracer

        code = frame.f_code
        func_name = code.co_name
        lineno = frame.f_lineno
        filename = code.co_filename

        if filename.endswith(self.watched_file):
            current_line = linecache.getline(filename, lineno)
            current_line = current_line[:-1]  # EAT NEWLINE
            vars_snapshot = {}
            for var in self.watched_vars:
                value = frame.f_locals.get(var)
                if value:
                    vars_snapshot[var] = deepcopy(value)

            # print(f"{line_no}: {vars_snapshot}")
            self.result.append((lineno, Snapshot(vars_snapshot, current_line, lineno)))

        return self.tracer  # Return the trace function itself to keep tracing

    def run(self):
        sys.settrace(self.tracer)
        runpy.run_path(str(self.filepath))
        sys.settrace(None)
        return self.result


def trace(filepath, watched_vars):
    tracer = Tracer(filepath, watched_vars)
    return tracer.run()


if __name__ == "__main__":
    print(
        trace(
            pathlib.Path("videoprograms/bubble_sort.py"), {"arr", "swapped", "i", "j"}
        )
    )
