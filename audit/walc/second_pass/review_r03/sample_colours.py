import sys, json
from PIL import Image, ImageDraw
import numpy as np
R='C:/Users/gotse/Documents/PurdueBlender-rossen-1-30/.claude/worktrees/building-model-geometry-fe019a/'
spec=json.load(open(sys.argv[1]))
out=[]
tiles=[]
for s in spec:
    im=Image.open(R+s['img']).convert('RGB')
    x,y,w,h=s['box']
    c=np.asarray(im.crop((x,y,x+w,y+h))).reshape(-1,3)
    p=s.get("pct",50); L=c.sum(1); thr=np.percentile(L,p); sel=c[np.abs(L-thr)<=np.percentile(np.abs(L-thr),20)] if p!=50 else c; med=np.median(sel,axis=0).astype(int).tolist()
    out.append((s['label'],med))
    # context tile
    cx,cy=x+w//2,y+h//2
    pad=60
    t=im.crop((cx-pad,cy-pad,cx+pad,cy+pad)).resize((160,160))
    d=ImageDraw.Draw(t); k=160/(2*pad)
    d.rectangle(((pad-w//2)*k,(pad-h//2)*k,(pad+w//2)*k,(pad+h//2)*k),outline=(0,255,0))
    d.text((2,2),s['label'][:24],fill=(255,255,0))
    tiles.append(t)
for l,m in out: print(f"{l:40s} {m}")
n=len(tiles); cols=6; rows=(n+cols-1)//cols
M=Image.new('RGB',(cols*160,rows*160))
for i,t in enumerate(tiles): M.paste(t,((i%cols)*160,(i//cols)*160))
M.save(sys.argv[2])
