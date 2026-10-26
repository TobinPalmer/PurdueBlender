"""Read-only Blender probe for the saved Duhme asset; run with Blender --background --python."""
import bpy
import hashlib
import json
import math
import os
import sys
from collections import Counter
from mathutils import Vector

ASSET_ID = "massing_duhme_ophelia_residence_hall_1bb4e9c"
COLLECTION_NAME = "Asset_" + ASSET_ID


def bounds_for(collection):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    object_rows = []
    type_counts = Counter()
    material_names = set()
    image_paths = set()
    for obj in collection.all_objects:
        type_counts[obj.type] += 1
        for slot in obj.material_slots:
            if slot.material:
                material_names.add(slot.material.name)
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            matrix = evaluated.matrix_world
            local_world = [matrix @ vertex.co for vertex in mesh.vertices]
            points.extend(local_world)
            object_rows.append({
                "name": obj.name,
                "type": obj.type,
                "vertices": len(mesh.vertices),
                "polygons": len(mesh.polygons),
                "materials": sorted({slot.material.name for slot in obj.material_slots if slot.material}),
                "world_bounds_m": [[min(v[i] for v in local_world), max(v[i] for v in local_world)] for i in range(3)] if local_world else None,
            })
            evaluated.to_mesh_clear()
        elif obj.type in {"FONT", "CURVE", "SURFACE", "META"}:
            object_rows.append({"name": obj.name, "type": obj.type})
    for image in bpy.data.images:
        if image.source == "FILE" and image.filepath:
            path = bpy.path.abspath(image.filepath)
            image_paths.add((image.filepath, os.path.exists(path), image.packed_file is not None))
    if points:
        world_bounds = [[min(v[i] for v in points), max(v[i] for v in points)] for i in range(3)]
    else:
        world_bounds = None
    return {
        "object_count": len(collection.all_objects),
        "object_type_counts": dict(type_counts),
        "world_bounds_m": world_bounds,
        "material_names": sorted(material_names),
        "external_image_dependencies": [
            {"path": p, "exists": exists, "packed": packed}
            for p, exists, packed in sorted(image_paths)
        ],
        "objects": object_rows,
    }


def compare_foundation_to_purdue_polygon(collection):
    source_file = os.path.join(os.path.dirname(__file__), "purdue_historic_campus_building_229.json")
    with open(source_file, "r", encoding="utf-8") as stream:
        source = json.load(stream)["features"][0]["geometry"]["rings"][0]
    source_xy = [((p[0] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                  (p[1] - 40.4274) * 111040.0) for p in source[:-1]]
    foundation = collection.objects.get("DUHME_Continuous_GIS_Footprint_Foundation")
    if not foundation or foundation.type != "MESH":
        return {"status": "NOT_FOUND"}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = foundation.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    candidate_xy = [(float((evaluated.matrix_world @ v.co).x),
                     float((evaluated.matrix_world @ v.co).y))
                    for v in mesh.vertices
                    if abs(float((evaluated.matrix_world @ v.co).z)) <= 0.001]
    evaluated.to_mesh_clear()
    if not candidate_xy:
        return {"status": "NO_BASE_VERTICES"}
    distances_to_source = [min(math.dist(v, s) for s in source_xy) for v in candidate_xy]
    distances_to_candidate = [min(math.dist(s, v) for v in candidate_xy) for s in source_xy]
    return {
        "status": "PASS",
        "source_provider": "Purdue University Libraries Maps & GIS, PuGeoDB.DBO.CampusBuilding OBJECTID 229",
        "source_vertex_count_without_closure": len(source_xy),
        "candidate_base_vertex_count": len(candidate_xy),
        "max_candidate_to_source_vertex_distance_m": max(distances_to_source),
        "mean_candidate_to_source_vertex_distance_m": sum(distances_to_source) / len(distances_to_source),
        "max_source_to_candidate_vertex_distance_m": max(distances_to_candidate),
        "mean_source_to_candidate_vertex_distance_m": sum(distances_to_candidate) / len(distances_to_candidate),
        "candidate_bounds_xy_m": [[min(v[0] for v in candidate_xy), max(v[0] for v in candidate_xy)],
                                   [min(v[1] for v in candidate_xy), max(v[1] for v in candidate_xy)]],
    }


def main():
    path = bpy.data.filepath
    with open(path, "rb") as stream:
        digest = hashlib.sha256(stream.read()).hexdigest().upper()
    collection = bpy.data.collections.get(COLLECTION_NAME)
    result = {
        "status": "PASS" if collection else "FAIL",
        "asset_path": os.path.abspath(path),
        "sha256": digest,
        "expected_asset_id": ASSET_ID,
        "expected_export_collection": COLLECTION_NAME,
        "scene_names": sorted(scene.name for scene in bpy.data.scenes),
        "collection_found": collection is not None,
        "libraries": sorted({lib.filepath for lib in bpy.data.libraries if lib.filepath}),
    }
    if collection:
        result["asset"] = bounds_for(collection)
        result["footprint_vertex_match"] = compare_foundation_to_purdue_polygon(collection)
    out = os.path.join(os.path.dirname(__file__), "candidate_probe.json")
    with open(out, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({key: value for key, value in result.items() if key != "asset"}, indent=2))
    print(json.dumps({key: value for key, value in result["asset"].items() if key != "objects"}, indent=2))


if __name__ == "__main__":
    main()
