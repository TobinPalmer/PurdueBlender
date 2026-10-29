"""Read a window of the Tippecanoe 2017-2019 QL2 3DEP normalized height model (NDHM) COG via HTTP range requests.

usage: python ndhm.py <out_prefix> <anchor_x> <anchor_y> <xmin> <ymin> <xmax> <ymax> [step_m=0.5]
Coordinates are asset-local metres (campus = anchor + local, project lon/lat approximation).
Writes <out_prefix>.npy (heights in metres, rows north->south at step_m), <out_prefix>.png (false colour with
5 m grid) and <out_prefix>.json (metadata). Source: Purdue Digital Forestry hosting of Indiana 2017-2019 QL2 LiDAR.
"""
import sys, json, math, io, urllib.request, datetime
import numpy as np
import tifffile
from pyproj import Transformer

URL = "https://lidar.digitalforestry.org/QL2_3DEP_LiDAR_IN_2017_2019_l2/tippecanoe/cog/tippecanoe_ndhm_2018.tif"
UA = {"User-Agent": "PurdueBlenderResearch/1.0"}
FT = 0.304800609601219
K = 111412.84 * math.cos(math.radians(40.4274))


class HttpFile(io.RawIOBase):
    def __init__(self, url):
        self.url, self.pos, self.cache = url, 0, {}
        req = urllib.request.Request(url, method="HEAD", headers=UA)
        self.size = int(urllib.request.urlopen(req, timeout=60).headers["Content-Length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def tell(self):
        return self.pos

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        blk = 1 << 16
        out = bytearray()
        p, end = self.pos, min(self.pos + n, self.size)
        while p < end:
            b = p // blk
            if b not in self.cache:
                h = dict(UA, Range=f"bytes={b * blk}-{min((b + 1) * blk, self.size) - 1}")
                self.cache[b] = urllib.request.urlopen(urllib.request.Request(self.url, headers=h), timeout=60).read()
            chunk = self.cache[b]
            o = p - b * blk
            take = min(len(chunk) - o, end - p)
            out += chunk[o:o + take]
            p += take
        self.pos = p
        return bytes(out)

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)


def main():
    out = sys.argv[1]
    ax, ay, x0, y0, x1, y1 = map(float, sys.argv[2:8])
    step = float(sys.argv[8]) if len(sys.argv) > 8 else 0.5
    f = HttpFile(URL)
    tf = tifffile.TiffFile(f)
    page = tf.pages[0]
    tags = page.tags
    scale = tags["ModelPixelScaleTag"].value
    tie = tags["ModelTiepointTag"].value
    geo = tf.geotiff_metadata or {}
    epsg = geo.get("ProjectedCSTypeGeoKey")
    epsg = int(epsg) if epsg is not None and not hasattr(epsg, "name") else (int(epsg.value) if epsg is not None else 2966)
    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    X0, Y0 = tie[3], tie[4]
    sx, sy = scale[0], scale[1]
    # local grid
    xs = np.arange(x0, x1 + 1e-6, step)
    ys = np.arange(y1, y0 - 1e-6, -step)
    gx, gy = np.meshgrid(xs, ys)
    lon = (gx + ax) / K - 86.9137
    lat = (gy + ay) / 111040.0 + 40.4274
    E, N = tr.transform(lon, lat)
    col = ((E - X0) / sx).astype(int)
    row = ((Y0 - N) / sy).astype(int)
    tw, th = page.tilewidth, page.tilelength
    tiles_across = math.ceil(page.imagewidth / tw)
    need = {}
    for r, c in zip(row.ravel(), col.ravel()):
        need[(r // th, c // tw)] = True
    cache = {}
    for (tr_, tc) in need:
        idx = tr_ * tiles_across + tc
        f.seek(page.dataoffsets[idx])
        data = f.read(page.databytecounts[idx])
        arr, _, shape = page.decode(data, idx)
        cache[(tr_, tc)] = arr.reshape(th, tw)
    H = np.empty(row.shape, dtype=np.float32)
    for i in range(row.shape[0]):
        for j in range(row.shape[1]):
            r, c = row[i, j], col[i, j]
            H[i, j] = cache[(r // th, c // tw)][r % th, c % tw]
    H_m = H * FT
    np.save(out + ".npy", H_m)
    from PIL import Image, ImageDraw
    v = np.clip(H_m / 30.0, 0, 1)
    rgb = (np.stack([v, np.clip(1.5 - abs(v * 3 - 1.5), 0, 1), 1 - v], -1) * 255).astype(np.uint8)
    im = Image.fromarray(rgb).resize((rgb.shape[1] * 2, rgb.shape[0] * 2), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for gxv in np.arange(math.ceil(x0 / 5) * 5, x1 + 1e-6, 5):
        px = (gxv - x0) / step * 2
        d.line([(px, 0), (px, im.height)], fill=(255, 255, 255) if gxv % 25 == 0 else (90, 90, 90))
        if gxv % 25 == 0:
            d.text((px + 2, im.height - 12), f"{gxv:g}", fill=(255, 255, 255))
    for gyv in np.arange(math.ceil(y0 / 5) * 5, y1 + 1e-6, 5):
        py = (y1 - gyv) / step * 2
        d.line([(0, py), (im.width, py)], fill=(255, 255, 255) if gyv % 25 == 0 else (90, 90, 90))
        if gyv % 25 == 0:
            d.text((2, py + 2), f"{gyv:g}", fill=(255, 255, 255))
    im.save(out + ".png")
    json.dump({"source": URL, "dataset": "Indiana 2017-2019 QL2 3DEP LiDAR, Tippecanoe NDHM (height above ground)",
               "epsg": epsg, "native_resolution": [sx, sy], "units": "US survey ft -> m", "anchor_xy": [ax, ay],
               "local_box": [x0, y0, x1, y1], "sample_step_m": step, "retrieved": datetime.date.today().isoformat(),
               "method": "nearest-cell sampling of the COG at local grid points via project lon/lat approximation"},
              open(out + ".json", "w"), indent=1)
    print("NDHM", H_m.shape, float(np.nanmax(H_m)), epsg, sx)


if __name__ == "__main__":
    main()
