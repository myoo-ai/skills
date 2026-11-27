import { exec } from 'node:child_process';
import { promisify } from 'node:util';

const run = promisify(exec);

// Lists the entries of an uploaded tarball; file is the path the upload was saved under,
// named after the customer's original file name.
export async function listArchive(file) {
  const { stdout } = await run(`tar -tf "${file}"`);
  return stdout.split('\n').filter(Boolean);
}
