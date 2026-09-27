import pytest

from algonim.resolution import Resolution
from algonim.window import AppWindow


@pytest.fixture(scope="session")
def window():
    """Text primitives need a GL context, like the real app provides."""
    win = AppWindow(Resolution.preset("1080p"), visible=False)  # type: ignore[abstract]
    yield win
    win.close()
