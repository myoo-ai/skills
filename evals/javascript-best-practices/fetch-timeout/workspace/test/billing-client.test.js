import { test } from 'node:test';
import assert from 'node:assert/strict';
import { getCustomer, getInvoice } from '../src/billing-client.js';

test('getInvoice returns the parsed invoice', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ id: 'INV-42', totalCents: 1999 }));
  assert.deepEqual(await getInvoice('INV-42'), { id: 'INV-42', totalCents: 1999 });
});

test('getCustomer requests the customer URL', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ id: 'C-7', email: 'ann@example.com' }));
  await getCustomer('C-7');
  assert.equal(String(globalThis.fetch.mock.calls[0].arguments[0]), 'https://billing.example.com/customers/C-7');
});
