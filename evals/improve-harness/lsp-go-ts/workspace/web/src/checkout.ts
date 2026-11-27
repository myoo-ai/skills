import { fetchQuote, type Zone } from "./api.js";

export async function shippingLabel(grams: number, zone: Zone): Promise<string> {
  const cents = await fetchQuote(grams, zone);
  return `Shipping: €${(cents / 100).toFixed(2)}`;
}
