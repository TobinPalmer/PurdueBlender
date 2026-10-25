from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path("audit/potter_engineering_refine/s03_upper_route_schematic.png")
im = Image.new("RGB", (1600, 1450), "#fbfcfd")
d = ImageDraw.Draw(im)
font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
title = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 38)
# A simple meter grid in asset-local coordinates.
x0, x1, y0, y1 = 8.2, 13.8, 32.1, 38.2
scale = 190
left, top = 140, 150
def pt(x, y): return (left + (x-x0)*scale, top + (y1-y)*scale)
d.text((left, 55), "S03 → 4S04 upper landing: current saved geometry check", fill="#1e2934", font=title)
for x in range(9, 14):
    X, _ = pt(x, y0)
    d.line((X, pt(x,y0)[1], X, pt(x,y1)[1]), fill="#e3e8ed", width=2)
    d.text((X-10, pt(x,y0)[1]+12), str(x), fill="#58636c", font=small)
for y in range(33, 39):
    _, Y = pt(x0, y)
    d.line((pt(x0,y)[0], Y, pt(x1,y)[0], Y), fill="#e3e8ed", width=2)
    d.text((50, Y-14), str(y), fill="#58636c", font=small)

def rect(bounds, fill=None, outline="#353b45", width=4):
    a,b,c,e = bounds
    d.rectangle((*pt(a,e), *pt(c,b)), fill=fill, outline=outline, width=width)

# Roof aperture and landing footprints (m).
rect((8.7,33.85,12.1,36.55), None, "#1e7db5", 5)
rect((8.8,33.85,10.4,36.55), "#f6e7c9", "#b27a1e", 3)
# 4S04 perimeter; west door is an intentional gap from y=34.6 to 35.8 m.
wall="#353b45"
for a,b in [((9.2,32.8),(13.1,32.8)),((13.1,32.8),(13.1,37.6)),((13.1,37.6),(9.2,37.6)),((9.2,32.8),(9.2,34.6)),((9.2,35.8),(9.2,37.6))]:
    d.line((*pt(*a),*pt(*b)), fill=wall, width=12)

# 0.8 m square person-footprint samples on landing; centerline turn to the doorway.
centers=[(9.262,35.725),(9.262,35.2),(9.45,35.2)]
for cx,cy in centers:
    rect((cx-.4,cy-.4,cx+.4,cy+.4), "#ed846c", "#a42b10", 3)
for a,b in zip(centers,centers[1:]):
    d.line((*pt(*a),*pt(*b)), fill="#a42b10", width=7)
    d.ellipse((pt(*b)[0]-8,pt(*b)[1]-8,pt(*b)[0]+8,pt(*b)[1]+8),fill="#a42b10")

d.text(pt(10.4,34.25), "Roof opening", fill="#1e7db5", font=small)
d.text(pt(10.5,37.0), "4S04 estimated walls", fill=wall, font=small)
d.text((left+10, pt(8.2,35.2)[1]-34), "West door gap: 1.2 m", fill=wall, font=small)
d.line((left+250, pt(8.2,35.2)[1]-5, pt(9.2,35.2)[0]-12, pt(9.2,35.2)[1]), fill=wall, width=2)
d.text((left, 1365), "Blue dashed = roof aperture | gold = landing | coral = 0.8 m proxy footprints", fill="#39434b", font=small)
d.text((left, 1400), "Plan, door and aperture dimensions are estimates. Geometric clearance only; not code/accessibility review.", fill="#58636c", font=small)
im.save(out)
print(out)
