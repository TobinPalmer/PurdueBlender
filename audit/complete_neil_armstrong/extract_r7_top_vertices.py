"""Export current R5 envelope roof vertices for read-only NDHM sampling."""
import bpy, json, os, hashlib
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","neil_armstrong_hall.blend")
OUT=os.path.join(ROOT,"audit","complete_neil_armstrong")
with open(os.path.join(OUT,"validation_r6.json"),encoding="utf-8") as f: val=json.load(f)
assert hashlib.sha256(open(ASSET,"rb").read()).hexdigest()==val["asset_sha256"]
bpy.ops.wm.open_mainfile(filepath=ASSET)
col=bpy.data.collections["Asset_neil_armstrong_hall"]
result={"asset_sha256":val["asset_sha256"],"revision":"R6","zones":[]}
for name in ("ARMS_R5_Coarse_LiDAR_wing_low","ARMS_R5_Coarse_LiDAR_wing_mid","ARMS_R5_Coarse_LiDAR_roof_high"):
    obj=bpy.data.objects[name]
    band=list(obj.get("height_band_m",[]))
    old_top=max(float(v.co.z) for v in obj.data.vertices)
    vertices=[{"index":v.index,"x":float(v.co.x),"y":float(v.co.y),"z_before":float(v.co.z)}
              for v in obj.data.vertices if abs(float(v.co.z)-old_top)<1e-4]
    result["zones"].append({"object":name,"height_band_m":band,"median_top_m":float(obj.get("modeled_top_height_m")),
                            "old_top_m":old_top,"vertices":vertices})
assert len(col.objects)==449
with open(os.path.join(OUT,"roof_vertices_r7.json"),"w",encoding="utf-8") as f: json.dump(result,f,indent=2)
print(json.dumps({"revision":"R6","collection_count":len(col.objects),"top_vertices":[{"object":z["object"],"count":len(z["vertices"])} for z in result["zones"]]},indent=2))
