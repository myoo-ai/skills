// lines: an iterable of log lines such as
//   "2026-11-02T10:00:00Z ERROR checkout failed for ann"
// Returns the first `limit` ERROR lines.
export function firstErrors(lines, limit) {
  const all = Array.from(lines);
  return all.filter((line) => line.split(' ')[1] === 'ERROR').slice(0, limit);
}

// requests: an array of { user, path } objects.
// Returns the requests grouped by user name.
export function requestsByUser(requests) {
  return requests.reduce((groups, request) => {
    if (!groups[request.user]) groups[request.user] = [];
    groups[request.user].push(request);
    return groups;
  }, {});
}

// lastWeek, thisWeek: arrays of user names (no duplicates within one array).
// Returns the users of this week who were also active last week.
export function returningUsers(lastWeek, thisWeek) {
  return thisWeek.filter((user) => lastWeek.includes(user));
}

// Returns the users of this week who were not active last week.
export function newUsers(lastWeek, thisWeek) {
  return thisWeek.filter((user) => !lastWeek.includes(user));
}
