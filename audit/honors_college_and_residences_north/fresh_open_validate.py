"""Fresh-open validation for the Honors North modular asset. Run via blender -b <asset> --python this_file.py."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
asset_id="massing_honors_college_and_residences_north_3de3b7c"
expected_scene="Building_"+asset_id
expected_collection="Asset_"+asset_id
scene=bpy.data.scenes.get(expected_scene)
collection=bpy.data.collections.get(expected_collection)
assert scene is not None, "expected building scene missing"
assert collection is not None, "expected asset collection missing"
assert scene.get("building_id")==asset_id
assert len(collection.objects)>1, "detailed geometry not present"
mins=[float("inf")]*3
maxs=[float("-inf")]*3
mesh_objects=0
for obj in collection.objects:
    if obj.type!="MESH":
        continue
    mesh_objects+=1
    for v in obj.data.vertices:
        co=obj.matrix_world @ v.co
        for i in range(3):
            mins[i]=min(mins[i],co[i])
            maxs[i]=max(maxs[i],co[i])
interior=bpy.data.scenes.get(expected_scene+"_SchematicInterior_NOT_AS_BUILT")
assert interior is not None, "schematic interior scene missing"
assert "not an as-built" in interior.get("status", "").lower()
assert bpy.data.images.__len__()==0, "asset unexpectedly depends on external images"
assert all(obj.library is None for obj in collection.objects), "linked external object found"
record={
  "result":"PASS",
  "reopened_file":bpy.data.filepath,
  "expected_scene":expected_scene,
  "expected_collection":expected_collection,
  "building_id":scene.get("building_id"),
  "collection_object_count":len(collection.objects),
  "mesh_object_count":mesh_objects,
  "world_bounds_m":{"x":[round(mins[0],3),round(maxs[0],3)],"y":[round(mins[1],3),round(maxs[1],3)],"z":[round(mins[2],3),round(maxs[2],3)]},
  "schematic_interior_scene":interior.name,
  "schematic_interior_object_count":sum(len(c.objects) for c in [interior.collection,*interior.collection.children_recursive]),
  "packed_or_external_image_count":len(bpy.data.images),
  "external_object_links":0,
  "material_count":len({m.name for o in collection.objects if o.type=="MESH" for m in o.data.materials if m}),
  "note":"Massing library is campus-coordinate geometry. Footprint follows Purdue GIS FID 544. Heights are modeled estimates because official OEP and GIS vertical fields conflict."
}
out=root/"audit"/"honors_college_and_residences_north"/"fresh_open_validation.json"
out.write_text(json.dumps(record,indent=2),encoding="utf-8")
print(json.dumps(record,indent=2))
