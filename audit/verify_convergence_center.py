"""Reopen and validate the standalone Convergence Center library."""
import bpy
import json
import os
from mathutils import Vector

collection = bpy.data.collections.get("Asset_convergence_center")
assert collection is not None, "missing exported collection"
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == "MESH"]
materials = {m for o in meshes for m in o.data.materials if m}
textured, missing = [], []
for material in sorted(materials, key=lambda m: m.name):
    connected_texture = False
    if material.use_nodes and material.node_tree:
        for node in material.node_tree.nodes:
            if node.type in {"TEX_NOISE", "TEX_IMAGE", "TEX_VORONOI", "TEX_WAVE", "TEX_CHECKER", "TEX_GRADIENT"}:
                if any(socket.is_linked for socket in node.outputs):
                    connected_texture = True
                    break
    (textured if connected_texture else missing).append(material.name)
minimum = [min((o.matrix_world @ Vector(corner))[axis] for o in meshes for corner in o.bound_box) for axis in range(3)]
maximum = [max((o.matrix_world @ Vector(corner))[axis] for o in meshes for corner in o.bound_box) for axis in range(3)]
project = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
preview = os.path.join(os.path.dirname(__file__), "convergence_center_preview.png")
result = {
    "opened_file": bpy.data.filepath,
    "collection": collection.name,
    "objects_in_export_collection": len(objects),
    "mesh_objects": len(meshes),
    "unique_materials": len(materials),
    "materials_with_connected_procedural_or_image_texture": textured,
    "materials_without_connected_texture": missing,
    "collection_local_bounds_m": [[round(minimum[i], 3), round(maximum[i], 3)] for i in range(3)],
    "preview_camera_present": bpy.data.objects.get("Preview_camera") is not None,
    "preview_render_exists": os.path.isfile(preview),
    "preview_path": os.path.relpath(preview, project),
}
assert meshes, "collection has no mesh geometry"
assert not missing, f"materials without connected textures: {missing}"
assert result["preview_render_exists"], "preview render is missing"
out = os.path.join(os.path.dirname(__file__), "convergence_center_validation.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
print(json.dumps(result))
