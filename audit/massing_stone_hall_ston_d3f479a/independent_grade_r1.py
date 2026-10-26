import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
SOURCE = AUDIT / "sources"


def evaluate_stone_hall():
    gis = json.loads((SOURCE / "purdue_building_gis_fid240_ston_4326.json").read_text(encoding="utf-8"))
    record = json.loads((SOURCE / "source_registry.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8"))
    build = json.loads((AUDIT / "build_validation.json").read_text(encoding="utf-8"))
    attrs = gis["features"][0]["attributes"]
    ring = gis["features"][0]["geometry"]["rings"][0]
    gis_source = next(s for s in record["sources"] if s.get("feature_id") == 240)
    hist = next(s for s in record["sources"] if s.get("feature_ids") == [1371, 1372, 1373, 1374])

    identity_ok = (attrs["FID"] == 240 and attrs["BLDG_ABBR"] == "STON"
                   and attrs["BUILDING_N"] == "Winthrop E. Stone Hall"
                   and validation["source_fid_property"] == 240)
    footprint_ok = validation.get("footprint_matches_source_ring") is True
    package_ok = (validation.get("status") == "pass"
                  and validation.get("external_image_dependencies") == []
                  and validation.get("collection_present") is True
                  and validation.get("collection_object_count") == 1)

    criteria = [
        {"name": "Identity and source-backed footprint", "score": 2.0, "max_score": 2,
         "status": "verified with source-data caveat" if identity_ok and footprint_ok else "uncertain",
         "evidence": [f"Official Purdue GIS FID {attrs['FID']} has BLDG_ABBR={attrs['BLDG_ABBR']}, name={attrs['BUILDING_N']}, address={attrs['ADDRESS']}.",
                      f"GIS ring has {len(ring)-1} unique vertices; saved reopen validation reports exact ring match={footprint_ok}.",
                      "GIS Shape__Area/Shape__Length conflict materially with ring-derived area/perimeter, so the ring is the usable geometry and summary metrics remain suspect."]},
        {"name": "Position, orientation, and scale", "score": 2.0 if footprint_ok else 0.5, "max_score": 2,
         "status": "supported by transformed GIS ring and saved asset geometry check" if footprint_ok else "unverified",
         "evidence": ["Saved reopen validation reports source-ring match and world bounds; GIS ring is in WGS84 and the recorded comparison uses the documented approximate campus transform, not a surveyed CRS.", "No independent survey control or separate quantitative registration residual is available."]},
        {"name": "Height, floors, and roof", "score": 0.75, "max_score": 2,
         "status": "partially supported; height uncertain and level cue conflicts",
         "evidence": [f"GIS NUM_LEVELS={attrs.get('NUM_LEVELS')}; model height {validation.get('height_m')} m derives from Extrution={attrs.get('Extrution')} interpreted as feet although units are undeclared.", "Rendered elevations show about four visible facade bands including a narrow top band, fewer than GIS NUM_LEVELS=6; floor count cannot be verified from supplied photos or model.", "Archive photos support a low flat/parapet roof silhouette, which the model approximates."]},
        {"name": "Facade, entrances, and distinctive architecture", "score": 1.0, "max_score": 2,
         "status": "partially supported stylization",
         "evidence": [f"Historic archival photographs {hist['feature_ids']} support brick, pale stone/concrete pilasters and horizontal bands, repeated rectangular windows, and a formal central entry.", "Model uses brick-colored walling, light trim/bands, repeated windows, and a central door, but facade bays/windows are squat and regularized; the historical tall framed windows, strongly expressed monumental entry with broad steps, and characteristic proportions are absent or simplified.", "Source photographs are historical qualitative evidence, not measured elevations or confirmation of current facade."]},
        {"name": "Modular export, portability, and evidence completeness", "score": 2.0 if package_ok else 0.5, "max_score": 2,
         "status": "verified from saved reopen report and evidence bundle" if package_ok else "incomplete",
         "evidence": ["Reopen validation reports expected scene/collection, one named mesh, no external image dependencies, and status pass.", "Audit bundle contains raw GIS feature and layer metadata, source registry with provider/URLs/date/CRS/uncertainties, archive record/photos, three rendered views, build validation, and reopen validation."]},
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
        "building_id": "massing_stone_hall_ston_d3f479a",
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": [str(AUDIT / "sources" / "purdue_building_gis_fid240_ston_4326.json"),
                     str(AUDIT / "sources" / "purdue_building_gis_layer_metadata.json"),
                     str(AUDIT / "sources" / "purdue_historic_building_record_71.html"),
                     str(AUDIT / "sources" / "stone_hall_archive_1371.jpg"),
                     str(AUDIT / "sources" / "stone_hall_1959_archive_1372.jpg"),
                     str(AUDIT / "sources" / "stone_hall_archive_1373.jpg"),
                     str(AUDIT / "sources" / "stone_hall_archive_1374.jpg"),
                     str(AUDIT / "preview" / "stone_hall_isometric.png"),
                     str(AUDIT / "preview" / "stone_hall_front.png"),
                     str(AUDIT / "preview" / "stone_hall_top.png"),
                     str(AUDIT / "build_validation.json"), str(AUDIT / "reopen_validation.json")],
        "findings": ["The source-linked GIS outline and identity are unusually well documented, but the GIS area/perimeter summary fields conflict with the actual geometry ring.",
                     "Location/plan receives full credit based on exact ring-match evidence; positional accuracy still inherits the approximate, non-survey transform.",
                     "The principal visual shortfall is facade fidelity, especially the much more monumental entry and tall window/pilaster proportions seen in the archival photos.",
                     "The number of modeled facade bands does not substantiate the GIS six-level attribute; roof and height are only partly supported."],
        "limitations": ["Visual assessment was made from saved front/isometric/top renders and archived photos; no interactive Blender session or measured elevation source was used.", "The asset's exact source-ring geometry match is taken from its saved reopen-validation record, while source identity/attributes and archival visuals were independently inspected here."],
    }


if __name__ == "__main__":
    result = evaluate_stone_hall()
    (AUDIT / "independent_grade_r1.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"score": result["score"], "max_score": result["max_score"], "criteria": [{"name": c["name"], "score": c["score"], "max_score": c["max_score"]} for c in result["criteria"]], "output": str(AUDIT / "independent_grade_r1.json")}, indent=2))
