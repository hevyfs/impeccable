"""Capture an actual Qt widget from a pytest-qt/QTest scenario.

The caller creates the widget and sets its application state. This module does
not render browser mockups, invent scenarios or start an application.
"""
from __future__ import annotations

import importlib
import json
import os
import platform
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_CASE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")


def _widget_binding(widget: object) -> str | None:
    for base in type(widget).__mro__:
        root = base.__module__.split(".", 1)[0]
        if root in ("PySide6", "PyQt6"):
            return root
    return None


def _qt_version(binding: str | None) -> str:
    if binding is None:
        return "unavailable"
    module = importlib.import_module(f"{binding}.QtCore")
    return str(module.qVersion())


def _settle_events(binding: str | None) -> None:
    if binding is None:
        return
    core = importlib.import_module(f"{binding}.QtCore")
    instance = core.QCoreApplication.instance()
    if instance is not None:
        instance.processEvents()


_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _real_qt_pixmap(binding: str | None, widget: object, pixmap: object) -> bool:
    """Only an actual Qt widget + QPixmap can claim native capture evidence."""
    if binding is None:
        return False
    widgets = importlib.import_module(f"{binding}.QtWidgets")
    gui = importlib.import_module(f"{binding}.QtGui")
    if not isinstance(widget, widgets.QWidget) or not isinstance(pixmap, gui.QPixmap):
        raise RuntimeError("Qt widget grab() must return a real QPixmap")
    return True


def _check_png(path: Path, binding: str | None, native: bool) -> None:
    """Reject mislabeled PNGs, then decode actual native rasters using Qt."""
    with path.open("rb") as stream:
        header = stream.read(24)
    if (len(header) < 24 or header[:8] != _PNG_SIGNATURE
            or header[12:16] != b"IHDR"
            or int.from_bytes(header[16:20], "big") == 0
            or int.from_bytes(header[20:24], "big") == 0):
        raise RuntimeError("Screenshot is not a valid PNG header")
    if native:
        reader = importlib.import_module(f"{binding}.QtGui").QImageReader(str(path))
        if reader.read().isNull():
            raise RuntimeError("Qt could not decode the captured PNG")


def _size_tuple(size: object) -> tuple[int, int]:
    if (not isinstance(size, (tuple, list)) or len(size) != 2
            or any(type(n) is not int or n < 1 or n > 16384 for n in size)):
        raise ValueError("Each capture size must be two integer dimensions in 1..16384")
    return size[0], size[1]


def capture_window(
    widget: object,
    output_dir: str | Path,
    *,
    case: str,
    sizes: tuple[tuple[int, int], ...] = ((1280, 800),),
    scenario: str = "default",
    theme: str = "application",
) -> list[Path]:
    """Capture a real Qt widget, returning paths to JSON evidence manifests.

    Caller must arrange the application state and wait for its signals.
    Requested dimensions are verified against actual widget geometry.
    """
    if not isinstance(case, str) or not _CASE.fullmatch(case):
        raise ValueError("case must be a safe 1..80-character filename segment")
    dimensions = [_size_tuple(size) for size in sizes]
    if not dimensions or len(dimensions) > 20 or len(set(dimensions)) != len(dimensions):
        raise ValueError("Provide 1..20 distinct capture sizes")
    if not isinstance(scenario, str) or not isinstance(theme, str):
        raise ValueError("scenario and theme must be strings")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    qt_binding = _widget_binding(widget)
    qt_version = _qt_version(qt_binding)
    evidence: list[Path] = []

    current_size = widget.size()
    old_width, old_height = current_size.width(), current_size.height()
    originally_hidden = (widget.isHidden() if hasattr(widget, "isHidden")
                         else not widget.isVisible() if hasattr(widget, "isVisible") else None)
    try:
        for width, height in dimensions:
            stem = f"{case}-{width}x{height}"
            png_path, json_path = out / f"{stem}.png", out / f"{stem}.json"
            # Clear previous evidence before attempting this case, including
            # constrained or failed resizes. Unlink removes symlinks, not targets.
            png_path.unlink(missing_ok=True)
            json_path.unlink(missing_ok=True)

            widget.resize(width, height)
            widget.show()
            _settle_events(qt_binding)
            widget.repaint()
            _settle_events(qt_binding)
            size = widget.size()
            actual_width, actual_height = size.width(), size.height()
            if (actual_width, actual_height) != (width, height):
                raise RuntimeError(
                    f"Qt constrained {case} to {actual_width}x{actual_height}, "
                    f"not the requested {width}x{height}"
                )
            pixmap = widget.grab()
            if pixmap.isNull():
                raise RuntimeError(f"Qt returned a null screenshot for {case}")
            native = _real_qt_pixmap(qt_binding, widget, pixmap)

            dpr = float(widget.devicePixelRatioF()) if hasattr(widget, "devicePixelRatioF") else 1.0
            record = {
                "schema_version": 1,
                "case": case,
                "scenario": scenario,
                "theme": theme,
                "png": png_path.name,
                "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                "platform": platform.system(),
                "platform_release": platform.release(),
                "qt_binding": qt_binding or "unavailable",
                "qt_version": qt_version,
                "qt_qpa_platform": os.getenv("QT_QPA_PLATFORM"),
                "qt_scale_factor": os.getenv("QT_SCALE_FACTOR"),
                "requested_logical_size": {"width": width, "height": height},
                "logical_size": {"width": actual_width, "height": actual_height},
                "device_pixel_ratio": dpr,
                "widget_type": type(widget).__name__,
                "verification_level": (
                    "native-raster-observation" if native else "simulated-capture"
                ),
                "capture_source": "qt-widget" if native else "test-double",
                "limitations": [
                    "A screenshot does not establish correct keyboard/focus behavior.",
                    "Headless Qt/offscreen is not a substitute for OS-native desktop testing.",
                ],
            }
            # The staging directory is private and unpredictable. Never pass a
            # predictable temporary path to QPixmap.save or JSON writes.
            with tempfile.TemporaryDirectory(prefix=f".{stem}-", dir=out) as staging:
                temporary_png = Path(staging) / png_path.name
                temporary_json = Path(staging) / json_path.name
                if (not pixmap.save(str(temporary_png), "PNG")
                        or not temporary_png.is_file()
                        or temporary_png.stat().st_size == 0):
                    raise RuntimeError(f"Unable to save screenshot: {png_path}")
                _check_png(temporary_png, qt_binding, native)
                temporary_json.write_text(
                    json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                # Replacing a destination symlink never follows its target.
                os.replace(temporary_png, png_path)
                try:
                    os.replace(temporary_json, json_path)
                except OSError:
                    png_path.unlink(missing_ok=True)
                    raise
            evidence.append(json_path)
    finally:
        widget.resize(old_width, old_height)
        if originally_hidden is True:
            widget.hide()
        elif originally_hidden is False:
            widget.show()
        _settle_events(qt_binding)
    return evidence
