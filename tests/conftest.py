"""Shared pytest setup for testing addon modules outside a live Anki install.

The addon's ``__init__.py`` wires up real ``aqt``/Anki hooks at import time,
so a plain ``import Ankimon...`` would require a full Anki environment. The
modules under test here (``battle_engine``, ``battle_functions``,
``business``, ``resources``, ``pokedex_functions``) don't actually need
Anki - they only pull in ``aqt.utils`` for error dialogs on failure paths.
So: stub out ``aqt`` and register ``Ankimon`` as a namespace package pointed
at ``src/Ankimon`` *without* executing the real ``src/Ankimon/__init__.py``.
"""
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if "aqt" not in sys.modules:
    aqt_stub = types.ModuleType("aqt")
    aqt_utils_stub = types.ModuleType("aqt.utils")
    aqt_utils_stub.showWarning = lambda *a, **k: None
    aqt_utils_stub.showInfo = lambda *a, **k: None
    aqt_utils_stub.tooltip = lambda *a, **k: None
    aqt_stub.utils = aqt_utils_stub
    aqt_stub.mw = types.SimpleNamespace()
    aqt_stub.gui_hooks = types.SimpleNamespace()
    sys.modules["aqt"] = aqt_stub
    sys.modules["aqt.utils"] = aqt_utils_stub

if "Ankimon" not in sys.modules:
    ankimon_stub = types.ModuleType("Ankimon")
    ankimon_stub.__path__ = [str(SRC_DIR / "Ankimon")]
    sys.modules["Ankimon"] = ankimon_stub
