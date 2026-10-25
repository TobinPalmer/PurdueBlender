from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); AUDIT=ROOT/'audit/neil_armstrong_hall_refine'; R=AUDIT/'renders_r12_5'
OUT=AUDIT/'comparison_plate_r12_5.png'; W,H=1800,1430; CW,CH=870,410; M,G=20,20
canvas=Image.new('RGB',(W,H),(245,245,245));d=ImageDraw.Draw(canvas);font=ImageFont.load_default()
rows=[
 ('2016 photo 03 · street-side canopy view',ROOT/'audit/complete_neil_armstrong/sources/wikimedia_neil_2016_03_r8.jpg','R12.5 · matching geotag start · heading is unknown',R/'r12_geotag_view03.png'),
 ('2016 photo 02 · campus parking approach',AUDIT/'sources_r12/arms_2016_02.jpg','R12.5 · adjusted exterior camera, shifted off exhibit case',R/'r12_courtyard_clear_view.png'),
 ('2023 Indiana orthophoto · roof/eaves only',ROOT/'audit/complete_neil_armstrong/sources/indiana_current_ortho_neil_extent.png','R12.5 · registered orthographic roof view',R/'r12_top_registered.png')]
for i,(lt,li,rt,ri) in enumerate(rows):
 y=M+i*(CH+65)
 for j,(title,path) in enumerate(((lt,li),(rt,ri))):
  x=M+j*(CW+G);d.text((x,y),title,fill=(20,20,20),font=font);im=Image.open(path).convert('RGB');im.thumbnail((CW,CH));px=x+(CW-im.width)//2;py=y+23+(CH-im.height)//2;canvas.paste(im,(px,py));d.rectangle((x,y+23,x+CW,y+23+CH),outline=(110,110,110),width=1)
canvas.save(OUT);print(OUT)
