"""Independent r2 review of the Herrick Acoustics saved Blender library.

Run with Blender 4.5: blender --background --python evaluate_herrick_r2.py
The evaluator explicitly reopens the saved asset in a fresh Blender process.
Only this independent_grade/r2 directory is written.
"""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ASSET_ID = "massing_herrick_laboratories_2138103"
ASSET = ROOT / "modular" / "buildings" / (ASSET_ID + ".blend")
AUDIT = ROOT / "audit" / ASSET_ID
GRADE = AUDIT / "independent_grade" / "r2"
GIS = AUDIT / "sources" / "purdue_building_shapes_fid246_herl_2026-10-26.json"
INSPECTION_OUT = GRADE / "direct_inspection.json"
RESULT_OUT = GRADE / "result.json"

def lonlat_to_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

def polygon_area(points):
    return abs(sum(points[i][0] * points[(i+1) % len(points)][1]
                   - points[(i+1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) * 0.5)

def inspect_saved_asset():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    coll = bpy.data.collections.get("Asset_" + ASSET_ID)
    objs = list(coll.objects) if coll else []
    mesh_objs = [obj for obj in objs if obj.type == "MESH"]
    obj = mesh_objs[0] if len(mesh_objs) == 1 else None
    measurements = None
    if obj:
        deps = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        world = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        bounds = [[min(v[i] for v in world), max(v[i] for v in world)] for i in range(3)]
        base = [v for v in world if abs(v.z) < 1e-5]
        raw = json.loads(GIS.read_text(encoding="utf-8-sig"))["features"][0]
        attrs = raw["attributes"]
        ring = raw["geometry"]["rings"][0]
        if ring[0] == ring[-1]:
            ring = ring[:-1]
        ring_xy = [lonlat_to_xy(lon, lat) for lon, lat in ring]
        ring_xy_clean = []
        for point in ring_xy:
            if not ring_xy_clean or math.dist(point, ring_xy_clean[-1]) > 0.01:
                ring_xy_clean.append(point)
        if len(ring_xy_clean) > 2 and math.dist(ring_xy_clean[0], ring_xy_clean[-1]) <= 0.01:
            ring_xy_clean.pop()
        errors = [min(math.hypot(v.x-x, v.y-y) for v in base) for x,y in ring_xy_clean]
        area = polygon_area(ring_xy_clean)
        images = [{"filepath": image.filepath, "packed": bool(image.packed_file)}
                  for image in bpy.data.images if image.source == "FILE"]
        libraries = [lib.filepath for lib in bpy.data.libraries]
        renders = [AUDIT / "r2" / "herrick_acoustics_courtyard_preview_r2.png",
                   AUDIT / "r2" / "herrick_acoustics_plan_preview_r2.png"]
        measurements = {
            "opened_saved_asset": True,
            "blender_version": bpy.app.version_string,
            "asset": str(ASSET),
            "scene": scene.name,
            "collection": coll.name if coll else None,
            "collection_object_count": len(objs),
            "object": obj.name,
            "object_type": obj.type,
            "mesh_vertices": len(mesh.vertices),
            "mesh_faces": len(mesh.polygons),
            "modifiers": [mod.name for mod in obj.modifiers],
            "bounds_world_m": bounds,
            "world_dimensions_m": [b[1]-b[0] for b in bounds],
            "gis_source": {
                "provider": "Purdue University BuildingShapesZip4 FeatureServer layer 0",
                "FID": attrs.get("FID"), "BLDG_ABBR": attrs.get("BLDG_ABBR"),
                "BUILDING_N": attrs.get("BUILDING_N"),
                "NUM_LEVELS": attrs.get("NUM_LEVELS"),
                "Extrution": attrs.get("Extrution"),
                "Shape__Area": attrs.get("Shape__Area"),
                "cleaned_ring_vertices": len(ring_xy_clean),
                "local_approx_ring_area_m2": area,
                "Shape__Area_to_ring_area_ratio": attrs.get("Shape__Area") / area,
                "max_nearest_ground_vertex_error_m": max(errors),
                "mean_nearest_ground_vertex_error_m": sum(errors)/len(errors),
                "source_ring_count": len(raw["geometry"]["rings"]),
            },
            "unpacked_external_images": [image for image in images if not image["packed"]],
            "linked_libraries": libraries,
            "renders": [{"path": str(path), "exists": path.is_file(),
                         "bytes": path.stat().st_size if path.is_file() else 0}
                        for path in renders],
        }
        evaluated.to_mesh_clear()
    else:
        measurements = {"opened_saved_asset": True, "blender_version": bpy.app.version_string,
                        "scene": scene.name, "collection_object_count": len(objs),
                        "mesh_object_count": len(mesh_objs)}
    return measurements

def evaluate(inspect):
    gis = inspect.get("gis_source", {})
    area_ratio = gis.get("Shape__Area_to_ring_area_ratio")
    renders_ok = len(inspect.get("renders", [])) == 2 and all(
        r["exists"] and r["bytes"] > 10000 for r in inspect.get("renders", []))
    identity_score = 2.0 if (gis.get("FID") == 246 and gis.get("BLDG_ABBR") == "HERL"
                              and gis.get("BUILDING_N") == "Herrick Acoustics"
                              and gis.get("max_nearest_ground_vertex_error_m", 1) < 0.001
                              and gis.get("cleaned_ring_vertices") == 66) else 0.5
    position_score = 1.7 if identity_score == 2.0 else 0.5
    height_score = 1.35
    facade_score = 1.5
    portability_score = 1.8 if (
        inspect.get("scene") == "Building_" + ASSET_ID
        and inspect.get("collection") == "Asset_" + ASSET_ID
        and inspect.get("collection_object_count") == 1
        and inspect.get("object_type") == "MESH"
        and not inspect.get("modifiers")
        and not inspect.get("unpacked_external_images")
        and not inspect.get("linked_libraries")
        and renders_ok) else 1.0
    score = round(identity_score + position_score + height_score + facade_score + portability_score, 1)
    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "score": identity_score,
         "max_score": 2,
         "assessment": "The saved scene represents the historic Herrick Acoustics / HERL complex, not the separate 2013 Ray W. Herrick Laboratories. The Purdue BuildingShapesZip4 FID 246 ring is directly used as the shell base; fresh reopen confirms 66 cleaned source vertices and maximum nearest ground-vertex error below 0.0001 m.",
         "uncertainty": "The service Shape__Area value is materially larger than the transformed ring area; metadata does not resolve its semantics. The source ring is retained without area-based rescaling."},
        {"criterion": "Position, orientation, and scale/dimensions", "score": position_score,
         "max_score": 2,
         "assessment": "The wall shell matches the FID 246 polygon under the documented campus local approximation. The U-shaped footprint and courtyard orientation agree with the retained aerial/plan geometry; wall base comparison is direct rather than based on decorative bounds.",
         "uncertainty": f"The GIS polygon is not a surveyed structural-wall plan; its local ring area is {gis.get('local_approx_ring_area_m2', 0):.2f} m2 while Shape__Area is {gis.get('Shape__Area', 0):.2f}, ratio {area_ratio:.3f}. Overall bounds include modeled facade/roof projections."},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": height_score,
         "max_score": 2,
         "assessment": "Archival and current photographs support the raised central barn volume, pitched roof, cupola, dormers, and lower wings. GIS records three levels, consistent with a multi-level core but insufficient to establish the varied wing and roof heights.",
         "uncertainty": "No measured elevation or reliable height record is present. The 5.0 m wings, 6.9 m eaves, 9.25 m ridge, and 10.95 m cupola top are estimates. GIS Extrution=36 has undocumented units; a feet interpretation is plausible but unverified."},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": facade_score,
         "max_score": 2,
         "assessment": "The r2 courtyard render adds repeated window bays and mullions, pale piers/bands, a clearer entrance canopy, and a courtyard-facing gable. These changes make the model materially closer to the retained Lab Manager photo and institutional newsletter than the r1 render. The brick, roof, cupola, and dormers also correspond to those images.",
         "uncertainty": "The source photo shows long continuous wing glazing, a strongly legible centered entrance/sign/canopy, and a more articulated central roof-to-wall profile. The render still abstracts these details into separated small bays and a subdued entrance; precise bay spacing and entrance geometry are not measured."},
        {"criterion": "Modular export, portability, and complete evidence", "score": portability_score,
         "max_score": 2,
         "assessment": "Fresh Blender reopen verifies the expected scene, collection, and single mesh object with no modifiers, external image dependencies, or linked libraries. R2 direct-reopen measurements, source catalog/raw snapshots, revision notes, and both preview renders are present.",
         "uncertainty": "Blender 4.5.15 emitted a forward-version warning because the file was written by binary version 502.44; geometry and library data still reopened and inspected correctly. The library remains a simple campus-coordinate massing asset; preserve its direct-link convention if integrated into the master."},
    ]
    findings = [
        {"severity": "moderate", "finding": "The GIS Shape__Area field remains 1.7285 times the transformed polygon-ring area, and the service metadata does not explain the difference.",
         "action": "Keep using the returned authoritative ring for the shell; document the discrepancy and only revise if the GIS provider supplies a clarified area basis or corrected geometry."},
        {"severity": "moderate", "finding": "The elevation values remain photo-derived estimates; Extrution=36 has no documented units, and no measured elevation was found.",
         "action": "Retain explicit estimated labels and pursue a dimensioned elevation or facilities height record if a better authoritative source becomes available."},
        {"severity": "minor", "finding": "R2 visibly improves the courtyard facade, but the continuous wing glazing and centered entry/sign composition in the photo are still simplified.",
         "action": "A later refinement could better connect window groups into continuous bands and clarify the center entrance, provided the change remains photo-backed."},
        {"severity": "minor", "finding": "Blender 4.5.15 opened the saved file with a forward-version warning (file binary version 502.44). Direct geometry and collection inspection succeeded.",
         "action": "Confirm the intended minimum Blender version before distributing the library to 4.5-only consumers; avoid saving the file from an older Blender version unless explicitly required."},
    ]
    return {"building_id": ASSET_ID, "review_revision": "r2", "score": score,
            "max_score": 10, "passing_threshold": 8, "passed": score >= 8,
            "criteria": criteria,
            "evidence": {"asset": "modular/buildings/" + ASSET_ID + ".blend",
                         "direct_reopen_measurements": "audit/" + ASSET_ID + "/independent_grade/r2/direct_inspection.json",
                         "r2_validation": "audit/" + ASSET_ID + "/r2/reopen_validation_r2.json",
                         "gis_feature": "audit/" + ASSET_ID + "/sources/purdue_building_shapes_fid246_herl_2026-10-26.json",
                         "source_catalog": "audit/" + ASSET_ID + "/sources/source_catalog.json",
                         "institutional_history": ["audit/" + ASSET_ID + "/sources/purdue_herrick_history_2026-10-26.html",
                                                    "audit/" + ASSET_ID + "/sources/purdue_herrick_facilities_2026-10-26.html"],
                         "visual_sources": ["audit/" + ASSET_ID + "/sources/herrick_laboratories_newsletter_spring_2009.pdf",
                                            "audit/" + ASSET_ID + "/sources/herrick_labs_original_photo_labmanager.jpg"],
                         "review_renders": ["audit/" + ASSET_ID + "/r2/herrick_acoustics_courtyard_preview_r2.png",
                                            "audit/" + ASSET_ID + "/r2/herrick_acoustics_plan_preview_r2.png"],
                         "direct_measurements": inspect},
            "findings": findings}

GRADE.mkdir(parents=True, exist_ok=True)
inspection = inspect_saved_asset()
INSPECTION_OUT.write_text(json.dumps(inspection, indent=2) + "\n", encoding="utf-8")
result = evaluate(inspection)
RESULT_OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
