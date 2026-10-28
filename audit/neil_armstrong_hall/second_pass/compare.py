"""python compare.py <second_pass_dir> <rev> <pairs.json>  pairs: [[shot, source_rel_path], ...]"""
import sys,json,os
from PIL import Image, ImageDraw
d,rev,pf=sys.argv[1],sys.argv[2],sys.argv[3]
pairs=json.load(open(pf)); out=os.path.join(d,f"comparisons_{rev}"); os.makedirs(out,exist_ok=True)
for shot,src in pairs:
    ims=[Image.open(os.path.join(d,src)).convert("RGB"),Image.open(os.path.join(d,f"baseline/r0_{shot}.png")).convert("RGB"),Image.open(os.path.join(d,f"{rev}/{rev}_{shot}.png")).convert("RGB")]
    H=420; ims=[im.resize((int(im.width*H/im.height),H)) for im in ims]
    W=sum(i.width for i in ims); b=Image.new("RGB",(W,H+24)); x=0; dr=ImageDraw.Draw(b)
    for lab,im in zip(["REFERENCE "+os.path.basename(src),"BASELINE r0",f"REVISION {rev}"],ims):
        b.paste(im,(x,24)); dr.text((x+6,5),lab,fill=(255,255,0)); x+=im.width
    b.save(os.path.join(out,f"{shot}_ref_before_after.jpg"),quality=88)
print("ok",len(pairs))
