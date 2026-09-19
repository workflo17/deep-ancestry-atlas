# Build the ice-sheet atlas the globe crossfades through: out/ice.png and out/ice.json.
# Source: PaleoMIST 1.0 ice margins (Gowan et al. 2021, CC-BY-4.0), 33 slices from 80 ka to
# present at 2,500-year steps, fetched by fetch-sources.sh into raw/paleomist/margins/.
# Present-day Antarctic ice shelves come from Natural Earth (public domain), because the
# PaleoMIST margin is the grounding line and the shelves would otherwise draw as bare lowland.
#
# Each slice is stored as a signed distance field rather than a mask. Mixing two distance
# fields and thresholding at zero makes the margin travel between slices; mixing two masks
# only fades one shape out while the other fades in.
import json, os, sys, glob
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

RAW, OUT = "raw", "out"
AGES = list(range(0, 80001, 2500))
REGIONS = ["North_America", "Eurasia", "Antarctica", "Patagonia"]   # North America carries Greenland
TW, TH = 512, 256            # one tile
SS = 6                       # margins are rasterised at SS x the tile size, then averaged down
COLS, ROWS = 8, 5            # 4096 x 1280 atlas, 33 of 40 tiles used
BAND = 24.0                  # distance is clamped to +-BAND tile pixels (about 17 degrees)
W0, H0 = TW * SS, TH * SS


def read_gmt(path):
    """OGR-GMT polygons -> list of (outer, [holes]); rings are (n,2) lon/lat arrays."""
    feats, ring, kind = [], [], "P"

    def flush():
        nonlocal ring
        if len(ring) >= 3:
            a = np.array(ring, dtype=np.float64)
            if kind == "H" and feats:
                feats[-1][1].append(a)
            else:
                feats.append((a, []))
        ring = []

    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith(">"):
                flush(); kind = "P"
            elif line.startswith("#"):
                t = line[1:].strip()
                if t.startswith("@P"):
                    flush(); kind = "P"
                elif t.startswith("@H"):
                    flush(); kind = "H"
            else:
                p = line.split()
                if len(p) >= 2:
                    ring.append((float(p[0]), float(p[1])))
    flush()
    return feats


def unwrap(ring):
    """Make longitudes continuous, and close a ring that circles a pole over that pole."""
    lon = ring[:, 0].copy(); lat = ring[:, 1]
    d = np.diff(lon)
    lon[1:] += np.cumsum(np.where(d > 180, -360.0, np.where(d < -180, 360.0, 0.0)))
    turn = lon[-1] - lon[0]
    if abs(abs(turn) - 360.0) < 1.0:                      # went once round the planet
        pole = -90.0 if lat.mean() < 0 else 90.0
        lon = np.concatenate([lon, [lon[-1], lon[0]]])
        lat = np.concatenate([lat, [pole, pole]])
    return lon, lat


def burn(mask, outer, holes):
    lon, lat = unwrap(outer)
    for shift in (-360.0, 0.0, 360.0):
        x = (lon + shift + 180.0) / 360.0 * W0
        y = (90.0 - lat) / 180.0 * H0
        if x.max() < 0 or x.min() > W0:
            continue
        x0, x1 = int(max(0, np.floor(x.min()))), int(min(W0, np.ceil(x.max()) + 1))
        y0, y1 = int(max(0, np.floor(y.min()))), int(min(H0, np.ceil(y.max()) + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        im = Image.new("L", (x1 - x0, y1 - y0), 0)
        dr = ImageDraw.Draw(im)
        dr.polygon(list(zip(x - x0, y - y0)), fill=1)
        for h in holes:                                     # holes never circle a pole
            hl, ht = unwrap(h)
            dr.polygon(list(zip((hl + shift + 180.0) / 360.0 * W0 - x0, (90.0 - ht) / 180.0 * H0 - y0)), fill=0)
        np.maximum(mask[y0:y1, x0:x1], np.asarray(im, dtype=np.uint8), out=mask[y0:y1, x0:x1])


def geojson_polys(path):
    for f in json.load(open(path, encoding="utf-8"))["features"]:
        g = f["geometry"]
        for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            yield np.array(poly[0], dtype=np.float64)[:, :2], [np.array(h, dtype=np.float64)[:, :2] for h in poly[1:]]


def sdf(mask):
    """Signed distance in tile pixels, positive inside the ice; longitude wraps."""
    pad = int(BAND * SS) + SS
    m = np.concatenate([mask[:, -pad:], mask, mask[:, :pad]], axis=1).astype(bool)
    if not m.any():
        return np.full((TH, TW), -BAND, dtype=np.float32)
    d = distance_transform_edt(m) - distance_transform_edt(~m)
    d = d[:, pad:-pad] / SS
    d -= np.sign(d) * (0.5 / SS)                            # distances are to pixel centres, not to the edge
    d = np.clip(d, -BAND, BAND).astype(np.float32)
    return d.reshape(TH, SS, TW, SS).mean(axis=(1, 3))


shelves = np.zeros((H0, W0), dtype=np.uint8)
sp = os.path.join(RAW, "ne_10m_antarctic_ice_shelves_polys.geojson")
for outer, holes in geojson_polys(sp):
    burn(shelves, outer, holes)

atlas = np.zeros((ROWS * TH, COLS * TW), dtype=np.uint8)
area = []
for k, age in enumerate(AGES):
    mask = shelves.copy()
    for r in REGIONS:
        for outer, holes in read_gmt(os.path.join(RAW, "paleomist", "margins", r, "%d.gmt" % age)):
            burn(mask, outer, holes)
    lat = np.deg2rad(90.0 - (np.arange(H0) + 0.5) / H0 * 180.0)
    km2 = float((mask.astype(np.float64).sum(axis=1) * np.cos(lat)).sum() * (40075.0 / W0) ** 2)
    area.append(round(km2 / 1e6, 2))
    code = np.clip(np.rint(128.0 + sdf(mask) / BAND * 127.0), 0, 255).astype(np.uint8)
    cy, cx = divmod(k, COLS)
    atlas[cy * TH:(cy + 1) * TH, cx * TW:(cx + 1) * TW] = code
    print("%6d BP  ice %.2f M km2" % (age, area[-1]), file=sys.stderr)

os.makedirs(OUT, exist_ok=True)
Image.fromarray(atlas, "L").save(os.path.join(OUT, "ice.png"), optimize=True, compress_level=9)
json.dump({"ages": AGES, "cols": COLS, "rows": ROWS, "tile": [TW, TH], "band": BAND, "zero": 128,
           "area_Mkm2": area,
           "source": "PaleoMIST 1.0 ice margins (Gowan et al. 2021), minimal MIS 3 scenario; "
                     "present-day Antarctic ice shelves from Natural Earth",
           "license": "CC-BY-4.0 (PaleoMIST); public domain (Natural Earth)"},
          open(os.path.join(OUT, "ice.json"), "w"), separators=(",", ":"))
print("ice.png %.0f KB" % (os.path.getsize(os.path.join(OUT, "ice.png")) / 1e3), file=sys.stderr)
