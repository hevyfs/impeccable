> **Additional context needed**: target platform/device or desktop OS, window-size range, input methods, and usage context.

Adapt an existing **native** design (`ios` / `android` / `adaptive` / `desktop`) to a different context: another device class, orientation, platform, desktop operating system, window size, input posture, or origin. The trap is treating adaptation as scaling. The job is rethinking the experience for the new context inside the applicable [ios.md](ios.md), [android.md](android.md), or [desktop.md](desktop.md) conventions. When a toolkit overlay such as [qt.md](qt.md) has been selected from project evidence, apply it in addition to the desktop baseline. Read the target platform baseline and any applicable overlay before planning if Setup has not already loaded them.

## Assess Adaptation Challenge

1. **Source context**: what was it designed for, and what assumptions did it make? Phone-only? Portrait-only? Fixed desktop window? Mouse-first? One OS's idioms? A website?
2. **Target context**: which device/window class, platform/OS, orientation, scaling/DPI range, input methods, and usage posture?
3. **What breaks**: navigation that does not fit, layouts that stretch instead of restructure, commands that become undiscoverable, gestures/hover/shortcuts that do not exist in the target, or information density that no longer matches the work?

## Mobile-specific adaptation guardrails

- Treat portrait, landscape, split-screen, and multi-window as layout states when the shipped app supports them. Do not assume a single phone aspect ratio.
- On foldables, respect hinge/occlusion regions and posture changes. Do not place primary controls or reading flow across an unusable fold.
- Preserve safe-area/system-bar behavior and software-keyboard recovery while restructuring content.
- iOS to Android and Android to iOS are interaction-model adaptations, not theme swaps. Re-map navigation, back behavior, top/app bars, sheets/dialogs, menus, selection, and standard system actions to the destination OS.
- `adaptive` means the same product intentionally expresses both mobile platform grammars. It does not mean one lowest-common-denominator UI.

## Mobile: Phone → Tablet / Large Screen

- **Restructure, don't stretch.** Use size classes (iOS) / window size classes (Android).
- **Navigation changes shape**: tab bar may become a sidebar on iPad; Android navigation bar becomes a rail or drawer on expanded width.
- **Use the width**: master-detail, multi-column grids, and popovers where appropriate.
- **Multitasking is a size, not an edge case**: iPad Split View and Android multi-window can hand you a compact window on a tablet.

## Desktop: Window and Workstation Adaptation

- **Layouts, not coordinates.** Move fixed geometry into the toolkit's managed layout system; use sensible minimums, flexible regions, resizable panes, and scrolling only where content genuinely overflows.
- **Restructure by available space.** A narrow laptop window may collapse secondary panes or move them behind a command; a wide workstation can expose comparison/detail panes. Preserve capability rather than hiding core tasks.
- **Treat workspace arrangement as user-owned when the product supports it.** Allow resizing/rearrangement where useful, and persist/restore window and pane state through the toolkit's normal mechanisms.
- **High DPI is a matrix.** Test supported scaling and moving the same window between monitors with different scale factors. Keep geometry in the toolkit's device-independent coordinate system and use scale-aware assets/custom painting.
- **Keyboard and mouse remain first-class.** Narrowing a window must not remove actions from menus/commands, shortcuts, context access, or focus traversal. Hover may enhance; it may not be the only explanation or access path.
- **OS adaptation is not a reskin.** Windows, macOS, and Linux differ in menu placement, standard shortcuts, dialog/button conventions, fonts, native file pickers, and window chrome. Prefer the toolkit's platform abstractions before adding OS-specific conditionals.

### Qt toolkit overlay

When Qt for Python evidence is present, apply `qt.md`: use layouts/`QSizePolicy`, `QSplitter`, `QMainWindow` state, `QStyle`/`QPalette`, `QKeySequence.StandardKey`, native dialogs, DPR-aware assets, and the project's QTest/pytest-qt harness where applicable.

## Platform → Platform

Translate idioms; never transplant them.

| Source | Target | Translation |
|---|---|---|
| iOS | Android | HIG navigation/controls → Material navigation/controls; preserve product intent |
| Android | iOS | Material idioms → HIG idioms; preserve product intent |
| Mobile | Desktop | touch navigation → desktop commands, resizable work areas, keyboard shortcuts, and denser data views |
| Desktop | Mobile | desktop command surfaces → touch navigation and sheets; simplify density without deleting core capability |
| Web | Desktop | browser navigation/cards/dropdowns → native window, toolkit controls, desktop commands, and keyboard focus |
| Desktop OS A | Desktop OS B | keep the product system and let the toolkit/platform abstractions resolve standard OS behavior |

### Web → desktop

Reconform, don't wrap and recolor. Replace webpage-shaped navigation with a desktop command model, card grids with appropriate panes/tables/forms, HTML-shaped controls with native toolkit controls, hover-only affordances with explicit commands/tooltips/focus, and CSS breakpoint thinking with resizable layouts. If the toolkit is Qt, apply the concrete QMainWindow/QAction/model-view guidance from `qt.md`; otherwise use the equivalent native mechanisms for that stack.

### Mobile ↔ desktop

Change information density and command topology intentionally. Desktop can expose persistent navigation, multi-pane comparison, rich tables, context menus, and shortcuts because keyboard/mouse and larger windows support them. Mobile must prioritize touch reach, safe areas, and progressive disclosure. Do not keep either platform's shell and merely resize it.

## Implement & Verify

**Mobile**
- Drive structure from size/window classes, not device model checks.
- Respect safe areas/window insets and keyboard/IME.
- Test simulators for breadth and hardware for posture, gesture, and performance truth.

**Desktop**
- Run the real application, not a browser approximation.
- Exercise the minimum supported window, a normal laptop window, and a large/wide workspace.
- Test the target OS scaling matrix; on Windows include fractional scaling when the product supports it. Move the app between mixed-DPI monitors when hardware allows.
- Verify light/dark/high-contrast appearances that the target OS/app supports, keyboard-only operation, standard shortcuts, focus order, long/localized strings, and persisted/restored window state.
- Use the project's native UI test harness for interaction regressions and screenshots from the running native window for visual evidence. When Qt is the detected overlay, that may be `QTest`, pytest-qt, or the existing Qt harness.
- Say which OS/scaling/device produced each visual claim.

When the adaptation is native to its target context, hand off to `/impeccable polish` for the final pass.

**NEVER**:
- Ship a stretched phone layout on a tablet
- Ship a fixed-coordinate desktop layout that clips when resized or scaled
- Port one platform's navigation/control vocabulary unchanged onto another
- Use hover as the only route to a desktop action
- Hide core functionality on smaller contexts instead of restructuring it
- Lock orientation or window size to dodge a layout bug
- Trust one DPI, one theme, one window size, or one simulator as the whole verification matrix
