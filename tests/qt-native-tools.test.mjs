import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import test from 'node:test';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const testDirectory = path.join(root, 'tests', 'qt-native-tools');

function run(cmd, args) {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, {
      cwd: root,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    let error = null;
    child.stdout.on('data', (data) => { stdout += data.toString(); });
    child.stderr.on('data', (data) => { stderr += data.toString(); });
    child.on('error', (err) => { error = err; });
    child.on('close', (code) => resolve({ code, stdout, stderr, error }));
  });
}

test('Qt native scanner and capture helper regression suite', async () => {
  const candidates = process.env.IMPECCABLE_PYTHON
    ? [[process.env.IMPECCABLE_PYTHON]]
    : process.platform === 'win32'
      ? [['py', '-3'], ['python']]
      : [['python3'], ['python']];

  let python = null;
  for (const parts of candidates) {
    const result = await run(parts[0], [
      ...parts.slice(1),
      '-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)',
    ]);
    if (!result.error && result.code === 0) {
      python = parts;
      break;
    }
  }
  assert.ok(
    python,
    'Python 3.11+ is required to run Qt helper regressions. '
      + 'Install Python or set IMPECCABLE_PYTHON to a valid interpreter.',
  );
  const result = await run(python[0], [
    ...python.slice(1), '-m', 'unittest', 'discover',
    '-s', testDirectory, '-p', 'test_*.py', '-v',
  ]);
  const output = [result.stdout, result.stderr, String(result.error ?? '')].join('\n');
  assert.equal(result.code, 0, output);

  const count = output.match(/\bRan\s+(\d+)\s+tests?\s+in\b/);
  assert.ok(count, `Missing Python unittest test-count summary:\n${output}`);
  assert.ok(
    Number(count[1]) >= 21,
    `Expected at least 21 Qt regression tests, found ${count[1]}:\n${output}`,
  );
  for (const name of [
    'test_python_literals_comments_and_docstrings_are_not_calls',
    'test_qss_selector_reports_its_actual_line',
    'test_qml_fixed_dimensions_are_advisory_not_inventory_only',
    'test_parent_hidden_child_preserves_implicit_visibility',
    'test_constrained_widget_does_not_publish_false_dimensions',
    'test_invalid_png_does_not_publish_fake_evidence',
    'test_predictable_metadata_symlink_is_not_followed',
    'test_final_symlink_destinations_cannot_overwrite_targets',
    'test_failed_json_publication_does_not_leave_png',
  ]) {
    assert.ok(
      output.includes(`${name} (`),
      `Critical Qt regression ${name} was not executed:\n${output}`,
    );
  }
  assert.match(output, /(?:^|\n)OK\s*(?:\n|$)/m);
});
