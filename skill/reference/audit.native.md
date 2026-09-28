Run systematic **technical** quality checks on a native app (`ios` / `android` / `adaptive` / `desktop`) and generate a comprehensive report. Don't fix issues; document them for other commands to address.

This is a code-level audit, not a design critique. Audit from source. Mobile native may be SwiftUI / UIKit / Compose / React Native / Flutter; desktop native may be Qt Widgets / Qt Quick through PySide6 or PyQt6. No browser tooling or `impeccable detect` applies. Score against the platform reference(s): [ios.md](ios.md), [android.md](android.md), both for `adaptive`, or [qt.md](qt.md) for `desktop`. Read the applicable reference before scoring if Setup has not already injected it. The report skeleton mirrors [audit.md](audit.md); keep the two in sync when changing shared reporting structure.

## Diagnostic Scan

Run comprehensive checks across 5 dimensions. Score each dimension 0-4 using the criteria below. Apply only the checks relevant to the declared platform; do not penalize a desktop app for lacking mobile gestures or a mobile app for lacking desktop menus.

### 1. Accessibility & Input

**Check for**:
- **Missing semantics**: interactive elements without accessible labels, roles/traits, state, or useful descriptions
- **Reading and focus order**: illogical traversal, unreachable controls, focus lost after navigation or updates
- **Scaling**: fixed type/layout choices that clip at large Dynamic Type / Android font scale / desktop DPI and text scaling
- **Target sizing and input reachability**: undersized mobile touch targets; desktop controls that are mouse-only, hover-only, or absent from the tab/shortcut path
- **Motion preferences**: nonessential motion with no reduced-motion path where the platform exposes one
- **Contrast and non-color cues**: state or validation that disappears in dark/high-contrast appearance or is conveyed only by color

**Desktop Qt specifics**: inspect `focusPolicy`, tab order, label buddies/mnemonics, `QKeySequence.StandardKey` / actions, visible keyboard focus, and `accessibleName` / `accessibleDescription` for icon-only or custom controls.

**Score 0-4**: 0=major tasks inaccessible without one input mode/assistive technology, 1=major gaps, 2=partial, 3=good with minor gaps, 4=excellent across the shipped input and accessibility paths.

### 2. Performance & Responsiveness

**Check for**:
- **Slow startup**: heavy work before the first usable frame/window
- **Unvirtualized or unmodeled data**: long mobile lists without recycling; large Qt tables/trees built as thousands of child widgets instead of model/view
- **Main/GUI-thread blocking**: synchronous I/O, calculation, parsing, or rendering in interaction paths
- **Wasted rendering**: unnecessary recomposition/re-rendering, full scene/table rebuilds for local changes, expensive paint handlers
- **Image/graphics handling**: full-size assets for thumbnails, unnecessary raster work, DPR mistakes, repeated plot/scene allocations
- **App weight**: unused dependencies, assets, plugins, or bundled runtimes

**Desktop Qt specifics**: look for expensive work in slots, event handlers, `paintEvent`, and model callbacks; unsafe QWidget access from worker threads; per-cell widgets at scale; avoidable `QGraphicsScene` churn.

**Score 0-4**: 0=interaction regularly stalls, 1=major blocking/jank, 2=partial, 3=good with isolated hotspots, 4=fast startup and responsive interaction under realistic data.

### 3. Appearance & Theming

**Check for**:
- **Hard-coded visual roles** that bypass the platform/design token system
- **Broken dark/light/high-contrast appearance**
- **Incomplete state vocabulary**: active/inactive, selected, focused, disabled, hover/pressed where applicable, error/warning/success
- **Off-platform materials/control painting** that sacrifices interaction semantics for decoration
- **Inconsistent typography, iconography, spacing, and density** across the product

**Desktop Qt specifics**: prefer `QStyle` / `QPalette` roles and their Active/Inactive/Disabled groups; review application-wide QSS for brittle global selectors, literal state colors, overwritten focus indicators, and custom-painted controls that ignore `QStyleOption`.

**Score 0-4**: 0=ad hoc styling everywhere, 1=minimal system, 2=partial/inconsistent, 3=coherent with minor drift, 4=semantic, state-complete, and robust across appearances.

### 4. Platform Conformance (CRITICAL)

Score against the loaded platform reference(s), including their slop tests.

**Mobile checks**:
- system navigation/back gestures and insets
- platform controls, icon language, safe areas, modality
- no web-shaped controls or hover-dependent affordances

**Desktop Qt checks**:
- recognizable desktop command structure where the workflow needs it: menu/actions, toolbars, context menus, status feedback, docks/splitters rather than mobile navigation transplanted onto a large window
- standard shortcuts, button/dialog conventions, file pickers, clipboard/drag-drop when those workflows exist
- native window management and resizing; no gratuitous fake title bars or fixed-canvas app shells
- standard Qt controls keep their interaction behavior even when branded
- data-heavy views use desktop-native selection, headers, keyboard navigation, sorting/filtering affordances, and contextual actions

**Score 0-4**: 0=foreign interaction model that fights the platform, 1=heavy violations, 2=several noticeable violations, 3=mostly conformant, 4=a platform-fluent user can operate every core workflow without relearning standard behavior.

### 5. Adaptivity & Environment

**Mobile checks**:
- phone/tablet restructuring, orientation, safe-area/IME handling, multitasking, foldables where applicable

**Desktop Qt checks**:
- useful minimum through large window sizes; no clipped fixed geometry
- layout behavior under 100%, 125%, 150%, 175%, and 200% scaling where the target OS supports those settings
- mixed-DPI/multi-monitor moves and restored window geometry
- light/dark/high-contrast or other target-OS appearance changes
- platform differences across the operating systems the app actually ships to
- long localization strings, numeric/unit formatting, and right-to-left behavior when in scope

**Score 0-4**: 0=one fixed environment only, 1=major resize/DPI/device breakage, 2=partial, 3=good with minor edge cases, 4=robust across the shipped size, scale, and windowing matrix.

## Generate Report

### Audit Health Score

| # | Dimension | Score | Key Finding |
|---|-----------|-------|-------------|
| 1 | Accessibility & Input | ? | [most critical issue or "--"] |
| 2 | Performance & Responsiveness | ? | |
| 3 | Appearance & Theming | ? | |
| 4 | Platform Conformance | ? | |
| 5 | Adaptivity & Environment | ? | |
| **Total** | | **??/20** | **[Rating band]** |

**Rating bands**: 18-20 Excellent (minor polish), 14-17 Good (address weak dimensions), 10-13 Acceptable (significant work needed), 6-9 Poor (major overhaul), 0-5 Critical (fundamental issues)

### Platform Conformance Verdict

**Start here.** Pass/fail: does the product read and behave as a native app for its declared platform, or as a ported interaction model? List concrete violations. For desktop Qt, distinguish visual branding from interaction conformance: a custom palette is not a platform violation; removing standard desktop behavior often is.

### Executive Summary
- Audit Health Score: **??/20** ([rating band])
- Total issues found (count by severity: P0/P1/P2/P3)
- Top 3-5 critical issues
- Recommended next steps

### Detailed Findings by Severity

Tag every issue with **P0-P3 severity**:
- **P0 Blocking**: Prevents task completion. Fix immediately
- **P1 Major**: Significant difficulty or platform-guideline violation. Fix before release
- **P2 Minor**: Annoyance, workaround exists. Fix in next pass
- **P3 Polish**: Nice-to-fix, no real user impact. Fix if time permits

For each issue, document:
- **[P?] Issue name**
- **Location**: Screen, file, line
- **Category**: Accessibility & Input / Performance / Theming / Conformance / Adaptivity
- **Impact**: How it affects users
- **Guideline**: The loaded platform rule it violates
- **Recommendation**: How to fix it in the actual framework
- **Suggested command**: Which command to use (prefer: {{available_commands}})

### Patterns & Systemic Issues

Identify recurring problems that indicate systemic gaps rather than one-off mistakes, for example:
- "Literal colors bypass QPalette roles across the shared Qt theme, so disabled/focus states drift together."
- "Long-running calculations execute synchronously from button slots in multiple tabs."
- "Tab order follows construction order rather than the form's reading order."

### Positive Findings

Note what is working well and should be preserved.

## Recommended Actions

List recommended commands in priority order (P0 first, then P1, then P2):

1. **[P?] `{{command_prefix}}command-name`**: Brief description
2. **[P?] `{{command_prefix}}command-name`**: Brief description

**Rules**: Only recommend commands from: {{available_commands}}. Map findings to the most appropriate command. End with `{{command_prefix}}impeccable polish` as the final step if any fixes were recommended.

After presenting the summary, tell the user:

> You can ask me to run these one at a time, all at once, or in any order you prefer.
>
> Re-run `{{command_prefix}}impeccable audit` after fixes to see your score improve.

**IMPORTANT**: Be thorough but actionable. Too many P3 issues creates noise. Focus on what actually matters.

**NEVER**:
- Report issues without explaining impact
- Apply mobile-only checks to desktop or desktop-only checks to mobile
- Provide generic recommendations
- Skip positive findings
- Forget to prioritize
- Report false positives without verification
