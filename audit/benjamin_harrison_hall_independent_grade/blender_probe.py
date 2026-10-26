from pathlib import Path
import json, hashlib, math, re, sys
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ASSET = ROOT / "modular/buildings/benjamin_harrison_hall.blend"
MANIFEST = ROOT / "modular/manifest.json"
GIS = ROOT / "audit/official_building_references.json"
EXPECTED_ID = "benjamin_harrison_hall"
EXPECTED_COLLECTION = "Asset_benjamin_harrison_hall"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
source_scene_name = scene.name
source_scene_building_id = scene.get("building_id")
source_scene_feature_id = scene.get("source_feature_id")
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entry = next(a for a in manifest["assets"] if a["id"] == EXPECTED_ID)
collection = bpy.data.collections.get(EXPECTED_COLLECTION)
assert collection is not None, f"Missing {EXPECTED_COLLECTION}"
assert entry["file"] == "buildings/benjamin_harrison_hall.blend"
assert entry["collection"] == EXPECTED_COLLECTION
assert entry["scene"] == scene.name

objects = sorted(collection.objects, key=lambda o:o.name)
object_names = [o.name for o in objects]
object_types = {}
for o in objects: object_types[o.type] = object_types.get(o.type,0)+1

def bounds_for_objs(objs):
    depsgraph=bpy.context.evaluated_depsgraph_get(); pts=[]; mesh_count=0
    for obj in objs:
        if obj.type not in {"MESH","CURVE","FONT","SURFACE","META"}: continue
        evaluated=obj.evaluated_get(depsgraph)
        if obj.type == "MESH":
            me=evaluated.to_mesh()
            try:
                pts.extend(evaluated.matrix_world @ v.co for v in me.vertices)
                mesh_count += 1
            finally: evaluated.to_mesh_clear()
        else:
            pts.extend(evaluated.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not pts: return None, mesh_count
    return [[float(min(p[i] for p in pts)),float(max(p[i] for p in pts))] for i in range(3)],mesh_count

bounds, mesh_count = bounds_for_objs(objects)
asset_geometry=[o for o in objects if o.name not in {"Site_Lawn_Ground","Site_MacArthur_Drive","Site_Courtyard_Walkway"} and o.type not in {"CAMERA","LIGHT"}]
geometry_bounds, _ = bounds_for_objs(asset_geometry)
# Structural base geometry: only the building's major brick massing/core objects; exclude landscaping and glazing.
structural=[o for o in objects if any(t in o.name for t in ("Brick_Core","Pavilion_Main_Brick","Pavilion_East_Block","West_Pavilion_S","West_Entrance_Bay","Courtyard_Core","North_Transition"))]
structural_bounds, structural_mesh_count = bounds_for_objs(structural)
structural_names = [o.name for o in structural]
# Evaluate actual collection bounds and overall bounds against source-derived local bounds.
gis=json.loads(GIS.read_text(encoding="utf-8"))
source=next(b for b in gis["buildings"] if b["code"]=="HARR")
origin=entry.get("placement_origin_xy_m")
gis_local=[[float(x-origin[0]),float(y-origin[1])] for ring in source["rings_xy_m"] for x,y in ring]
gis_local_bounds=[[min(p[i] for p in gis_local),max(p[i] for p in gis_local)] for i in range(2)]
# Object-local and transformed centers from the manifest origin.
placements={"manifest_origin_xy_m":origin,"source_polygon_center_xy_m":source["official_polygon_center_xy_m"],
            "source_center_minus_origin_m":[source["official_polygon_center_xy_m"][i]-origin[i] for i in range(2)]}
# External dependencies and collection export checks.
linked_libraries=[str(lib.filepath) for lib in bpy.data.libraries if lib.filepath]
external_image_paths=[]; packed_images=[]
for img in bpy.data.images:
    if img.source not in {"GENERATED","VIEWER"} and img.filepath:
        if img.packed_file: packed_images.append(img.filepath)
        else: external_image_paths.append(img.filepath)
image_material_refs=[]
for obj in objects:
    for slot in obj.material_slots:
        mat=slot.material
        if not mat or not mat.use_nodes: continue
        for n in mat.node_tree.nodes:
            if n.type=="TEX_IMAGE" and n.image:
                image_material_refs.append({"object":obj.name,"image":n.image.name,"filepath":n.image.filepath,"packed":bool(n.image.packed_file)})

# Save and reopen only the exported collection, in a separate probe file.
probe_path=OUT/"collection_export_probe.blend"
bpy.data.libraries.write(str(probe_path), {collection}, path_remap="RELATIVE_ALL", fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(probe_path))
exported=bpy.data.collections.get(EXPECTED_COLLECTION)
assert exported is not None
export_names=sorted(o.name for o in exported.objects)
export_types={}
for o in exported.objects: export_types[o.type]=export_types.get(o.type,0)+1
probe={"asset_file":str(ASSET.relative_to(ROOT)),"asset_sha256":hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 "blender_version":bpy.app.version_string,"scene":source_scene_name,"collection":EXPECTED_COLLECTION,
 "manifest_id":entry["id"],"manifest_collection":entry["collection"],"manifest_count":entry["object_count"],"manifest_name_count":len(entry["objects"]),
 "original_collection_object_count":len(objects),"original_object_types":object_types,"original_object_names":object_names,
 "evaluated_full_bounds_local_m":bounds,"evaluated_building_bounds_local_m":geometry_bounds,
 "structural_object_names":structural_names,"structural_object_count":len(structural),"structural_mesh_count":structural_mesh_count,
 "structural_bounds_local_m":structural_bounds,"source_feature_id":source["fid"],"source_name":source["name"],"source_levels_attribute":source["num_levels_attribute"],
 "source_official_center_xy_m":source["official_polygon_center_xy_m"],"source_aabb_xy_m":source["aabb_xy_m"],"source_polygon_local_bounds_m":gis_local_bounds,
 "source_rotated_rect":source["minimum_rotated_rectangle"],"placement":placements,
 "linked_libraries_before_export":linked_libraries,"external_image_paths":external_image_paths,"packed_images":packed_images,"image_material_refs":image_material_refs,
 "export_probe_file":probe_path.name,"export_collection_object_count":len(exported.objects),"export_object_names":export_names,
 "export_object_types":export_types,"export_name_set_matches_manifest":set(export_names)==set(entry["objects"]),
 "export_has_camera_or_light":any(o.type in {"CAMERA","LIGHT"} for o in exported.objects),
 "exported_external_linked_libraries":[str(lib.filepath) for lib in bpy.data.libraries if lib.filepath],
 "scene_building_id":source_scene_building_id,"scene_source_feature_id":source_scene_feature_id}
(OUT/"blender_probe.json").write_text(json.dumps(probe,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({k:probe[k] for k in ["blender_version","scene","original_collection_object_count","original_object_types","evaluated_building_bounds_local_m","structural_object_count","structural_bounds_local_m","source_feature_id","source_polygon_local_bounds_m","placement","manifest_count","manifest_name_count","export_collection_object_count","export_object_types","export_name_set_matches_manifest","export_has_camera_or_light","linked_libraries_before_export","external_image_paths"]},indent=2))
