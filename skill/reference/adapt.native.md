> **Additional context needed**: target platform/device or desktop OS, window-size range, input methods, and usage context.

Adapt an existing **native** design (`ios` / `android` / `adaptive` / `desktop`) to a different context: another device class, orientation, platform, desktop operating system, window size, input posture, or origin. The trap is treating adaptation as scaling. The job is rethinking the experience for the new context inside the applicable [ios.md](ios.md), [android.md](android.md), or [qt.md](qt.md) conventions; read the target platform reference before planning if Setup has not already loaded it.

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

## Desktop Qt: Window and Workstation Adaptation

- **Layouts, not coordinates.** Move fixed geometry into layouts; use `sizePolicy`, sensible minimums, stretch factors, `QSplitter`, and scroll areas only where content genuinely overflows. <!-- rule:qt-adapt-layouts-not-coordinates -->
- **Restructure by available space.** A narrow laptop window may collapse secondary panes or dock them; a wide workstation can expose comparison/detail panes. Preserve capability rather than hiding core tasks. <!-- rule:qt-adapt-restructure-window -->
- **Treat docks and splitters as user-owned workspace.** Allow resizing/rearrangement when the workflow benefits, and persist/restore geometry and main-window state without restoring a window off-screen. <!-- rule:qt-adapt-persist-workspace -->
- **High DPI is a matrix.** Test fractional scaling and moving the same window between monitors with different DPR. Use device-independent widget geometry and DPR-aware assets rather than multiplying coordinates manually. <!-- rule:qt-adapt-high-dpi -->
- **Keyboard and mouse remain first-class.** Narrowing a window must not remove the action from menus, shortcuts, context menus, or focus traversal. Hover may enhance; it may not be the only explanation or access path. <!-- rule:qt-adapt-input-parity -->
- **OS adaptation is not a reskin.** Windows, macOS, and Linux differ in menu placement, standard shortcuts, dialog/button conventions, fonts, native file pickers, and window chrome. Let Qt's style/actions/standard keys carry those differences before adding platform conditionals. <!-- rule:qt-adapt-os-conventions -->

## Platform → Platform

Translate idioms; never transplant them.

| Source | Target | Translation |
|---|---|---|
| iOS | Android | HIG navigation/controls → Material navigation/controls; preserve product intent |
| Android | iOS | Material idioms → HIG idioms; preserve product intent |
| Mobile | Qt desktop | touch navigation → menu/actions/toolbars/docks/splitters; expose keyboard shortcuts and denser data views |
| Qt desktop | Mobile | desktop command surfaces → touch navigation and sheets; simplify density without deleting core capability |
| Web | Qt desktop | browser nav/cards/dropdowns → native window, actions, standard widgets, model/view, keyboard focus |
| Qt desktop OS A | Qt desktop OS B | keep product system, let QStyle/QPalette/standard keys/dialogs/window chrome resolve OS behavior |

### Web → Qt desktop

Reconform, don't wrap and recolor. Replace webpage-shaped navigation with a desktop command model, card grids with appropriate panes/tables/forms, HTML-shaped controls with Qt controls, hover-only affordances with explicit actions/tooltips/focus, and CSS breakpoint thinking with resizable layouts. A QMainWindow that still behaves like a browser dashboard has not been adapted.

### Mobile ↔ desktop

Change information density and command topology intentionally. Desktop can expose persistent navigation, multi-pane comparison, rich tables, context menus, and shortcuts because keyboard/mouse and larger windows support them. Mobile must prioritize touch reach, safe areas, and progressive disclosure. Do not keep either platform's shell and merely resize it.

## Implement & Verify

**Mobile**
- Drive structure from size/window classes, not device model checks.
- Respect safe areas/window insets and keyboard/IME.
- Test simulators for breadth and hardware for posture, gesture, and performance truth.

**Desktop Qt**
- Run the real application, not a browser approximation.
- Exercise the minimum supported window, a normal laptop window, and a large/wide workspace.
- Test the target OS scaling matrix; on Windows include fractional scaling. Move the app between mixed-DPI monitors when hardware allows.
- Verify light/dark/high-contrast appearances that the target OS/app supports, keyboard-only operation, standard shortcuts, focus order, long/localized strings, and persisted/restored window state.
- Use Qt/Python UI tests (`QTest`, pytest-qt, or the project's existing harness) for interaction regressions; use screenshots from the running native window for visual evidence.
- Say which OS/scaling/device produced each visual claim.

When the adaptation is native to its target context, hand off to `{{command_prefix}}impeccable polish` for the final pass.

**NEVER**:
- Ship a stretched phone layout on a tablet
- Ship a fixed-coordinate desktop layout that clips when resized or scaled
- Port one platform's navigation/control vocabulary unchanged onto another
- Use hover as the only route to a desktop action
- Hide core functionality on smaller contexts instead of restructuring it
- Lock orientation or window size to dodge a layout bug
- Trust one DPI, one theme, one window size, or one simulator as the whole verification matrix
