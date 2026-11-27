const BASE_URL = 'https://billing.example.com';

export async function getInvoice(id) {
  const res = await fetch(`${BASE_URL}/invoices/${encodeURIComponent(id)}`);
  return res.json();
}

export async function getCustomer(id) {
  const res = await fetch(`${BASE_URL}/customers/${encodeURIComponent(id)}`);
  return res.json();
}
