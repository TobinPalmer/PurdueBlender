"""Quantify GIS-to-plan outline alignment on Purdue's official L2/L3 PDFs."""
import json
import math
from pathlib import Path
from PIL import Image

ROOT=Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
AUD=ROOT/"audit/batch2_lawson"
gis=json.loads((ROOT/"modular/buildings/target_buildings_gis.json").read_text(encoding="utf8"))["LWSN"]["world_polygon"]
marker=(-282.5,44.0)
ring=[(x-marker[0],y-marker[1]) for x,y in gis]
if ring[0]==ring[-1]: ring=ring[:-1]
sx0,sy0=.092105,.0923377778
sx,sy=sx0*.9,sy0*.9
x0=-13.209-sx0*323
y0=40.611+sy0*86
def px(x,y): return ((x-x0)/sx,(y0-y)/sy)

result={"method":"21 GIS boundary samples per edge searched for the nearest low-chroma teal perimeter stroke on the official Purdue plan raster; registration uses R7 L1/GIS controls rescaled for 120 dpi rasterization.","registration":{"control_points_l1_px":[[323,86],[627,86],[298,986]],"control_local_xy_m":[[-13.209,40.611],[14.791,40.547],[-15.553,-42.493]],"l2_l3_m_per_px":[sx,sy],"raster_pick_uncertainty_m":"approx. 0.3 m from source line width and manual control-point picks"},"floors":{}}
for floor in (2,3):
    im=Image.open(AUD/f"plan_l{floor}_round8.png").convert("RGB")
    width,height=im.size
    rgb=im.load()
    distances=[]
    for i,a in enumerate(ring):
        end_pt=ring[(i+1)%len(ring)]
        for j in range(21):
            t=j/20
            wx=a[0]*(1-t)+end_pt[0]*t;wy=a[1]*(1-t)+end_pt[1]*t
            qx,qy=px(wx,wy);cx,cy=round(qx),round(qy)
            best=math.inf
            for xx in range(max(0,cx-6),min(width,cx+7)):
                for yy in range(max(0,cy-6),min(height,cy+7)):
                    red,green,blue=rgb[xx,yy]
                    if green>=red+8 and blue>=red+8 and green>=50 and green<=225 and abs(green-blue)<=70:
                        d=math.hypot((xx-qx)*sx,(yy-qy)*sy)
                        if d<best: best=d
            if math.isfinite(best): distances.append(best)
    result["floors"][str(floor)]={
        "source_pdf":f"https://www.cs.purdue.edu/resources/docs/lawson_{floor}.PDF",
        "raster":f"plan_l{floor}_round8.png",
        "sample_count":len(distances),
        "total_expected_samples":len(ring)*21,
        "mean_nearest_teal_stroke_distance_m":sum(distances)/len(distances),
        "max_nearest_teal_stroke_distance_m":max(distances),
        "within_0_30m":sum(d<=.30 for d in distances),
        "overlay":f"gis_plan_overlay_l{floor}_round8.png",
        "caveat":"The nearest-stroke metric is a raster outline check, not survey accuracy; colored edge aliasing and printed-plan line width still impose about 0.3 m registration uncertainty."
    }
out=AUD/"upper_plan_registration_round8.json"
out.write_text(json.dumps(result,indent=2),encoding="utf8")
print(json.dumps(result,indent=2))
