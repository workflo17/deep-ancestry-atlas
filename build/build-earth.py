# Build the globe's ground: terrain rasters, relief, present-day coastline and the sea-level curve.
# Run after build-ice.py, from this directory, with the sources fetch-sources.sh downloads.
#   pip install rasterio numpy pillow scipy
# Emits out/earth-4096.webp + out/earth-2048.webp  elevation, lossless (see ENCODING below)
#       out/relief-4096.webp + out/relief-2048.webp  slope gradient, east stacked over north, lossy
#       out/coast.bin.txt                            Natural Earth 10m coastline, routes format
#       out/earth.json                               every constant the page needs to decode them
#
# ENCODING. The page moves the coastline by comparing elevation with the sea level of the date on
# the timeline, so the raster needs metre precision near sea level and none of it anywhere else.
#   R  mean elevation for tinting, square-root companded: 128 is sea level, 1 is -8000 m, 255 is +6500 m
#   G  MEDIAN elevation for the coastline, 1 m per code from -150 m (0) to +105 m (255). A texel
#      is land at sea level S exactly when more than half of its cells stand above S, and the
#      median is the one number for which that holds at every S. A mean does not: a few deep
#      cells pull a texel of +1 m polder or coastal plain under water.
#   B  lake fraction
# Land that is dry today but lies below sea level (polders, the Caspian depression, Qattara, the
# Dead Sea rift) is lifted to +1 m in G using the Natural Earth land mask: nothing connects it to
# the ocean, so a falling or rising sea must not flood it. Lakes are written as permanent water.
import json, math, os, sys, base64, struct
import numpy as np
from PIL import Image
import rasterio
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin

Image.MAX_IMAGE_PIXELS = None
RAW, OUT = "raw", "out"
SIZES = [(4096, 2048), (2048, 1024)]
G_LO, G_HI = -150.0, 105.0          # G channel range, metres
R_SEA, R_LAND = 8000.0, 6500.0      # R channel full-scale depth and height, metres
GRAD0 = 0.25                        # gradient (m per m) that saturates the relief channel
GRAD_POW, GRAD_DEAD = 0.6, 0.001    # companding power, and the slope below which ground is flat
SEA_K = 0.4                         # deep sea floor relief, relative to land
LAKE_TINT = -30.0                   # lakes tint as shallow water unless their floor is deeper
COAST_TOL = 0.012                   # coastline simplification, degrees (about 1.3 km)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def shapes(path, keep=lambda p: True):
    for f in json.load(open(path, encoding="utf-8"))["features"]:
        if f["geometry"] and keep(f.get("properties") or {}):
            yield f["geometry"], 1


# ---------------- 1. ETOPO 2022 and today's land and lakes, at 60 arc-seconds ----------------
# --cached reuses the downsampled fields from the last full run, to re-encode without the
# six-minute pass over 233 million cells.
CACHED = "--cached" in sys.argv and all(os.path.exists(os.path.join(RAW, "_earth_fields_%d.npz" % w)) for w, _ in SIZES)
H = None
if not CACHED:
    with rasterio.open(os.path.join(RAW, "etopo2022_60s_surface.tif")) as ds:
        log("ETOPO", ds.width, "x", ds.height, ds.dtypes[0])
        H = ds.read(1).astype(np.float32)
        T0 = ds.transform
    FH, FW = H.shape
    land = rasterize(list(shapes(os.path.join(RAW, "ne_10m_land.geojson"))) +
                     list(shapes(os.path.join(RAW, "ne_10m_minor_islands.geojson"))),
                     out_shape=(FH, FW), transform=T0, fill=0, dtype="uint8").astype(bool)
    natural = lambda p: "reservoir" not in str(p.get("featurecla", "")).lower()
    lake = rasterize(list(shapes(os.path.join(RAW, "ne_10m_lakes.geojson"), natural)),
                     out_shape=(FH, FW), transform=T0, fill=0, dtype="uint8").astype(bool)
    dry = land & ~lake & (H < 1.0)
    log("land %.1f%%  lakes %.2f%%  dry land below +1 m %.2f%%" %
        (100 * land.mean(), 100 * lake.mean(), 100 * dry.mean()))
    hG = H.copy(); hG[dry] = 1.0; hG[lake] = G_LO
    hR = H.copy(); hR[dry] = 1.0; hR[lake] = np.minimum(H[lake], LAKE_TINT)
    lakef = lake.astype(np.float32)
    del land, dry


def down(src, w, h, how=Resampling.average):
    dst = np.zeros((h, w), dtype=np.float32)
    reproject(src, dst, src_transform=T0, src_crs="EPSG:4326",
              dst_transform=from_origin(-180.0, 90.0, 360.0 / w, 180.0 / h), dst_crs="EPSG:4326",
              resampling=how)
    return dst


def enc_r(h):
    up, dn = np.clip(h, 0, R_LAND), np.clip(-h, 0, R_SEA)
    c = np.where(h >= 0, 128.0 + 127.0 * np.sqrt(up / R_LAND), 128.0 - 127.0 * np.sqrt(dn / R_SEA))
    return np.clip(np.rint(c), 1, 255).astype(np.uint8)


def enc_grad(g):
    a = np.maximum(np.abs(g) - GRAD_DEAD, 0.0)
    c = 128.0 + 127.0 * np.sign(g) * np.minimum(a / GRAD0, 1.0) ** GRAD_POW
    return np.clip(np.rint(c), 1, 255).astype(np.uint8)


# ---------------- 2. downsample, encode ----------------
os.makedirs(OUT, exist_ok=True)
sizes = {}
for (w, h) in SIZES:
    cache = os.path.join(RAW, "_earth_fields_%d.npz" % w)
    if CACHED:
        d = np.load(cache); mR, mG, mL, mH = d["mR"], d["mG"], d["mL"], d["mH"]
    else:
        mR, mL, mH = down(hR, w, h), down(lakef, w, h), down(H, w, h)
        mG = np.clip(down(hG, w, h, Resampling.med), G_LO, G_HI)
        np.savez(cache, mR=mR, mG=mG, mL=mL, mH=mH)
    rgb = np.dstack([enc_r(mR),
                     np.clip(np.rint(mG - G_LO), 0, 255).astype(np.uint8),
                     np.clip(np.rint(mL * 255.0), 0, 255).astype(np.uint8)])
    p = os.path.join(OUT, "earth-%d.webp" % w)          # lossless WebP: a quarter smaller than PNG here
    Image.fromarray(rgb, "RGB").save(p, lossless=True, quality=100, method=6)
    assert (np.asarray(Image.open(p).convert("RGB")) == rgb).all(), "elevation raster did not round-trip"
    # Slope of the mean surface, metres per metre, east over north. Lakes are flat. The deep sea
    # floor is rougher than the land at this scale and the page mutes it anyway, so it is scaled
    # down here, which is where most of the file size goes.
    lat = np.deg2rad(90.0 - (np.arange(h) + 0.5) / h * 180.0)[:, None]
    cell = 40075016.7 / w
    gx = (np.roll(mH, -1, axis=1) - np.roll(mH, 1, axis=1)) / (2.0 * cell * np.maximum(np.cos(lat), 0.05))
    gy = np.zeros_like(mH)
    gy[1:-1] = (mH[:-2] - mH[2:]) / (2.0 * cell)
    k = (1.0 - np.clip(mL * 1.5, 0, 1)) * (1.0 - (1.0 - SEA_K) * np.clip((-mH - 150.0) / 250.0, 0, 1))
    q = os.path.join(OUT, "relief-%d.webp" % w)
    Image.fromarray(np.vstack([enc_grad(gx * k), enc_grad(gy * k)]), "L").save(q, quality=80, method=6)
    sizes[w] = (os.path.getsize(p), os.path.getsize(q))
    log("%d: earth %.2f MB  relief %.2f MB" % (w, sizes[w][0] / 1e6, sizes[w][1] / 1e6))
    if w == SIZES[0][0]:
        CHECK = (mG, w, h)

# ---------------- 3. present-day coastline, simplified ----------------
def simplify(pts, tol):
    n = len(pts)
    if n < 3:
        return pts
    keep = np.zeros(n, dtype=bool); keep[0] = keep[-1] = True
    x = pts[:, 0] * math.cos(math.radians(float(pts[:, 1].mean()))); y = pts[:, 1]
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        dx, dy = x[b] - x[a], y[b] - y[a]
        L = math.hypot(dx, dy)
        i = np.arange(a + 1, b)
        d = np.hypot(x[i] - x[a], y[i] - y[a]) if L < 1e-12 else np.abs(dx * (y[i] - y[a]) - dy * (x[i] - x[a])) / L
        k = int(d.argmax())
        if d[k] > tol:
            keep[a + 1 + k] = True
            stack.append((a, a + 1 + k)); stack.append((a + 1 + k, b))
    return pts[keep]


lines, raw_n = [], 0
for f in json.load(open(os.path.join(RAW, "ne_10m_coastline.geojson"), encoding="utf-8"))["features"]:
    g = f["geometry"]
    for c in ([g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]):
        p = np.array(c, dtype=np.float64)[:, :2]
        raw_n += len(p)
        s = simplify(p, COAST_TOL)
        if len(s) >= 4 or (len(s) >= 2 and np.hypot(*(s[0] - s[-1])) > 0.05):   # drop specks that collapse
            lines.append(s)
chunks = []
for s in lines:                                           # the routes format counts vertices in a uint16
    for a in range(0, len(s) - 1, 60000):
        chunks.append(s[a:a + 60001])
b = bytearray(struct.pack("<I", len(chunks)))
for s in chunks:
    b += struct.pack("<HBB", len(s), 0, 1)
    b += np.column_stack([np.rint(s[:, 1] * 1e5), np.rint(s[:, 0] * 1e5)]).astype("<i4").tobytes()
open(os.path.join(OUT, "coast.bin.txt"), "w").write(base64.b64encode(bytes(b)).decode())
coast_n = sum(len(s) for s in chunks)
log("coast: %d of %d vertices in %d lines, %.2f MB base64" %
    (coast_n, raw_n, len(chunks), os.path.getsize(os.path.join(OUT, "coast.bin.txt")) / 1e6))

# ---------------- 4. sea level, Spratt & Lisiecki 2016 ----------------
# Column 2 is the short stack (0-430 ka), metres above present, scaled by its authors to 0 m at
# 5 ka. That scaling leaves +3 to +8 m for 0-4 ka, inside the stack's own 95% interval of zero
# and contradicted by Holocene shoreline records, so those five values are drawn as 0 m.
sea, sd = [], []
for line in open(os.path.join(RAW, "spratt2016.txt"), encoding="utf-8", errors="ignore"):
    p = line.split("\t")
    if line.startswith("#") or len(p) < 3:
        continue
    try:
        ka, v, s = int(p[0]), float(p[1]), float(p[2])
    except ValueError:
        continue
    if ka <= 300 and ka == len(sea):
        sea.append(0.0 if ka <= 5 else v); sd.append(s)
assert len(sea) == 301, len(sea)
log("sea level: %d values, min %.1f m at %d ka" % (len(sea), min(sea), sea.index(min(sea))))

# build-ice.py leaves its tile layout in out/ice.json. It is folded into earth.json here and then
# removed, so that everything in out/ is something the page fetches.
ICEJ, EARTHJ = os.path.join(OUT, "ice.json"), os.path.join(OUT, "earth.json")
ice = (json.load(open(ICEJ)) if os.path.exists(ICEJ)
       else json.load(open(EARTHJ)).get("ice") if os.path.exists(EARTHJ) else None)
if ice is None:
    log("warning: no ice atlas metadata found; run build-ice.py first or the globe will have no ice")
json.dump({"sizes": [s[0] for s in SIZES],
           "elev": {"g_lo": G_LO, "g_hi": G_HI, "r_sea": R_SEA, "r_land": R_LAND, "grad0": GRAD0, "grad_pow": GRAD_POW, "grad_dead": GRAD_DEAD,
                    "source": "ETOPO 2022 60 arc-second surface elevation (NOAA NCEI), doi:10.25921/fd45-gt74",
                    "license": "not subject to copyright protection within the United States"},
           "sea": {"step_yr": 1000, "m": sea, "sd": sd, "holocene_rule": "0-5 ka drawn as 0 m",
                   "source": "Spratt & Lisiecki 2016, Clim. Past 12, 1079-1092, short stack PC1, "
                             "doi:10.5194/cp-12-1079-2016; data NOAA WDS-Paleo study 19982"},
           "coast": {"n": coast_n, "tol_deg": COAST_TOL, "source": "Natural Earth 10m coastline", "license": "public domain"},
           "ice": ice},
          open(EARTHJ, "w"), separators=(",", ":"))
if os.path.exists(ICEJ):
    os.remove(ICEJ)

# ---------------- 5. check the raster against the raw grid, by a different route ----------------
# Expected values come straight from the 60 arc-second cell and its neighbourhood, never from
# the encoder above: a site is "water at S" when most raw cells around it lie below S.
mG, w, h = CHECK
SITES = [("Bering Strait", 65.8, -168.9), ("Sunda shelf", 3.0, 107.0), ("Doggerland", 54.6, 2.8),
         ("Sahul, Arafura", -9.5, 135.0), ("Persian Gulf", 26.5, 52.0), ("Mid Atlantic", 30.0, -42.0),
         ("Java Sea", -5.5, 111.0), ("Caspian depression", 47.2, 48.6), ("Qattara", 29.6, 27.4),
         ("Flevoland polder", 52.5, 5.5), ("Caspian Sea", 42.0, 50.5), ("Lake Superior", 47.7, -87.5),
         ("Nile delta", 31.2, 31.0), ("Ganges delta", 22.6, 90.2), ("Mekong delta", 9.9, 105.6),
         ("Strait of Dover", 51.0, 1.45), ("Red Sea", 20.0, 38.6), ("Bass Strait", -39.8, 146.0)]
bad = 0
log("%-20s %9s %9s  %-6s %-6s" % ("site", "raw m", "G m", "0 m", "-120 m"))
for name, la, lo in SITES:
    fi, fj = int((90 - la) * 60), int((lo + 180) * 60)
    blk = H[fi - 3:fi + 4, fj - 3:fj + 4] if H is not None else np.array([np.nan])
    i, j = int((90 - la) / 180 * h), int((lo + 180) / 360 * w)
    g = float(mG[i, j])
    now, lgm = ("water" if g < 0 else "land"), ("water" if g < -120 else "land")
    log("%-20s %9.1f %9.1f  %-6s %-6s" % (name, float(np.median(blk)), g, now, lgm))
EXPECT = {"Bering Strait": ("water", "land"), "Sunda shelf": ("water", "land"), "Doggerland": ("water", "land"),
          "Sahul, Arafura": ("water", "land"), "Persian Gulf": ("water", "land"), "Mid Atlantic": ("water", "water"),
          "Java Sea": ("water", "land"), "Caspian depression": ("land", "land"), "Qattara": ("land", "land"),
          "Flevoland polder": ("land", "land"), "Caspian Sea": ("water", "water"), "Lake Superior": ("water", "water"),
          "Nile delta": ("land", "land"), "Ganges delta": ("land", "land"), "Mekong delta": ("land", "land"),
          "Strait of Dover": ("water", "land"), "Red Sea": ("water", "water"), "Bass Strait": ("water", "land")}
for name, la, lo in SITES:
    i, j = int((90 - la) / 180 * h), int((lo + 180) / 360 * w)
    g = float(mG[i, j])
    got = ("water" if g < 0 else "land", "water" if g < -120 else "land")
    if got != EXPECT[name]:
        bad += 1; log("MISMATCH", name, got, "expected", EXPECT[name])
log("site check: %d of %d as expected" % (len(SITES) - bad, len(SITES)))
sys.exit(1 if bad else 0)
