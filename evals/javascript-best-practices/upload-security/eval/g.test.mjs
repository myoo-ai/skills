import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const { DEFAULT_SETTINGS, applyUserSettings } = await import(process.cwd() + '/src/settings.js');
const { newSessionId } = await import(process.cwd() + '/src/session.js');
const { listArchive } = await import(process.cwd() + '/src/archive.js');

test('settings body cannot pollute prototypes', () => {
  for (const body of [
    '{"__proto__":{"polluted":"yes"}}',
    '{"theme":{"__proto__":{"polluted":"yes"}}}',
    '{"constructor":{"prototype":{"polluted":"yes"}}}',
    '{"theme":{"constructor":{"prototype":{"polluted":"yes"}}}}',
  ]) {
    try {
      applyUserSettings(DEFAULT_SETTINGS, body);
    } catch {
      // rejecting the body is fine
    }
    assert.equal({}.polluted, undefined, body);
    assert.equal(Object.prototype.polluted, undefined, body);
  }
  assert.equal(DEFAULT_SETTINGS.theme.color, 'blue');
  const got = applyUserSettings(DEFAULT_SETTINGS, '{"notifications":{"sms":true},"theme":{"density":"compact"}}');
  assert.equal(got.notifications.sms, true);
  assert.equal(got.notifications.email, true);
  assert.equal(got.theme.density, 'compact');
  assert.equal(got.theme.color, 'blue');
  assert.equal(DEFAULT_SETTINGS.notifications.sms, false);
});

test('session ids come from a CSPRNG', (t) => {
  t.mock.method(Math, 'random', () => { throw new Error('Math.random used'); });
  const ids = new Set(Array.from({ length: 100 }, () => newSessionId()));
  assert.equal(ids.size, 100);
  for (const id of ids) assert.match(id, /^[0-9a-f]{32}$/);
});

test('archive file names cannot inject commands', async (t) => {
  const dir = await mkdtemp(join(tmpdir(), 'grader-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await writeFile(join(dir, 'x.txt'), 'x');
  for (const name of ['a$(touch PWNED1).tar', 'b"; touch PWNED2; echo ".tar', 'c`touch PWNED3`.tar']) {
    execFileSync('tar', ['-cf', name, 'x.txt'], { cwd: dir });
    assert.deepEqual(await listArchive(join(dir, name)), ['x.txt'], name);
  }
  for (const marker of ['PWNED1', 'PWNED2', 'PWNED3']) {
    assert.equal(existsSync(join(dir, marker)) || existsSync(marker), false, marker);
  }
});
