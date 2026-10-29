"""Drum / fascia height derivation for r3 (python drum_heights_r3.py, run from this folder).

1. LiDAR (sources/mackey_ndhm_2018.npy, Indiana 2017-2019 QL2 NDHM, 0.5 m resampled grid of 5 ft cells):
   median height in 0.5 m radial rings around the drum centre (0, -14.1375) over the SW/W/S sector where the
   concourse ring roof is open (190-300 deg), giving the ring-roof and fascia/rim levels.
2. Photo ratios measured on the same slotted bays (full-res pixel rows, see change_log r3):
   sources/purdue_athletics_2025_west_aerial.jpg, slotted bay x 1213-1393 px: fascia rows 1116-1146,
   channel above the louvres 1146-1182, louvres 1182-1280  -> 0.31 : 0.37 : 1
   sources/exponent_drone_2025_04.jpg, slotted bay x 864-1075 px: fascia rows 339-366, channel 366-405,
   louvres 405-509 -> 0.26 : 0.38 : 1   (both elevated views: equal foreshortening of vertical faces).
3. Solve ring roof -> curb (0.35 m) -> louvre -> channel -> fascia -> LiDAR fascia top.
"""
import math
import numpy as np

H = np.load("sources/mackey_ndhm_2018.npy")
x0, y1, step = -80.0, 150.0, 0.5
C = (0.0, -14.1375)


def ring(r0, r1, a0=190, a1=300):
    vals = []
    for a in np.arange(a0, a1, 0.5):
        for r in np.arange(r0, r1, 0.25):
            x = C[0] + r * math.cos(math.radians(a))
            y = C[1] + r * math.sin(math.radians(a))
            j = int(round((x - x0) / step))
            i = int(round((y1 - y) / step))
            if 0 <= i < H.shape[0] and 0 <= j < H.shape[1]:
                vals.append(H[i, j])
    return float(np.median(vals)), float(np.percentile(vals, 90))


for r0 in np.arange(44.0, 56.0, 1.0):
    med, p90 = ring(r0, r0 + 1.0)
    print("r %4.1f-%4.1f  median %5.2f  p90 %5.2f" % (r0, r0 + 1, med, p90))

ring_roof, fascia_top, curb = 4.4, 12.2, 0.35
for f, g in ((0.31, 0.37), (0.26, 0.38), (0.28, 0.38)):
    lv = (fascia_top - ring_roof - curb) / (1 + g + f)
    print("ratios f %.2f g %.2f -> louvre %.2f m (top %.2f), channel %.2f, fascia %.2f (underside %.2f), "
          "drum/10deg-chord %.2f" % (f, g, lv, ring_roof + curb + lv, g * lv, f * lv, fascia_top - f * lv,
                                     (fascia_top - f * lv - ring_roof) / (2 * 47.5 * math.sin(math.radians(5)))))
