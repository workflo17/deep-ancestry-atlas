"""List or extract members of a remote .zip over HTTP range requests, so a 3.5 GB archive
does not have to be downloaded for the few files the atlas needs.

  python remotezip.py URL                 # list members
  python remotezip.py URL OUTDIR PATTERN  # extract members whose name contains PATTERN
"""
import io, sys, os, zipfile, urllib.request


class HttpFile(io.RawIOBase):
    def __init__(self, url, block=1 << 20):
        self.url, self.pos, self.block = url, 0, block
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=60) as r:
            self.size = int(r.headers["Content-Length"])
            if r.headers.get("Accept-Ranges", "").lower() != "bytes":
                print("warning: server did not advertise byte ranges", file=sys.stderr)
        self.cache = {}
        self.fetched = 0

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def _get(self, a, b):
        req = urllib.request.Request(self.url, headers={"Range": "bytes=%d-%d" % (a, b - 1)})
        with urllib.request.urlopen(req, timeout=300) as r:
            d = r.read()
        self.fetched += len(d)
        return d

    def readinto(self, buf):
        n = min(len(buf), self.size - self.pos)
        if n <= 0:
            return 0
        out = bytearray()
        p = self.pos
        while len(out) < n:
            k = p // self.block
            if k not in self.cache:
                a = k * self.block
                self.cache[k] = self._get(a, min(self.size, a + self.block))
                if len(self.cache) > 64:
                    self.cache.pop(next(iter(self.cache)))
            blk = self.cache[k]
            o = p - k * self.block
            take = blk[o:o + (n - len(out))]
            out += take
            p += len(take)
        buf[:n] = out
        self.pos += n
        return n


if __name__ == "__main__":
    url = sys.argv[1]
    f = HttpFile(url)
    z = zipfile.ZipFile(io.BufferedReader(f, buffer_size=1 << 20))
    if len(sys.argv) < 4:
        for i in z.infolist():
            print("%12d %12d  %s" % (i.file_size, i.compress_size, i.filename))
        print("archive %d bytes, fetched %d" % (f.size, f.fetched), file=sys.stderr)
    else:
        out, pats = sys.argv[2], sys.argv[3:]
        os.makedirs(out, exist_ok=True)
        for i in z.infolist():
            if i.is_dir() or not any(p in i.filename for p in pats):
                continue
            dst = os.path.join(out, os.path.basename(i.filename))
            if os.path.exists(dst) and os.path.getsize(dst) == i.file_size:
                continue
            with z.open(i) as src, open(dst, "wb") as o:
                while True:
                    b = src.read(1 << 20)
                    if not b:
                        break
                    o.write(b)
            print("got", dst, i.file_size)
        print("fetched %d bytes of %d" % (f.fetched, f.size), file=sys.stderr)
