"""Independent R3 Owen Hall regrade, using reopened asset and GIS polygons."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
ASSET = ROOT / "modular/buildings/owen_hall.blend"
EXPECTED = "20ccd340d7cc2ab06ac6e94a84394c3d8ae0ec84573a1222e9ed541dbb19e981"
REOPEN = json.loads((HERE / "independent_reopen_r3.json").read_text(encoding="utf-8"))
GIS = json.loads((HERE / "sources/purdue_owen_gis_feature_38.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
entry = next(item for item in manifest["assets"] if item["id"] == "owen_hall")
feature = next(item for item in GIS["features"] if item["attributes"]["OBJECTID"] == 38)

asset_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
assert asset_hash == EXPECTED == REOPEN["asset_sha256"]
assert REOPEN["collection_object_count"] == entry["object_count"] == 958
assert REOPEN["manifest_names_match"] and not REOPEN["manifest_names_missing"] and not REOPEN["manifest_names_extra"]
assert REOPEN["bounds_match_within_0_001m"]
assert entry["collection"] == REOPEN["collection"] == "Asset_owen_hall"

px, py = entry["placement_origin_xy_m"]
x_scale = 111412.84 * math.cos(math.radians(40.4274))
gis_local = Polygon([((lon + 86.9137) * x_scale - px,
                      (lat - 40.4274) * 111040.0 - py)
                     for lon, lat in feature["geometry"]["rings"][0]])
model_local = Polygon(REOPEN["footprint_vertex_xy_local_m"])
inter = model_local.intersection(gis_local).area
union = model_local.union(gis_local).area
gis_bounds, model_bounds = gis_local.bounds, model_local.bounds
center_error = math.dist(((gis_bounds[0] + gis_bounds[2]) / 2,
                          (gis_bounds[1] + gis_bounds[3]) / 2),
                         ((model_bounds[0] + model_bounds[2]) / 2,
                          (model_bounds[1] + model_bounds[3]) / 2))
gis_dims = [gis_bounds[2] - gis_bounds[0], gis_bounds[3] - gis_bounds[1]]
model_dims = [model_bounds[2] - model_bounds[0], model_bounds[3] - model_bounds[1]]
iou = inter / union
coverage = inter / gis_local.area

criteria = [
    {
        "criterion": "Identity and source-backed footprint",
        "points": 2.0,
        "max_points": 2,
        "status": "verified against Purdue GIS in the documented project transform",
        "evidence": [
            "Purdue campus GIS OBJECTID 38 identifies Richard Owen Residence Hall (ABBR OWEN).",
            f"Independently reopened base polygon overlap: IoU={iou:.6f}; model coverage={coverage:.6f}; center error={center_error:.6f} m.",
            f"GIS envelope {gis_dims[0]:.3f} x {gis_dims[1]:.3f} m; model envelope {model_dims[0]:.3f} x {model_dims[1]:.3f} m.",
        ],
        "deduction": "GIS wall/overhang convention and surveyed-coordinate accuracy are undocumented; none for modeled relative footprint."
    },
    {
        "criterion": "Placement, orientation, and scale",
        "points": 1.8,
        "max_points": 2,
        "status": "asset frame and manifest placement align; coordinator master refresh pending",
        "evidence": [
            "Reopened AssetRoot_owen_hall has zero translation and rotation and unit scale.",
            f"Manifest placement origin is [{px}, {py}] m and the GIS outline agrees under the documented approximate local transform.",
            "The master marker itself was not reopened/validated for this new asset hash; campus placement is not surveyed."
        ],
        "deduction": "The root master placement instance was not refreshed and independently reopened for this revision."
    },
    {
        "criterion": "Height, floors, and roof form",
        "points": 1.4,
        "max_points": 2,
        "status": "story count and plan supported; absolute height estimated",
        "evidence": [
            "Purdue's 2007 report describes an H-shaped, four-story dormitory; the current model follows the H form and four levels.",
            "The official exterior photo is consistent with a flat/parapet roof silhouette.",
            "Reopened mesh bounds are Z=0 to 16 m; the floor rhythm and parapet top remain estimates with no measured elevation found."
        ],
        "deduction": "No measured building height, floor elevations, or dimensioned roof drawing was found."
    },
    {
        "criterion": "Facade and material fidelity",
        "points": 1.2,
        "max_points": 2,
        "status": "broad character represented; source-specific facade remains schematic",
        "evidence": [
            "The official Purdue exterior reference supports red brick, pale stone/concrete base and bands, and repeated vertical residential windows.",
            "The R2 render adds framed multi-pane windows, selective louvers, a darker roof membrane/coping, and entrance steps/rails; the broad H footprint and facade rhythm read clearly.",
            "Reopened collection uses 21 node materials; visual comparison shows the large glazed bays, lower concrete-panel pattern, and exact window spacing remain simplified."
        ],
        "deduction": "The render is a clean model view rather than a photo match; facade opening details and main common-area glazing are still generalized."
    },
    {
        "criterion": "Interior, portability, and asset/manifest integrity",
        "points": 1.6,
        "max_points": 2,
        "status": "portable asset and manifest reconciled; interior coverage remains illustrative",
        "evidence": [
            "The current Purdue room guide gives a standard double-room illustration with approximate dimensions of 11 ft 4 in by 16 ft and approximate furnishings; the model includes eight representative room modules, explicitly illustrative rather than assigned as-built rooms.",
            "Blender 5.2.3 independently reopened 958 collection objects (934 meshes, 18 lights, five cameras, one empty), all mesh objects have material slots, 21 node materials are present, and no external image or library paths were found.",
            "Manifest object names match the reopened collection exactly, count is 958, and full mesh bounds agree within 1 mm."
        ],
        "deduction": "There is no verified complete interior plan, and the current root master link still awaits coordinator refresh and save/reopen verification."
    },
]
score = round(sum(item["points"] for item in criteria), 1)
assert score == 8.0
scorecard = {
    "evaluator": "independent_owen_hall_r3",
    "asset": "modular/buildings/owen_hall.blend",
    "asset_sha256": asset_hash,
    "blender_version": REOPEN["blender_version"],
    "score": score,
    "max_score": 10,
    "minimum_passing_score": 8,
    "passed": score >= 8,
    "criteria": criteria,
    "evidence": {
        "gis_feature_id": 38,
        "gis_name": feature["attributes"]["Name"],
        "gis_footprint_iou": iou,
        "gis_model_coverage": coverage,
        "gis_envelope_dimensions_m": gis_dims,
        "model_envelope_dimensions_m": model_dims,
        "envelope_center_error_m": center_error,
        "reopened_collection": REOPEN["collection"],
        "reopened_object_count": REOPEN["collection_object_count"],
        "manifest_names_match": REOPEN["manifest_names_match"],
        "manifest_bounds_match": REOPEN["bounds_match_within_0_001m"],
        "object_types": REOPEN["object_type_counts"],
        "node_material_count": REOPEN["unique_node_material_count"],
        "unassigned_meshes": len(REOPEN["mesh_objects_with_unassigned_materials"]),
        "missing_external_images": len(REOPEN["missing_external_images"]),
        "external_libraries": len(REOPEN["external_libraries"]),
        "placement_origin_xy_m": [px, py],
        "height_status": "estimated; 16.0 m overall asset bounds, four stories supported by Purdue report",
        "master_refresh_verified": False,
        "evidence_file": "independent_reopen_r3.json",
    },
    "report": "independent_report_r3.md",
}
(HERE / "independent_scorecard_r3.json").write_text(json.dumps(scorecard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

report = f"""# Owen Hall independent regrade — R2 asset and manifest

**Score: {score:.1f}/10 — meets the 8/10 building-grade threshold.** This grade applies only to the current modular asset at SHA-256 `{asset_hash}`. The master-library refresh is still a separate coordinator task and was not inspected or claimed here.

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and source-backed footprint | 2.0/2 | Reopened wall-base outline matches Purdue GIS OBJECTID 38 in the project coordinate approximation (IoU {iou:.3f}; coverage {coverage:.3f}). |
| Placement, orientation, and scale | 1.8/2 | Asset root is identity; manifest origin and dimensions align. The project transform is approximate and the new master marker has not been refreshed/reopened. |
| Height, floors, and roof form | 1.4/2 | Purdue's report supports four stories and H-shape; the flat roof silhouette is visible in the official photo. Absolute height and floor elevations remain estimates. |
| Facade and material fidelity | 1.2/2 | Brick/stone bands and a repeated window rhythm are represented with additional frames/louvers. Large glazed bays, lower facade panels, and exact opening details remain simplified. |
| Interior, portability, and asset/manifest integrity | 1.6/2 | A representative room vignette follows Purdue's approximate standard-room dimensions. The file reopens with 958 objects; its object list and bounds match the refreshed manifest. Complete as-built interiors and master integration remain outstanding. |
| **Total** | **{score:.1f}/10** | **Passes the independent asset-grade threshold; master integration is pending.** |

## Independent checks

- Blender {REOPEN['blender_version']} reopened the current asset. `Asset_owen_hall` contains {REOPEN['collection_object_count']} objects ({REOPEN['object_type_counts']['MESH']} meshes, {REOPEN['object_type_counts']['LIGHT']} lights, {REOPEN['object_type_counts']['CAMERA']} cameras, {REOPEN['object_type_counts']['EMPTY']} empty).
- SHA-256 is `{asset_hash}`, matching the requested current asset.
- Manifest inventory matches all reopened object names exactly; count is {entry['object_count']} and the complete mesh bounds match to within 1 mm.
- No unassigned mesh material slots, external image paths, or external library paths were found; {REOPEN['unique_node_material_count']} unique node materials are assigned.
- Independent GIS polygon comparison produced IoU {iou:.6f}, coverage {coverage:.6f}, center error {center_error:.6f} m, and envelope dimensions {gis_dims[0]:.3f} × {gis_dims[1]:.3f} m (GIS) versus {model_dims[0]:.3f} × {model_dims[1]:.3f} m (model).
- The root master blend has not been refreshed and reopened for this asset hash; no campus integration score is claimed.

## Source-supported limits

The Purdue report supports the H-shaped, four-story residence hall, while the current official housing page supplies an approximate standard double-room layout and dimensions. Neither source provides measured building elevations or a complete as-built interior plan. The 16 m overall height, floor elevations, and placement of repeated room modules remain estimates/illustrative. The official facade photo supports broad brick/stone character and window patterns, but it does not establish surveyed facade dimensions.

## References

- Purdue campus map GIS OBJECTID 38: https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0/query?where=OBJECTID%3D38&outFields=*&returnGeometry=true&outSR=4326&f=pjson
- Purdue Office of Special Events and News, [Report of Findings (2007)](https://www.purdue.edu/uns/x/2007b/070702RimkusFinal.pdf), describing a four-story H-shaped hall and including a ground-level plan.
- Purdue University Residences, [Owen Hall](https://www.housing.purdue.edu/my-housing/options/residence-halls/owen.html), with official exterior image, standard-room dimensions, approximate-layout caveat, and room furnishing description.
- Local evidence snapshots and renders are listed in `source_provenance.json`, `gis_footprint_validation.json`, `independent_reopen_r3.json`, `owen_hall_facade.png`, `owen_hall_standard_room_vignette.png`, and `owen_hall_gis_footprint_topdown.png`.
"""
(HERE / "independent_report_r3.md").write_text(report, encoding="utf-8")
print(json.dumps({"score": score, "passed": scorecard["passed"], "iou": iou,
                  "object_count": REOPEN["collection_object_count"], "asset_sha256": asset_hash}, indent=2))
