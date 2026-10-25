from PIL import Image,ImageDraw
from pathlib import Path
ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
src=ROOT/"audit/complete_neil_armstrong/sources/indiana_current_ortho_neil_extent.png"
out=ROOT/"audit/neil_armstrong_hall_refine/roof_trace_overlay_r12.png"
im=Image.open(src).convert("RGBA")
layer=Image.new("RGBA",im.size,(0,0,0,0))
d=ImageDraw.Draw(layer)
outer=[(345,153),(1509,173),(1720,441),(565,414),(376,355)]
inner=[(600,205),(1492,222),(1604,390),(565,358),(510,246)]
d.polygon(outer,fill=(232,55,46,55),outline=(250,45,40,255),width=5)
d.polygon(inner,fill=(0,0,0,0),outline=(20,210,255,255),width=5)
for i,(x,y) in enumerate(outer):
    d.ellipse((x-6,y-6,x+6,y+6),fill=(255,30,25,255))
    d.text((x+7,y+3),f"O{i}",fill=(20,20,20,255),stroke_width=2,stroke_fill=(255,255,255,255))
for i,(x,y) in enumerate(inner):
    d.ellipse((x-6,y-6,x+6,y+6),fill=(0,190,255,255))
    d.text((x+7,y+3),f"I{i}",fill=(20,20,20,255),stroke_width=2,stroke_fill=(255,255,255,255))
Image.alpha_composite(im,layer).convert("RGB").save(out)
print(out)
