from PIL import Image, ImageDraw
from pathlib import Path
import math

p=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\neil_armstrong_hall_refine\renders_r12_1")
files=sorted(f for f in p.glob("*.png") if not f.name.startswith("contact"))
out=Image.new("RGB",(1800,math.ceil(len(files)/3)*420),(255,255,255))
d=ImageDraw.Draw(out)
for i,f in enumerate(files):
    im=Image.open(f).convert("RGB")
    im.thumbnail((590,380))
    x=(i%3)*600; y=(i//3)*420
    out.paste(im,(x,y+25))
    d.text((x+3,y+3),f.stem,fill=(0,0,0))
out.save(p/"contact_r12_1.png")
