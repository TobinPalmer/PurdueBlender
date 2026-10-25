from PIL import Image, ImageDraw

ROOT = r"C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/"
sx, sy = 0.092105 * 0.9, 0.0923377778 * 0.9
x0 = -13.209 - 0.092105 * 323
y0 = 40.611 + 0.0923377778 * 86
points = [(-16.872,-23.211), (0.12,-21.606), (5.973,38.433)]
for floor in (2,3):
    im = Image.open(ROOT + f"plan_l{floor}_round8.png").convert("RGB")
    draw = ImageDraw.Draw(im)
    for i, (x,y) in enumerate(points):
        px, py = (x-x0)/sx, (y0-y)/sy
        draw.ellipse((px-7,py-7,px+7,py+7), outline=(255,0,0), width=3)
        draw.text((px+8,py-8), str(i+1), fill=(255,0,0))
    im.save(ROOT + f"plan_stairs_l{floor}_round8.png")
