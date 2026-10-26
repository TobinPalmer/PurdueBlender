"""Fresh-process checks for the Family Express library; run with Blender -b asset --python."""
import bpy
import json
import hashlib
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSET_ID = "massing_family_express_a07e1fb"
COLLECTION = "Asset_" + ASSET_ID
SCENE = "Building_" + ASSET_ID
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fresh_open_validation.json")
SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources", "osm_way_374563309_2026-10-26.json")

if bpy.context.scene.name != SCENE:
    raise RuntimeError("Unexpected scene: %s" % bpy.context.scene.name)
root = bpy.data.collections.get(COLLECTION)
if root is None:
    raise RuntimeError("Expected asset collection missing")
objs = list(root.objects)
mesh_objects = [o for o in objs if o.type == "MESH"]
fonts = [o for o in objs if o.type == "FONT"]
if len(objs) != 503 or len(mesh_objects) != 500 or len(fonts) != 3:
    raise RuntimeError("Unexpected asset collection object counts: %s/%s/%s" % (len(objs),len(mesh_objects),len(fonts)))

walls = bpy.data.objects.get("FEXP source footprint brick exterior walls")
if walls is None or walls.data.uv_layers.get("FacadeUV_meters") is None:
    raise RuntimeError("Source wall shell or meter UV layer is missing")
with open(SOURCE, encoding="utf-8") as f:
    source = json.load(f)
way = next(e for e in source["elements"] if e["type"] == "way" and e["id"] == 374563309)
nodes = {e["id"]: (e["lat"],e["lon"]) for e in source["elements"] if e["type"] == "node"}
ring_ids = way["nodes"][:-1]
expected=[]
for node_id in ring_ids:
    lat,lon=nodes[node_id]
    expected.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
if len(walls.data.vertices) < 2*len(expected):
    raise RuntimeError("Wall shell has fewer footprint vertices than the source ring")
base=[(v.co.x,v.co.y) for v in walls.data.vertices[:len(expected)]]
source_to_model=max(min(math.hypot(x-sx,y-sy) for x,y in base) for sx,sy in expected)
model_to_source=max(min(math.hypot(x-sx,y-sy) for sx,sy in expected) for x,y in base)
max_footprint_vertex_error=max(source_to_model,model_to_source)
if max_footprint_vertex_error > 0.001:
    raise RuntimeError("Footprint mismatch %.6f m" % max_footprint_vertex_error)

world_vertices=[]
for obj in mesh_objects:
    for corner in obj.bound_box:
        p=obj.matrix_world @ Vector(corner)
        world_vertices.append((p.x,p.y,p.z))
bounds=[[min(v[i] for v in world_vertices) for i in range(3)], [max(v[i] for v in world_vertices) for i in range(3)]]
asset_path=bpy.data.filepath
with open(asset_path,"rb") as f:
    sha=hashlib.sha256(f.read()).hexdigest()
report={
    "status":"PASS",
    "fresh_process_opened":True,
    "blender_version":bpy.app.version_string,
    "asset_path":os.path.relpath(asset_path,ROOT).replace("\\","/"),
    "sha256":sha,
    "scene":bpy.context.scene.name,
    "asset_collection":COLLECTION,
    "object_count":len(objs),
    "mesh_object_count":len(mesh_objects),
    "font_object_count":len(fonts),
    "material_names":sorted({m.name for o in objs if o.type=="MESH" for m in o.data.materials if m}),
    "material_count":len({m.name for o in objs if o.type=="MESH" for m in o.data.materials if m}),
    "image_datablocks":[{"name":i.name,"source":i.source,"filepath":i.filepath} for i in bpy.data.images],
    "external_image_dependencies":sum(bool(i.filepath) and i.source not in {"GENERATED","VIEWER"} for i in bpy.data.images),
    "linked_libraries":len(bpy.data.libraries),
    "python_text_blocks":len(bpy.data.texts),
    "footprint_source_way_id":way["id"],
    "footprint_ring_vertex_count":len(expected),
    "footprint_max_source_to_model_vertex_error_m":source_to_model,
    "footprint_max_model_to_source_vertex_error_m":model_to_source,
    "world_bounds_m":bounds,
    "preview_collection_exists":bpy.data.collections.get("Preview_only_context_exclude_from_master") is not None,
    "expected_export_collection_present":True,
}
with open(OUT,"w",encoding="utf-8") as f:
    json.dump(report,f,indent=2)
print("FEXP_FRESH_OPEN_PASS",json.dumps(report))
