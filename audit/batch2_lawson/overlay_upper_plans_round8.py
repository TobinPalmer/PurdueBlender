import json
from PIL import Image, ImageDraw

ROOT = r"C:/Users/Tobin/Documents/Blender/PurdueMap/"
gis = json.load(open(ROOT + "modular/buildings/target_buildings_gis.json", encoding="utf8"))["LWSN"]["world_polygon"]
marker = (-282.5, 44.0)
ring = [(x - marker[0], y - marker[1]) for x, y in gis]
# The R7 registration maps the 918x1188 first-floor raster. These R8 plan
# pages were rasterized at 120 dpi (1020x1320), i.e. 10/9 the R7 pixels.
sx, sy = 0.092105 * 0.9, 0.0923377778 * 0.9
x0 = -13.209 - 0.092105 * 323
y0 = 40.611 + 0.0923377778 * 86
def to_pixel(pt):
    return ((pt[0] - x0) / sx, (y0 - pt[1]) / sy)

for floor, filename in [(2, "plan_l2_round8.png"), (3, "plan_l3_round8.png")]:
    im = Image.open(ROOT + "audit/batch2_lawson/" + filename).convert("RGBA")
    draw = ImageDraw.Draw(im, "RGBA")
    pix = [to_pixel(pt) for pt in ring]
    draw.line(pix + [pix[0]], fill=(242, 30, 40, 220), width=2)
    for i, pt in enumerate(pix):
        draw.ellipse((pt[0]-2, pt[1]-2, pt[0]+2, pt[1]+2), fill=(242,30,40,255))
    draw.rectangle((18, 18, 420, 50), fill=(255,255,255,235), outline=(25,25,25,255), width=1)
    draw.text((28, 28), f"Purdue LWSN floor {floor} plan + GIS FID 59 registration", fill=(10,10,10,255))
    out = ROOT + f"audit/batch2_lawson/gis_plan_overlay_l{floor}_round8.png"
    im.save(out)
    print(out)
