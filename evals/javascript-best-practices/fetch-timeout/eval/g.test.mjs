import { test } from 'node:test';
import assert from 'node:assert/strict';
const { getInvoice, getCustomer, HttpError } = await import(process.cwd() + '/src/billing-client.js');
const hang = (_url, init) => new Promise((_resolve, reject) => {
  init?.signal?.addEventListener('abort', () => reject(init.signal.reason), { once: true });
});
test('ok response is parsed', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ id: 'INV-7' }));
  assert.deepEqual(await getInvoice('INV-7'), { id: 'INV-7' });
  assert.equal(String(globalThis.fetch.mock.calls[0].arguments[0]), 'https://billing.example.com/invoices/INV-7');
});
test('non-2xx rejects with HttpError', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ error: 'gone' }, { status: 404 }));
  await assert.rejects(getCustomer('C-1'), (e) => typeof HttpError === 'function' && e instanceof HttpError && e instanceof Error && e.name === 'HttpError' && e.status === 404);
  t.mock.method(globalThis, 'fetch', async () => new Response('oops', { status: 500 }));
  await assert.rejects(getInvoice('INV-1'), (e) => e instanceof HttpError && e.status === 500);
});
test('times out', { timeout: 3000 }, async (t) => {
  t.mock.method(globalThis, 'fetch', hang);
  await assert.rejects(getInvoice('INV-1', { timeoutMs: 50 }));
});
test('caller can cancel', { timeout: 3000 }, async (t) => {
  t.mock.method(globalThis, 'fetch', hang);
  const controller = new AbortController();
  const pending = getCustomer('C-1', { signal: controller.signal });
  setTimeout(() => controller.abort(), 20);
  await assert.rejects(pending);
});
test('network failure keeps the cause', async (t) => {
  const boom = new TypeError('fetch failed');
  t.mock.method(globalThis, 'fetch', async () => { throw boom; });
  await assert.rejects(getInvoice('INV-1'), (e) => e instanceof Error && e.cause === boom);
});
