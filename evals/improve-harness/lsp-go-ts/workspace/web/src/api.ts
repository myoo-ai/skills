export type Zone = "domestic" | "eu" | "world";

export async function fetchQuote(grams: number, zone: Zone, signal?: AbortSignal): Promise<number> {
  const timeout = AbortSignal.timeout(5_000);
  const res = await fetch(`/quote?grams=${grams}&zone=${zone}`, {
    signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
  });
  if (!res.ok) {
    throw new Error(`quote failed: ${res.status}`);
  }
  const body: { cents: number } = await res.json();
  return body.cents;
}
