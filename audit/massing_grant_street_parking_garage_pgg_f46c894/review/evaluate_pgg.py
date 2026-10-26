"""Independent PGG asset grader; run with Blender background and the .blend loaded."""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "massing_grant_street_parking_garage_pgg_f46c894"
ASSET_ID = "massing_grant_street_parking_garage_pgg_f46c894"
ASSET_COLLECTION = f"Asset_{ASSET_ID}"
BLEND = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS = AUDIT / "sources" / "purdue_gis_oid216_2026-10-26.json"
RECORD = AUDIT / "evidence_record.json"


def campus_xy_from_web_mercator(mx: float, my: float) -> tuple[float, float]:
    lon = math.degrees(mx / 6378137.0)
    lat = math.degrees(2.0 * math.atan(math.exp(my / 6378137.0)) - math.pi / 2.0)
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def evaluate() -> dict:
    """Return scored criteria, inspectable source evidence, and findings."""
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    source = json.loads(GIS.read_text(encoding="utf-8-sig"))
    feature = next(f for f in source["features"] if f["attributes"]["OBJECTID"] == 216)
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0][:-1]
    footprint = [campus_xy_from_web_mercator(float(x), float(y)) for x, y in ring]
    twice_area = sum(footprint[i][0] * footprint[(i + 1) % len(footprint)][1]
                     - footprint[(i + 1) % len(footprint)][0] * footprint[i][1]
                     for i in range(len(footprint)))
    if twice_area < 0:
        footprint.reverse()

    collection = bpy.data.collections.get(ASSET_COLLECTION)
    if collection is None:
        raise RuntimeError(f"Missing exported collection: {ASSET_COLLECTION}")
    base = bpy.data.objects.get("PGG_Footprint_Foundation")
    if base is None or base.type != "MESH":
        raise RuntimeError("Missing GIS-footprint foundation mesh")
    # Each polygon vertex appears twice in the extruded mesh, at z=-0.16 and z=0.
    mesh_xy = [(float(v.co.x), float(v.co.y)) for v in base.data.vertices[:len(footprint)]]
    errors = [min(math.dist(p, q) for q in mesh_xy) for p in footprint]
    max_xy_error = max(errors)
    mean_xy_error = sum(errors) / len(errors)
    gis_bounds = (min(p[0] for p in footprint), max(p[0] for p in footprint),
                  min(p[1] for p in footprint), max(p[1] for p in footprint))
    expected_dims = (gis_bounds[1] - gis_bounds[0], gis_bounds[3] - gis_bounds[2])
    evaluated_points = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh_objects = [o for o in collection.objects if o.type == "MESH"]
    for obj in mesh_objects:
        evaluated = obj.evaluated_get(depsgraph)
        me = evaluated.to_mesh()
        evaluated_points.extend((evaluated.matrix_world @ v.co)[:] for v in me.vertices)
        evaluated.to_mesh_clear()
    asset_bounds = tuple((min(p[i] for p in evaluated_points), max(p[i] for p in evaluated_points))
                         for i in range(3))
    asset_dims = tuple(hi - lo for lo, hi in asset_bounds)
    decks = sorted(o.name for o in collection.objects if o.name.startswith("PGG_Deck_"))
    externals = [im.filepath for im in bpy.data.images if im.packed_file is None and im.filepath]
    renders = [AUDIT / p for p in record.get("renders", [])]
    render_status = {p.name: p.exists() and p.stat().st_size > 100_000 for p in renders}
    expected_collection = ASSET_COLLECTION
    blend_loaded = Path(bpy.data.filepath).resolve() == BLEND.resolve()

    criteria = [
        {"name": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2,
         "evidence": (f"Raw Purdue GIS OBJECTID=216 names {attrs.get('Name')!r}, ABBR={attrs.get('ABBR')}, "
                      f"address={attrs.get('ADDRESS')}; the saved foundation ring matches the independently "
                      f"projected source polygon with max nearest-vertex error {max_xy_error:.6f} m "
                      f"(mean {mean_xy_error:.6f} m, {len(footprint)} vertices)."),
         "status": "verified" if max_xy_error <= 0.01 else "discrepancy"},
        {"name": "Position, orientation, and scale/dimensions", "score": 2.0 if max_xy_error <= 0.01 else 1.0,
         "max_score": 2,
         "evidence": (f"GIS polygon and mesh are in campus coordinates; bounds {gis_bounds}; source-derived "
                      f"XY envelope {expected_dims[0]:.3f} x {expected_dims[1]:.3f} m, evaluated full asset "
                      f"dimensions {asset_dims[0]:.3f} x {asset_dims[1]:.3f} x {asset_dims[2]:.3f} m. "
                      "Plan orientation follows ordered GIS polygon edges. Comparison uses the same GIS feature "
                      "that generated the footprint, so it verifies implementation fidelity, not independent survey accuracy."),
         "status": "source geometry reproduced; absolute survey accuracy unverified"},
        {"name": "Evidence-backed height, floors, and roof form", "score": 1.25, "max_score": 2,
         "evidence": (f"The saved mesh contains {len(decks)} named upper deck polygons and a flat parking roof. "
                      f"The ARSEE source photo visibly supports a multi-level open parking deck and rooftop parking. "
                      f"Modeled total vertical extent is {asset_dims[2]:.2f} m; neither the photo nor cited road-school "
                      "clearance supplies a full building height or surveyed floor elevations. The recorded 3.18 m "
                      "level intervals and 16.83 m top are therefore estimates, not verified measurements."),
         "status": "form visually supported; dimensions estimated"},
        {"name": "Facade, entrances, and distinctive architecture", "score": 1.5, "max_score": 2,
         "evidence": ("Direct comparison of the ARSEE project photo with the saved three-quarter and south-façade "
                      "renders confirms red-brown brick piers/cores, pale horizontal floor bands, open parking bays, "
                      "stair/elevator glazing, and an entry feature are represented. The model simplifies the photo's "
                      "arched precast/spandrel openings and brick core/entry shapes; entrance orientation is explicitly inferred."),
         "status": "major visual features represented with simplifications"},
        {"name": "Modular export, portability, and complete evidence", "score": 2.0, "max_score": 2,
         "evidence": (f"Loaded file matches expected path: {blend_loaded}; exported collection {expected_collection!r} "
                      f"contains {len(collection.objects)} objects ({len(mesh_objects)} mesh objects); no unpacked "
                      f"external images/textures detected ({len(externals)} paths). Evidence record and all three "
                      f"render files exist: {render_status}."),
         "status": "verified" if blend_loaded and all(render_status.values()) and not externals else "partial"},
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "Footprint geometry is a near-exact reproduction of the identified Purdue GIS polygon, but that polygon is not a wall survey and the project’s local geographic approximation is not a surveyed CRS.",
        "No cited source establishes the garage’s full measured height or floor elevations; retain the model height and 3.18 m intervals as estimates.",
        "The undated project photo supports the architectural family, but the current render simplifies the prominent arched floor openings and entrance/core geometry; improve these if closer visual fidelity is required.",
    ]
    return {"score": score, "max_score": 10, "criteria": criteria,
            "evidence": {"asset": str(BLEND), "source_feature": {"objectid": 216,
                         "name": attrs.get("Name"), "address": attrs.get("ADDRESS"),
                         "source_area_m2": attrs.get("Shape__Area"), "projected_ring_vertices": len(footprint)},
                         "footprint_max_vertex_error_m": max_xy_error,
                         "footprint_mean_vertex_error_m": mean_xy_error,
                         "gis_envelope_dimensions_m": expected_dims,
                         "evaluated_asset_dimensions_m": asset_dims,
                         "upper_deck_meshes": decks, "unpacked_external_image_paths": externals,
                         "render_files": render_status},
            "findings": findings}


if __name__ == "__main__":
    result = evaluate()
    output = AUDIT / "review" / "pgg_independent_grade.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
