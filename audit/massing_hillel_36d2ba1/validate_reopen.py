"""Read-only Hillel asset validation; run with Blender -b <asset> -P this file."""
import bpy
import json
import os

asset_id = "massing_hillel_36d2ba1"
scene_name = "Building_" + asset_id
collection_name = "Asset_" + asset_id
asset_path = os.path.abspath(bpy.data.filepath)
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
assert scene is not None, f"Missing scene: {scene_name}"
assert collection is not None, f"Missing collection: {collection_name}"
depsgraph = bpy.context.evaluated_depsgraph_get()
vertices = []
mesh_objects = []
shell_vertices = []
ground_shell_vertices = []
for obj in collection.objects:
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        vertices.extend([evaluated.matrix_world @ v.co for v in mesh.vertices])
        if obj.name == "Hillel":
            shell_vertices.extend([evaluated.matrix_world @ v.co for v in mesh.vertices])
            ground_shell_vertices.extend([evaluated.matrix_world @ v.co for v in mesh.vertices if abs(v.co.z) < 1e-6])
        mesh_objects.append({
            "name": obj.name,
            "vertices": len(mesh.vertices),
            "polygons": len(mesh.polygons),
            "modifiers": [m.name for m in obj.modifiers],
            "materials": [m.name for m in obj.data.materials],
            "linked_library": obj.library.filepath if obj.library else None,
        })
    finally:
        evaluated.to_mesh_clear()
assert vertices, "No evaluated mesh vertices in asset collection"
mins = [min(v[i] for v in vertices) for i in range(3)]
maxs = [max(v[i] for v in vertices) for i in range(3)]
shell_mins = [min(v[i] for v in shell_vertices) for i in range(3)]
shell_maxs = [max(v[i] for v in shell_vertices) for i in range(3)]
assert len(ground_shell_vertices) == 12, f"Expected 12 GIS ground-ring vertices, found {len(ground_shell_vertices)}"
ground_mins = [min(v[i] for v in ground_shell_vertices) for i in range(3)]
ground_maxs = [max(v[i] for v in ground_shell_vertices) for i in range(3)]
expected_xy = [[-337.395863, -305.997686], [-341.539272, -315.957570]]
for axis in range(2):
    assert abs(ground_mins[axis] - expected_xy[axis][0]) < 0.0001
    assert abs(ground_maxs[axis] - expected_xy[axis][1]) < 0.0001
assert "Hillel" in collection.objects, "Expected source mesh object name Hillel"
assert len(collection.objects) == 4, f"Expected four asset meshes, found {len(collection.objects)}"
assert not any(o.library for o in collection.objects), "Asset collection contains linked objects"
assert not bpy.data.libraries, "Blend contains external linked libraries"
external_images = [
    img.filepath for img in bpy.data.images
    if img.source == "FILE" and img.filepath and not img.packed_file
]
report = {
    "status": "passed",
    "asset_id": asset_id,
    "asset_path": asset_path,
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "collection": collection.name,
    "asset_object_count": len(collection.objects),
    "blend_written_by_version": "4.5.15 LTS; original 5.2 file was rebuilt after no 5.2 executable was available locally",
    "scene_object_count": len(scene.objects),
    "overall_evaluated_bounds_world_m": [[round(float(v), 6) for v in mins], [round(float(v), 6) for v in maxs]],
    "overall_evaluated_dimensions_m": [round(float(maxs[i] - mins[i]), 6) for i in range(3)],
    "shell_plus_roof_eave_bounds_world_m": [[round(float(v), 6) for v in shell_mins], [round(float(v), 6) for v in shell_maxs]],
    "shell_plus_roof_eave_dimensions_m": [round(float(shell_maxs[i] - shell_mins[i]), 6) for i in range(3)],
    "GIS_ground_ring_vertex_count": len(ground_shell_vertices),
    "GIS_ground_ring_bounds_world_m": [[round(float(v), 6) for v in ground_mins], [round(float(v), 6) for v in ground_maxs]],
    "GIS_ground_ring_bounds_check": "passed against the 12-point source footprint bounds within 0.0001 m",
    "mesh_objects": mesh_objects,
    "external_libraries": [lib.filepath for lib in bpy.data.libraries],
    "unpacked_external_images": external_images,
    "collection_instance_offset_m": [round(float(collection.instance_offset[i]), 6) for i in range(3)],
    "notes": [
        "Asset geometry is in campus world coordinates, as required for a massing library.",
        "The shell wall-height placeholder is 3.6576 m; GIS Extrution=12 has undocumented units and does not verify architectural height.",
    ],
}
out_path = os.path.join(os.path.dirname(__file__), "reopen_validation.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))

