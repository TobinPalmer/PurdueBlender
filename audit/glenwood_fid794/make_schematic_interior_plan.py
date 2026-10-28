from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json, math
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD=ROOT/'audit/glenwood_fid794'; SRC=AUD/'sources'
feat=json.loads((SRC/'purdue_gis_fid794_2026-10-28_4326.json').read_text(encoding='utf-8'))['features'][0]
ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in feat['geometry']['rings'][0][:-1]]
xmin=min(x for x,y in ring); xmax=max(x for x,y in ring); ymin=min(y for x,y in ring); ymax=max(y for x,y in ring)
W,H=1800,1040
im=Image.new('RGB',(W,H),(248,249,247)); d=ImageDraw.Draw(im)
try:
    title=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf',42)
    head=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf',27)
    body=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',21)
    small=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',18)
except OSError:
    title=head=body=small=ImageFont.load_default()
d.text((60,38),'GLENWOOD · FID 794 — SCHEMATIC INTERIOR',font=title,fill=(25,39,52))
d.text((62,98),'Not as built: no floor plan or interior photograph was found. Room dividers, circulation and furniture are placeholders.',font=body,fill=(78,83,86))

panels=[(60,160,840,650,'GROUND LEVEL'),(900,160,1680,650,'UPPER LEVEL')]
# Approximate empty plan partitions follow the schematic insert coordinates used by the builder.
main_partitions=[
    ((xmin+2,ymin+3),(xmin+2,ymax-3)),((xmin+8,ymin+2),(xmin+8,ymax-2)),
    ((xmin+15,ymin+2),(xmin+15,ymax-2)),((xmin+22,ymin+2),(xmin+22,ymax-2)),
    ((xmin+1,ymin+4),(xmax-2,ymin+4)),((xmin+2,ymax-4),(xmax-2,ymax-4))]
upper_partitions=[
    ((xmin+5,ymin+3),(xmin+5,ymax-3)),((xmin+14,ymin+3),(xmin+14,ymax-3)),
    ((xmin+22,ymin+3),(xmin+22,ymax-3)),((xmin+2,ymin+4),(xmax-2,ymin+4))]

def draw_panel(box,label,upper=False):
    x0,y0,x1,y1=box
    d.text((x0,y0-45),label,font=head,fill=(37,66,82))
    pad=22; px0=x0+pad; px1=x1-pad; py0=y0+pad; py1=y1-pad
    # fit exact GIS outline while preserving its shape
    sx=(px1-px0)/(xmax-xmin); sy=(py1-py0)/(ymax-ymin); scale=min(sx,sy)
    cx=(px0+px1)/2; cy=(py0+py1)/2
    def pt(x,y): return (round(cx+(x-(xmin+xmax)/2)*scale),round(cy-(y-(ymin+ymax)/2)*scale))
    poly=[pt(x,y) for x,y in ring]
    d.polygon(poly,fill=(238,233,220))
    d.line(poly+[poly[0]],fill=(34,54,66),width=5,joint='curve')
    parts=upper_partitions if upper else main_partitions
    for a,b in parts: d.line([pt(*a),pt(*b)],fill=(105,112,110),width=8)
    if not upper:
        # stair run near east-side extension, and generic dining/common-room furniture symbols
        stair_x=xmax-6.2
        for i in range(11):
            y=ymin+2.0+i*0.45
            d.line([pt(stair_x-1.1,y),pt(stair_x+1.1,y)],fill=(83,100,107),width=4)
        d.rectangle([pt(xmin+4.4,ymin+5.6),pt(xmin+7.6,ymin+4.35)],fill=(166,137,100),outline=(87,72,56),width=3)
        d.rectangle([pt(xmin+0.8,ymin+8.5),pt(xmin+1.5,ymin+3.5)],fill=(193,177,148),outline=(87,72,56),width=3)
        for x,y in [(xmin+4,ymin+5),(xmin+8,ymin+5),(xmin+16,ymin+6),(xmin+20,ymin+6)]:
            p=pt(x,y); d.rectangle((p[0]-10,p[1]-10,p[0]+10,p[1]+10),fill=(87,116,143),outline=(37,55,72),width=2)
    else:
        for x,y in [(xmin+5,ymax-7),(xmin+18,ymax-7)]:
            p=pt(x,y); d.rounded_rectangle((p[0]-24,p[1]-10,p[0]+24,p[1]+10),radius=4,fill=(86,115,144),outline=(37,55,72),width=2)
        p=pt(xmin+10,ymax-6); d.rectangle((p[0]-22,p[1]-12,p[0]+22,p[1]+12),fill=(166,137,100),outline=(87,72,56),width=3)
    # GIS north arrow, with no implied facade heading.
    ax=x1-58; ay=y0+26
    d.line((ax,ay+35,ax,ay),fill=(25,39,52),width=4); d.polygon([(ax,ay-3),(ax-9,ay+12),(ax+9,ay+12)],fill=(25,39,52)); d.text((ax-8,ay-28),'N',font=small,fill=(25,39,52))
    return

draw_panel(panels[0][:4],panels[0][4],False)
draw_panel(panels[1][:4],panels[1][4],True)
# Legend and uncertainty footer
d.line((66,890,138,890),fill=(105,112,110),width=8); d.text((154,874),'Illustrative partition',font=small,fill=(58,66,70))
d.rectangle((420,878,462,902),fill=(166,137,100),outline=(87,72,56),width=2); d.text((478,874),'Generic table/counter',font=small,fill=(58,66,70))
d.rectangle((785,878,820,903),fill=(87,116,143),outline=(37,55,72),width=2); d.text((838,874),'Furniture placeholder',font=small,fill=(58,66,70))
d.line((62,944,1738,944),fill=(202,207,205),width=2)
d.text((62,965),'Perimeter uses Purdue GIS FID 794 in the project approximate local transform. Interior dimensions and room functions are not documented.',font=small,fill=(88,87,82))
im.save(AUD/'schematic_interior_plan.png')
print(AUD/'schematic_interior_plan.png')
