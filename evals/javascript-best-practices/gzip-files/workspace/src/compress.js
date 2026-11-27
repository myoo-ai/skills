import fs from 'fs';
import zlib from 'zlib';

// Gzips src into dest and calls cb(err) when done.
export function compressFile(src, dest, cb) {
  fs.createReadStream(src)
    .pipe(zlib.createGzip())
    .pipe(fs.createWriteStream(dest))
    .on('finish', () => cb(null));
}

// Calls cb(err, isGzip) with whether the file starts with the gzip magic bytes.
export function isGzip(file, cb) {
  fs.open(file, 'r', (err, fd) => {
    if (err) return cb(err);
    const buf = Buffer.alloc(2);
    fs.read(fd, buf, 0, 2, 0, (err, bytesRead) => {
      if (err) return cb(err);
      fs.close(fd, () => {});
      cb(null, bytesRead === 2 && buf[0] === 0x1f && buf[1] === 0x8b);
    });
  });
}
