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

test('Qt native scanner and capture helper regression suite', async (t) => {
  const candidates = process.env.IMPECCABLE_PYTHON
    ? [[process.env.IMPECCABLE_PYTHON]]
    : process.platform === 'win32'
      ? [['py', '-3'], ['python']]
      : [['python3'], ['python']];

  let python = null;
  for (const parts of candidates) {
    const result = await run(parts[0], [...parts.slice(1), '--version']);
    if (!result.error && result.code === 0) {
      python = parts;
      break;
    }
  }
  if (!python) {
    t.skip('Python 3 is not installed; native Qt helper tests require Python 3.11+');
    return;
  }
  const result = await run(python[0], [
    ...python.slice(1), '-m', 'unittest', 'discover',
    '-s', testDirectory, '-p', 'test_*.py', '-v',
  ]);
  assert.equal(result.code, 0, [result.stdout, result.stderr, String(result.error)].join('\n'));
  assert.match(result.stderr, /OK\s*$/m);
});
