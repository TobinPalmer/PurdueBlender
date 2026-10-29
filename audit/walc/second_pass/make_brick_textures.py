"""Generate the WALC brick textures (tileable PNGs) used by build_walc_second_pass.py.

python audit/walc/second_pass/make_brick_textures.py

- walc_brick_running.png: running bond, 203 x 68 mm modules, variegated red / plum / brown bricks, buff mortar.
- walc_brick_basketweave.png: the WALC spandrel pattern - squares of THREE parallel bricks whose direction alternates
  square by square (basketweave), the whole weave turned 45 degrees, so the alternating squares read as small crosses
  (user close-up sources/user_provided_basketweave_closeup.jpg). Square side = one brick length = three brick heights.
Colours: k-means clusters of the close-up's bricks, lifted slightly in saturation for the variegation; mortar sampled.
"""
import math, os
import numpy as np
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
MORTAR = (226, 211, 191)
BRICKS = [(140, 62, 55), (128, 58, 52), (118, 66, 60), (96, 64, 68), (82, 58, 60), (108, 70, 62), (134, 74, 64)]
WEIGHTS = [0.2, 0.17, 0.15, 0.16, 0.1, 0.12, 0.1]
BL, BH, MJ = 0.2032, 0.0677, 0.010     # brick module length/height incl. joint, joint width (m)


def palette(h):
    """Deterministic brick colour from an integer hash, with a little speckle-free value jitter."""
    r = (h * 2654435761) & 0xFFFFFFFF
    u = (r % 10000) / 10000.0
    acc = 0.0
    for c, w in zip(BRICKS, WEIGHTS):
        acc += w
        if u <= acc:
            break
    j = 0.92 + 0.16 * (((r >> 13) % 1000) / 1000.0)
    return tuple(min(255, int(v * j)) for v in c)


def noise(shape, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(0, 7, shape)   # fine surface grain (the bricks are wire-cut/textured)


def running(px=1024):
    tw, th = 10 * BL, 30 * BH            # 2.032 x 2.031 m tile
    ys, xs = np.mgrid[0:px, 0:px]
    X = xs / px * tw
    Y = (px - 1 - ys) / px * th
    row = np.floor(Y / BH).astype(int)
    off = (row % 2) * BL / 2
    col = np.floor((X + off) / BL).astype(int) % 10
    fx = ((X + off) % BL) / BL
    fy = (Y % BH) / BH
    mort = (fx < MJ / BL) | (fy < MJ / BH)
    img = np.zeros((px, px, 3))
    ids = (row % 30) * 131 + col * 7919 + 17
    for i in np.unique(ids):
        img[ids == i] = palette(int(i))
    img += noise(img.shape, 1)
    img[mort] = MORTAR
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def basketweave(px=1024, periods=6):
    c = BL                                # square side: one brick length = three brick heights
    tile = periods * c * math.sqrt(2)     # tileable: lattice vectors (c,-c),(c,c) in the turned frame
    ys, xs = np.mgrid[0:px, 0:px]
    X = xs / px * tile
    Y = (px - 1 - ys) / px * tile
    u = (X + Y) / math.sqrt(2)
    v = (Y - X) / math.sqrt(2)
    i = np.floor(u / c).astype(int)
    j = np.floor(v / c).astype(int)
    fu, fv = u / c - i, v / c - j
    horiz = ((i + j) % 2) == 0            # direction of the three bricks in this square
    a = np.where(horiz, fv, fu)           # across the bricks
    b = np.where(horiz, fu, fv)           # along the bricks
    k = np.floor(a * 3).astype(int)
    ja = (a * 3) % 1.0
    mj = MJ / (c / 3)
    mort = (ja < mj) | (b < MJ / c)
    s, d = (i + j) % (2 * periods), (i - j) % (2 * periods)
    ids = s * 1009 + d * 37 + k * 5 + 3
    img = np.zeros((px, px, 3))
    for q in np.unique(ids):
        img[ids == q] = palette(int(q) * 31 + 7)
    img += noise(img.shape, 2)
    img[mort] = MORTAR
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), tile


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    running().save(os.path.join(OUT, "walc_brick_running.png"))
    im, tile = basketweave()
    im.save(os.path.join(OUT, "walc_brick_basketweave.png"))
    print("textures written; running tile 2.032 m, basketweave tile %.4f m" % tile)
