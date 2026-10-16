import assert from 'node:assert/strict';
import test from 'node:test';
import { isStaleAstroCssHmrError, assertAstroRecoveredStyles } from './astro-hmr-console.mjs';

const staleUrl = 'http://127.0.0.1:4321/src/pages/index.astro?t=1792164382080&astro&type=style&index=1&lang.css';
const viteUrl = 'http://127.0.0.1:4321/src/pages/index.astro?astro&type=style&index=1&lang.css';

test('recognizes only the temporary deleted second Astro style module', () => {
  assert.equal(isStaleAstroCssHmrError(
    `console.error: Failed to load resource: the server responded with a status of 500 (Internal Server Error) [${staleUrl}]`,
  ), true);
  assert.equal(isStaleAstroCssHmrError(
    `console.error: [vite] Failed to reload /src/pages/index.astro?astro&type=style&index=1&lang.css. This could be due to syntax errors or importing non-existent modules. (see errors above) [${viteUrl}]`,
  ), true);
});

test('rejects actual stylesheet and module errors', () => {
  for (const entry of [
    'Failed to load resource: status of 500 [/src/pages/index.astro?astro&type=style&index=0&lang.css]',
    'Failed to load resource: the server responded with a status of 500 [http://127.0.0.1:4321/api/results]',
    'Failed to load resource: the server responded with a status of 500 [/src/pages/index.astro?astro&type=style&index=2&lang.css]',
    '[vite] Failed to reload /src/pages/dashboard.astro?astro&type=style&index=1&lang.css',
    'Uncaught TypeError: Cannot read properties of undefined',
    'Failed to load resource: the server responded with a status of 404 [/favicon.ico]',
    'Failed to load resource: the server responded with a status of 500 [/src/pages/index.astro?astro&type=style&index=1&lang.css&broken]',
  ]) {
    assert.equal(isStaleAstroCssHmrError(entry), false, entry);
  }
});

test('Astro stale HMR recovery must prove the final stylesheet is applied', () => {
  const valid = {
    rulePresent: true,
    hookColor: 'rgb(85, 85, 85)',
    pagePaddingLeft: '32px',
  };
  assert.doesNotThrow(() => assertAstroRecoveredStyles(valid));
  for (const witness of [
    { ...valid, rulePresent: false },
    { ...valid, hookColor: 'rgb(0, 0, 0)' },
    { ...valid, pagePaddingLeft: '0px' },
    null,
  ]) {
    assert.throws(() => assertAstroRecoveredStyles(witness), /Astro final reload/);
  }
});
