"""Read-only validation of the saved assigned building library."""
import bpy, json, os
from mathutils import Vector

asset_id = "massing_village_bottle_shoppe_6a17e23"
expected_scene = "Building_" + asset_id
expected_collection = "Asset_" + asset_id
expected_object = "Village Bottle Shoppe"
scene = bpy.data.scenes.get(expected_scene)
collection = bpy.data.collections.get(expected_collection)
obj = bpy.data.objects.get(expected_object)
issues = []
if scene is None: issues.append("missing stable scene")
if collection is None: issues.append("missing stable asset collection")
if obj is None or obj.type != "MESH": issues.append("missing stable mesh object")
if collection and [o.name for o in collection.objects] != [expected_object]: issues.append("asset collection object set differs from manifest")
if scene and [o.name for o in scene.objects] != [expected_object]: issues.append("asset scene contains non-export objects")
if obj and collection not in obj.users_collection: issues.append("mesh is not linked to stable asset collection")

result = {"file": bpy.data.filepath, "scene": scene.name if scene else None,
          "collection": collection.name if collection else None,
          "collection_object_names": [o.name for o in collection.objects] if collection else [],
          "scene_object_names": [o.name for o in scene.objects] if scene else [],
          "mesh_vertices": len(obj.data.vertices) if obj else None,
          "mesh_faces": len(obj.data.polygons) if obj else None,
          "materials": [m.name if m else None for m in obj.data.materials] if obj else [],
          "external_library_links": len(bpy.data.libraries),
          "external_image_paths": [i.filepath for i in bpy.data.images if i.source == "FILE"],
          "bound_box_world_m": [[min((obj.matrix_world @ Vector(v))[a] for v in obj.bound_box),
                                  max((obj.matrix_world @ Vector(v))[a] for v in obj.bound_box)] for a in range(3)] if obj else None,
          "footprint_area_m2": obj.get("footprint_area_m2") if obj else None,
          "source_shape_area_raw": obj.get("source_shape_area_raw") if obj else None,
          "evidence_geometry": obj.get("footprint_source") if obj else None,
          "issues": issues}
out = os.path.join(os.path.dirname(__file__), "fresh_open_verification.json")
with open(out, "w", encoding="utf-8") as f: json.dump(result, f, indent=2)
print("FRESH_OPEN_VERIFY", json.dumps(result))
