// Astro dev's CSS HMR may race with removal of the temporary live-preview
// <style> block, leaving a stale virtual module index=1 (the final page
// retains only index=0). Only these exact transient errors are candidates
// for recovery; the caller MUST reload and fail on any post-reload error.
export function isStaleAstroCssHmrError(entry) {
  const value = String(entry || '');
  const staleCssUrl = /\/src\/pages\/index\.astro\?(?:t=\d+&)?astro&type=style&index=1&lang\.css(?:\b|$)/;
  if (!staleCssUrl.test(value)) return false;
  return /Failed to load resource: the server responded with a status of 500|\[vite\] Failed to reload/.test(value);
}
