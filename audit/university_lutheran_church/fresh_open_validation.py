import bpy
import bmesh
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset_id = "massing_university_lutheran_church_20903f1"
expected_scene = "Building_" + asset_id
expected_collection = "Asset_" + asset_id
scene = bpy.data.scenes.get(expected_scene)
collection = bpy.data.collections.get(expected_collection)
errors = []
if scene is None: errors.append("expected building scene is missing")
if collection is None: errors.append("expected asset collection is missing")

def bounds_for(objects):
    points=[]
    for obj in objects:
        if obj.type != "MESH":
            continue
        for p in obj.bound_box:
            points.append(obj.matrix_world @ bpy.mathutils.Vector(p) if hasattr(bpy, "mathutils") else obj.matrix_world @ __import__('mathutils').Vector(p))
    if not points: return None
    return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]

objs = list(collection.all_objects) if collection else []
mesh_objs = [o for o in objs if o.type == "MESH"]
images = [i.filepath for i in bpy.data.images if i.source == "FILE"]
libraries = [lib.filepath for lib in bpy.data.libraries]
envelope = bpy.data.objects.get("ULu | brick building envelope and sloped roof")
topology = None
if envelope and envelope.type == "MESH":
    bm=bmesh.new(); bm.from_mesh(envelope.data)
    topology={"vertices":len(bm.verts),"edges":len(bm.edges),"faces":len(bm.faces),
              "boundary_edges":sum(1 for e in bm.edges if e.is_boundary),
              "non_manifold_edges":sum(1 for e in bm.edges if not e.is_manifold),
              "loose_vertices":sum(1 for v in bm.verts if not v.link_edges)}
    bm.free()

# Inspect computed mesh bounds from the envelope, excluding decorative awnings.
envelope_bounds=None
if envelope:
    pts=[envelope.matrix_world @ __import__('mathutils').Vector(corner) for corner in envelope.bound_box]
    envelope_bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]

report={
  "scene_present":scene is not None,
  "collection_present":collection is not None,
  "asset_collection_object_count":len(objs),
  "mesh_object_count":len(mesh_objs),
  "materials_used":sorted({m.name for o in objs if hasattr(o.data,"materials") for m in o.data.materials if m}),
  "external_image_paths":images,
  "external_library_paths":libraries,
  "envelope_bounds_world_m":envelope_bounds,
  "envelope_topology":topology,
  "errors":errors,
  "result":"PASS" if not errors and scene is not None and collection is not None and envelope_bounds is not None and topology and topology["boundary_edges"]==0 and topology["non_manifold_edges"]==0 and not images and not libraries else "FAIL"
}
out=root/"audit"/"university_lutheran_church"/"fresh_open_validation.json"
out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))
