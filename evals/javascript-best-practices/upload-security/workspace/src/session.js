// Returns a new session id: 32 lowercase hex characters.
export function newSessionId() {
  let id = '';
  while (id.length < 32) {
    id += Math.floor(Math.random() * 16).toString(16);
  }
  return id;
}
