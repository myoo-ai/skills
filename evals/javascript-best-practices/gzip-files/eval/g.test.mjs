import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readdirSync } from 'node:fs';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { gunzipSync } from 'node:zlib';

const { compressFile, isGzip } = await import(process.cwd() + '/src/compress.js');

async function scratch(t) {
  const dir = await mkdtemp(join(tmpdir(), 'grader-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  return dir;
}

const openFds = () => readdirSync('/dev/fd').length;

test('compressFile returns a promise and round-trips', async (t) => {
  const dir = await scratch(t);
  const src = join(dir, 'big.csv');
  const data = Buffer.from('row,'.repeat(500_000));
  await writeFile(src, data);
  const pending = compressFile(src, `${src}.gz`);
  assert.equal(typeof pending?.then, 'function');
  await pending;
  assert.deepEqual(gunzipSync(await readFile(`${src}.gz`)), data);
});

test('missing source rejects and leaves no partial output', { timeout: 5000 }, async (t) => {
  const dir = await scratch(t);
  const dest = join(dir, 'missing.csv.gz');
  await assert.rejects(compressFile(join(dir, 'missing.csv'), dest), { code: 'ENOENT' });
  assert.equal(existsSync(dest), false);
});

test('unwritable destination rejects', { timeout: 5000 }, async (t) => {
  const dir = await scratch(t);
  const src = join(dir, 'a.csv');
  await writeFile(src, 'a');
  await assert.rejects(compressFile(src, join(dir, 'no-such-dir', 'a.csv.gz')));
});

test('isGzip resolves a boolean', async (t) => {
  const dir = await scratch(t);
  const src = join(dir, 'a.csv');
  await writeFile(src, 'a,b\n');
  await compressFile(src, `${src}.gz`);
  assert.equal(await isGzip(`${src}.gz`), true);
  assert.equal(await isGzip(src), false);
  await writeFile(join(dir, 'one'), 'x');
  assert.equal(await isGzip(join(dir, 'one')), false);
  await assert.rejects(isGzip(join(dir, 'nope')), { code: 'ENOENT' });
});

test('isGzip closes the file when reading fails', async (t) => {
  const dir = await scratch(t);
  const sub = join(dir, 'a-directory');
  await mkdir(sub);
  const before = openFds();
  for (let i = 0; i < 50; i++) {
    await assert.rejects(isGzip(sub));
  }
  assert.ok(openFds() - before < 5, `${openFds() - before} file descriptors leaked`);
});
