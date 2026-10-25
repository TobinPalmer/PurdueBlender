from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
AUDIT=ROOT/"audit/neil_armstrong_hall_refine"
OUT=AUDIT/"comparison_plate_r12.png"
W,H=1800,1450
CELL_W,CELL_H=870,410
MARGIN,GAP=20,20
canvas=Image.new("RGB",(W,H),(245,245,245))
d=ImageDraw.Draw(canvas)
font=ImageFont.load_default()
rows=[
 ("2016 exterior 03 · 48 mm · POV 40.431433, -86.916781",ROOT/"audit/complete_neil_armstrong/sources/wikimedia_neil_2016_03_r8.jpg","R12 matching geotag · z=1.7 m inferred",AUDIT/"renders_r12/r12_geotag_view03.png"),
 ("2016 courtyard 02 · 24 mm · POV 40.430861, -86.915212",AUDIT/"sources_r12/arms_2016_02.jpg","R12 courtyard comparison · z=1.7 m inferred",AUDIT/"renders_r12/r12_geotag_view02_courtyard.png"),
 ("2023 orthophoto roof plan",ROOT/"audit/complete_neil_armstrong/sources/indiana_current_ortho_neil_extent.png","R12 roof view · orthographic · asset local frame",AUDIT/"renders_r12/r12_top_registered.png"),
]
for row,(left_title,left_img,right_title,right_img) in enumerate(rows):
    y=MARGIN+row*(CELL_H+80)
    for col,(title,path) in enumerate(((left_title,left_img),(right_title,right_img))):
        x=MARGIN+col*(CELL_W+GAP)
        d.text((x,y),title,fill=(20,20,20),font=font)
        im=Image.open(path).convert("RGB")
        im.thumbnail((CELL_W,CELL_H))
        px=x+(CELL_W-im.width)//2; py=y+24+(CELL_H-im.height)//2
        canvas.paste(im,(px,py))
        d.rectangle((x,y+24,x+CELL_W,y+24+CELL_H),outline=(100,100,100),width=1)
canvas.save(OUT)
print(OUT)
