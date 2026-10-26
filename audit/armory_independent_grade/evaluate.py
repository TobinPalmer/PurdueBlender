from pathlib import Path
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def evaluate():
    manifest = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
    asset = next(a for a in manifest["assets"] if a["id"] == "armory")
    record = json.loads((HERE / "purdue_gis_feature_207.json").read_text(encoding="utf-8"))
    feature = record["query_response"]["features"][0]
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0][:-1]
    points = []
    for x3857, y3857 in ring:
        lon = math.degrees(x3857 / 6378137.0)
        lat = math.degrees(2 * math.atan(math.exp(y3857 / 6378137.0)) - math.pi / 2)
        points.append(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                       (lat - 40.4274) * 111040.0))
    gis_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in (0, 1)]
    gis_center = [sum(p[i] for p in points) / len(points) for i in (0, 1)]
    model_bounds = asset["exterior_bounds_world_m"][:2]
    model_dims = [b[1] - b[0] for b in model_bounds]
    gis_dims = [b[1] - b[0] for b in gis_bounds]
    center_delta = [((b[0] + b[1]) / 2) - gis_center[i] for i, b in enumerate(model_bounds)]
    center_error = math.hypot(*center_delta)
    dim_error_pct = [abs(model_dims[i] - gis_dims[i]) / gis_dims[i] * 100 for i in (0, 1)]

    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "score": 1.1, "max_score": 2,
         "evidence": [f"Purdue GIS OBJECTID {attrs['OBJECTID']} identifies ABBR={attrs['ABBR']}, {attrs['Name']}, {attrs['ADDRESS']}.",
                      "The brick armory identity and historic masonry character are supported by Purdue's archived exterior photograph.",
                      f"GIS envelope is {gis_dims[0]:.2f} x {gis_dims[1]:.2f} m; model exterior is {model_dims[0]:.2f} x {model_dims[1]:.2f} m. Axis size errors are {dim_error_pct[0]:.1f}% and {dim_error_pct[1]:.1f}%. The saved report calls the geometry an approximate AI reconstruction."]},
        {"criterion": "Position, orientation, and scale/dimensions", "score": 1.2, "max_score": 2,
         "evidence": [f"GIS and model exterior-envelope centers differ by {center_error:.2f} m (dx={center_delta[0]:.2f}, dy={center_delta[1]:.2f}).",
                      f"The plan axes are broadly cardinal, but model dimensions {model_dims[0]:.2f} x {model_dims[1]:.2f} m differ from GIS {gis_dims[0]:.2f} x {gis_dims[1]:.2f} m.",
                      "GIS EPSG:3857 coordinates were converted using modular/AGENTS.md's documented local-meter approximation; this is not a survey."]},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": 0.4, "max_score": 2,
         "evidence": [f"The manifest envelope reaches Z={asset['bounds_world_m'][2][1]:.1f} m, but the saved evidence has no authoritative height or story count.",
                      "The archive photo supports a central gable; the current render shows a broad hipped/clerestory roof and four raised corner blocks unsupported by the reference.",
                      "The building evidence states that roof profile and architectural details differ from the historical reference; roof finish is unverified."]},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": 1.0, "max_score": 2,
         "evidence": ["Both archive photo and model show brick fields, pale trim, repeated multi-pane windows, and a central entrance.",
                      "The model simplifies the historic central gable/arched entrance and window rhythm; colors and textures are artistic approximations, not measured.",
                      "No current dated facade or measured elevation is saved in the evidence folder."]},
        {"criterion": "Modular export, portability, and complete evidence", "score": 1.4, "max_score": 2,
         "evidence": [f"Manifest retains id={asset['id']}, file={asset['file']}, collection={asset['collection']}, and local placement contract; it records {asset['object_count']} objects.",
                      "Building-specific verification.json records a reopened asset, collection count, packed images, and roof/window geometry-repair checks. A preview and historic reference image are present.",
                      "There is no dedicated modular/buildings/build_armory.py module or comprehensive current-source record; this evaluation did not have an independent Blender reopen probe."]},
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        {"severity": "major", "finding": f"Purdue GIS plan envelope differs from the model: {dim_error_pct[0]:.1f}% on X and {dim_error_pct[1]:.1f}% on Y; exterior-center offset {center_error:.2f} m."},
        {"severity": "major", "finding": "The roof silhouette and corner blocks conflict with the archival Purdue exterior photo; height and story count are unsupported."},
        {"severity": "moderate", "finding": "Brick, repeated windows, and central entry are directionally supported, but the facade pattern is not a close match."},
        {"severity": "moderate", "finding": "The library has useful portability checks and renders, but lacks the dedicated builder module and a complete current-source record."},
        {"severity": "positive", "finding": "Purdue GIS and archives corroborate identity; stable asset ID and collection names match the manifest."},
    ]
    return {
        "score": score, "max_score": 10, "pass_threshold": 8, "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "asset_path": asset["file"], "export_collection": asset["collection"],
            "retrieved_date": record["retrieved_date"],
            "gis_provider": "Purdue University, PuGeoDB.DBO.CampusBuilding ArcGIS MapServer layer 0",
            "gis_source_url": record["source_url"], "gis_crs": "EPSG:3857; converted using repository local-meter approximation",
            "gis_feature": {k: attrs.get(k) for k in ("OBJECTID", "ABBR", "Name", "OWNER", "ADDRESS", "Shape.STArea()", "Shape.STLength()")},
            "gis_bounds_local_m": gis_bounds, "gis_vertex_mean_center_local_m": gis_center,
            "model_structural_exterior_bounds_world_m": model_bounds,
            "model_structural_exterior_dimensions_m": model_dims,
            "center_delta_xy_m": center_delta, "center_offset_m": center_error,
            "dimension_error_percent_xy": dim_error_pct,
            "model_bounds_world_m": asset["bounds_world_m"], "manifest_object_count": asset["object_count"],
            "supporting_files": ["materials/buildings/armory/report.md", "materials/buildings/armory/verification.json",
                                 "materials/buildings/armory/reference.jpg", "materials/buildings/armory/hero.png",
                                 "renders/armory/armory_render.png", "audit/armory_independent_grade/purdue_gis_feature_207.json"],
            "external_authoritative_sources": [
                {"title": "Purdue Campus Facilities and Buildings Historic Database — Armory", "url": "https://collections.lib.purdue.edu/campus/buildings"},
                {"title": "Purdue e-Archives — Armory photograph", "url": "https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/140/"},
                {"title": "Purdue Campus ArcGIS REST layer", "url": "https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0"},
            ],
        },
        "findings": findings,
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
