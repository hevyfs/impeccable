# Qt desktop platform

For native desktop applications built with **Qt for Python**, primarily PySide6 or PyQt6 using Qt Widgets and/or Qt Quick, on Windows, macOS, and Linux.

Desktop is an interaction model, not a skin. The user brings decades of muscle memory for windows, menus, shortcuts, focus, selection, dialogs, tables, files, and mouse/keyboard workflows. Brand can shape palette, typography, iconography, density, charts, and domain visualization, but standard desktop behavior remains recognizable. For data-heavy professional tools, Qt Widgets is usually the natural default; use Qt Quick when touch, fluid animation, or a scene-oriented UI is genuinely central rather than to make a desktop tool resemble a web app.

## The Qt desktop slop test

Would a fluent desktop user understand the application's command structure without being taught a new operating system? Warning signs are a QMainWindow that behaves like a responsive website, giant mobile controls, every group turned into a rounded card, hover-only commands, fixed-pixel geometry, custom title bars with lost window behavior, decorative sidebars replacing discoverable menus/actions, and heavily restyled controls whose focus/disabled/selection states no longer read.

Use Qt to make a native desktop product, not to host a browser-shaped product.

## Application shell & command structure

- **Use QMainWindow as a desktop workspace when the product has persistent commands or panes.** Put the primary work surface in the central widget; use QMenuBar, QToolBar, QStatusBar, and QDockWidget when the workflow needs those roles rather than rebuilding them from generic frames.
- **Actions are the command source of truth.** Reuse QAction for menu, toolbar, shortcut, and contextual entry points so enabled/checked/text/icon state does not drift across duplicate controls.
- **Use QSplitter for user-resizable work areas.** Engineering editors, navigators, plots, inspectors, and result panels benefit from direct pane control more than fixed percentage layouts.
- **Persist workspace state deliberately.** QSettings plus QMainWindow saveGeometry/saveState can restore the user's working arrangement. `restoreGeometry()` already handles ordinary off-screen restoration; add manual screen clamping only for a demonstrated edge case, such as application-owned secondary-window coordinates that bypass Qt's normal restoration path.
- **Keep native window management unless the product has a real reason not to.** Frameless/custom title bars inherit responsibility for move, resize, snap, system menu, accessibility, focus, maximization, multi-monitor, and platform-specific chrome. Cosmetic novelty alone does not earn that cost.

## Layout, density & resizing

- **Layouts own geometry.** Use QHBoxLayout/QVBoxLayout/QGridLayout/QFormLayout and nested composition; fixed `setGeometry()` coordinates are for deliberately custom canvases, not ordinary application UI.
- **Size hints and policies carry intent.** Prefer `sizeHint`, `minimumSizeHint`, `QSizePolicy`, layout stretch, and content-driven sizing over magic widths/heights. Fixed dimensions are reserved for genuine primitives such as an icon target or a domain drawing invariant.
- **Design a useful window range, not one screenshot size.** Establish a meaningful minimum size, verify normal laptop dimensions, then verify wide/large workstations. Reflow, collapse secondary detail, or make panes user-resizable before introducing horizontal scrolling.
- **Professional density is allowed.** Forms, tables, trees, inspectors, and engineering results can be compact. Density stays legible through alignment, grouping, headers, spacing rhythm, and hierarchy rather than card padding.
- **Use scroll areas only for actual overflow.** A scroll area is not a substitute for resolving a layout that cannot fit its essential controls.

## High DPI & multi-monitor

- **Treat widget geometry as device-independent.** Qt's high-level Widgets/Quick APIs already map logical geometry through the device pixel ratio; do not manually multiply widget sizes by DPR.
- **Assets must survive scaling.** Prefer QIcon/SVG or provide appropriate high-resolution raster variants. When working directly with QImage/QPixmap or lower-level rendering, carry devicePixelRatio correctly.
- **Mixed-DPI moves are a real state change.** Re-check custom canvases, cached pixmaps, plots, rulers, hit areas, and text when a window moves between monitors with different scale factors.
- **Never infer virtual-desktop adjacency by raw coordinates.** Use QGuiApplication.screens() and each QScreen's available geometry when placing/restoring windows.

## Styling & theming

- **QStyle owns standard control behavior and metrics.** Qt's built-in widgets delegate their native look/feel to QStyle. Preserve that machinery even when the visual system is branded. QProxyStyle is the narrow tool for metric/behavior adjustments that genuinely belong at style level.
- **QPalette is semantic color infrastructure.** Start from the current style/application palette and modify roles, not every widget with literal colors. Cover Active, Inactive, and Disabled groups and the roles the product actually uses. Native styles do not necessarily honor every palette role, so verify the rendered result and use QStyle, scoped QSS, or custom painting only where a role has no effect.
- **QSS is a controlled visual layer, not a replacement rendering engine.** Use stylesheets for deliberate brand treatment, but avoid global selectors that erase platform metrics, inaccessible focus indicators, or state-specific behavior. Prefer object names/dynamic properties for scoped variants.
- **Style standard widgets in all states.** Default, hover where meaningful, keyboard focus, pressed, checked/selected, disabled, inactive-window, validation error, and read-only states must remain distinguishable.
- **Choose native style vs Fusion intentionally.** Native styles maximize OS familiarity; Fusion can provide cross-platform visual consistency. Either choice still owes desktop command, focus, dialog, and window semantics.
- **Dark mode is not inversion.** Build semantic palette roles and verify plots, icons, alternating rows, tooltips, disabled text, selections, and custom painting in every shipped appearance.

## Typography & icons

- **System UI typography is a strong default for Operate surfaces.** A product font may carry headings or branded moments, but dense labels, forms, tables, menus, and controls prioritize clarity and OS text scaling.
- **Use QFont roles/point sizing, not CSS pixel thinking.** Respect the application/system font and user scaling; avoid dozens of local hard-coded font sizes.
- **Tabular data deserves numeric discipline.** Align comparable values, use locale-aware formatting where appropriate, keep units explicit, and use tabular numerals when the chosen font supports them.
- **Use a coherent icon system through QIcon.** Standard platform actions may use QStyle standard pixmaps/theme icons; custom product actions use one consistent authored/library set. Never use Unicode glyphs or emoji as substitute icons.
- **Icon-only controls need names.** Pair a concise tooltip with accessibleName; add accessibleDescription only when the action needs more context.

## Forms, validation & data entry

- **QFormLayout is a semantic default for label/control pairs.** Keep labels aligned and close to their field; use sections only when they reflect a real mental model.
- **Use the right control for the data.** QSpinBox/QDoubleSpinBox for bounded numbers, QComboBox for a real option set, validators for formatted free entry, date/time controls for dates, and explicit unit labels/suffixes for engineering values.
- **Labels provide keyboard access.** Use mnemonic text and QLabel.setBuddy() where appropriate so forms remain efficient without the mouse.
- **Validation is local and actionable.** Mark the field, state the problem and recovery, preserve the user's input, and move focus only when doing so helps. A modal warning for every bad cell is desktop-hostile.
- **Enter/Escape and default buttons stay predictable.** Use default/autoDefault deliberately in dialogs; do not let an accidental Enter trigger a destructive operation.

## Tables, trees & model/view

- **Use model/view for scalable or shared data.** QTableView/QTreeView/QListView with QAbstractItemModel (or an appropriate standard model) separates data from presentation and supports large/dynamic datasets better than proliferating item widgets.
- **Prefer delegates to per-cell child widgets.** QStyledItemDelegate keeps editing/painting scalable and consistent. Persistent cell widgets are for rare controls, not thousands of rows.
- **Sorting/filtering belongs in the model pipeline.** QSortFilterProxyModel and domain models keep view code from becoming a second data engine.
- **Selection is a first-class state.** Current item, multi-selection, hover, disabled rows, validation, and keyboard navigation must remain visually distinct.
- **Headers carry interaction.** Set sensible resize modes, alignment, sort indicators, units, and column persistence. Do not truncate the meaning out of an engineering table to make a screenshot tidy.
- **Virtualize custom heavy views.** For very large datasets/scenes, avoid rebuilding every visual object on each edit; update the affected model range or scene items.

## Keyboard, focus & accessibility

- **Tab order follows the task, not construction order.** Verify Tab and Shift+Tab across every form and dialog; setTabOrder where implicit order does not match reading/workflow order.
- **Focus remains visible.** Branded QSS/custom painting must preserve a clear keyboard focus indication with sufficient contrast.
- **Use standard shortcuts where the OS already has a convention.** QKeySequence.StandardKey lets Copy/Paste/Undo/Redo/Open/Save and peers resolve appropriately across platforms.
- **Actions stay reachable without hover.** Tooltips may explain; hover may preview; neither may be the only route to a command.
- **Name custom/icon controls for assistive technology.** Set accessibleName and, when needed, accessibleDescription; expose coherent roles/state for custom widgets.
- **Do not encode meaning only in color.** Error, warning, selection, convergence, utilization, and engineering pass/fail states need text/icon/pattern/shape support as appropriate.

## Dialogs, menus & transient UI

- **Modality is earned.** Use a modal dialog for a bounded decision/task that must complete before the parent can continue; use docks, inline expansion, inspectors, or modeless windows for persistent reference/workflows.
- **QDialogButtonBox carries platform ordering.** Use standard button roles instead of hand-ordering OK/Cancel differently on every OS.
- **Use native/system file dialogs by default.** They carry platform locations, permissions, history, keyboard behavior, and user expectations.
- **Context menus are contextual, not hidden primary navigation.** Every essential command needs an obvious normal path too.
- **Tooltips are explanations, not labels the UI forgot to show.** A user should not have to sweep the mouse across a toolbar to understand the primary workflow.

## Domain canvases, plots & engineering visualization

- **Custom drawing is for domain meaning.** QPainter/QGraphicsView/pyqtgraph can own plans, reinforcement, soil profiles, interaction diagrams, and other specialized views; standard controls around them should remain standard.
- **Zoom/pan/fit are consistent.** Mouse wheel/drag semantics, zoom limits, Reset/Fit action, cursor feedback, and selection behavior should match across every canvas in the product.
- **Keep annotations legible at every DPR and zoom.** Screen-space labels, line weights, selection handles, and hit areas need intentional scaling; do not let a beautiful print coordinate system make the interactive view unreadable.
- **Separate engineering truth from painting.** Views render model/results; they do not own structural/geotechnical equations merely because the numbers are visible there.
- **Do not compute heavily inside paintEvent.** Prepare/cache domain geometry and invalidate only what changed.

## Responsiveness, threading & long work

- **The GUI thread must remain interactive.** Long I/O, optimization, report generation, meshing, or numerical calculation does not run synchronously inside button slots or change handlers.
- **Workers report through signals.** QThread/QThreadPool/QtConcurrent or the project's concurrency layer may do background work; QWidget and other GUI objects are updated on the GUI thread.
- **Cancellation/progress reflect real work.** Long operations expose meaningful progress when measurable, an indeterminate state when not, and cancellation only when it is actually safe.
- **Batch UI updates.** Model resets, scene rebuilds, signal storms, and repeated relayouts can dominate otherwise fast engineering code; coalesce updates around the smallest changed range.

## Motion

- **Motion communicates continuity or state.** Short QPropertyAnimation/Qt Quick transitions may explain expansion, docking, selection, or mode change; a professional tool does not need page-load choreography.
- **Never delay the task for animation.** Keyboard commands and repeated operations must remain fast enough that animation does not become input latency.

## Verifying the build

- **Capture the real native window, never a browser recreation.** Run the application on each supported desktop OS that materially changes behavior; identify the OS, Qt binding/version, theme, and scaling behind screenshots or findings.
- **Resize in one bounded pass.** Check the meaningful minimum, normal laptop, and large/wide workspace; include dialogs and secondary windows.
- **Test DPI explicitly.** On Windows include 100%, 125%, 150%, and 200% (plus other supported scales that exposed defects); when possible move the same window across mixed-DPI displays. Qt's `QT_SCALE_FACTOR` is useful for controlled regression coverage but does not replace a real OS scaling pass.
- **Keyboard-only pass.** Traverse every core workflow with Tab/Shift+Tab, standard shortcuts, menus, Escape, Enter/default buttons, table/tree navigation, and context alternatives.
- **Appearance pass.** Verify shipped light/dark/high-contrast behavior, inactive windows, disabled controls, selection, focus, tooltips, plots/canvases, and validation.
- **Automate interaction regressions.** Reuse the project's QTest/pytest-qt tests when available; add focused tests for tab/shortcut/state behavior rather than snapshotting implementation details.

## Qt Widgets vs Qt Quick

Choose by interaction needs, not trend. This reference is authoritative for Qt Widgets behavior and desktop conventions. Qt Quick shares the desktop principles here, but its Controls, styling, focus, layout, and scene-graph details require Qt Quick-specific guidance rather than treating QWidget rules as literal implementation instructions.

- **Qt Widgets**: default for mature desktop conventions, forms, data tables/trees, MDI-like workspaces, menus/toolbars/docks, engineering and productivity tools.
- **Qt Quick**: appropriate for scene-oriented, touch-heavy, highly animated, embedded, or custom visual experiences where the declarative item model is the product's natural grammar.
- **Hybrid**: possible, but every bridge adds focus, styling, DPI, rendering, and lifecycle complexity. Use it for a concrete benefit, not to gradually rewrite ordinary forms.

## Never

- Never translate a web design system into QSS property-for-property and call the result native.
- Never use fixed coordinates for ordinary form/application layout.
- Never remove standard focus, disabled, selection, or shortcut behavior for visual cleanliness.
- Never make hover the only discovery/access path.
- Never hand-build thousands of table cell widgets when model/view/delegates fit.
- Never run heavy domain computation synchronously in GUI event handlers or paint paths.
- Never update QWidget objects from worker threads.
- Never ship a custom title bar without reproducing the platform behaviors it replaced.
- Never validate a desktop UI at one window size, one DPI, and one theme.
- Never confuse visual restraint with low capability: professional desktop software may be dense when the task is dense.
