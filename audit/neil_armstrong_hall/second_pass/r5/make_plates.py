"""photo | before (r4) | after (r5) comparison plates for the red-roof wing views.
python make_plates.py <user_images_dir>"""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "sources")
U = sys.argv[1] if len(sys.argv) > 1 else ""
S = lambda f: os.path.join(SRC, f)
PAIRS = [
    ("match_2016_01_NW", S("Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg"), None),
    ("point_below", S("Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg"), (450, 0, 1550, 1500)),
    ("photo5_point_W", os.path.join(U, "5.webp"), None),
    ("photo2_NNW", os.path.join(U, "2.webp"), None),
    ("figA_entrance", S("researchgate_sensors2020_fig4_full.jpg"), (175, 5, 630, 305)),
    ("photo3_aerial", os.path.join(U, "3.webp"), None),
    ("aerial_NW", os.path.join(U, "6.webp"), None),
    ("dd24_wing_side", S("Purdue_University_West_Lafayette_Indiana_Estados_Unidos_2012-10-15_DD_24.jpg"), None),
    ("top_NW", S("na_ortho_2023_hr.jpg"), (0, 160, 520, 620)),
    ("top_fixed", S("na_ortho_2023_hr.jpg"), None),
    ("obl_SE_fixed", None, None),
]
H = 560
os.makedirs(os.path.join(HERE, "plates"), exist_ok=True)
for name, ph, crop in PAIRS:
    tiles = []
    if ph and os.path.exists(ph):
        im = Image.open(ph).convert("RGB")
        if crop:
            im = im.crop(crop)
        tiles.append(("photo: " + os.path.basename(ph), im))
    for lab, d, pre in (("before (r4)", "before", "before"), ("after (r5)", "after", "after")):
        tiles.append((lab, Image.open(os.path.join(HERE, d, f"{pre}_{name}.png")).convert("RGB")))
    rs = [im.resize((int(im.width * H / im.height), H), Image.LANCZOS) for _, im in tiles]
    W = sum(r.width for r in rs) + 8 * (len(rs) - 1)
    out = Image.new("RGB", (W, H + 26), (255, 255, 255))
    dr = ImageDraw.Draw(out)
    x = 0
    for (lab, _), r in zip(tiles, rs):
        out.paste(r, (x, 26))
        dr.text((x + 4, 6), lab, fill=(0, 0, 0))
        x += r.width + 8
    out.save(os.path.join(HERE, "plates", f"plate_{name}.png"))
    print("plate", name)
