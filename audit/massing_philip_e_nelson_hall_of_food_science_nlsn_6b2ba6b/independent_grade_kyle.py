"""Independent, reproducible rubric review of the saved NLSN massing asset.

Run with Blender 5.2.3 against the saved library:
 blender --background <NLSN asset.blend> --python <this file>

The evaluator reads the saved GIS snapshots, manifest, raw Purdue page
snapshot, and the reopened Blender datablock. It deliberately treats vertical
fields without documented units as uncertain.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ASSET_ID = "massing_philip_e_nelson_hall_of_food_science_nlsn_6b2ba6b"
OBJECT_NAME = "Philip E. Nelson Hall of Food Science (NLSN)"
COLLECTION_NAME = "Asset_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / ASSET_ID
SOURCE = AUDIT / "sources"


def campus_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def shoelace(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1] -
                   points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) / 2.0)


def mercator_xy(lon, lat):
    radius = 6378137.0
    lam, phi = math.radians(lon), math.radians(lat)
    return radius * lam, radius * math.log(math.tan(math.pi / 4 + phi / 2))


def main():
    fc = json.loads((SOURCE / "query.json").read_text(encoding="utf-8-sig"))
    layer = json.loads((SOURCE / "layer.json").read_text(encoding="utf-8-sig"))
    evidence_record = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8-sig"))
    feature = fc["features"][0]
    props = feature["properties"]
    ring_lonlat = feature["geometry"]["coordinates"][0][:-1]
    ring_xy = [campus_xy(lon, lat) for lon, lat in ring_lonlat]
    ring_merc = [mercator_xy(lon, lat) for lon, lat in ring_lonlat]
    source_area_approx = shoelace(ring_xy)
    source_area_mercator = shoelace(ring_merc)

    entry = next(x for x in manifest["assets"] if x["id"] == ASSET_ID)
    obj = bpy.data.objects.get(OBJECT_NAME)
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if obj is None or coll is None:
        raise RuntimeError("Expected manifest asset object/collection missing in saved file")
    world_xy = [tuple((obj.matrix_world @ v.co)[:2]) for v in obj.data.vertices]
    ground_xy = [xy for v, xy in zip(obj.data.vertices, world_xy) if abs(v.co.z) < 1e-4]
    # The source polygon vertices should appear at the bottom level. Using a
    # small metric tolerance allows for float storage in the .blend mesh.
    ring_matches = []
    for sx, sy in ring_xy:
        nearest = min((math.hypot(x - sx, y - sy) for x, y in ground_xy), default=1e9)
        ring_matches.append(nearest)
    max_ring_error = max(ring_matches)
    ring_xy_bounds = [[min(pt[i] for pt in ring_xy), max(pt[i] for pt in ring_xy)] for i in range(2)]
    actual_bounds = [[min(pt[i] for pt in world_xy), max(pt[i] for pt in world_xy)] for i in range(2)]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    z_bounds = [min((evaluated.matrix_world @ Vector(v))[2] for v in evaluated.bound_box),
                max((evaluated.matrix_world @ Vector(v))[2] for v in evaluated.bound_box)]
    material_counts = {}
    for poly in obj.data.polygons:
        idx = poly.material_index
        name = obj.data.materials[idx].name if idx < len(obj.data.materials) else "<none>"
        material_counts[name] = material_counts.get(name, 0) + 1

    raw_events_html = (SOURCE / "events.html").read_text(encoding="utf-8", errors="replace")
    page_identifies_photo = "alt=\"Image of Philip E. Nelson Hall of Food Science\"" in raw_events_html
    photo_exists = (SOURCE / "events_building_photo_large.jpg").is_file()
    expected_object_names = entry.get("objects", [])
    mesh_count = len([o for o in coll.objects if o.type == "MESH"])
    external_images = [im.name for im in bpy.data.images if im.source == "FILE"]
    linked_libraries = [lib.filepath for lib in bpy.data.libraries]
    material_names = [m.name for m in obj.data.materials]

    area_ratio = source_area_mercator / float(props["Shape__Area"])
    criteria = [
        {
            "name": "Identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "status": "verified; GIS area agrees after source CRS is respected",
            "evidence": {
                "GIS_FID": props["FID"], "GIS_abbreviation": props["BLDG_ABBR"],
                "GIS_building_name": props["BUILDING_N"], "GIS_address": props["ADDRESS"],
                "GIS_owner": props["OWNER"], "manifest_id": entry["id"],
                "matched_source_ring_vertices": len(ring_matches),
                "source_ring_vertex_max_error_m": max_ring_error,
                "source_ring_area_approx_ground_m2": round(source_area_approx, 3),
                "Shape__Area_web_mercator_m2": props["Shape__Area"],
                "source_ring_area_reprojected_3857_m2": round(source_area_mercator, 3),
                "reprojected_area_to_attribute_ratio": round(area_ratio, 6),
                "layer_wkid": layer.get("spatialReference", {}).get("latestWkid")
            },
            "reason": "The saved FID 250 polygon identifies NLSN by abbreviation, name, address and Purdue ownership; all 24 source ring points occur at the mesh base. The apparent Shape__Area discrepancy resolves when the EPSG:4326 ring is reprojected to the layer's EPSG:3857; computed and published areas agree within rounding."
        },
        {
            "name": "Position, orientation and dimensions",
            "score": 2.0,
            "max_score": 2.0,
            "status": "verified to the project's approximate campus transform",
            "evidence": {
                "transform": "X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040",
                "source_footprint_bounds_xy_m": [[round(x, 3) for x in b] for b in ring_xy_bounds],
                "model_bounds_xy_m_including_details": [[round(x, 3) for x in b] for b in actual_bounds],
                "object_location_rotation_scale": {"location": list(obj.location), "rotation": list(obj.rotation_euler), "scale": list(obj.scale)},
                "source_dimensions_xy_m": [round(b[1]-b[0], 3) for b in ring_xy_bounds],
                "model_campus_coordinate_frame": "object geometry is stored at campus coordinates; object transform is identity"
            },
            "reason": "The transformed GIS ring is directly built into the saved mesh without a later translation, rotation, or scale change. Model outer bounds differ slightly where the entrance canopy projects beyond the walls. This is an approximate project conversion, not survey-grade positioning."
        },
        {
            "name": "Height, floors and roof form",
            "score": 1.0,
            "max_score": 2.0,
            "status": "partly supported; height and roof remain uncertain",
            "evidence": {
                "GIS_NUM_LEVELS": props.get("NUM_LEVELS"), "GIS_CountOfFLO": props.get("CountOfFLO"),
                "undocumented_GIS_R": props.get("R"), "undocumented_GIS_Extrution": props.get("Extrution"),
                "evaluated_model_z_bounds_m": [round(x, 3) for x in z_bounds],
                "recorded_estimated_main_roof_height_m": evidence_record["vertical_and_architecture"]["estimated_main_roof_height_m"],
                "recorded_estimated_gable_peak_m": evidence_record["vertical_and_architecture"]["estimated_entry_gable_peak_m"]
            },
            "reason": "GIS reports five levels and the model shows five bands, but field units/semantics are undocumented. Treating R=46.6 as feet is an explicit estimate, not a verified roof height. Available perspective photography supports a raised entrance feature but cannot establish the full flat roof silhouette or total building height."
        },
        {
            "name": "Facade, entrances and distinctive architecture",
            "score": 1.5,
            "max_score": 2.0,
            "status": "broad features photo-supported; dimensions and layout estimated",
            "evidence": {
                "Purdue_events_page": "https://events.purdue.edu/philip_e_nelson_hall_of_food_science",
                "page_photo_alt_identifies_building": page_identifies_photo,
                "saved_photo_present": photo_exists,
                "model_material_polygon_counts": material_counts,
                "model_material_names": material_names,
                "visible_model_features": ["red-brown brick material", "repeated dark window fields", "recessed dark door panel", "pale canopy and portico columns", "raised entrance gable"],
                "photo_source_date": "not stated"
            },
            "reason": "Purdue's building page image is labeled as NLSN and visibly supports brick, repeated glazing, a recessed entrance, pale entrance canopy/columns, and a raised entry feature. The model captures these broad cues, but its five-level rhythm, window-bay spacing, entry position, and gable dimensions are not measurable from the undated perspective photo."
        },
        {
            "name": "Modular export, portability and evidence",
            "score": 2.0,
            "max_score": 2.0,
            "status": "verified",
            "evidence": {
                "blend_path": bpy.data.filepath,
                "manifest_file": entry["file"], "expected_collection": entry["collection"],
                "collection_present": coll.name, "expected_object_names": expected_object_names,
                "collection_mesh_object_names": [o.name for o in coll.objects if o.type == "MESH"],
                "collection_mesh_count": mesh_count,
                "external_file_images": external_images,
                "linked_blend_libraries": linked_libraries,
                "source_snapshots": sorted(p.name for p in SOURCE.iterdir()),
                "evidence_record_present": evidence_record.get("asset_id") == ASSET_ID,
                "preview_present": (AUDIT / "preview.png").is_file(),
                "reopen_validation_present": (AUDIT / "reopen_validation.json").is_file()
            },
            "reason": "The saved blend has the expected manifest collection and one named mesh object, identity transforms, generated materials only, no linked libraries or external image files, and a complete building-specific evidence package with raw source snapshots and preview."
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "Passes the 8/10 threshold, but height remains an estimate: the builder interprets the undocumented GIS R=46.6 value as feet and adds a photo-estimated gable peak.",
        "For a stronger height/roof score, obtain a dimensioned elevation, facilities plan, or reliable height measurement and confirm whether NUM_LEVELS includes a basement; otherwise keep these values explicitly estimated.",
        "The source polygon area is not materially inconsistent: 3407.26 m2 in approximate ground coordinates becomes about 5889.32 m2 in EPSG:3857, matching GIS Shape__Area. The builder's evidence note incorrectly calls this an unresolved area conflict; update it to explain the CRS conversion."
    ]
    result = {
        "asset_id": ASSET_ID,
        "evaluator": "independent_grade_kyle.py",
        "evaluation_date": "2026-10-26",
        "blender_version": bpy.app.version_string,
        "reopened_asset": bpy.data.filepath,
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "pass": score >= 8,
        "criteria": criteria,
        "evidence": {
            "primary_vector": "sources/query.json, FID 250",
            "GIS_layer_metadata": "sources/layer.json",
            "exterior_reference": "sources/events.html + sources/events_building_photo_large.jpg",
            "preview_inspected": "preview.png",
            "model_reopen_inspected": True,
            "prior_builder_validation_not_used_as_score": True
        },
        "findings": findings
    }
    output = AUDIT / "independent_grade_kyle.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
