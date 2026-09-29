# Operate mode depth (and Read notes)

When design SERVES the product: app UIs, admin dashboards, settings panels, data tables, native desktop tools, authenticated surfaces, anything where the user is in a task. The essentials live in SKILL.md's modes and [craft-floor.md](craft-floor.md); this file is extended depth, written for Operate surfaces. Read surfaces (docs, guides, long-form) take SKILL.md's Read mode plus this file's typography and consistency rules; their prose measure and navigation matter more than component density. On native platforms, the loaded platform reference owns control anatomy, units, windowing, focus, and verification; web-specific examples below are illustrative, not an instruction to recreate browser idioms.

## The product slop test

Familiarity is often a feature here. The test is whether a category-fluent user can trust the interface immediately or must pause at every subtly-off component.

Product UI's failure mode isn't flatness, it's strangeness without purpose: over-decorated buttons, mismatched form controls, gratuitous motion, display fonts where labels should be, invented affordances for standard tasks. The bar is earned familiarity. The tool should disappear into the task.

## Typography

- **One family is often right.** Product UIs don't need display/body pairing. A well-tuned sans carries headings, buttons, labels, body, data. <!-- rule:product-typo-one-family -->
- **Fixed role-based scale, not fluid display math.** On web this commonly means a fixed rem scale; on native use the platform typography units and system scaling from its reference. Clamp-sized headings do not serve product UI. <!-- rule:product-typo-fixed-rem-scale -->
- **Tighter scale ratio.** 1.125–1.2 between steps is typical. More type elements here than on brand surfaces; exaggerated contrast creates noise. <!-- rule:product-typo-tighter-ratio -->
- **Line length still applies for prose** (65–75ch). Data and compact UI can run denser; tables at 120ch+ are fine. <!-- rule:product-typo-line-length -->

## Color

Product defaults to Restrained. A single surface can earn Committed (a dashboard where one category color carries a report, an onboarding flow with a drenched welcome screen), but Restrained is the floor. <!-- rule:product-color-restrained-default -->

- State-rich semantic vocabulary: hover, focus, active, disabled, selected, loading, error, warning, success, info. Standardize these. <!-- rule:product-color-state-vocab -->
- Accent color used for primary actions, current selection, and state indicators only, not decoration. <!-- rule:product-color-accent-only -->
- A second neutral layer for sidebars, toolbars, and panels (slightly cooler or warmer than the content surface). <!-- rule:product-color-second-neutral -->

## Layout

- Responsive behavior is structural (collapse sidebar, responsive table, breakpoint-driven columns), not fluid typography. <!-- rule:product-layout-responsive-structural -->

## Components

Every interactive component has: default, hover, focus, active, disabled, loading, error. Don't ship with half of these. <!-- rule:product-components-all-states -->

- Skeleton states for loading, not spinners in the middle of content. <!-- rule:product-components-skeleton-loading -->
- Empty states that teach the interface, not "nothing here." <!-- rule:product-components-empty-states -->
- Consistent affordances across the surface. Same button shape. Same form-control vocabulary. Same icon style. <!-- rule:product-components-consistent-affordances -->
- Overlays escape their container. On web, use a top-layer/dialog/popover/portal rather than clipping inside overflow. On native desktop, use the toolkit's popup, menu, completer, tooltip, or dialog surfaces rather than simulating browser overlay mechanics. <!-- rule:skill-interaction-dropdown-clipping -->

## Motion

- 150–250 ms on most transitions. Users are in flow; don't make them wait for choreography. <!-- rule:product-motion-quick-transitions -->
- Motion conveys state, not decoration. State change, feedback, loading, reveal: nothing else. <!-- rule:product-motion-state-not-decoration -->
- No orchestrated page-load sequences. Product loads into a task; users don't want to watch it load. <!-- rule:product-motion-no-page-load-sequence -->

## Product constraints

- Decorative motion that doesn't convey state. <!-- rule:product-ban-decorative-motion -->
- Inconsistent component vocabulary across screens. If the "save" button looks different in two places, one is wrong. <!-- rule:product-ban-inconsistent-components -->
- Display fonts in UI labels, buttons, data. <!-- rule:product-ban-display-fonts-ui -->
- Reinventing standard affordances for flavor (custom scrollbars, weird form controls, non-standard modals). <!-- rule:product-ban-reinvented-affordances -->
- Heavy color or full-saturation accents on inactive states. <!-- rule:product-ban-heavy-inactive-color -->
- Modal as first thought. Modals are usually laziness. Exhaust inline / progressive alternatives first. <!-- rule:product-ban-modal-first-thought -->

## Product permissions

Product can afford things brand surfaces can't.

- System fonts and familiar sans defaults.
- Standard navigation patterns: top bar + side nav, breadcrumbs, tabs, command palettes.
- Density. Tables with many rows, panels with many labels, dense information when users need it.
- Consistency over surprise. The same visual vocabulary screen to screen is a virtue; delight is saved for moments, not pages.
