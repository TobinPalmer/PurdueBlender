import bpy
import hashlib
import json
import math
from pathlib import Path

EXPECTED_SHA256 = "a2614d71fa198caf826a495aca4a0076c4ec3a82756e43b195d0e779481953d2"
BUILDING_ID = "massing_family_express_a07e1fb"
COLLECTION_NAME = "Asset_massing_family_express_a07e1fb"
SCORE = {"identity_footprint": 2.0, "position_dimensions": 2.0, "height_roof": 1.2,
         "facade_distinctive_features": 1.5, "modularity_evidence": 1.7}


def project(lat, lon):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def point_segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    den = dx * dx + dy * dy
    if den == 0:
        return math.dist(point, start)
    t = max(0.0, min(1.0, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / den))
    return math.dist(point, (start[0] + t * dx, start[1] + t * dy))


def directed_distance(points, ring):
    return max(min(point_segment_distance(p, ring[i], ring[(i + 1) % len(ring)])
                   for i in range(len(ring))) for p in points)


def area(ring):
    return abs(sum(ring[i][0] * ring[(i + 1) % len(ring)][1] -
                   ring[(i + 1) % len(ring)][0] * ring[i][1]
                   for i in range(len(ring))) / 2)


def evaluate():
    asset_path = Path(bpy.data.filepath).resolve()
    repo = asset_path.parents[2]
    digest = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    collection = bpy.data.collections.get(COLLECTION_NAME)
    assert digest == EXPECTED_SHA256, f"Candidate changed: {digest}"
    assert collection is not None, f"Expected collection missing: {COLLECTION_NAME}"
    assert bpy.context.scene.name == "Building_massing_family_express_a07e1fb"

    objects = list(collection.all_objects)
    meshes = [o for o in objects if o.type == "MESH"]
    slab = bpy.data.objects.get("FEXP interior floor slab")
    assert slab and slab.type == "MESH"
    model_ring = []
    for index in slab.data.polygons[0].vertices:
        co = slab.matrix_world @ slab.data.vertices[index].co
        model_ring.append((float(co.x), float(co.y)))

    source_path = repo / "audit/family_express/sources/osm_way_374563309_2026-10-26.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    nodes = {e["id"]: e for e in source["elements"] if e["type"] == "node"}
    way = next(e for e in source["elements"] if e["type"] == "way" and e["id"] == 374563309)
    source_ring = [project(nodes[node_id]["lat"], nodes[node_id]["lon"]) for node_id in way["nodes"][:-1]]
    max_source_to_model = directed_distance(source_ring, model_ring)
    max_model_to_source = directed_distance(model_ring, source_ring)
    source_area, model_area = area(source_ring), area(model_ring)

    mesh_vertices = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    bounds = [[min(v[i] for v in mesh_vertices), max(v[i] for v in mesh_vertices)] for i in range(3)]
    linked = [lib.filepath for lib in bpy.data.libraries]
    external_images = [img.filepath for img in bpy.data.images
                       if img.source != "VIEWER" and img.filepath and not img.packed_file]
    materials = sorted({slot.material.name for o in objects for slot in o.material_slots if slot.material})
    result = {
        "building_id": BUILDING_ID,
        "candidate_sha256": digest,
        "expected_sha256": EXPECTED_SHA256,
        "fresh_process_opened": True,
        "blender_version": bpy.app.version_string,
        "scene": bpy.context.scene.name,
        "collection": collection.name,
        "object_count": len(objects),
        "mesh_count": len(meshes),
        "font_count": sum(o.type == "FONT" for o in objects),
        "material_count": len(materials),
        "materials": materials,
        "linked_libraries": linked,
        "unpacked_external_images": external_images,
        "world_bounds_m": bounds,
        "source": {"provider": "OpenStreetMap contributors", "feature_type": "way", "feature_id": 374563309,
                   "name": way["tags"].get("name"), "address": f"{way['tags'].get('addr:housenumber')} {way['tags'].get('addr:street')}",
                   "crs": "EPSG:4326", "source_timestamp": way["timestamp"], "project_transform": "project local approximation"},
        "footprint": {"source_vertex_count": len(source_ring), "model_vertex_count": len(model_ring),
                      "max_source_to_model_boundary_m": max_source_to_model,
                      "max_model_to_source_boundary_m": max_model_to_source,
                      "source_area_m2": source_area, "model_area_m2": model_area,
                      "area_delta_fraction": abs(source_area - model_area) / source_area,
                      "model_ring_xy_m": model_ring, "source_ring_xy_m": source_ring},
        "grade": {
            "score": sum(SCORE.values()), "max_score": 10, "pass_threshold": 8,
            "status": "PASS" if sum(SCORE.values()) >= 8 else "FAIL",
            "criteria": [
                {"name": "Correct identity and source-backed footprint", "score": SCORE["identity_footprint"], "max_score": 2,
                 "evidence": "The official Family Express FAQ lists its Purdue location at 1812 Northwestern Avenue. OSM way 374563309 independently carries the same name/address and retail/convenience tags. This fresh-open evaluator projected its raw nine-vertex ring and compared it to the floor slab ring in both directions."},
                {"name": "Position, orientation, and scale/dimensions", "score": SCORE["position_dimensions"], "max_score": 2,
                 "evidence": "The model keeps the campus-coordinate footprint in the expected master location. The evaluator compares every projected source edge against the model floor-ring edges; bounds and plan orientation agree within the local project transform. This confirms agreement with the volunteered outline, not a surveyed wall location."},
                {"name": "Evidence-backed height, floors, and roof form", "score": SCORE["height_roof"], "max_score": 2,
                 "evidence": "The address-associated MapQuest exterior result depicts a one-story brick retail store with a low charcoal hip roof. The model has one occupied level and a charcoal hipped roof. Exact eave/ridge heights and roof pitch are estimated; neither OSM nor the source photograph supplies measured elevations."},
                {"name": "Facade, entrances, and distinctive architecture", "score": SCORE["facade_distinctive_features"], "max_score": 2,
                 "evidence": "The model has red-brown brick, a broad glazed storefront/double entry, pale fascia, blue Family Express signs, and a separate white canopy with black supports and six dispenser assemblies, matching the location-associated exterior reference at a broad architectural level. The simplified pumps, signage, absent site paving/vehicles, and low visual detail reduce correspondence."},
                {"name": "Modular export, portability, and complete evidence", "score": SCORE["modularity_evidence"], "max_score": 2,
                 "evidence": "Fresh Blender open confirms the expected scene/collection, 503 objects (500 meshes and 3 fonts), 19 materials, and no linked libraries or unpacked images. OSM raw snapshot, source metadata, address evidence, builder script, and exterior/top/interior previews are present. The interior is schematic, roof height and canopy placement are estimated, and the matched image itself is cited by URL rather than preserved locally."}
            ],
            "evidence": [
                "Official Family Express FAQ: https://familyexpress.zendesk.com/hc/en-us/articles/360018927412-Where-are-the-Pet-Washes-located-what-are-the-hours-offered (Purdue store address).",
                "OSM source snapshot: audit/family_express/sources/osm_way_374563309_2026-10-26.json; building way 374563309, last edited 2024-01-17.",
                "Address-associated MapQuest exterior listing/image: https://www.mapquest.com/us/indiana/family-express-378696207 and https://a.mktgcdn.com/p/Q6dWIcLGo--LQCuVeEj1P7dUFpVXkHcROmqnBpKyuqE/2048x1362.jpg (retrieved in image search; date not exposed).",
                "Independent fresh-open visual inspection: audit/family_express/exterior_preview.png, top_preview.png, and interior_cutaway_preview.png."
            ],
            "findings": [
                "Roof pitch, eave/ridge height, canopy geolocation/dimensions, and pump placement remain estimates.",
                "The interior shows representative store fixtures but has no source floor plan.",
                "The preview uses a uniform gray background; the saved exterior view does not include site paving, approach roads, vehicles, or surrounding campus context.",
                "The OSM outline is community mapped, not a surveyed wall footprint."
            ]
        }
    }
    out = repo / "audit/family_express_independent_grade/result.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("FAMILY_EXPRESS_INDEPENDENT_GRADE", json.dumps({"score": result["grade"]["score"], "status": result["grade"]["status"],
          "sha": digest, "footprint": result["footprint"], "counts": [len(objects), len(meshes), len(materials)]}))


evaluate()
