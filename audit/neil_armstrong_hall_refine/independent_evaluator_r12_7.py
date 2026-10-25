from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
PROBE = ROOT / "audit/neil_armstrong_hall_refine/independent_probe_r12_7.json"
EXPECTED_SHA = "a85ef78d82e5c50b09fcd4fb7bc191798fad0132a9a89b84297203186f2ae549"


def evaluate() -> dict:
    actual_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if actual_sha != EXPECTED_SHA:
        raise RuntimeError(f"Asset changed after review: {actual_sha}")
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    if probe.get("sha256") != actual_sha or not probe.get("fresh_blender_open"):
        raise RuntimeError("Independent Blender probe does not match the current asset")
    if probe.get("collection_object_count") != 445 or probe.get("mesh_object_count") != 415:
        raise RuntimeError("Fresh reopen inventory differs from the reviewed inventory")
    if probe.get("meshes_without_material") or probe.get("meshes_with_null_slots") or probe.get("missing_external_images"):
        raise RuntimeError("Material or dependency validation changed")

    criteria = [
      {"criterion":"Correct identity and source-backed footprint","score":1.55,"max_score":2.0,
       "evidence":["Purdue GIS BuildingShapesZip4 feature 642 and attributed campus photos identify Neil Armstrong Hall; see evidence_r11.json and source_review_r12.md.","The 2023 Indiana orthophoto trace supports the roof/eaves outline and folded roof plan.","The GIS feature is generalized and the aerial trace follows eaves, not verified structural wall or courtyard edges."],
       "limitations":["No measured wall plan or verified structural wall footprint is available."]},
      {"criterion":"Position, orientation, and scale/dimensions","score":1.55,"max_score":2.0,
       "evidence":["Independent fresh Blender probe confirms AssetRoot_neil_armstrong_hall has identity transform at local (0,0,0).","Manifest placement is [-109.0, 400.1893310546875] m; the R12.4 independent review inspected the master marker and reported it matches the manifest origin.","Registered orthophoto verifies roof/eaves plan only; geotag photo headings/roll and facade registration are unavailable."],
       "limitations":["Architectural wall position, facade stationing, and measured dimensions are not independently established."]},
      {"criterion":"Evidence-backed height, floors, and roof form","score":1.35,"max_score":2.0,
       "evidence":["Purdue source review and emergency-plan information support the building identity, four levels, atrium, and a wing-like cantilever.","The 2023 aerial supports roof/eaves plan; 2016 photos show the distinctive folded canopy.","The current 21.5 m localized canopy peak is inferred and bounded only by coarse LiDAR; current R12.7 renders still show substantial canopy thickness/proportion differences and a very dark underside compared with the cited photos."],
       "limitations":["Canopy height, warp, and structural profile are not measured; visual camera poses lack heading/roll calibration."]},
      {"criterion":"Facade, entrances, and distinctive architecture","score":1.4,"max_score":2.0,
       "evidence":["R12.7 adds an upper-level glazing/mullion band based on Wikimedia Commons 2016 photo 02, restores a low entrance deck, and removes 12 lower-story ribbon-window planes unsupported by attributed photos.","Fresh independent R12.7 render shows the prior blue obstruction is gone from the courtyard-comparison view.","The current facade views still show broad, simplified brick faces, a generic horizontal upper glazing strip, and sparse openings relative to the large curtain-wall zones visible in the 2016 source images; the canopy-to-entrance relation remains visibly approximate."],
       "limitations":["No dimensioned elevation or facade stationing locates the openings; the deck and added mullion cadence remain photo-derived approximations."]},
      {"criterion":"Modular export, portability, and complete evidence","score":1.8,"max_score":2.0,
       "evidence":["Independent Blender 5.2.3 reopen confirms the expected scene/collection, 445 objects, 415 mesh objects, and root identity.","All mesh objects have material assignments; no null slots or missing external images were found.","Current SHA-256 is recorded with source, validation, evaluator, and fresh current-revision renders in this audit folder."],
       "limitations":["Evidence remains visual/generalized rather than a dimensioned as-built drawing set."]}
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
      "building":"Neil Armstrong Hall of Engineering",
      "building_id":"neil_armstrong_hall",
      "revision_reviewed":"R12.7",
      "review_type":"independent_read_only_grade",
      "asset":"modular/buildings/neil_armstrong_hall.blend",
      "asset_sha256":actual_sha,
      "fresh_reopen_validation":True,
      "score":score,"max_score":10.0,"pass_threshold":8.0,"passed":score>=8.0,
      "criteria":criteria,
      "evidence":{
        "independent_probe":"audit/neil_armstrong_hall_refine/independent_probe_r12_7.json",
        "current_revision_renders":"audit/neil_armstrong_hall_refine/renders_independent_r12_7/",
        "current_render_driver":"audit/neil_armstrong_hall_refine/render_independent_r12_7.py",
        "builder_validation":"audit/neil_armstrong_hall_refine/validation_r12_7.json",
        "source_review":"audit/neil_armstrong_hall_refine/source_review_r12.md",
        "source_photos":["audit/neil_armstrong_hall_refine/sources_r12/arms_2016_01.jpg","audit/neil_armstrong_hall_refine/sources_r12/arms_2016_02.jpg","audit/complete_neil_armstrong/sources/wikimedia_neil_2016_03_r8.jpg"],
        "roof_aerial":"audit/complete_neil_armstrong/sources/indiana_current_ortho_neil_extent.png",
        "camera_pose_caveat":"2016 photo geotags provide starting positions; heading and roll are unknown, so perspective comparison is qualitative."
      },
      "findings":[
        "The courtyard camera obstruction was a review-camera problem; the modeled display case was correctly retained and the new clear render is useful.",
        "The low entrance deck and added upper glazing band address identified gaps, but their geometry is not dimensionally registered.",
        "The roof/eaves trace cannot establish wall footprint. Current renders continue to show a broad, thick, dark canopy and simplified facade compared with the distinctive folded wing and larger curtain-wall zones in source photos.",
        "Score: 7.65/10, rounded for reporting to 7.7/10; below the 8.0 passing threshold."
      ]
    }

if __name__ == "__main__":
    result=evaluate()
    output=ROOT / "audit/neil_armstrong_hall_refine/independent_grade_r12_7.json"
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
