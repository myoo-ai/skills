export interface Usage {
  account: string;
  day: string;
  requests: number;
}

export function dailyTotals(rows: Usage[]): Map<string, number> {
  const totals = new Map<string, number>();
  for (const row of rows) {
    totals.set(row.day, (totals.get(row.day) ?? 0) + row.requests);
  }
  return totals;
}

export function topAccounts(rows: Usage[], limit: number): string[] {
  const perAccount = Map.groupBy(rows, (row) => row.account);
  return [...perAccount]
    .map(([account, list]) => ({ account, requests: list.reduce((sum, r) => sum + r.requests, 0) }))
    .toSorted((a, b) => b.requests - a.requests)
    .slice(0, limit)
    .map((entry) => entry.account);
}
