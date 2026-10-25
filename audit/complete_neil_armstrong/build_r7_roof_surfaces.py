"""Shape the existing LiDAR masses with locally sampled NDHM roof heights."""
import bpy, json, hashlib, os, statistics
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","neil_armstrong_hall.blend")
OUT=os.path.join(ROOT,"audit","complete_neil_armstrong")
with open(os.path.join(OUT,"validation_r6.json"),encoding="utf-8") as f: r6=json.load(f)
with open(os.path.join(OUT,"roof_surface_samples_r7.json"),encoding="utf-8") as f: samples=json.load(f)
before=hashlib.sha256(open(ASSET,"rb").read()).hexdigest()
if before!=r6["asset_sha256"] or before!=samples["source_asset_sha256"]:
    raise RuntimeError("Neil source changed after the validated R6 snapshot")
bpy.ops.wm.open_mainfile(filepath=ASSET)
col=bpy.data.collections.get("Asset_neil_armstrong_hall")
root=bpy.data.objects.get("AssetRoot_neil_armstrong_hall")
if not col or not root or len(col.objects)!=449 or tuple(root.location)!=(0.0,0.0,0.0):
    raise RuntimeError("Unexpected source identity/count/root")
acm=bpy.data.materials["ARMS_R6_Mayflower_Red_ACM"]
changed=[]
for zone in samples["zones"]:
    obj=bpy.data.objects[zone["object"]]
    if obj.parent!=root:
        raise RuntimeError(f"{obj.name} left the local root frame")
    expected={int(v["index"]):v for v in zone["roof_surface_vertices"]}
    top_ids=set(expected)
    if len(expected)==0 or max(expected)>=len(obj.data.vertices):
        raise RuntimeError(f"Invalid exported roof vertex set for {obj.name}")
    if acm.name not in [m.name for m in obj.data.materials if m]:
        obj.data.materials.append(acm)
    acm_index=next(i for i,m in enumerate(obj.data.materials) if m and m.name==acm.name)
    for index,row in expected.items():
        vert=obj.data.vertices[index]
        if abs(float(vert.co.z)-float(row["z_before"]))>1e-4:
            raise RuntimeError(f"R6 vertex changed unexpectedly: {obj.name}[{index}]")
        vert.co.z=float(row["z_after"])
    obj.data.update()
    top_faces=0
    for poly in obj.data.polygons:
        if all(i in top_ids for i in poly.vertices):
            poly.material_index=acm_index
            top_faces+=1
    if top_faces==0:
        raise RuntimeError(f"No cap faces found on {obj.name}")
    heights=[float(row["z_after"]) for row in expected.values()]
    old_median=float(obj.get("modeled_top_height_m"))
    obj["r5_median_top_height_m"]=old_median
    obj["modeled_top_height_m"]=max(heights)
    obj["modeled_surface_median_height_m"]=statistics.median(heights)
    obj["roof_surface_method_r7"]="Top vertices retain R5 GIS/local XY and are vertically sampled from a 3x3 median of same-band 5-ft NDHM cells; high-zone samples above 22m excluded. Top caps use Mayflower Red ACM; vertical envelope sides retain brick. No roof edges, wall lines, or truss geometry were inferred."
    obj["roof_surface_vertex_height_range_m"]=[min(heights),max(heights)]
    obj["roof_surface_red_acm_top_faces"]=top_faces
    changed.append({"object":obj.name,"top_vertices_changed":len(expected),"acm_cap_faces":top_faces,
                    "surface_min_m":min(heights),"surface_median_m":statistics.median(heights),"surface_max_m":max(heights)})

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(json.dumps({"saved":ASSET,"revision":"R7","objects":changed,"object_count":len(col.objects),"sha256_before":before},indent=2))
