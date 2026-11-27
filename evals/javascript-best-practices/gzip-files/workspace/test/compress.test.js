import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { gunzipSync } from 'node:zlib';
import { compressFile, isGzip } from '../src/compress.js';

test('compressFile gzips the file', async (t) => {
  const dir = await mkdtemp(join(tmpdir(), 'archiver-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const src = join(dir, 'export.csv');
  await writeFile(src, 'id,total\n1,10\n');
  await new Promise((resolve, reject) => compressFile(src, `${src}.gz`, (err) => (err ? reject(err) : resolve())));
  assert.equal(gunzipSync(await readFile(`${src}.gz`)).toString(), 'id,total\n1,10\n');
  const gz = await new Promise((resolve, reject) => isGzip(`${src}.gz`, (err, ok) => (err ? reject(err) : resolve(ok))));
  const plain = await new Promise((resolve, reject) => isGzip(src, (err, ok) => (err ? reject(err) : resolve(ok))));
  assert.equal(gz, true);
  assert.equal(plain, false);
});
