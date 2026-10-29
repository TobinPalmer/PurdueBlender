"""python compare_r3.py  (run from this folder) -> comparisons_r3/<shot>_ref_r2_r3.jpg

Reference photo | r2 (SHA 5ad01722..., rendered at the same camera into r3/before_r2/) | r3, at equal height.
Matched-view cameras are estimates (r3/closeup_cameras.json); compare features and proportions, not pixels."""
import os
from PIL import Image, ImageDraw

PAIRS = [  # shot, reference, optional reference crop box (full-res px)
    ("match_2016_02_SW_ground", "sources/Mackey_Arena_Purdue_University_2016_02.jpg", None),
    ("match_drone04_SW", "sources/exponent_drone_2025_04.jpg", None),
    ("match_drone05_E", "sources/exponent_drone_2025_05.jpg", None),
    ("match_2016_01_SE", "sources/Mackey_Arena_Purdue_University_2016_01.jpg", None),
    ("match_hntb2_plaza", "sources/hntb_Purdue-2.jpg", None),
    ("match_m27_west_aerial", "sources/purdue_athletics_2025_west_aerial.jpg", None),
    ("close_lobby_plaza", "sources/hntb_Purdue-2.jpg", (700, 20, 1360, 480)),
    ("close_drum_bay", "sources/Mackey_Arena_Purdue_University_2016_02.jpg", (930, 200, 1450, 420)),
]
OUT = "comparisons_r3"
os.makedirs(OUT, exist_ok=True)
for shot, ref, box in PAIRS:
    a = Image.open(ref).convert("RGB")
    if box:
        a = a.crop(box)
    ims = [a, Image.open(f"r3/before_r2/r2_{shot}.png").convert("RGB"), Image.open(f"r3/r3_{shot}.png").convert("RGB")]
    H = 440
    ims = [im.resize((int(im.width * H / im.height), H)) for im in ims]
    W = sum(i.width for i in ims)
    b = Image.new("RGB", (W, H + 24))
    dr = ImageDraw.Draw(b)
    x = 0
    for lab, im in zip(["REFERENCE " + os.path.basename(ref), "r2 (5ad01722)", "r3"], ims):
        b.paste(im, (x, 24))
        dr.text((x + 6, 5), lab, fill=(255, 255, 0))
        x += im.width
    b.save(os.path.join(OUT, f"{shot}_ref_r2_r3.jpg"), quality=88)
# standard-camera before/after for the r2 review set (same cameras, no reference)
for shot in ("close_east_entrance", "close_SDAC_west_plaza", "close_drum_slots", "close_SW_entrance",
             "close_north_entrance", "obl_SW", "obl_NW", "obl_NE", "obl_SE"):
    ims = [Image.open(f"r2/r2_{shot}.png").convert("RGB"), Image.open(f"r3/r3_{shot}.png").convert("RGB")]
    H = 440
    ims = [im.resize((int(im.width * H / im.height), H)) for im in ims]
    b = Image.new("RGB", (sum(i.width for i in ims), H + 24))
    dr = ImageDraw.Draw(b)
    x = 0
    for lab, im in zip(["r2", "r3"], ims):
        b.paste(im, (x, 24))
        dr.text((x + 6, 5), lab + " " + shot, fill=(255, 255, 0))
        x += im.width
    b.save(os.path.join(OUT, f"{shot}_r2_r3.jpg"), quality=88)
print("ok")
