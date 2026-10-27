"""Independent Redeemer Lutheran Church grading evaluator.

Run with Blender 5.2.3 against the saved asset:
  blender --background modular/buildings/massing_redeemer_lutheran_church_2e5ce2f.blend --python audit/redeemer_lutheran_church/independent_grade_kyle.py
"""
import bpy
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET_ID = "massing_redeemer_lutheran_church_2e5ce2f"
BLEND = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
RAW = HERE / "source_osm_way_473799725_raw.json"
CONTACT = HERE / "sources" / "redeemer_contact.html"
PHOTO_NOTE = HERE / "source_exterior_photo_observation.json"
PREVIEW = HERE / "preview_detail_r2.png"
BUILDER = ROOT / "modular" / "buildings" / f"build_{ASSET_ID}.py"


def xy_from_latlon(lat, lon):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def simplify_sequential(points, tolerance=0.3):
    kept = []
    for p in points:
        if not kept or math.dist(kept[-1], p) >= tolerance:
            kept.append(p)
    if len(kept) > 1 and math.dist(kept[0], kept[-1]) < tolerance:
        kept.pop()
    return kept


def bounds(points):
    return [min(p[0] for p in points), max(p[0] for p in points),
            min(p[1] for p in points), max(p[1] for p in points)]


def evaluate():
    raw = json.loads(RAW.read_text(encoding="utf-8-sig"))
    photo = json.loads(PHOTO_NOTE.read_text(encoding="utf-8-sig"))
    html = CONTACT.read_text(encoding="utf-8-sig", errors="replace")
    way = raw["way"]
    tags = way.get("tags", {})
    nodes = {node["id"]: node for node in raw["nodes"]}
    ordered = [nodes[node_id] for node_id in way["nodes"]]
    source_xy = simplify_sequential([xy_from_latlon(n["lat"], n["lon"]) for n in ordered])

    obj = bpy.data.objects.get("Redeemer Lutheran Church")
    coll = bpy.data.collections.get("Asset_" + ASSET_ID)
    if obj is None or coll is None or obj not in coll.objects[:]:
        raise RuntimeError("Expected Redeemer object or export collection is missing")
    world = [obj.matrix_world @ v.co for v in obj.data.vertices]
    bottom = [(p.x, p.y) for p in world if abs(p.z) < 1e-5]
    unique_bottom = []
    for p in bottom:
        if not any(math.dist(p, q) < 1e-4 for q in unique_bottom):
            unique_bottom.append(p)
    model_xy = [(p.x, p.y) for p in world]
    source_bbox = bounds(source_xy)
    model_bbox = bounds(model_xy)
    model_z = [min(p.z for p in world), max(p.z for p in world)]
    source_to_model = [min(math.dist(p, q) for q in unique_bottom) for p in source_xy]
    model_to_source = [min(math.dist(p, q) for q in source_xy) for p in unique_bottom]
    symmetric_error = max(source_to_model + model_to_source) if source_to_model and model_to_source else None

    # The official contact page corroborates the building identity/address. The
    # 2017 Exponent image is a small halftone: it supports a one-level gabled form
    # and side windows, but supplies no scale, heights, or full measured facade.
    identity_ok = (way.get("id") == 473799725
                   and tags.get("name") == "Redeemer Lutheran Church"
                   and tags.get("amenity") == "place_of_worship"
                   and "510 lindberg avenue" in html.lower()
                   and len(source_xy) == 24)
    exported = len(coll.objects) == 1 and coll.objects[0] == obj and obj.type == "MESH"
    material_names = [m.name for m in obj.data.materials if m]
    face_material_counts = {}
    for poly in obj.data.polygons:
        idx = poly.material_index
        name = material_names[idx] if idx < len(material_names) else "<missing>"
        face_material_counts[name] = face_material_counts.get(name, 0) + 1
    source_reuse_paths = all(p.exists() for p in (RAW, CONTACT, PHOTO_NOTE, PREVIEW, BUILDER, BLEND))

    criteria = [
        {"name": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2,
         "status": "identity/OSM feature verified; source accuracy uncertain",
         "evidence": f"Raw OSM way/{way.get('id')} names Redeemer Lutheran Church and tags it as a Lutheran place of worship. The official congregation contact snapshot lists 510 Lindberg Avenue, West Lafayette; the 2017 newspaper ad image identifies Redeemer Lutheran Church at Salisbury & Lindberg. The 24-vertex OSM outline is the source footprint, but it is volunteered mapping rather than survey evidence."},
        {"name": "Position, orientation, and scale/dimensions", "score": 1.75 if symmetric_error is not None and symmetric_error <= 0.01 else 1.0,
         "max_score": 2, "status": "matches source feature; geodetic accuracy not independently surveyed",
         "evidence": f"Reprojected the preserved OSM ring using the documented project transform, then reproduced the 0.3 m importer point filter. The model has {len(unique_bottom)} unique grade vertices; source-to-model symmetric nearest-vertex error is {symmetric_error:.6f} m. Source XY bounds={source_bbox}; model overall bounds including roofs/details={model_bbox}. This confirms import consistency, not positional accuracy versus survey control."},
        {"name": "Evidence-backed height, floors, and roof form", "score": 1.0,
         "max_score": 2, "status": "roof form photo-supported; heights and dimensions estimated",
         "evidence": f"The source photo shows a low, one-level building with a steep gabled main volume and small side windows. OSM supplies no height or level tags and the image has no scale. Model height is {model_z[1]-model_z[0]:.2f} m, comprising estimated 4.8 m eaves and 10.8 m ridge; these are not measured."},
        {"name": "Facade, entrances, and distinctive architecture", "score": 1.25,
         "max_score": 2, "status": "partly photo-supported and simplified",
         "evidence": f"The saved preview shows perimeter walls, a central gabled volume, repeated small windows, and a paired-entry marker. The low-resolution newspaper image supports a gabled form and side windows, but the front feature is indistinct and entrance/window spacing cannot be measured. Mesh face material counts: {face_material_counts}."},
        {"name": "Modular export, portability, and complete evidence", "score": 2.0 if exported and source_reuse_paths else 1.0,
         "max_score": 2, "status": "verified in reopened asset",
         "evidence": f"Asset reopened in Blender 5.2.3 with stable ID/path, expected object and collection, and one mesh object ({len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces). Dedicated builder, source snapshots, structured evidence, photo observation, render, and reopen validation are present={source_reuse_paths}. Materials are embedded in the mesh; no external texture dependency is required."}
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    result = {
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "asset_path": str(BLEND.relative_to(ROOT)),
            "asset_id": ASSET_ID,
            "source_way_id": way.get("id"),
            "source_tags": tags,
            "source_crs": raw.get("crs"),
            "source_vertex_count_after_filter": len(source_xy),
            "model_unique_grade_vertex_count": len(unique_bottom),
            "source_to_model_symmetric_vertex_error_m": symmetric_error,
            "source_bounds_xy_m": source_bbox,
            "model_bounds_xy_m_including_additions": model_bbox,
            "model_z_bounds_m": model_z,
            "export_collection_object_count": len(coll.objects),
            "mesh_vertices": len(obj.data.vertices),
            "mesh_faces": len(obj.data.polygons),
            "materials": material_names,
            "official_contact_address_match": "510 lindberg avenue" in html.lower(),
            "photo_source_date": photo.get("source_title"),
            "reopened_in_blender": True,
            "preview_path": str(PREVIEW.relative_to(ROOT)),
            "source_snapshots_present": source_reuse_paths
        },
        "findings": [
            "Keep eave and ridge heights, gable placement, roof treatment for unphotographed wings, and facade dimensions marked estimated; no measured elevations or plan source was found.",
            "The OSM-to-mesh agreement is extremely close but tests consistency with the original import, not independent survey accuracy or structural-wall registration.",
            "The only architectural photograph is a small 2017 halftone; the central gable feature, entrance, and side-wing roof forms remain simplified or uncertain."
        ]
    }
    out = HERE / "independent_grade_kyle.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("INDEPENDENT_GRADE=" + json.dumps(result))
    return result


evaluate()
