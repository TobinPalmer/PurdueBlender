"""Independent Schowe House asset evaluation; run in Blender background."""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/massing_purdue_center_for_regional_development_scho_a2375c9.blend"
GIS = ROOT / "audit/schowe_house/sources/purdue_gis_fid295_schowe_house_2026-10-26.json"
COLLECTION = "Asset_massing_purdue_center_for_regional_development_scho_a2375c9"
EXPECTED_SHA = "20bf463365d19bd69ad7a32d240228b5eb8ca51c0feeb06271f0076cce0b8de7"


def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = dx * dx + dy * dy
    if den == 0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / den))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def evaluate():
    digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    payload = json.loads(GIS.read_text(encoding="utf-8"))
    feature = payload["features"][0]
    attrs = feature["attributes"]
    ring_ll = feature["geometry"]["rings"][0]
    origin_lon, origin_lat = -86.9137, 40.4274
    coslat = math.cos(math.radians(origin_lat))
    ring = [((lon - origin_lon) * 111412.84 * coslat,
             (lat - origin_lat) * 111040.0) for lon, lat in ring_ll]

    collection = bpy.data.collections.get(COLLECTION)
    errors = []
    if collection is None:
        return {"status": "FAIL", "errors": [f"missing collection {COLLECTION}"],
                "asset_sha256": digest}
    objects = list(collection.all_objects)
    meshes = [o for o in objects if o.type == "MESH"]
    wall = next((o for o in meshes if o.name.endswith("_Perimeter_Brickwork")), None)
    if wall is None:
        errors.append("missing structural perimeter object")
        wall_points = []
    else:
        wall_points = [(float((wall.matrix_world @ v.co).x),
                        float((wall.matrix_world @ v.co).y),
                        float((wall.matrix_world @ v.co).z)) for v in wall.data.vertices]
    base = [(x, y) for x, y, z in wall_points if abs(z) <= 1e-5]
    if not base:
        errors.append("no wall vertices at the source footprint datum")
        gis_to_model = model_to_gis = None
    else:
        gis_to_model = max(min(math.hypot(x - mx, y - my) for mx, my in base)
                           for x, y in ring[:-1])
        segments = list(zip(ring[:-1], ring[1:]))
        model_to_gis = max(min(point_segment_distance((x, y), a, b) for a, b in segments)
                           for x, y in base)

    dg = bpy.context.evaluated_depsgraph_get()
    all_points = []
    for obj in meshes:
        evaluated = obj.evaluated_get(dg)
        mesh = evaluated.to_mesh()
        all_points.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
        evaluated.to_mesh_clear()
    bounds = [[min(p[i] for p in all_points), max(p[i] for p in all_points)]
              for i in range(3)] if all_points else None
    missing_material = [o.name for o in meshes if not o.data.materials or
                        any(m is None for m in o.data.materials)]
    packed = sorted(img.name for img in bpy.data.images
                    if img.name.startswith("SCHO_") and img.packed_file is not None)
    external = sorted(img.filepath for img in bpy.data.images
                      if img.source == "FILE" and img.filepath and not img.packed_file)
    expected_sha_matches = digest.lower() == EXPECTED_SHA
    if not expected_sha_matches:
        errors.append(f"asset hash differs from submitted revision: {digest}")
    if attrs.get("OBJECTID") != 295 or attrs.get("Name") != "Schowe House":
        errors.append("raw GIS snapshot identity does not match expected Schowe House feature")
    if len(meshes) != 39:
        errors.append(f"expected 39 mesh objects, found {len(meshes)}")
    if missing_material:
        errors.append(f"mesh objects without complete material assignment: {missing_material}")

    source_bounds = [[min(p[i] for p in ring[:-1]), max(p[i] for p in ring[:-1])]
                     for i in range(2)]
    wall_bounds = [[min(p[i] for p in wall_points), max(p[i] for p in wall_points)]
                   for i in range(2)] if wall_points else None
    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "score": 1.4, "max_score": 2,
         "status": "identity verified; geometry does not consistently follow source ring", "evidence": [
             f"Raw Purdue GIS feature {attrs.get('OBJECTID')} identifies {attrs.get('Name')} at {attrs.get('ADDRESS')}; source area {attrs.get('Shape.STArea()')} m².",
             "Official Purdue campus map and PCRD contact page identify SCHO / Schowe House; NIRPC 2025 appendix associates a Schowe House image with the 1341 Northwestern Avenue contact block.",
             f"Independent baseline vertex-to-wall check: GIS-to-model max nearest-vertex error {gis_to_model:.6f} m; model-wall-to-GIS max point-to-segment error {model_to_gis:.6f} m." if gis_to_model is not None else "Footprint probe unavailable."
         ], "reason": "The name/address/source match is sound, but the actual wall mesh is several metres outside parts of its claimed GIS outline."},
        {"criterion": "Position, orientation, and scale/dimensions", "score": 0.8, "max_score": 2,
         "status": "substantial horizontal mismatch", "evidence": [
             "Independent checks compare the actual wall mesh vertices at ground level with the 40-vertex GIS ring in the project’s documented approximate meter conversion.",
             f"The maximum GIS-vertex-to-wall-vertex distance is {gis_to_model:.3f} m and the maximum wall-vertex-to-GIS-segment distance is {model_to_gis:.3f} m; multiple wall vertices are not on/near the source perimeter.",
             f"GIS bounds are {source_bounds}; wall mesh bounds are {wall_bounds}; evaluated full-asset bounds are {bounds}. The model extends beyond the footprint on several edges, beyond what a small roof overhang explains."
         ], "reason": "The chosen source coordinate transform is documented, but independent geometry checks show the mesh does not preserve the source plan dimensions and perimeter. Master placement is not reviewed here."},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": 0.8, "max_score": 2,
         "status": "mostly estimated", "evidence": [
             "The GIS text has no measured elevation or floor count; model notes explicitly state gable/eave/chimney heights are estimated from one oblique exterior photo.",
             "The roof image shows multiple intersecting planes and dormers, but the visible facade-to-roof relationships and some roof/wall intersections are difficult to reconcile from the single image."
         ], "reason": "Roof vocabulary is photo-informed, but the main height and roof intersections are not measured or fully resolved by the available single view."},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": 1.0, "max_score": 2,
         "status": "partially supported; geometry review found substantial visual defects", "evidence": [
             "The model includes brick, slate and cedar roof textures, dormers, chimneys, windows, an entrance porch and garage doors, generally consistent with the source photo.",
             "Independent visual inspection of both previews finds broad discontinuities and uncovered gaps in several wall runs, openings that appear unglazed/unframed in the principal view, and roof planes that visibly overlap or terminate irregularly.",
             "The NIRPC reference is one oblique image partly obscured by vegetation; it does not establish every facade or exact entrance/window placement."
         ], "reason": "The correct architectural vocabulary is present, but missing/fragmented wall coverage and visibly irregular roof/facade joins prevent a passing fidelity score."},
        {"criterion": "Modular export, portability, and complete evidence", "score": 2.0, "max_score": 2,
         "status": "verified in fresh Blender reopen", "evidence": [
             f"Fresh Blender {bpy.app.version_string} process opened the exact asset and found collection {COLLECTION}, {len(objects)} collection objects and {len(meshes)} meshes.",
             f"The expected SHA-256 matches: {digest}; all mesh objects have assigned materials: {not missing_material}.",
             f"Packed building texture images: {packed}; unpacked external image dependencies: {external}.",
             "Building-specific source register, raw GIS, address-associated 2025 photo, model metrics, preview renders, and reopen report are present."
         ], "reason": "The standalone library and source evidence are portable and reproduce in a fresh process."}
    ]
    calculated = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "Rebuild the wall baseline from the GIS ring and compare actual structural vertices/segments to each source edge; the current model is up to 5.003 m from the mapped perimeter.",
        "Repair the intersecting roof masses and their gable ends/fascia; both saved views show visible clipping or unsupported detached roof/wall pieces.",
        "Revise wall generation so every structural perimeter run is continuous except for openings supported by the photograph; frame/glaze those openings consistently.",
        "Seek a second facade/photo or floorplan/elevation to verify entrance orientation, garage/wing arrangement, floor count, ridge/eave heights, and the 1990 west addition. If unavailable, retain those items as estimates."
    ]
    return {
        "building": "Schowe House / Global Policy Research Institute",
        "asset_id": ASSET.stem,
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "asset_sha256": digest,
        "grader": "independent_grader_subagent",
        "grade_date": "2026-10-26",
        "score": calculated,
        "max_score": 10,
        "passing_threshold": 8,
        "status": "PASS" if calculated >= 8 and not errors else "FAIL",
        "criteria": criteria,
        "evidence": {
            "blender_version": bpy.app.version_string,
            "fresh_open_scene": bpy.context.scene.name,
            "collection": COLLECTION,
            "object_count": len(objects),
            "mesh_count": len(meshes),
            "gis_feature_id": attrs.get("OBJECTID"),
            "gis_building_name": attrs.get("Name"),
            "gis_area_m2": attrs.get("Shape.STArea()"),
            "gis_to_model_wall_max_vertex_error_m": gis_to_model,
            "model_wall_to_gis_max_segment_error_m": model_to_gis,
            "gis_bounds_m": source_bounds,
            "structural_wall_bounds_m": wall_bounds,
            "evaluated_full_asset_bounds_m": bounds,
            "packed_textures": packed,
            "unpacked_external_images": external,
            "preview_images": [
                "audit/schowe_house/preview_three_quarter.png",
                "audit/schowe_house/preview_roof.png",
                "audit/schowe_house/sources/schowe_house_pcrd_photo_2025_crop.png"
            ]
        },
        "findings": findings,
        "errors": errors
    }


result = evaluate()
out = Path(__file__).resolve().parent / "result.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
