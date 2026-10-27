"""Export the Gemini foundation slab's lower perimeter for the independent check."""
import json
from pathlib import Path

import bpy

obj = bpy.data.objects.get("Gemini | footprint ground and lower-floor slab")
if obj is None or obj.type != "MESH":
    raise RuntimeError("Expected structural footprint slab is missing")
verts = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
zmin = min(v.z for v in verts)
bottom_faces = [poly for poly in obj.data.polygons
                if all(abs(verts[index].z-zmin) < 1e-5 for index in poly.vertices)]
if not bottom_faces:
    raise RuntimeError("No bottom footprint face found on structural slab")
bottom_face = max(bottom_faces, key=lambda poly: len(poly.vertices))
ring = [(round(verts[index].x, 7), round(verts[index].y, 7)) for index in bottom_face.vertices]
result = {"object": obj.name, "bottom_z_m": zmin, "lower_xy_vertices_local_m": ring,
          "total_mesh_vertices": len(verts), "lower_vertex_count": len(ring)}
out = Path(bpy.data.filepath).resolve().parents[2] / "audit" / "gemini" / "independent_grade_r1" / "slab_ring.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
