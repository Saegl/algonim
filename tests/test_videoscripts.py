import importlib
from pathlib import Path

import pytest

VIDEOSCRIPTS_DIR = Path(__file__).parent.parent / "videoscripts"
MODULE_NAMES = sorted(
    path.stem for path in VIDEOSCRIPTS_DIR.glob("*.py") if not path.name.startswith("_")
)


@pytest.mark.parametrize("module_name", MODULE_NAMES)
def test_build_script(window, module_name):
    module = importlib.import_module(f"videoscripts.{module_name}")
    script = module.build_script()
    assert script.steps
