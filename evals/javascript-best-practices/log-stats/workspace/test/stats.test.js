import { test } from 'node:test';
import assert from 'node:assert/strict';
import { firstErrors, newUsers, requestsByUser, returningUsers } from '../src/stats.js';

test('firstErrors returns the first ERROR lines', () => {
  const lines = [
    '2026-11-02T10:00:00Z INFO login ann',
    '2026-11-02T10:00:01Z ERROR checkout failed for ann',
    '2026-11-02T10:00:02Z ERROR payment declined for bob',
    '2026-11-02T10:00:03Z ERROR checkout failed for cem',
  ];
  assert.deepEqual(firstErrors(lines, 2), [lines[1], lines[2]]);
});

test('requestsByUser groups by user', () => {
  const groups = requestsByUser([
    { user: 'ann', path: '/' },
    { user: 'bob', path: '/cart' },
    { user: 'ann', path: '/checkout' },
  ]);
  const ann = groups instanceof Map ? groups.get('ann') : groups.ann;
  assert.deepEqual(ann.map((r) => r.path), ['/', '/checkout']);
});

test('returning and new users', () => {
  assert.deepEqual(returningUsers(['ann', 'bob'], ['bob', 'cem']), ['bob']);
  assert.deepEqual(newUsers(['ann', 'bob'], ['bob', 'cem']), ['cem']);
});
