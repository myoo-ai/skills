import { test } from 'node:test';
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
const m = await import(process.cwd() + '/src/orders.js');
const data = process.cwd() + '/data/orders.json';
test('loadOrders returns a promise', async () => {
  assert.equal((await m.loadOrders(data)).length, 5);
});
test('invalid JSON keeps the parse error as cause', async () => {
  const bad = process.env.GRADER_DIR + '/bad.json';
  await writeFile(bad, '{nope');
  await assert.rejects(m.loadOrders(bad), (e) => e instanceof Error && e.cause instanceof SyntaxError);
});
test('helpers do not mutate their input', async () => {
  const list = await m.loadOrders(data);
  const before = structuredClone(list);
  assert.deepEqual(m.newestFirst(list).map((o) => o.id), ['A-1003', 'A-1005', 'A-1002', 'A-1004', 'A-1001']);
  assert.equal(m.withDiscount(list[0], 10).lines[0].priceCents, 1125);
  const groups = m.groupByCustomer(list);
  const keys = groups instanceof Map ? [...groups.keys()] : Object.keys(groups);
  assert.deepEqual(keys.sort(), ['ann@example.com', 'bob@example.com', 'cem@example.com']);
  assert.equal((groups instanceof Map ? groups.get('bob@example.com') : groups['bob@example.com']).length, 2);
  assert.equal(m.orderTotal(list[1]), 3797);
  assert.deepEqual(list, before);
});
