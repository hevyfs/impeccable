"""Behavioral tests for the public Qt audit CLI and native capture API.

Runs without Qt: fake widget covers I/O, failure and provenance contracts.
Actual render/interaction acceptance belongs to a consuming Qt project.
"""
from __future__ import annotations

import base64
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / "skill"


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load("qt_audit", "qt_audit.py")
capture = load("qt_capture", "qt_capture.py")


class StaticAuditTests(unittest.TestCase):
    def test_detects_source_patterns_with_locations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "views").mkdir()
            (root / "views" / "window.py").write_text(
                "w.setGeometry(0, 0, 800, 600)\n"
                "w.setFixedWidth(200)\n"
                "# w.setGeometry(0, 0, 1, 1)\n", encoding="utf-8")
            (root / "views" / "light.qss").write_text(
                "QWidget, QMainWindow {\n background-color: #fff;\n}\n", encoding="utf-8")
            ignored = root / ".venv"
            ignored.mkdir()
            (ignored / "bad.py").write_text("w.setGeometry(0,0,1,1)", encoding="utf-8")
            report = audit.audit(root)
            self.assertEqual(report["files_scanned"], 2)
            self.assertEqual([f["rule"] for f in report["findings"]],
                             ["QT201", "QT101", "QT102"])
            self.assertEqual(report["findings"][1]["file"], "views/window.py")
            self.assertEqual(report["findings"][1]["line"], 1)
            self.assertTrue(all(f["severity"] == "advisory" for f in report["findings"]))

    def test_utf8_bom_is_valid_python_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bom.py").write_bytes(
                b"\\xef\\xbb\\xbfw.setGeometry(0, 0, 800, 600)\\n"
            )
            findings = audit.audit(root)["findings"]
            self.assertEqual(
                [(item["rule"], item["line"]) for item in findings],
                [("QT101", 1)],
            )

    def test_pep263_latin1_is_decoded_like_python(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "legacy.py").write_bytes(
                b"# coding: latin-1\\n"
                b"label = 'caf\\xe9'\\n"
                b"widget.setFixedHeight(200)\\n"
            )
            findings = audit.audit(root)["findings"]
            self.assertEqual(
                [(item["rule"], item["line"]) for item in findings],
                [("QT102", 3)],
            )

    def test_bad_encoding_is_a_read_error_not_ast_syntax_hint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad_bytes.py").write_bytes(
                b"# coding: utf-8\\nlabel = '\\xff'\\n"
            )
            findings = audit.audit(root)["findings"]
            self.assertEqual([item["rule"] for item in findings], ["QT000"])
            self.assertEqual(findings[0]["severity"], "error")

    def test_unknown_pep263_encoding_reports_decode_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unknown.py").write_bytes(
                b"# coding: made-up-charset\\nx = 1\\n"
            )
            findings = audit.audit(root)["findings"]
            self.assertEqual([item["rule"] for item in findings], ["QT000"])
            self.assertEqual(findings[0]["severity"], "error")

    def test_python_literals_comments_and_docstrings_are_not_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Multiline attribute invocation is valid Python inside parentheses.
            (root / "screen.py").write_text(
                '"""Example: w.setGeometry(1, 2, 3, 4)"""\n'
                'sample = "w.setFixedHeight(123)"\n'
                '# w.setGeometry(0, 0, 1, 1)\n'
                '(widget.setFixedWidth\n'
                ' (320))\n',
                encoding="utf-8",
            )
            findings = audit.audit(root)["findings"]
            self.assertEqual([(v["rule"], v["line"]) for v in findings], [("QT102", 4)])

    def test_qml_fixed_dimensions_are_advisory_not_inventory_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Window.qml").write_text(
                'import QtQuick\n'
                '/* width: 111 */\n'
                '// height: 999\n'
                'Item {\n'
                '  property string note: "width: 123"\n'
                '  width: 320\n'
                '  height: 240\n'
                '  Item { implicitWidth: 44 }\n'
                '}\n',
                encoding="utf-8",
            )
            report = audit.audit(root)
            self.assertEqual(report["files_scanned"], 1)
            self.assertEqual(
                [(item["rule"], item["line"]) for item in report["findings"]],
                [("QT301", 6), ("QT301", 7)],
            )

    def test_qml_dynamic_dimensions_are_not_flagged(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "View.qml").write_text(
                'Item {\n  width: parent.width\n  height: parent.height\n}\n',
                encoding="utf-8",
            )
            self.assertEqual(audit.audit(Path(directory))["findings"], [])

    def test_qss_selector_reports_its_actual_line(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "theme.qss").write_text(
                "QLineEdit { color: blue; }\n"
                "\n"
                "/* theme grouping */\n"
                " QWidget { color: red; }\n",
                encoding="utf-8",
            )
            findings = audit.audit(root)["findings"]
            self.assertEqual([(v["rule"], v["line"]) for v in findings], [("QT201", 4)])

    def test_blocking_sleep_in_ui_handlers_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "callbacks.py").write_text(
                "import time as clock\n"
                "from time import sleep as wait\n"
                "class Window:\n"
                "    def paintEvent(self, event):\n"
                "        clock.sleep(0.1)\n"
                "    @Slot()\n"
                "    def refresh(self):\n"
                "        wait(1)\n"
                "    def background(self):\n"
                "        clock.sleep(10)\n"
                "    def on_save_clicked(self):\n"
                "        example = 'time.sleep(3)'\n"
                "        clock.sleep(0.5)\n",
                encoding="utf-8",
            )
            findings = audit.audit(root)["findings"]
            self.assertEqual(
                [(f["rule"], f["line"]) for f in findings],
                [("QT401", 5), ("QT401", 8), ("QT401", 13)],
            )

    def test_cell_widget_loop_is_advisory_not_single_widget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "table.py").write_text(
                "class Results:\n"
                "    def load(self, rows):\n"
                "        for row in rows:\n"
                "            self.table.setCellWidget(row, 2, build())\n"
                "        self.table.setIndexWidget(index, editor)\n"
                "        for row in rows:\n"
                "            self.table.setIndexWidget(row, editor)\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [(f["rule"], f["line"]) for f in audit.audit(root)["findings"]],
                [("QT402", 4), ("QT402", 7)],
            )

    def test_model_reset_protocol_hint_and_safe_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "model.py").write_text(
                "class Model:\n"
                "    def reset_bad(self):\n"
                "        self.modelReset.emit()\n"
                "    def reset_good(self):\n"
                "        self.beginResetModel()\n"
                "        self.endResetModel()\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [(f["rule"], f["line"]) for f in audit.audit(root)["findings"]],
                [("QT403", 3)],
            )

    def test_ast_parse_incompatibility_is_advisory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "incompatible.py").write_text(
                "def broken():\n    return 1 2\n", encoding="utf-8",
            )
            findings = audit.audit(root)["findings"]
            self.assertEqual([f["rule"] for f in findings], ["QT004"])
            self.assertEqual(findings[0]["severity"], "advisory")

    def test_cli_json_and_strict_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "form.py").write_text(
                "field.setFixedHeight(31)\n", encoding="utf-8")
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = audit.main([directory, "--json", "--strict"])
            result = json.loads(stream.getvalue())
            self.assertEqual(code, 2)
            self.assertEqual(result["findings"][0]["rule"], "QT102")
            self.assertTrue(result["limitations"])

    def test_clean_directory_is_not_a_failed_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(audit.audit(Path(directory))["findings"], [])
            self.assertEqual(audit.main([directory, "--strict"]), 0)

    def test_invalid_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(audit.main([str(Path(directory) / "missing")]), 1)


class FakeSize:
    def __init__(self, w, h):
        self._w, self._h = w, h

    def width(self):
        return self._w

    def height(self):
        return self._h


class FakePixmap:
    def __init__(self, good=True):
        self.good = good

    def isNull(self):
        return not self.good

    def save(self, destination, _format):
        if not self.good:
            return False
        sample = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlE"
            "QVR4nGNgYGD4DwABBAEAX+XDSwAAAABJRU5ErkJggg=="
        )
        Path(destination).write_bytes(sample)
        return True


class FakeWidget:
    def __init__(self, good=True):
        self.width = 640
        self.height = 480
        self.good = good
        self.shown = False

    def size(self):
        return FakeSize(self.width, self.height)

    def resize(self, w, h):
        self.width, self.height = w, h

    def show(self):
        self.shown = True

    def hide(self):
        self.shown = False

    def isVisible(self):
        return self.shown

    def isHidden(self):
        return not self.shown

    def repaint(self):
        pass

    def grab(self):
        return FakePixmap(self.good)

    def devicePixelRatioF(self):
        return 1.25


class NativeCaptureTests(unittest.TestCase):
    def test_capture_records_case_and_restores_original_geometry(self):
        with tempfile.TemporaryDirectory() as directory:
            widget = FakeWidget()
            paths = capture.capture_window(
                widget, directory, case="aba-7", scenario="validation-error",
                theme="light", sizes=((800, 600), (1280, 800)))
            self.assertEqual(len(paths), 2)
            self.assertFalse(widget.shown)
            self.assertEqual((widget.width, widget.height), (640, 480))
            for path in paths:
                self.assertTrue(path.is_file())
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data["scenario"], "validation-error")
                self.assertEqual(data["device_pixel_ratio"], 1.25)
                self.assertEqual(data["verification_level"], "simulated-capture")
                self.assertEqual(data["capture_source"], "test-double")
                self.assertEqual(data["qt_binding"], "unavailable")
                self.assertTrue((path.parent / data["png"]).exists())

    def test_parent_hidden_child_preserves_implicit_visibility(self):
        class ChildOfHiddenParent(FakeWidget):
            def __init__(self):
                super().__init__()
                self.hide_calls = 0

            def isVisible(self):
                return False  # Parent hidden, but child not explicitly hidden.

            def isHidden(self):
                return False

            def hide(self):
                self.hide_calls += 1
                super().hide()

        with tempfile.TemporaryDirectory() as directory:
            child = ChildOfHiddenParent()
            capture.capture_window(child, directory, case="child")
            self.assertEqual(child.hide_calls, 0)

    def test_invalid_png_does_not_publish_fake_evidence(self):
        class InvalidPixmap(FakePixmap):
            def save(self, destination, _format):
                Path(destination).write_bytes(b"fake-native-raster")
                return True

        class InvalidWidget(FakeWidget):
            def grab(self):
                return InvalidPixmap()

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "PNG header"):
                capture.capture_window(InvalidWidget(), directory, case="invalid")
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_already_visible_widget_stays_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            widget = FakeWidget()
            widget.show()
            capture.capture_window(widget, directory, case="visible")
            self.assertTrue(widget.shown)
            self.assertEqual((widget.width, widget.height), (640, 480))

    def test_unsafe_case_is_rejected_without_write(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                capture.capture_window(FakeWidget(), directory, case="../escape")
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_null_capture_fails_and_restores_size(self):
        with tempfile.TemporaryDirectory() as directory:
            widget = FakeWidget(good=False)
            with self.assertRaisesRegex(RuntimeError, "null screenshot"):
                capture.capture_window(widget, directory, case="empty")
            self.assertEqual((widget.width, widget.height), (640, 480))
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_failed_recapture_clears_old_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "old-800x600.png").write_bytes(b"stale")
            (root / "old-800x600.json").write_text('{"stale": true}', encoding="utf-8")
            with self.assertRaises(RuntimeError):
                capture.capture_window(
                    FakeWidget(good=False), root, case="old", sizes=((800, 600),))
            self.assertEqual(list(root.iterdir()), [])

    def test_constrained_widget_does_not_publish_false_dimensions(self):
        class Constrained(FakeWidget):
            def resize(self, width, height):
                self.width = max(1000, width)
                self.height = max(700, height)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stem = "constrained-400x300"
            (root / f"{stem}.json").write_text('{"stale": true}', encoding="utf-8")
            (root / f"{stem}.png").write_bytes(b"stale")
            with self.assertRaisesRegex(RuntimeError, "Qt constrained"):
                capture.capture_window(
                    Constrained(), root, case="constrained", sizes=((400, 300),))
            self.assertEqual(list(root.iterdir()), [])

    def test_predictable_metadata_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "out"
            output.mkdir()
            victim = root / "victim.txt"
            victim.write_text("untouched", encoding="utf-8")
            link = output / "safe-1280x800.json.tmp"
            try:
                link.symlink_to(victim)
            except (NotImplementedError, OSError):
                self.skipTest("Symlink creation unavailable")
            paths = capture.capture_window(FakeWidget(), output, case="safe")
            self.assertEqual(victim.read_text(encoding="utf-8"), "untouched")
            self.assertEqual(len(paths), 1)
            self.assertTrue(link.is_symlink())

    def test_final_symlink_destinations_cannot_overwrite_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "out"
            output.mkdir()
            victim = root / "victim.txt"
            victim.write_text("untouched", encoding="utf-8")
            try:
                (output / "safe-1280x800.json").symlink_to(victim)
                (output / "safe-1280x800.png").symlink_to(victim)
            except (NotImplementedError, OSError):
                self.skipTest("Symlink creation unavailable")
            capture.capture_window(FakeWidget(), output, case="safe")
            self.assertEqual(victim.read_text(encoding="utf-8"), "untouched")
            self.assertFalse((output / "safe-1280x800.json").is_symlink())
            self.assertFalse((output / "safe-1280x800.png").is_symlink())

    def test_failed_json_publication_does_not_leave_png(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original_replace = capture.os.replace

            def fail_json(source, target):
                if str(target).endswith(".json"):
                    raise PermissionError("metadata publication rejected")
                return original_replace(source, target)

            with mock.patch.object(capture.os, "replace", side_effect=fail_json):
                with self.assertRaisesRegex(PermissionError, "metadata publication"):
                    capture.capture_window(FakeWidget(), root, case="failure")
            self.assertEqual(list(root.iterdir()), [])

    def test_duplicate_sizes_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                capture.capture_window(
                    FakeWidget(), directory, case="duplicates",
                    sizes=((640, 480), (640, 480)),
                )

    def test_invalid_size_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                capture.capture_window(FakeWidget(), directory, case="a", sizes=((0, 1),))
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
