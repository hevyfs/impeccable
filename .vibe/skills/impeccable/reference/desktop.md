# Native desktop platform

Use this reference for native desktop applications on Windows, macOS, and Linux. It defines the desktop interaction model without assuming a toolkit. Toolkit-specific references may layer on top of it when repository evidence supports them.

## Desktop interaction model

Desktop users expect persistent windows, dense information when the task needs it, precise pointer input, efficient keyboard operation, standard selection behavior, and discoverable commands. Do not translate a phone layout or web dashboard literally into a desktop shell.

- Keep primary commands discoverable through the platform's normal menu, toolbar, command, or action mechanisms.
- Support keyboard traversal and standard shortcuts for frequent actions.
- Preserve conventional selection, focus, disabled, read-only, and inactive-window states.
- Use context menus as secondary access, not the only way to find an action.
- Keep window-management behavior native unless the product has a concrete reason to replace it.

## Window and layout behavior

- Design for a meaningful range of window sizes rather than one screenshot size.
- Prefer managed layout systems and resizable regions over fixed coordinates.
- Make minimum sizes reflect the smallest usable workflow, not the smallest technically renderable frame.
- Persist user-owned workspace choices such as window size, pane proportions, and dock placement when the toolkit supports it.
- Verify restored state after monitor topology changes and on systems with multiple displays.

## Input and accessibility

- Mouse and keyboard are both first-class. Hover may reinforce state but never be the only route to a command or explanation.
- Tab/focus order follows task order. Focus indication remains visible.
- Standard copy, paste, undo, redo, save, open, close, and selection shortcuts follow platform conventions.
- Accessible names, roles, descriptions, and state changes must survive custom styling.
- Do not encode status only by color. Use text, icons, shape, or another redundant cue where meaning matters.

## Data-heavy professional software

Desktop tools often need higher information density than consumer mobile interfaces.

- Tables, trees, grids, inspectors, properties, plots, and document panes may be dense when the workflow benefits from comparison and scanning.
- Prefer model-backed or virtualized collections for large datasets.
- Keep units, numeric alignment, precision, validation, and editable/read-only distinctions explicit.
- Domain canvases and plots need predictable pan, zoom, fit, selection, and reset behavior.

## Appearance and theming

- Treat light, dark, high-contrast, inactive-window, selected, focused, disabled, warning, error, and success states as semantic roles rather than isolated colors.
- Respect system text scaling and display scaling.
- Verify icons and custom painting at supported scale factors.
- Branding may shape typography, iconography, palette, density, and domain visualization without erasing desktop control semantics.

## Performance and responsiveness

- Keep the UI thread responsive. Long computation, I/O, parsing, exports, and large model updates must not freeze pointer, keyboard, window, or paint handling.
- Show progress only when it communicates real work; provide cancellation when the operation is meaningfully interruptible.
- Batch expensive visual/model updates where the toolkit provides an efficient mechanism.

## Verification matrix

Run the actual desktop application, not a browser recreation.

1. Minimum usable, normal, and large/wide window sizes.
2. Keyboard-only core workflows and standard shortcuts.
3. Light/dark and any supported high-contrast appearance.
4. Supported display scaling, including a mixed-DPI move when relevant.
5. Maximized/restored state, dialogs, menus, secondary windows, and persisted geometry.
6. Long localized labels, numeric/unit-heavy data, and real error/empty/loading states.

## Toolkit overlays

This file is deliberately toolkit-neutral. When the project uses Qt for Python through PySide/PyQt, also apply `qt.md`. Other desktop stacks need their own toolkit guidance rather than inheriting Qt implementation rules by analogy.
