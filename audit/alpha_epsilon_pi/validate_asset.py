"""Fresh-open validation for the Alpha Epsilon Pi standalone asset."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/"modular"/"buildings"/"alpha_epsilon_pi.blend"
OUT=Path(__file__).resolve().parent/"validation.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.data.scenes.get("Building_alpha_epsilon_pi")
collection=bpy.data.collections.get("Asset_alpha_epsilon_pi")
root=bpy.data.objects.get("AssetRoot_alpha_epsilon_pi")
assert scene and collection and root
assert bool(collection.get("local_coordinates"))
origin=collection.get("placement_origin_xy_m")
assert origin and len(origin)==2
assert scene.get("building_id")=="alpha_epsilon_pi"
objects=list(collection.all_objects)
meshes=[o for o in objects if o.type=="MESH"]
assert len(meshes)>100 and len(objects)>100
assert all(o.parent==root for o in meshes),"All exported meshes should be under the local asset root"
external_images=[im.name for im in bpy.data.images if im.source=="FILE" and not im.packed_file]
assert not external_images,f"Found un-packed image files: {external_images}"
materials={m.name for o in meshes for m in o.data.materials if m}
missing_materials=[o.name for o in meshes if len(o.data.materials)==0]
mins=[float("inf")]*3;maxs=[float("-inf")]*3
for o in meshes:
    for corner in o.bound_box:
        p=o.matrix_world@Vector(corner)
        for i in range(3):
            mins[i]=min(mins[i],p[i]);maxs[i]=max(maxs[i],p[i])
summary={
 "status":"PASS",
 "fresh_open":True,
 "asset":str(ASSET),
 "scene":scene.name,
 "collection":collection.name,
 "object_count":len(objects),
 "mesh_count":len(meshes),
 "material_count":len(materials),
 "missing_material_objects":missing_materials,
 "unpacked_external_images":external_images,
 "local_coordinates":collection.get("local_coordinates"),
 "placement_origin_xy_m":[float(origin[0]),float(origin[1])],
 "local_bounds_m":{"min":mins,"max":maxs},
 "roof_surface_triangle_counts":{
  "lower":len(bpy.data.objects["AEPi_Mansard_Lower_Slope"].data.polygons),
  "upper":len(bpy.data.objects["AEPi_Mansard_Upper_Slope"].data.polygons),
  "cap":len(bpy.data.objects["AEPi_Mansard_Flat_Cap"].data.polygons)},
 "caveats":["Interior remains representative/estimated; the GIS name conflict is captured in audit/evidence.json."]
}
OUT.write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
