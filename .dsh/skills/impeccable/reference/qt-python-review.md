# PySide6 / PyQt6 Widgets review overlay

Use this review checklist for Python desktop applications built with Qt Widgets. Combine it with [qt.md](qt.md) and [desktop.md](desktop.md) when auditing, adapting, or reviewing native UI. It is **not** a C++ lint checklist and does **not** assume that the application uses QML, Qt Quick, Qt Designer, or CMake.

The categories here are independently adapted from review and design concepts in the Qt Company's [Qt AI agent skills](https://github.com/TheQtCompanyRnD/agent-skills), especially [qt-cpp-review](https://github.com/TheQtCompanyRnD/agent-skills/tree/main/skills/qt-cpp-review) and [qt-ui-design](https://github.com/TheQtCompanyRnD/agent-skills/tree/main/skills/qt-ui-design) (accessed 2026-10-16). These are original PySide6-oriented instructions, not a copied linter or a direct translation of C++ APIs. Upstream material is offered under BSD-3-Clause or Qt commercial terms; check the applicable licenses before copying source or examples.

## 1. Model/view state transitions

- For custom `QAbstractItemModel` implementations, trace every mutation from call site through `beginInsertRows`/`endInsertRows`, `beginRemoveRows`/`endRemoveRows`, `beginMoveRows`/`endMoveRows`, `beginResetModel`/`endResetModel`. Check inclusive row ranges and parent `QModelIndex` arguments, persistent-index expectations, and that data matches notifications. Do not treat `layoutChanged` or `modelReset.emit()` as replacements for mutation protocol.
- Verify `dataChanged` includes correct top-left/bottom-right indexes and roles, and `flags`, `headerData`, `setData` and `roleNames` agree with editable/selectable behavior.
- For tables and trees with large datasets, prefer `QAbstractItemModel`, `QSortFilterProxyModel` and `QStyledItemDelegate`. Flag `setCellWidget()` or `setIndexWidget()` in large population loops as a **scaling investigation**, not proof that a small table is incorrect.
- Confirm selection, editing and sorting remain stable across source/proxy changes; use `QPersistentModelIndex` where needed.

## 2. QObject lifecycle and threading

- Understand Python wrapper lifetime **and** underlying Qt object ownership. Check parent-child relationships and avoid retaining wrappers after native objects have been destroyed; use `deleteLater()` intentionally, not as a guarantee of immediate destruction.
- Qt GUI objects must be manipulated in the GUI thread. Worker tasks (`QThread`, `QObject.moveToThread`, `QThreadPool`/`QRunnable`) deliver results through signals/queued connections, not by touching widgets directly.
- Verify cleanup on cancellation, widget close and application shutdown: worker stop signal, connection lifetime, no deadlocks from `wait()`, and no stale result arriving into a deleted view.
- In UI callbacks, `paintEvent`, resize handlers and state-change slots, synchronous sleeps, blocking subprocess calls, heavy calculations and nested `processEvents()` loops deserve a targeted latency/reentrancy review.
- Do not confuse `QThread` object affinity with the thread executing `run()`; review receiver lifetime and connection type before suggesting `DirectConnection` or `BlockingQueuedConnection`.

## 3. Native desktop UX and accessibility

- Audit the **existing application workflow** before prescribing a design system. Do not apply QML control styles (Material, FluentWinUI3, etc.) directly to Widgets: use the application's current `QStyle`, semantic `QPalette` roles, scoped QSS and standard QWidget controls.
- Verify keyboard traversal, `QLabel.setBuddy`, `QAction` commands, `QKeySequence.StandardKey`, default/Escape dialog buttons and menus. A hover tooltip is supporting information, not the only way to discover or operate a command.
- Custom/icon controls expose useful `accessibleName` and `accessibleDescription`; status colors must also have labels, icons or other noncolor cues. Check focus contrast and disabled/selection states in **all shipped themes**.
- Use `QLocale` where locale-sensitive presentation is appropriate, while maintaining explicit domain units, sign, precision and stable serialization. Truncation in labels and table headers is a correctness/UX defect even if the numbers remain intact.
- Prefer size policies, layouts and content-driven geometry over arbitrary responsive breakpoints. Dense scientific/engineering interfaces can use smaller typography and more than three text styles when legibility and workflow benefit; no universal 16 px minimum or Golden Ratio positioning requirement.
- Review empty, loading, populated, error and long-running states. Feedback must reflect real progress; only offer cancellation where supported.

## 4. Charts, engineering canvases and performance

- For `pyqtgraph`, inspect whether `PlotDataItem.setData()`, targeted updates or cached geometry can replace repeated scene/view recreation. Profile before describing a redraw as expensive; verify axes, units, tooltip precision and labels at supported DPR.
- In `paintEvent`/`QGraphicsView`, keep domain calculations separate from rendering, cache only safe intermediates, and invalidate on data, theme and device-scale changes.
- Inspect long-running numerical computations triggered by UI actions for worker handoff, state-locking while results are pending and stale-results suppression after rapid repeated inputs.

## 5. Evidence and classification

- Run the optional `.dsh/skills/impeccable/scripts/qt_audit.py` source checker first, then manually verify every advisory at the actual call site. Static rules `QT401` (blocking sleep inside named UI callbacks), `QT402` (cell widgets in loops) and `QT403` (direct model reset emission) are **investigation cues**, not proof of a user-visible failure.
- For confirmed defects, report file, line, UI context, triggering input, affected platform, reproducible consequence, recommendation and an appropriate `pytest-qt`/`QTest` regression.
- Treat UI-thread access and QObject lifetime as requiring **runtime/source-flow evidence**. A scanner cannot prove thread affinity, event-loop ordering, correct model indices, accessibility or actual render quality.
- Capture real QWidget images with `.dsh/skills/impeccable/scripts/qt_capture.py`. Review actual PNGs alongside keyboard tests and an OS/DPI/theme matrix. A simulated/offscreen image does not establish that Windows desktop rendering is correct.

## 6. Official Qt reference lookup (optional)

When exact behavior, supported signatures, version-specific deprecations or obscure event-loop semantics matter, retrieve the **matching version** of the official [Qt Widgets](https://doc.qt.io/qt-6/qtwidgets-index.html) and [Qt for Python](https://doc.qt.io/qtforpython-6/) documentation before proposing changes. The Qt Company's optional hosted [Qt Documentation MCP](https://github.com/TheQtCompanyRnD/agent-skills/tree/main/mcp/qt-documentation-mcp) provides `qt_documentation_search` and `qt_documentation_read` at `https://qt-docs-mcp.qt.io/mcp`. Pin `version` and `module=qtwidgets`/`qtcore` when available. A C++ documentation example must be translated and checked against the actual PySide6 version; do not invent binding symbols or require users to install an MCP server to run the skill.
