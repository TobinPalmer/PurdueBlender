"""Smooth the initial R7 faceted roof caps against same-band LiDAR medians."""
import bpy,json,hashlib,os,statistics
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","neil_armstrong_hall.blend")
OUT=os.path.join(ROOT,"audit","complete_neil_armstrong")
with open(os.path.join(OUT,"validation_r7.json"),encoding="utf-8") as f: prior=json.load(f)
with open(os.path.join(OUT,"roof_surface_samples_r7_smooth.json"),encoding="utf-8") as f:samples=json.load(f)
if hashlib.sha256(open(ASSET,"rb").read()).hexdigest()!=prior["source_hash"]:
    raise RuntimeError("Neil asset changed since initial R7 validation")
bpy.ops.wm.open_mainfile(filepath=ASSET)
root=bpy.data.objects["AssetRoot_neil_armstrong_hall"]
changed=[]
for zone in samples["zones"]:
    obj=bpy.data.objects[zone["object"]]
    if obj.parent!=root: raise RuntimeError(f"Unexpected parent on {obj.name}")
    vals=[]
    for row in zone["roof_surface_vertices"]:
        v=obj.data.vertices[int(row["index"])]
        if abs(float(v.co.x)-float(row["x"]))>1e-5 or abs(float(v.co.y)-float(row["y"]))>1e-5:
            raise RuntimeError(f"XY changed unexpectedly on {obj.name}[{row['index']}]")
        v.co.z=float(row["z_after"]); vals.append(float(row["z_after"]))
    obj.data.update()
    obj["modeled_top_height_m"]=max(vals)
    obj["modeled_surface_median_height_m"]=statistics.median(vals)
    obj["roof_surface_vertex_height_range_m"]=[min(vals),max(vals)]
    obj["roof_surface_method_r7"]=samples["height_sampling"]
    changed.append({"object":obj.name,"vertex_count":len(vals),"min_m":min(vals),"median_m":statistics.median(vals),"max_m":max(vals)})
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(json.dumps({"saved":ASSET,"refinement":"R7 5x5 median blend","zones":changed},indent=2))
