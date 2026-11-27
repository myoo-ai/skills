import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DEFAULT_SETTINGS, applyUserSettings } from '../src/settings.js';
import { newSessionId } from '../src/session.js';
import { listArchive } from '../src/archive.js';

test('applyUserSettings deep-merges without touching the defaults', () => {
  const got = applyUserSettings(DEFAULT_SETTINGS, '{"theme":{"color":"red"},"locale":"nl"}');
  assert.deepEqual(got, {
    theme: { color: 'red', density: 'normal' },
    notifications: { email: true, sms: false },
    locale: 'nl',
  });
  assert.equal(DEFAULT_SETTINGS.theme.color, 'blue');
});

test('newSessionId returns 32 hex characters', () => {
  assert.match(newSessionId(), /^[0-9a-f]{32}$/);
  assert.notEqual(newSessionId(), newSessionId());
});

test('listArchive lists the tarball entries', async (t) => {
  const dir = await mkdtemp(join(tmpdir(), 'upload-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await writeFile(join(dir, 'a.txt'), 'a');
  execFileSync('tar', ['-cf', 'upload.tar', 'a.txt'], { cwd: dir });
  assert.deepEqual(await listArchive(join(dir, 'upload.tar')), ['a.txt']);
});
