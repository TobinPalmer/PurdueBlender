"""Fresh-open, source-footprint, portability, and collection audit for the bookstore asset."""
import bpy
import hashlib
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_university_book_store_717bf2c.blend"
EVIDENCE = ROOT / "audit" / "purdue_university_book_store"
OSM = EVIDENCE / "osm_way_117396621_full.json"
SCENE_NAME = "Building_massing_university_book_store_717bf2c"
COLLECTION_NAME = "Asset_massing_university_book_store_717bf2c"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
METRES_PER_LON = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
METRES_PER_LAT = 111040.0
ANCHOR_LAT, ANCHOR_LON = 40.4242313, -86.9100869
ANCHOR = ((ANCHOR_LON - ORIGIN_LON) * METRES_PER_LON,
          (ANCHOR_LAT - ORIGIN_LAT) * METRES_PER_LAT)


def run():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE_NAME)
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if scene is None or collection is None:
        raise RuntimeError("Expected building scene or asset collection is missing after reopen")
    shell = bpy.data.objects.get("Building shell | exact OpenStreetMap footprint")
    if shell is None or shell.type != "MESH":
        raise RuntimeError("Source-backed OSM shell mesh was not found")

    source = json.loads(OSM.read_text(encoding="utf-8-sig"))
    nodes = {str(e["id"]): e for e in source["elements"] if e["type"] == "node"}
    way = next(e for e in source["elements"] if e["type"] == "way" and e["id"] == 117396621)
    expected = []
    for node_id in way["nodes"][:-1]:
        node = nodes[str(node_id)]
        expected.append(((float(node["lon"]) - ORIGIN_LON) * METRES_PER_LON - ANCHOR[0],
                         (float(node["lat"]) - ORIGIN_LAT) * METRES_PER_LAT - ANCHOR[1]))
    lower_ring = [shell.matrix_world @ shell.data.vertices[i].co for i in range(len(expected))]
    distances = []
    for point in expected:
        distances.append(min(math.hypot(p.x - point[0], p.y - point[1]) for p in lower_ring))
    max_footprint_vertex_error = max(distances)
    if max_footprint_vertex_error > 0.00002:
        raise RuntimeError(f"OSM footprint mismatch {max_footprint_vertex_error:.8f}m")

    asset_objects = list(collection.objects)
    local_bounds = [[min((o.matrix_world @ v.co)[axis] for o in asset_objects if o.type == "MESH" for v in o.data.vertices),
                     max((o.matrix_world @ v.co)[axis] for o in asset_objects if o.type == "MESH" for v in o.data.vertices)]
                    for axis in range(3)]
    external_images = [image.filepath for image in bpy.data.images
                       if image.source == "FILE" and image.filepath and not image.packed_file]
    external_libraries = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
    if external_images or external_libraries:
        raise RuntimeError(f"External dependencies detected: images={external_images}, libraries={external_libraries}")
    for obj in asset_objects:
        if collection not in obj.users_collection:
            raise RuntimeError(f"Asset object not directly linked to expected collection: {obj.name}")

    report = {
        "fresh_open": True,
        "scene": scene.name,
        "collection": collection.name,
        "asset_object_count": len(asset_objects),
        "mesh_object_count": sum(obj.type == "MESH" for obj in asset_objects),
        "text_object_count": sum(obj.type == "FONT" for obj in asset_objects),
        "other_asset_object_count": sum(obj.type not in {"MESH", "FONT"} for obj in asset_objects),
        "asset_local_bounds_m": local_bounds,
        "campus_anchor_xy_m": list(ANCHOR),
        "osm_way": "way/117396621",
        "osm_version": way["version"],
        "osm_timestamp": way["timestamp"],
        "osm_footprint_vertex_count": len(expected),
        "max_osm_footprint_vertex_error_m": max_footprint_vertex_error,
        "external_unpacked_images": external_images,
        "external_libraries": external_libraries,
        "independent_grade": "pending",
        "integrated_in_master": False,
        "limitation": "The floor plan and rear elevations are inferred; rooftop form and heights are estimates. The asset is standalone and awaits coordinator-side manifest/placement/master integration."
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    model = json.loads((EVIDENCE / "model_evidence.json").read_text(encoding="utf-8"))
    model["asset"] = "modular/buildings/massing_university_book_store_717bf2c.blend"
    model["validation"] = {
        "asset_reopen": "passed",
        "geometry_review": "passed; 9 OSM source vertices match within 0.00002 m",
        "independent_grade": "pending",
        "master_integration": "pending coordinator-owned placement marker and index update"
    }
    (EVIDENCE / "model_evidence.json").write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    (EVIDENCE / "asset_sha256.txt").write_text(f"{digest}  {ASSET.relative_to(ROOT).as_posix()}\n", encoding="utf-8")
    print(json.dumps({"asset_sha256": digest, **report}, indent=2))


if __name__ == "__main__":
    run()
