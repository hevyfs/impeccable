"""Opt-in real PySide6 Widgets smoke on Windows CI; unlike mocks, decodes a Qt grab.

Run with: python tests/qt-native-tools/native_widget_smoke.py
For headless self-hosted services set QT_QPA_PLATFORM=offscreen; that checks Qt
integration, NOT native Windows compositor/theme fidelity.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / "skill" / "scripts" / "qt_capture.py"
spec = importlib.util.spec_from_file_location("qt_capture", source)
assert spec is not None and spec.loader is not None
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)

app = QApplication.instance() or QApplication([])
widget = QWidget()
layout = QVBoxLayout(widget)
field = QLineEdit()
field.setText("Representative numerical input")
layout.addWidget(field)

original_size = (widget.width(), widget.height())
originally_hidden = widget.isHidden()
assert originally_hidden, "Fresh smoke-test window should initially be hidden"

with tempfile.TemporaryDirectory(prefix="impeccable-qt-real-") as directory:
    manifests = capture.capture_window(
        widget, directory, case="pyside6-real-widget",
        scenario="real-qt-render", sizes=((800, 600),),
    )
    assert len(manifests) == 1
    record = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert record["qt_binding"] == "PySide6", record
    assert record["verification_level"] == "native-raster-observation", record
    assert record["capture_source"] == "qt-widget", record
    assert record["logical_size"] == {"width": 800, "height": 600}, record
    assert (manifests[0].parent / record["png"]).is_file()
    assert (widget.width(), widget.height()) == original_size
    assert widget.isHidden() is originally_hidden
    print(
        "Qt real QWidget capture PASS:",
        record["qt_version"], record["platform"],
        record["qt_qpa_platform"], record["device_pixel_ratio"],
    )

widget.close()
