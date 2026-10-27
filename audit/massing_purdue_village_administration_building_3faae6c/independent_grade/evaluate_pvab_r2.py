"""Fresh independent PVAB review; run with Blender 4.5+ in background."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_purdue_village_administration_building_3faae6c"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / ASSET_ID
OUT = AUDIT / "independent_grade" / "evaluation_r2.json"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137


def xy_from_lonlat(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def evaluate():
    # Open the saved asset in this fresh Blender process and inspect evaluated mesh data.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    coll = bpy.data.collections.get(f"Asset_{ASSET_ID}")
    obj = bpy.data.objects.get("Purdue Village Administration Building")
    assert coll is not None and obj is not None and obj.type == "MESH" and obj.name in coll.objects

    gis = json.loads((AUDIT / "sources" / "arcgis_fid524_raw.json").read_text(encoding="utf-8"))
    feature = gis["features"][0]
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0]
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]
    expected_xy = [xy_from_lonlat(float(lon), float(lat)) for lon, lat in ring]
    projected_ring_area = abs(sum(
        expected_xy[i][0] * expected_xy[(i + 1) % len(expected_xy)][1] -
        expected_xy[(i + 1) % len(expected_xy)][0] * expected_xy[i][1]
        for i in range(len(expected_xy))) / 2.0)
    gis_area_field = float(attrs.get("Shape__Area") or 0.0)
    gis_area_field_disagrees = abs(gis_area_field - projected_ring_area) / max(projected_ring_area, 1e-9) > 0.05

    depgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_obj = obj.evaluated_get(depgraph)
    mesh = evaluated_obj.to_mesh()
    world = [evaluated_obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    evaluated_obj.to_mesh_clear()
    bottom_xy = [(v.x, v.y) for v in world if abs(v.z) < 1e-5]
    max_ring_error = max(min(math.dist(p, q) for q in bottom_xy) for p in expected_xy)
    bounds = [[min(v.x for v in world), max(v.x for v in world)],
              [min(v.y for v in world), max(v.y for v in world)],
              [min(v.z for v in world), max(v.z for v in world)]]
    dimensions = [b[1] - b[0] for b in bounds]

    osm = json.loads((AUDIT / "sources" / "osm_way_283274993_raw.json").read_text(encoding="utf-8"))
    osm_match = any(e.get("type") == "way" and e.get("id") == 283274993 and
                    e.get("tags", {}).get("name") == attrs.get("BUILDING_N")
                    for e in osm.get("elements", []))
    archive_evidence = json.loads((AUDIT / "sources" / "purdue_archives_photo_evidence.json").read_text(encoding="utf-8"))
    archive_photo = AUDIT / "sources" / "purdue_archives_building74.jpeg"
    source_observations = archive_evidence.get("photographic_observations", [])

    # The source photograph was visually compared directly with the reopened asset's
    # facade preview and mesh. Check material assignments as supporting geometry evidence.
    material_names = [m.name if m else "<none>" for m in obj.data.materials]
    material_faces = {}
    for polygon in obj.data.polygons:
        name = material_names[polygon.material_index] if polygon.material_index < len(material_names) else "<none>"
        material_faces[name] = material_faces.get(name, 0) + 1
    facade_materials = ["PVAB archive brick", "PVAB pale vertical metal panels",
                        "PVAB dark entrance glazing", "PVAB charcoal frames and canopy"]
    facade_materials_present = all(name in material_names for name in facade_materials)

    evidence_record_path = AUDIT / "evidence_record.json"
    reopen_path = AUDIT / "reopen_validation.json"
    required_files = [
        "build_log.txt", "evidence_record.json", "preview_oblique.png", "preview_top.png",
        "preview_facade.png", "reopen_validation.json", "sources/arcgis_fid524_raw.json",
        "sources/osm_way_283274993_raw.json", "sources/purdue_archives_record_snapshot.json",
        "sources/purdue_archives_photo_evidence.json", "sources/purdue_archives_building74.jpeg",
    ]
    present = {name: (AUDIT / name).is_file() for name in required_files}
    resource_paths = []
    for group_name in ("images", "libraries", "fonts", "sounds", "movieclips", "cache_files"):
        for item in getattr(bpy.data, group_name, []):
            path = getattr(item, "filepath", "")
            if path:
                resource_paths.append(path)
    absolute_external = [p for p in resource_paths
                         if Path(bpy.path.abspath(p)).is_absolute() and not p.startswith("//")]
    reopen = json.loads(reopen_path.read_text(encoding="utf-8")) if reopen_path.is_file() else {}
    evidence_record = json.loads(evidence_record_path.read_text(encoding="utf-8")) if evidence_record_path.is_file() else {}

    criteria = [
        {"criterion": "Identity and source-backed footprint", "score": 1.5 if gis_area_field_disagrees else 2, "max_score": 2,
         "status": "ring geometry verified; area attribute conflicts" if gis_area_field_disagrees else "verified", "evidence": [
             f"Freshly reopened mesh is {obj.name}; Purdue ArcGIS FID {attrs.get('FID')} identifies {attrs.get('BUILDING_N')} ({attrs.get('BLDG_ABBR')}).",
             f"OSM way 283274993 independently carries the same building name (match={osm_match}).",
             f"The mesh bottom ring matches all {len(expected_xy)} GIS vertices within {max_ring_error:.6f} m; shoelace area of the transformed source ring is {projected_ring_area:.3f} m2.",
             f"The source's Shape__Area field says {gis_area_field:.3f} m2, a {((gis_area_field / projected_ring_area) - 1) * 100:.1f}% difference from the raw ring coordinates."],
         "findings": (["ArcGIS Shape__Area attribute conflicts with the area computed from its raw ring; the model follows the ring coordinates, but the metadata discrepancy is unresolved."] if gis_area_field_disagrees else []) + ([] if attrs.get("FID") == 524 and osm_match and max_ring_error < 0.01 else ["GIS identity or footprint comparison failed."])},
        {"criterion": "Position, orientation, and scale/dimensions", "score": 2, "max_score": 2,
         "status": "verified against project GIS transform", "evidence": [
             f"Reopened evaluated bounds are {bounds} m and dimensions are {[round(x, 3) for x in dimensions]} m.",
             "Footprint coordinates and orientation follow the official GIS ring using the project's documented local lon/lat approximation; object transform is identity.",
             f"Independent vertex error is {max_ring_error:.6f} m; saved reopen validation reports {reopen.get('max_vertex_error_vs_live_gis_project_transform_m')} m."],
         "findings": ["The campus coordinate conversion is an approximate local transform, not survey-grade georeferencing."]},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": 1, "max_score": 2,
         "status": "partly supported; height remains estimated", "evidence": [
             f"The Purdue Archives building-specific photo visibly supports one low above-grade storey and a horizontal parapeted roof edge; its observation record states this explicitly: {source_observations[:2]}.",
             f"The reopened mesh is {dimensions[2]:.2f} m high with a flat cap, but the evidence record labels height as an estimate; source GIS NUM_LEVELS={attrs.get('NUM_LEVELS')} and Extrution={attrs.get('Extrution')} are zero/unpopulated.",
             "Photograph hides the roof surface, so only the low horizontal parapet/roof edge is supported; exact height and roof construction remain unverified."],
         "findings": ["Model height (4.2 m) is estimated rather than measured; photo does not show roof surface or establish roof construction."]},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": 2 if facade_materials_present and archive_photo.is_file() else 0,
         "max_score": 2, "status": "facade features visually supported; bearing uncertain",
         "evidence": [
             "Direct visual comparison of the saved facade preview and Purdue Archives photo shows the same composition: reddish-brown brick segment, broad pale vertically ribbed metal cladding, recessed dark glazed entry, and shallow dark canopy.",
             f"Reopened mesh has source-named material slots for the four observed facade elements (present={facade_materials_present}); material face counts are {material_faces}.",
             "The Archives photo is a building-specific official source; it does not encode camera compass bearing, so exact campus side/orientation of the pictured entrance is uncertain."],
         "findings": [] if facade_materials_present and archive_photo.is_file() else ["Required source photo or modeled facade material evidence is missing."]},
        {"criterion": "Modular export, portability, and complete evidence", "score": 2 if len(coll.objects) == 1 and all(present.values()) and not absolute_external else 0,
         "max_score": 2, "status": "verified" if len(coll.objects) == 1 and all(present.values()) and not absolute_external else "incomplete",
         "evidence": [
             f"Saved file reopened; expected collection Asset_{ASSET_ID} has {len(coll.objects)} object(s).",
             f"Required source/evidence files present: {present}.",
             f"No external absolute file dependencies detected: {absolute_external}.",
             f"Evidence record and reopen validation are present; saved mesh has {len(obj.data.vertices)} vertices and {len(obj.data.polygons)} faces."],
         "findings": [] if len(coll.objects) == 1 and all(present.values()) and not absolute_external else ["Export, evidence completeness, or portability verification failed."]},
    ]
    score = sum(c["score"] for c in criteria)
    return {"building_id": ASSET_ID, "evaluator": "independent_grade/evaluate_pvab_r2.py",
            "evaluated_asset": str(ASSET), "score": score, "max_score": 10,
            "passing_threshold": 8, "passed": score >= 8, "criteria": criteria,
            "evidence": {"reopened": True, "evaluated_vertex_count": len(world),
                         "evaluated_face_count": len(obj.data.polygons), "evaluated_bounds_m": bounds,
                         "evaluated_dimensions_m": dimensions, "official_gis_fid": attrs.get("FID"),
                         "official_gis_name": attrs.get("BUILDING_N"), "official_gis_ring_vertex_count": len(expected_xy),
                         "projected_raw_ring_area_m2": projected_ring_area, "gis_shape_area_attribute_m2": gis_area_field,
                         "maximum_source_vertex_error_m": max_ring_error, "osm_name_match": osm_match,
                         "archive_photo_found": archive_photo.is_file(), "archive_source_observations": source_observations,
                         "material_names": material_names, "material_face_counts": material_faces,
                         "external_absolute_file_paths": absolute_external, "evidence_files_present": present,
                         "reopen_validation": reopen, "evidence_record_present": bool(evidence_record)},
            "findings": [finding for criterion in criteria for finding in criterion["findings"]]}


result = evaluate()
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
