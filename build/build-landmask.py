import json, math, base64, struct

d = json.load(open('ne110_land.geojson'))
polys = []   # (bbox, outer_ring, [holes])
for f in d['features']:
    g = f['geometry']
    rings = g['coordinates']
    outer = rings[0]; holes = rings[1:]
    xs = [p[0] for p in outer]; ys = [p[1] for p in outer]
    polys.append(((min(xs),min(ys),max(xs),max(ys)), outer, holes))

def in_ring(x, y, ring):
    inside = False
    n = len(ring)
    j = n-1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > y) != (yj > y)):
            xint = (xj-xi)*(y-yi)/(yj-yi) + xi
            if x < xint: inside = not inside
        j = i
    return inside

def is_land(lon, lat):
    for (bb, outer, holes) in polys:
        if lon < bb[0] or lon > bb[2] or lat < bb[1] or lat > bb[3]: continue
        if in_ring(lon, lat, outer):
            if any(in_ring(lon, lat, h) for h in holes): continue
            return True
    return False

# Fibonacci sphere -> uniform density, no polar bunching
N = 48000
GA = math.pi * (3.0 - math.sqrt(5.0))
bits = bytearray((N + 7)//8)
count = 0
for i in range(N):
    y = 1 - (i / (N - 1.0)) * 2      # y in [1,-1]
    lat = math.degrees(math.asin(y))
    lon = math.degrees((GA * i) % (2*math.pi))
    if lon > 180: lon -= 360
    if is_land(lon, lat):
        bits[i >> 3] |= (1 << (i & 7)); count += 1
print("N=%d land=%d (%.1f%%)" % (N, count, 100.0*count/N))
b64 = base64.b64encode(bytes(bits)).decode()
open('landmask.b64','w').write(b64)
print("landmask b64 bytes:", len(b64))
