"""Read-only Blender probe for the ADDL independent grade."""
import bpy
import json

building_id = "animal_disease_diagnostic_laboratory"
collection_name = "Asset_animal_disease_diagnostic_laboratory"
collection = bpy.data.collections.get(collection_name)
assert bpy.context.scene.name == "Scene"
assert collection is not None
assert collection.get("building_id") == building_id
shell = bpy.data.objects.get("ADDL_GIS_Footprint_Primary_Shell")
assert shell is not None and shell.type == "MESH" and shell.name in collection.objects
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = shell.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
points = [(round((evaluated.matrix_world @ v.co).x, 6),
           round((evaluated.matrix_world @ v.co).y, 6),
           round((evaluated.matrix_world @ v.co).z, 6)) for v in mesh.vertices]
evaluated.to_mesh_clear()
unique_xy = sorted({(x, y) for x, y, _ in points})
all_objects = sorted(o.name for o in collection.objects)
external_images = []
for obj in collection.objects:
    for slot in obj.material_slots:
        mat = slot.material
        if mat and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image and node.image.filepath:
                    external_images.append(node.image.filepath)
bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
print("INDEPENDENT_GRADE_JSON=" + json.dumps({
    "scene": bpy.context.scene.name,
    "collection": collection.name,
    "building_id": collection.get("building_id"),
    "source_feature_id": collection.get("source_feature_id"),
    "story_count": collection.get("story_count"),
    "object_count": len(collection.objects),
    "object_names": all_objects,
    "object_types": {kind: sum(o.type == kind for o in collection.objects)
                     for kind in sorted({o.type for o in collection.objects})},
    "shell_unique_xy_count": len(unique_xy),
    "shell_unique_xy": unique_xy,
    "shell_bounds_m": bounds,
    "external_image_paths": sorted(set(external_images)),
    "nonzero_object_transforms": [o.name for o in collection.objects
                                  if o.type != "FONT" and any(abs(v) > 1e-6 for v in o.location)],
}, sort_keys=True))
