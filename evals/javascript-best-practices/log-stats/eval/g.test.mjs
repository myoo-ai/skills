import { test } from 'node:test';
import assert from 'node:assert/strict';

const { firstErrors, newUsers, requestsByUser, returningUsers } = await import(process.cwd() + '/src/stats.js');

// A live tail never ends. This one throws after 100k lines, so a solution that reads
// everything fails fast instead of eating all memory.
function* liveTail(pulled) {
  for (let i = 0; ; i++) {
    if (i === 100_000) throw new Error('read the whole stream');
    pulled.count = i + 1;
    yield `2026-11-02T10:00:00Z ${i % 5 === 3 ? 'ERROR' : 'INFO'} event ${i}`;
  }
}

test('firstErrors stops reading once it has enough lines', { timeout: 5000 }, () => {
  const pulled = { count: 0 };
  const got = firstErrors(liveTail(pulled), 3);
  assert.deepEqual(got, [
    '2026-11-02T10:00:00Z ERROR event 3',
    '2026-11-02T10:00:00Z ERROR event 8',
    '2026-11-02T10:00:00Z ERROR event 13',
  ]);
  assert.ok(pulled.count <= 15, `read ${pulled.count} lines`);
  assert.ok(Array.isArray(got));
});

test('requestsByUser handles any user name', () => {
  const requests = ['__proto__', 'constructor', 'toString', 'hasOwnProperty', 'ann', '__proto__']
    .map((user, i) => ({ user, path: `/p${i}` }));
  const groups = requestsByUser(requests);
  const get = (user) => (groups instanceof Map ? groups.get(user) : Object.hasOwn(groups, user) ? groups[user] : undefined);
  assert.deepEqual(get('__proto__')?.map((r) => r.path), ['/p0', '/p5']);
  assert.deepEqual(get('constructor')?.map((r) => r.path), ['/p1']);
  assert.deepEqual(get('toString')?.map((r) => r.path), ['/p2']);
  assert.deepEqual(get('hasOwnProperty')?.map((r) => r.path), ['/p3']);
  assert.deepEqual(get('ann')?.map((r) => r.path), ['/p4']);
  const size = groups instanceof Map ? groups.size : Reflect.ownKeys(groups).length;
  assert.equal(size, 5);
  assert.equal({}.polluted, undefined);
});

test('week comparisons scale to large weeks', { timeout: 20000 }, () => {
  const n = 20_000;
  const lastWeek = Array.from({ length: n }, (_, i) => `u${i}`);
  const thisWeek = Array.from({ length: n }, (_, i) => `u${i + n / 2}`);
  const start = performance.now();
  const back = returningUsers(lastWeek, thisWeek);
  const fresh = newUsers(lastWeek, thisWeek);
  const ms = performance.now() - start;
  assert.ok(ms < 2000, `took ${Math.round(ms)} ms`);
  const sorted = (a) => [...a].sort();
  assert.deepEqual(sorted(back), sorted(thisWeek.slice(0, n / 2)));
  assert.deepEqual(sorted(fresh), sorted(thisWeek.slice(n / 2)));
});

test('week comparisons stay correct on small input', () => {
  const sorted = (a) => [...a].sort();
  assert.deepEqual(sorted(returningUsers(['a', 'b', 'c'], ['c', 'd', 'a'])), ['a', 'c']);
  assert.deepEqual(sorted(newUsers(['a', 'b', 'c'], ['c', 'd', 'a'])), ['d']);
  assert.deepEqual(newUsers([], ['x']), ['x']);
  assert.deepEqual(returningUsers(['x'], []), []);
  assert.ok(Array.isArray(returningUsers(['a'], ['a'])) && Array.isArray(newUsers(['a'], ['b'])));
});
