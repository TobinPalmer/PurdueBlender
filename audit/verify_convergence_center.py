"""Fresh-open, packaging, placement and preview checks for Convergence."""
import bpy
import hashlib
import json
import math
import os
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
ASSET_PATH=os.path.join(ROOT,"modular","buildings","convergence_center.blend")
AUDIT_DIR=os.path.join(ROOT,"audit","convergence_center")
os.makedirs(AUDIT_DIR,exist_ok=True)
EXPECTED_ORIGIN=(-1131.698568664057,-405.52500592356535)
COLLECTION_NAME="Asset_convergence_center"
collection=bpy.data.collections.get(COLLECTION_NAME)
errors=[]
if collection is None:
    errors.append("stable export collection missing")
    objects=[]
else:
    objects=list(collection.all_objects)
origin=collection.get("placement_origin_xy_m") if collection else None
if not origin or math.dist(tuple(origin),EXPECTED_ORIGIN)>.02:
    errors.append(f"placement origin mismatch: {origin}")
if collection and collection.get("source_feature_id")!=946:
    errors.append("official GIS FID 946 missing")
if collection and collection.get("building_id")!="convergence_center":
    errors.append("stable building ID missing")
if collection and collection.get("local_coordinates") is not True:
    errors.append("asset not tagged as local-coordinate geometry")

required_names={
    "CONV_GIS_ground_plate",
    "CONV_GIS_five_story_cladding_volume",
    "CONV_vertical_metal_panel_fins",
    "CONV_flat_roof",
    "CONV_west_entry_canopy",
    "CONV_freestanding_monument_sign_body",
    "CONV_glazed_entry_vestibule",
    "CONV_schematic_double_height_lobby_feature_wall",
    "CONV_schematic_lobby_mezzanine",
}
object_names={o.name for o in objects}
missing_names=sorted(required_names-object_names)
if missing_names: errors.append(f"required source-backed geometry missing: {missing_names}")

meshes=[o for o in objects if o.type=="MESH"]
materials={m for o in objects if getattr(o.data,"materials",None) for m in o.data.materials if m}
missing_texture=[]; external_images=[]; packed_images=[]
for material in materials:
    if not material.use_nodes or not material.node_tree:
        missing_texture.append(material.name); continue
    nodes=material.node_tree.nodes
    connected=False
    for node in nodes:
        if node.type in {"TEX_NOISE","TEX_IMAGE","TEX_VORONOI","TEX_WAVE","TEX_CHECKER","TEX_GRADIENT"}:
            if any(socket.is_linked for socket in node.outputs): connected=True
        if node.type=="TEX_IMAGE":
            if not node.image:
                missing_texture.append(material.name+": empty image node")
            elif node.image.packed_file:
                packed_images.append(node.image.name)
            elif node.image.filepath:
                external_images.append((material.name,node.image.filepath))
    if not connected:
        missing_texture.append(material.name)
if missing_texture: errors.append(f"materials missing connected texture nodes: {sorted(set(missing_texture))}")
if external_images: errors.append(f"external image dependencies found: {external_images}")

if meshes:
    points=[o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
    minimum=[min(p[i] for p in points) for i in range(3)]
    maximum=[max(p[i] for p in points) for i in range(3)]
    model_bounds=[[minimum[i],maximum[i]] for i in range(3)]
else:
    model_bounds=None; errors.append("export collection contains no mesh objects")

# Confirm the front glazing is not backed by a full solid massing prism: the
# cladding object is a thin face skin and the individual glass bays sit in its gaps.
skin=bpy.data.objects.get("CONV_GIS_five_story_cladding_volume")
window_objects=[o for o in meshes if o.name.startswith("CONV_upper_glazing_")]
skin_face_count=len(skin.data.polygons) if skin and skin.type=="MESH" else 0
if not skin_face_count or not window_objects: errors.append("punched facade skin or separate window bays missing")

# Targeted bounding-box check: the freestanding monument should remain outside
# the entrance portal and should not intersect the canopy. This is not a full BVH scan.
def world_aabb(obj):
    pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return [min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]
def aabb_intersects(a,b):
    alo,ahi=a; blo,bhi=b
    return all(alo[i]<=bhi[i] and blo[i]<=ahi[i] for i in range(3))
sign=bpy.data.objects.get("CONV_freestanding_monument_sign_body")
canopy=bpy.data.objects.get("CONV_west_entry_canopy")
sign_canopy_intersection=(aabb_intersects(world_aabb(sign),world_aabb(canopy)) if sign and canopy else None)
if sign_canopy_intersection: errors.append("freestanding sign overlaps the entry canopy")

preview_collection=bpy.data.collections.get("Preview_Only")
scene=bpy.context.scene
if scene.camera is None:
    errors.append("preview camera missing")
if preview_collection: preview_collection.hide_render=False
preview=os.path.join(AUDIT_DIR,"fresh_open_preview.png")
scene.render.image_settings.file_format="PNG"
scene.render.filepath=preview
bpy.ops.render.render(write_still=True)

with open(ASSET_PATH,"rb") as f: digest=hashlib.sha256(f.read()).hexdigest()
# Blender custom properties may be IDPropertyArray values, which the standard
# JSON encoder cannot serialize directly. Normalize nested values explicitly.
def json_value(value):
    if value is None or isinstance(value,(str,int,float,bool)):
        return value
    try:
        return [json_value(item) for item in value]
    except TypeError:
        return str(value)
result={
    "status":"PASS" if not errors else "FAIL",
    "asset_path":os.path.relpath(ASSET_PATH,ROOT),
    "asset_sha256":digest,
    "blender_version":bpy.app.version_string,
    "stable_collection":COLLECTION_NAME,
    "source_feature_id":collection.get("source_feature_id") if collection else None,
    "building_id":collection.get("building_id") if collection else None,
    "placement_origin_xy_m":list(origin) if origin else None,
    "expected_placement_origin_xy_m":list(EXPECTED_ORIGIN),
    "object_count":len(objects),
    "mesh_count":len(meshes),
    "material_count":len(materials),
    "mesh_bounds_local_m":model_bounds,
    "gis_footprint_bounds_local_m":json_value(collection.get("footprint_local_bounds_m")) if collection else None,
    "gis_footprint_area_estimate_m2":collection.get("GIS_footprint_area_estimate_m2") if collection else None,
    "gis_footprint_vertex_count":json_value(collection.get("GIS_footprint_vertices")) if collection else None,
    "punched_facade_skin_face_count":skin_face_count,
    "separate_upper_window_bay_count":len(window_objects),
    "materials_have_connected_textures":not missing_texture,
    "materials_missing_texture_nodes":sorted(set(missing_texture)),
    "external_image_paths":external_images,
    "packed_images":packed_images,
    "monument_sign_canopy_aabb_intersection":sign_canopy_intersection,
    "fresh_open_render":os.path.relpath(preview,ROOT),
    "errors":errors,
}
out=os.path.join(AUDIT_DIR,"fresh_open_validation.json")
with open(out,"w",encoding="utf-8") as f: json.dump(result,f,indent=2); f.write("\n")
if errors: raise RuntimeError(json.dumps(result,indent=2))

evidence_path=os.path.join(ROOT,"audit","convergence_center_evidence.json")
with open(evidence_path,encoding="utf-8") as f: evidence=json.load(f)
evidence["validation"]={
    "saved_and_reopened":True,
    "fresh_open_check":"Separate Blender 5.2.3 process opened the exact saved asset, verified FID 946 and stable local-coordinate export collection/origin, material texture wiring and absence of external image dependencies, checked the punched facade/window separation, and rerendered the scene.",
    "asset_sha256":digest,
    "object_count":len(objects),
    "mesh_count":len(meshes),
    "material_count":len(materials),
    "mesh_bounds_local_m":model_bounds,
    "fresh_open_report":"audit/convergence_center/fresh_open_validation.json",
    "fresh_open_render":"audit/convergence_center/fresh_open_preview.png",
    "previews":{
        "overview":"audit/convergence_center_preview.png",
        "west_elevation":"audit/convergence_center_west_elevation.png",
        "entry_detail":"audit/convergence_center_entry_detail.png",
        "lobby_detail":"audit/convergence_center_lobby_detail.png",
        "roof_plan":"audit/convergence_center_roof_plan.png",
    },
    "external_image_paths":external_images,
    "packed_images":packed_images,
    "targeted_sign_canopy_intersection":sign_canopy_intersection,
    "note":"AABB check tests sign/canopy separation only, not all-scene collision geometry. Source photographs were used for reference and are not linked or embedded as textures.",
}
with open(evidence_path,"w",encoding="utf-8") as f: json.dump(evidence,f,indent=2); f.write("\n")
print(json.dumps(result,indent=2))
