"""Independent Blender 4.x probe for the AHF candidate; run with -b asset --python this_file.py."""
import bpy, bmesh, json, math
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular/buildings/massing_animal_holding_facility_4733f46.blend"
out = Path(__file__).resolve().parent / "blender_probe.json"
collection_name = "Asset_massing_animal_holding_facility_4733f46"
collection = bpy.data.collections.get(collection_name)
assert collection is not None, "expected exported collection absent"
members = list(collection.objects)
assert len(members) == 1, f"expected one object, got {len(members)}"
obj = members[0]
assert obj.name == "Animal Holding Facility" and obj.type == "MESH"
bm = bmesh.new(); bm.from_mesh(obj.data)
boundary = sum(edge.is_boundary for edge in bm.edges)
nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
bm.free()
dg = bpy.context.evaluated_depsgraph_get()
ev = obj.evaluated_get(dg); mesh = ev.to_mesh()
pts = [obj.matrix_world @ v.co for v in mesh.vertices]
bounds = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
ev.to_mesh_clear()
src_geo = json.loads((root / "audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json").read_text(encoding="utf-8-sig"))
ring = src_geo["features"][0]["geometry"]["rings"][0][:-1]
source_xy = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
              (lat - 40.4274) * 111040.0) for lon,lat in ring]
mesh_xy = [(p.x,p.y) for p in pts]
nearest = [min(math.hypot(x-vx,y-vy) for vx,vy in mesh_xy) for x,y in source_xy]
result = {
  "asset": str(asset), "scene": bpy.context.scene.name,
  "collection": collection.name, "object_count": len(members),
  "object": obj.name, "type": obj.type,
  "vertices": len(obj.data.vertices), "edges": len(obj.data.edges), "faces": len(obj.data.polygons),
  "boundary_edges": boundary, "nonmanifold_edges": nonmanifold,
  "modifiers": [m.name for m in obj.modifiers],
  "image_dependencies": [img.filepath for img in bpy.data.images if img.source == "FILE"],
  "bounds_world_m": bounds,
  "source_ring_vertex_nearest_mesh_vertex_m": {"count":len(nearest),"max":max(nearest),"mean":sum(nearest)/len(nearest)},
  "materials": [m.name if m else None for m in obj.data.materials],
  "material_slots": len(obj.material_slots),
  "result": "PASS" if boundary == 0 and nonmanifold == 0 else "FAIL"
}
# Test portability after clearing the opened library file from Blender's main database.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(asset), link=True) as (src, dst):
  assert collection_name in src.collections
  dst.collections = [collection_name]
linked = dst.collections[0]
assert linked is not None
bpy.context.scene.collection.children.link(linked)
linked_members = list(linked.objects)
result["fresh_scene_link"] = {
  "collection": linked.name, "objects": [o.name for o in linked_members],
  "image_dependencies": [img.filepath for img in bpy.data.images if img.source == "FILE"],
  "pass": len(linked_members) == 1 and linked_members[0].name == "Animal Holding Facility"
}
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
