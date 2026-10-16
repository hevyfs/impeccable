// Astro dev's CSS HMR may race with removal of the temporary live-preview
// <style> block, leaving a stale virtual module index=1 (the final page
// retains only index=0). Only these exact transient errors are candidates
// for recovery; the caller MUST reload and fail on any post-reload error.
export function isStaleAstroCssHmrError(entry) {
  const value = String(entry || '');
  const staleCssUrl = /\/src\/pages\/index\.astro\?(?:t=\d+&)?astro&type=style&index=1&lang\.css(?=\]|\. This could|$)/;
  if (!staleCssUrl.test(value)) return false;
  return /Failed to load resource: the server responded with a status of 500|\[vite\] Failed to reload/.test(value);
}

/**
 * A clean DOM after Vite HMR does not prove that Astro compiled and applied
 * the fixture's surviving stylesheet. This independent visual-computed-style
 * witness must hold after the full reload before any stale HMR error is waived.
 *
 * Fixture invariant: index.astro keeps ".hero-hook { color: #555; }" and
 * ".page { padding: 2rem; }" after accepting changes to its hero title.
 */
export function assertAstroRecoveredStyles(witness) {
  if (!witness?.rulePresent) {
    throw new Error('Astro final reload lost its .hero-hook stylesheet rule');
  }
  if (witness?.hookColor !== 'rgb(85, 85, 85)') {
    throw new Error(`Astro final reload did not apply .hero-hook color: ${witness?.hookColor ?? 'missing'}`);
  }
  if (witness?.pagePaddingLeft !== '32px') {
    throw new Error(`Astro final reload did not apply .page padding: ${witness?.pagePaddingLeft ?? 'missing'}`);
  }
}
