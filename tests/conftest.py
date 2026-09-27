import pytest

from algonim.window import AppWindow


@pytest.fixture(scope="session")
def window():
    """Text primitives need a GL context, like the real app provides."""
    win = AppWindow(visible=False, double_buffer=False)  # type: ignore[abstract]
    yield win
    win.close()
