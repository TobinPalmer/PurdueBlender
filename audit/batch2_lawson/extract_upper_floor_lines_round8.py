"""Extract only long, near-neutral, orthogonal linework from the Purdue floor-plan raster.

This is a schematic partition guide, not a substitute for vector/CAD dimensions. The
overlay is saved so every auto-traced segment can be checked against its source page.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson")
BODY = {2: (320, 710, 70, 1120), 3: (320, 710, 70, 1120)}
MIN_LEN = 42

def fill_small_gaps(mask, gap=2):
    out = mask.copy()
    for step in range(1, gap + 1):
        out[:-step] |= mask[step:]
        out[step:] |= mask[:-step]
    return out

def runs(mask):
    idx = np.flatnonzero(mask)
    if not len(idx):
        return []
    groups = []
    start = last = int(idx[0])
    for v in map(int, idx[1:]):
        if v - last <= 3:
            last = v
        else:
            groups.append((start, last))
            start = last = v
    groups.append((start, last))
    return groups

def collect(floor):
    filename = ROOT / f"plan_l{floor}_round8.png"
    image = Image.open(filename).convert("RGB")
    rgb = np.asarray(image, dtype=np.int16)
    maxc, minc = rgb.max(axis=2), rgb.min(axis=2)
    # Retain dark neutral architectural strokes, suppress colored room names and the
    # turquoise exterior/window line. Allow a small antialias gap across a line.
    line_mask = (maxc < 215) & ((maxc-minc) < 46)
    x0, x1, y0, y1 = BODY[floor]
    segs = []
    for y in range(y0, y1):
        mask = fill_small_gaps(line_mask[y, x0:x1])
        for a,b in runs(mask):
            if b-a+1 >= MIN_LEN:
                segs.append([x0+a, y, x0+b, y])
    for x in range(x0, x1):
        mask = fill_small_gaps(line_mask[y0:y1, x])
        for a,b in runs(mask):
            if b-a+1 >= MIN_LEN:
                segs.append([x, y0+a, x, y0+b])
    # Collapse doubled raster edges representing one architectural wall; retain a
    # centerline between near-parallel strokes with similar extents.
    merged = []
    for seg in segs:
        x1s,y1s,x2s,y2s = seg
        orient = "h" if y1s == y2s else "v"
        lo, hi = (x1s,x2s) if orient == "h" else (y1s,y2s)
        fixed = y1s if orient == "h" else x1s
        match = None
        for j, old in enumerate(merged):
            ox1,oy1,ox2,oy2 = old
            oo = "h" if oy1 == oy2 else "v"
            if oo != orient: continue
            olo,ohi = (ox1,ox2) if oo == "h" else (oy1,oy2)
            ofixed = oy1 if oo == "h" else ox1
            overlap = min(hi,ohi)-max(lo,olo)
            if abs(fixed-ofixed) <= 2 and overlap >= MIN_LEN*0.55:
                match=j;break
        if match is None:
            merged.append(seg)
        else:
            old=merged[match]
            if orient=="h": merged[match]=[min(old[0],x1s),round((old[1]+y1s)/2),max(old[2],x2s),round((old[1]+y1s)/2)]
            else: merged[match]=[round((old[0]+x1s)/2),min(old[1],y1s),round((old[0]+x1s)/2),max(old[3],y2s)]
    # Exclude the outer perimeter rails in the floorplan; these correspond to the
    # existing envelope and should not be duplicated as interior partition geometry.
    filtered=[]
    for x1s,y1s,x2s,y2s in merged:
        if (y1s==y2s and y1s < 105) or (y1s==y2s and y1s>1090): continue
        if (x1s==x2s and (x1s<340 or x1s>690)): continue
        filtered.append([x1s,y1s,x2s,y2s])
    # Source-mapped overlay of retained wall centerlines.
    overlay=image.copy();draw=ImageDraw.Draw(overlay)
    for s in filtered: draw.line(s,fill=(240,40,20),width=2)
    overlay.save(ROOT/f"floor{floor}_walltrace_round8.png")
    data={"floor":floor,"source_pdf":f"lawson_{floor}.pdf","raster":filename.name,"raster_size_px":list(image.size),"minimum_pixel_length":MIN_LEN,"line_count":len(filtered),"segments_px":filtered,"overlay":f"floor{floor}_walltrace_round8.png","mapping":{"x_m":"-42.959 + 0.0828945 * pixel_x","y_m":"48.550 - 0.0831040 * pixel_y"}}
    (ROOT/f"floor{floor}_walltrace_round8.json").write_text(json.dumps(data,indent=2),encoding="utf8")
    return data

for floor in (2,3):
    d=collect(floor)
    print(f"L{floor}: {d['line_count']} candidate wall segments; {d['overlay']}")
