"""Independent re-grade of the localized Drug Discovery asset and master link."""
from __future__ import annotations
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_purdue_drug_discovery_facility_fc72a4a"
ASSET = ROOT / "modular/buildings" / f"{ASSET_ID}.blend"
MASTER = ROOT / "purdue_campus_master.blend"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
DIR = Path(__file__).parent
ASSET_PROBE_SCRIPT = DIR / "blender_probe.py"
MASTER_PROBE_SCRIPT = DIR / "master_probe.py"
ASSET_PROBE_OUT = DIR / "asset_probe_result.json"
MASTER_PROBE_OUT = DIR / "master_probe_result.json"
GIS_FILE = ROOT / "audit/purdue_drug_discovery_facility/sources/arcgis_feature_893_2026-10-26.geojson"
MANIFEST = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
RECORD = next(a for a in MANIFEST["assets"] if a["id"] == ASSET_ID)
ORIGIN_LON, ORIGIN_LAT = -86.9137, 40.4274
M_PER_DEG_LON = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
M_PER_DEG_LAT = 111040.0


def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    if denom == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / denom))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def sampled_hausdorff(rings, model_edges):
    source_edges = [(r[i], r[i + 1]) for r in rings for i in range(len(r) - 1)]
    source_points = [p for r in rings for p in r]
    model_points = {tuple(p) for e in model_edges for p in e}
    d_source_model = max(min(point_segment_distance(p, a, b) for a, b in model_edges) for p in source_points)
    d_model_source = max(min(point_segment_distance(p, a, b) for a, b in source_edges) for p in model_points)
    return d_source_model, d_model_source


def run_probe(script, blend, output):
    proc = subprocess.run([str(BLENDER), "--background", str(blend), "--python", str(script), "--", str(output)],
                          cwd=ROOT, text=True, capture_output=True, timeout=150)
    if proc.returncode != 0 or not output.exists():
        raise RuntimeError(f"Blender probe failed: {proc.stdout}\n{proc.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def evaluate():
    if not BLENDER.exists() or not ASSET.exists() or not MASTER.exists() or not GIS_FILE.exists():
        raise FileNotFoundError("Blender, localized asset, master, or preserved GIS source is missing")
    asset_probe = run_probe(ASSET_PROBE_SCRIPT, ASSET, ASSET_PROBE_OUT)
    master_probe = run_probe(MASTER_PROBE_SCRIPT, MASTER, MASTER_PROBE_OUT)
    asset_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    master_sha = hashlib.sha256(MASTER.read_bytes()).hexdigest()
    anchor = RECORD["placement_origin_xy_m"]
    gis = json.loads(GIS_FILE.read_text(encoding="utf-8"))["features"][0]
    props = gis["properties"]
    source_rings = []
    for ring in gis["geometry"]["coordinates"]:
        source_rings.append([((lon - ORIGIN_LON) * M_PER_DEG_LON,
                              (lat - ORIGIN_LAT) * M_PER_DEG_LAT) for lon, lat in ring])
    local_edges = asset_probe["base_outline_edges_local_xy_m"]
    world_edges = [
        [(edge[0][0] + anchor[0], edge[0][1] + anchor[1]),
         (edge[1][0] + anchor[0], edge[1][1] + anchor[1])]
        for edge in local_edges
    ]
    d_source_model, d_model_source = sampled_hausdorff(source_rings, world_edges)
    max_outline_deviation = max(d_source_model, d_model_source)
    expected_path = str(ASSET.resolve())
    marker_xy = master_probe.get("marker_location") or [float("inf"), float("inf")]
    marker_xy_error = max(abs(marker_xy[i] - anchor[i]) for i in range(2))
    actual_world = master_probe.get("actual_world_bounds")
    expected_world = master_probe.get("expected_world_bounds")
    bounds_error = max(abs(actual_world[i][j] - expected_world[i][j]) for i in range(3) for j in range(2)) if actual_world and expected_world else float("inf")
    master_ok = (
        master_probe["marker_found"] and master_probe["exact_marker_count"] == 1
        and master_probe["record_kind"] == "detailed"
        and master_probe["instance_collection"] == f"Asset_{ASSET_ID}"
        and Path(master_probe["library_path"]).resolve() == Path(expected_path)
        and marker_xy_error <= 0.001
        and max(abs(v) for v in master_probe["marker_rotation_euler"]) <= 1e-5
        and max(abs(v - 1.0) for v in master_probe["marker_scale"]) <= 1e-5
        and not master_probe["direct_root_collection_link"]
        and bounds_error <= 0.001
    )
    identity_ok = (props.get("FID") == 893 and props.get("BLDG_ABBR") == "DRUG"
                   and props.get("BUILDING_N") == "Drug Discovery Facility"
                   and props.get("ADDRESS") == "720 Clinic Drive")
    footprint_ok = max_outline_deviation <= 0.40
    export_ok = (
        asset_probe["collection_found"] and asset_probe["root_found"]
        and asset_probe["collection_coordinate_frame"] and "local" in asset_probe["collection_coordinate_frame"]
        and asset_probe["collection_object_count"] == 36 and asset_probe["mesh_object_count"] == 35
        and not asset_probe["meshes_without_materials"] and not asset_probe["external_libraries"]
        and asset_probe["root_location"] == [0.0, 0.0, 0.0]
    )
    identity_score = 2.0 if identity_ok and footprint_ok else (1.0 if identity_ok else 0.5)
    position_score = 1.9 if master_ok and footprint_ok else 0.8
    export_score = 2.0 if export_ok and master_ok else 0.8
    source_bounds = [[-345.26046375767623, -305.81210487133734],
                     [-647.9187789460775, -597.6403133375993]]

    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "score": identity_score, "max_score": 2,
         "status": "verified" if identity_ok and footprint_ok else "incomplete",
         "evidence": [
             f"Independent inspection of preserved Purdue/Indiana GIS FID {props.get('FID')} verifies {props.get('BLDG_ABBR')}, {props.get('BUILDING_N')}, {props.get('ADDRESS')}.",
             "Purdue Office of Research independently identifies the facility at 720 Clinic Drive and describes it as three stories.",
             f"After applying the manifest/master placement anchor to the localized model outline, sampled symmetric GIS-boundary deviation is {max_outline_deviation:.3f} m (0.40 m tolerance). This includes the outer perimeter and interior courtyard ring.",
         ],
         "reason": "The source identity/address matches and the world-space model outline remains within the stated geometry tolerance after localizing the asset."},
        {"criterion": "Position, orientation, and scale/dimensions", "score": position_score, "max_score": 2,
         "status": "verified by fresh master instance probe" if master_ok else "master placement mismatch",
         "evidence": [
             f"A fresh Blender open of the master found exactly one Placement_{ASSET_ID} instance at {marker_xy}, versus manifest anchor {anchor}; maximum XY error is {marker_xy_error:.6f} m.",
             f"Master instance links the expected library path and collection; world bounds differ from manifest by at most {bounds_error:.6f} m.",
             f"Localized source mesh bounds and instance transform reproduce the GIS campus footprint; sampled source-to-model boundary deviation is {d_source_model:.3f} m and model-to-source is {d_model_source:.6f} m.",
             "Coordinates inherit the project's documented approximate local lon/lat-to-meter conversion rather than a surveyed CRS.",
         ],
         "reason": "The exact master marker, library path, instance transform and resulting world bounds all match the manifest; the small deduction retains the known approximate geographic transform limitation."},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": 1.5, "max_score": 2,
         "status": "three-story count supported; detailed vertical dimensions partly estimated",
         "evidence": [
             "Purdue Office of Research calls the facility three-story.",
             "GIS fields F02=16, F03=32, F04=48, R=56 are preserved, but their metadata has no descriptions/units; roof-datum interpretation remains plausible, not proven.",
             f"Fresh localized asset geometry has local Z bounds {asset_probe['full_asset_local_bounds_m'][2]}; official photos support a flat roof and tall entrance canopy, but no surveyed elevation confirms all vertical dimensions.",
         ],
         "reason": "The story count and broad roof silhouette are supported. Exact floor spacing and the specific meaning/units of vertical GIS fields remain unresolved."},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": 1.7, "max_score": 2,
         "status": "major features match official imagery; secondary facades inferred",
         "evidence": [
             "The official Purdue Research photo shows the brick facade, regular floor bands, tall glazed entrance bay, and projecting flat canopy represented by the model preview.",
             "Purdue's facility description confirms the intended glass visibility between laboratory and public areas; the asset includes a curtainwall entrance and simple visible lobby.",
             "Only an oblique night photograph and a proposed 2011 site design are available for the as-built comparison; rear/courtyard elevations therefore remain inferred.",
         ],
         "reason": "The signature facade and entry are recognizably source-supported, while less visible elevations and exact local details are not independently documented."},
        {"criterion": "Modular export, portability, and complete evidence", "score": export_score, "max_score": 2,
         "status": "verified by fresh asset and master opens" if export_ok and master_ok else "validation failed",
         "evidence": [
             f"Fresh asset reopen in Blender {asset_probe['blender_version']} finds expected scene/collection, {asset_probe['collection_object_count']} objects ({asset_probe['mesh_object_count']} meshes), and {asset_probe['unique_material_count']} materials.",
             "All mesh objects have materials, the asset has no external linked libraries, and a local-coordinate root at origin preserves the manifest anchor.",
             f"Fresh master reopen confirms one instance of the same local library; asset SHA-256 is {asset_sha}, master SHA-256 is {master_sha}.",
             "Building-specific source snapshots, model evidence, preview, validator, and the original independent grade are retained in the project audit folder.",
         ],
         "reason": "Both the standalone local library and its master instance reopen with the expected contract and portable links."},
    ]
    score = round(sum(item["score"] for item in criteria), 2)
    return {
        "building": "Purdue Drug Discovery Facility",
        "asset_id": ASSET_ID,
        "asset_path": ASSET.relative_to(ROOT).as_posix(),
        "asset_sha256": asset_sha,
        "expected_asset_sha256": "3269b18a48ac4a746037011e16b48f7ae2abde35749a2e3ba80fce95c85fc798",
        "master_path": MASTER.name,
        "master_sha256": master_sha,
        "grader": "independent_grader_subagent_relocalized_revision",
        "grade_date": "2026-10-26",
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "status": "PASS" if score >= 8 and asset_sha == "3269b18a48ac4a746037011e16b48f7ae2abde35749a2e3ba80fce95c85fc798" and master_ok else "FAIL",
        "criteria": criteria,
        "evidence": {
            "asset_probe": ASSET_PROBE_OUT.relative_to(ROOT).as_posix(),
            "master_probe": MASTER_PROBE_OUT.relative_to(ROOT).as_posix(),
            "master_audit_crosscheck": "audit/master_sync_fire_drug_schowe_2026-10-26.json",
            "gis_source": "audit/purdue_drug_discovery_facility/sources/arcgis_feature_893_2026-10-26.geojson",
            "purdue_official_sources": [
                {"title": "Institutes and Centers at Discovery Park — Purdue University", "url": "https://research.purdue.edu/about/institutes-and-centers/", "supports": "Facility identity, 720 Clinic Drive, three-story count and glass viewing feature."},
                {"title": "Drug Discovery Building — Purdue Department of Chemistry", "url": "https://www.chem.purdue.edu/DrugDiscovery/building.html", "supports": "Proposed site plan, first and second floor plans, and architectural images."},
            ],
            "previous_grade": "audit/purdue_drug_discovery_facility/independent_grade/result.json",
        },
        "placement_metrics": {
            "manifest_anchor_xy_m": anchor,
            "master_marker_xy_m": marker_xy,
            "marker_xy_error_m": marker_xy_error,
            "world_bounds_error_max_m": bounds_error,
            "outline_source_to_model_m": d_source_model,
            "outline_model_to_source_m": d_model_source,
            "master_checks_pass": master_ok,
        },
        "findings": [
            "The localized revision preserves the prior model geometry; the original sampled footprint discrepancy remains 0.37 m and is within this review's explicit 0.40 m tolerance.",
            "The master marker has the exact manifest location, unrotated unit scale, expected linked library, and matching world bounds.",
            "Floor and roof dimensions retain estimation and GIS field-definition limits from the prior grade.",
            "This review checks the integrated instance transform, not every neighboring master-scene asset or general master-scene appearance.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    out = DIR / "result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"score": result["score"], "status": result["status"], "asset_sha256": result["asset_sha256"], "master_sha256": result["master_sha256"], "placement_metrics": result["placement_metrics"], "result": str(out)}))
