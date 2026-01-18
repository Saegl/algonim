import importlib
from pathlib import Path


def get_videoscript_modules():
    videoscripts_dir = Path(__file__).parent.parent / "videoscripts"
    for path in videoscripts_dir.glob("*.py"):
        if path.name.startswith("_"):
            continue
        yield path.stem


def test_build_script():
    for module_name in get_videoscript_modules():
        module = importlib.import_module(f"videoscripts.{module_name}")
        script = module.build_script()
        assert script is not None
