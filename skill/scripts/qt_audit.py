"""Conservative, evidence-linked static hints for native Qt for Python UI files.

This is NOT a visual, accessibility or runtime verifier. Exit code 2 with
--strict means advisory findings were present, not that the app is broken.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import tokenize
from pathlib import Path

EXTENSIONS = {".py", ".qss", ".qml", ".ui"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build"}
LIMITATIONS = [
    "Static heuristics cannot establish visual quality or real Qt interaction behavior.",
    "Inspect the running native window for keyboard/focus, DPI, layout, state and theming.",
    "Warnings may be intentional on custom canvases or narrowly scoped widgets.",
]


def inspect_file(path: Path, root: Path) -> list[dict]:
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeError, OSError) as exc:
        return [finding(path, root, 1, "QT000", "error", "Unable to read source", str(exc))]
    results: list[dict] = []
    if path.suffix.lower() == ".py":
        # Tokenize rather than searching source lines: comments, docstrings and
        # string literals must not be mistaken for Qt method calls.
        try:
            tokens = list(tokenize.generate_tokens(io.StringIO(content).readline))
        except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
            return [finding(path, root, 1, "QT000", "error", "Unable to tokenize Python", str(exc))]
        rules = {
            "setGeometry": (
                "QT101", "Absolute widget geometry may defeat resize/DPI behavior",
                "Use Qt layouts for ordinary forms; exempt deliberate canvases.",
            ),
            "setFixedWidth": (
                "QT102", "Fixed widget dimensions warrant a resizing check",
                "Use sizeHint/QSizePolicy unless this is a genuine fixed primitive.",
            ),
            "setFixedHeight": (
                "QT102", "Fixed widget dimensions warrant a resizing check",
                "Use sizeHint/QSizePolicy unless this is a genuine fixed primitive.",
            ),
            "setFixedSize": (
                "QT102", "Fixed widget dimensions warrant a resizing check",
                "Use sizeHint/QSizePolicy unless this is a genuine fixed primitive.",
            ),
        }
        source_lines = content.splitlines()
        for index in range(1, len(tokens) - 1):
            token = tokens[index]
            if token.type != tokenize.NAME or token.string not in rules:
                continue
            before, after = index - 1, index + 1
            while before >= 0 and tokens[before].type in (tokenize.NL, tokenize.COMMENT):
                before -= 1
            while after < len(tokens) and tokens[after].type in (tokenize.NL, tokenize.COMMENT):
                after += 1
            if (before < 0 or after >= len(tokens)
                    or tokens[before].string != "."
                    or tokens[after].string != "("):
                continue
            rule, message, recommendation = rules[token.string]
            results.append(finding(
                path, root, token.start[0], rule, "advisory", message,
                source_lines[token.start[0] - 1].strip(), recommendation,
            ))
    if path.suffix.lower() == ".qss":
        source = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group().count("\n"), content, flags=re.S)
        for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", source):
            selectors = [s.strip() for s in match.group(1).split(",")]
            declaration = match.group(2)
            if "QWidget" in selectors and re.search(
                r"(?:background(?:-color)?|color|font(?:-family|-size)?)\s*:", declaration
            ):
                results.append(finding(
                    path, root,
                    source.count("\n", 0,
                                 match.start(1) + len(match.group(1))
                                 - len(match.group(1).lstrip())) + 1,
                    "QT201", "advisory",
                    "Broad QWidget styling may override native and custom widget states",
                    ", ".join(selectors),
                    "Scope QSS or use QPalette/QStyle roles; verify focus, disabled and selection.",
                ))
    if path.suffix.lower() == ".qml":
        # Mask QML/JS comments and string literals, preserving line numbers.
        literals = re.compile(
            r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|'
            r"'(?:\\.|[^'\\])*'|\x60(?:\\.|[^\x60\\])*\x60"
        )
        masked = literals.sub(
            lambda match: re.sub(r"[^\n]", " ", match.group(0)), content
        )
        lines = content.splitlines()
        for match in re.finditer(
            r"(?m)^[ \t]*(width|height)[ \t]*:[ \t]*\d+(?:\.\d+)?[ \t]*(?=;|$)", masked
        ):
            number = content.count("\n", 0, match.start()) + 1
            results.append(finding(
                path, root, number, "QT301", "advisory",
                "Fixed QML dimensions warrant a resizing/DPI check",
                lines[number - 1].strip(),
                "Prefer responsive sizing for resizable surfaces; explicit pixel sizes are legitimate for primitives.",
            ))
    return results


def finding(path: Path, root: Path, line: int, rule: str, severity: str,
            message: str, evidence: str, recommendation: str = "") -> dict:
    return {
        "file": path.relative_to(root).as_posix(), "line": line, "rule": rule,
        "severity": severity, "message": message, "evidence": evidence,
        "recommendation": recommendation,
    }


def audit(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    files: list[Path] = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(
            d for d in dirs
            if d not in SKIP_DIRS and not (Path(directory) / d).is_symlink()
        )
        for name in sorted(names):
            path = Path(directory) / name
            if path.suffix.lower() in EXTENSIONS and path.is_file() and not path.is_symlink():
                files.append(path)
                if len(files) > 10000:
                    raise ValueError("Source scan exceeds 10000 files; narrow the target directory")
    files.sort()
    findings = [f for p in files for f in inspect_file(p, root)]
    return {
        "schema_version": 1, "root": str(root), "files_scanned": len(files),
        "extensions": sorted(EXTENSIONS), "findings": findings,
        "limitations": LIMITATIONS,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Qt project directory")
    parser.add_argument("--json", action="store_true", help="Machine-readable report")
    parser.add_argument("--strict", action="store_true", help="Exit 2 on advisory findings")
    args = parser.parse_args(argv)
    try:
        report = audit(args.root)
    except (ValueError, OSError) as exc:
        print(f"qt-audit: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Qt source hints: {report['files_scanned']} files scanned")
        for item in report["findings"]:
            print(f"{item['file']}:{item['line']} {item['rule']} "
                  f"[{item['severity']}] {item['message']}")
        print("Static hints only. Inspect a real Qt window before accepting any finding.")
    has_error = any(x["severity"] == "error" for x in report["findings"])
    if has_error:
        return 1
    return 2 if args.strict and report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
