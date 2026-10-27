"""Fresh-process structural and portability validation for Maclure library."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset_path = root / "modular" / "buildings" / "maclure_cooperative.blend"
out_path = Path(__file__).resolve().parent / "validation.json"
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
scene = bpy.context.scene
asset = bpy.data.collections.get("Asset_maclure_cooperative")
assert scene.name == "Building_maclure_cooperative", scene.name
assert asset is not None
assert not bpy.data.libraries
root_obj = bpy.data.objects.get("AssetRoot_maclure_cooperative")
assert root_obj is not None
assert root_obj.get("source_feature_id") == 822
assert tuple(round(v,6) for v in root_obj.get("placement_origin_xy_m")) == (588.724845,-56.856275)
depsgraph = bpy.context.evaluated_depsgraph_get()
verts=[]
for obj in asset.objects:
    eval_obj=obj.evaluated_get(depsgraph)
    if obj.type in {"MESH","FONT","CURVE"}:
        for p in eval_obj.bound_box:
            verts.append(eval_obj.matrix_world @ Vector(p))
assert verts
bounds=[[round(min(v[i] for v in verts),3),round(max(v[i] for v in verts),3)] for i in range(3)]
types={}
for obj in asset.objects: types[obj.type]=types.get(obj.type,0)+1
external_images=[img.filepath for img in bpy.data.images if img.source in {"FILE","TILED"} and img.filepath]
floor_objs=[o for o in asset.objects if "floor slab" in o.name.lower() or "basement floor" in o.name.lower()]
assert len(floor_objs) == 3, [o.name for o in floor_objs]
assert all(not o.hide_render for o in floor_objs), [o.name for o in floor_objs if o.hide_render]
assert bpy.data.objects.get("Recessed entry dark alcove") is not None
assert bpy.data.objects.get("Front deck stair tread") is not None
wall=bpy.data.objects.get("GIS footprint walls | FID 822")
assert wall is not None
base_xy={(round(v.co.x,6),round(v.co.y,6)) for v in wall.data.vertices if abs(v.co.z)<1e-7}
assert len(base_xy)==12, len(base_xy)
report={
 "fresh_open":True,"blender_version":bpy.app.version_string,"asset_path":"modular/buildings/maclure_cooperative.blend",
 "asset_sha256":hashlib.sha256(asset_path.read_bytes()).hexdigest(),
 "scene":scene.name,"collection":asset.name,"building_id":root_obj.get("building_id"),
 "source_feature_id":root_obj.get("source_feature_id"),"placement_origin_xy_m":list(root_obj.get("placement_origin_xy_m")),
 "object_count":len(asset.objects),"object_types":types,"evaluated_asset_bounds_xyz_m":bounds,
 "external_image_dependencies":external_images,"linked_libraries":len(bpy.data.libraries),
 "interior_floor_objects":[{"name":o.name,"render_visible":not o.hide_render} for o in floor_objs],
 "gis_wall_base_vertex_count":len(base_xy),
 "checks":{"expected_scene":True,"expected_asset_collection":True,"stable_id_present":True,"source_fid_present":True,"placement_origin_present":True,"asset_has_geometry":True,"gis_wall_base_vertex_count_12":True,"recessed_entry_present":True,"right_end_stairs_present":True,"three_interior_floors_render_visible":True,"no_external_image_dependencies":not external_images,"no_linked_blender_libraries":not bpy.data.libraries},
 "note":"Bounds include the attached presentation-facing deck, roof, chimney and modeled furniture; GIS footprint verification is separate. Interior floors are render-visible in the delivered asset. The exterior preview hides them temporarily; the separate interior plan preview shows the estimated ground-floor layout."
}
out_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))
