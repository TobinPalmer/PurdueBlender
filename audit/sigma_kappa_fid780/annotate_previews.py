from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path('audit/sigma_kappa_fid780')
labels={
 'exterior_preview.png':'ESTIMATED EXTERIOR  |  Roof, facade dimensions and orientation unverified',
 'front_elevation_preview.png':'NORTH-FACING INTERPRETATION  |  Entry orientation is provisional',
 'interior_cutaway_preview.png':'SCHEMATIC INTERIOR  |  Not an as-built plan; room uses and dimensions unknown'
}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for name,label in labels.items():
 p=root/name
 if not p.exists(): continue
 im=Image.open(p).convert('RGB'); d=ImageDraw.Draw(im); h=58
 d.rectangle((0,im.height-h,im.width,im.height),fill=(24,31,39))
 d.text((24,im.height-h+12),label,font=font,fill=(248,245,235))
 im.save(p)
 print('annotated',name)
