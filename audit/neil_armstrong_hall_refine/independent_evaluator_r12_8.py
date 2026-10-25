"""Independent R12.8 evaluator for Neil Armstrong Hall.
Run with: python audit/neil_armstrong_hall_refine/independent_evaluator_r12_8.py
"""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
PROBE = ROOT / "audit/neil_armstrong_hall_refine/independent_probe_r12_8.json"
VALIDATION = ROOT / "audit/neil_armstrong_hall_refine/validation_r12_8.json"
EXPECTED_SHA = "59fd4e7ac4b4887cad2951e06ded82cf09e713592d320ca4fab4e0445e97649e"

def evaluate():
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    actual = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    assert actual == EXPECTED_SHA == probe["sha256"] == validation["sha256"]
    assert probe["fresh_blender_open"] and probe["collection_object_count"] == 445
    assert probe["root_location"] == [0.0, 0.0, 0.0]
    assert not probe["meshes_without_material"] and not probe["missing_external_images"]
    criteria = [
      {"criterion":"Correct identity and source-backed footprint","score":1.55,"max_score":2.0,
       "evidence":["Purdue OEP BEP names Neil Armstrong Hall of Engineering (ARMS).","The registered 2023 Indiana orthophoto supports the roof/eaves plan, not wall edges.","Prior structural GIS outline FID 642 has only partial overlap with the modeled roof slabs; no measured wall/courtyard plan was located."],
       "limitations":["No authoritative measured wall footprint or courtyard plan; the eaves trace is not a structural-wall trace."]},
      {"criterion":"Position, orientation, and scale/dimensions","score":1.55,"max_score":2.0,
       "evidence":["Fresh independent reopen confirms the local AssetRoot remains identity at [0,0,0].","Manifest placement is [-109.0, 400.1893310546875] m; prior independent master review checked the marker at that origin with zero rotation and unit scale.","R12.8 does not change the building local frame or the previously reported marker."],
       "limitations":["This grade did not reopen the whole campus master to recheck the marker; facade stationing and measured dimensions remain unverified."]},
      {"criterion":"Evidence-backed height, floors, and roof form","score":1.45,"max_score":2.0,
       "evidence":["Purdue OEP describes four levels (lower, grade, two upper); FRP corroborates a three-story frame with basement and mechanical penthouse.","2016 project photos show the distinctive wing-like cantilever roof; 2023 ortho supports only its plan/eaves outline.","R12.8 reduces inferred shell thickness to 0.18 m and assigns a muted red-brown soffit, improving the photo match; the canopy remains a broad, simplified inferred ring/profile."],
       "limitations":["The 21.5 m peak, shell warp/thickness, roof elevations, and structural roof profile are not measured; LiDAR is a coarse upper bound only."]},
      {"criterion":"Facade, entrances, and distinctive architecture","score":1.45,"max_score":2.0,
       "evidence":["Kawneer project photos and system list support large 1600UT curtain wall and Versoleil outrigger sunshades; FRP corroborates the atrium bridges and cantilever truss.","Fresh R12.8 views retain brick/glass volumes, a curved glazed entrance, and a red-brown canopy underside; six duplicate entrance-deck faces and fifteen roof-seam duplicates are removed.","Direct render/source comparison still shows broad plain brick faces, thin generic ribbon openings, and a canopy-to-curtain-wall relationship unlike the larger glazed zones and folded triangular wing in the project photos."],
       "limitations":["No dimensioned elevation or facade schedule locates window bays, mullions, sunshades, or entrance details; views are not heading/roll-calibrated."]},
      {"criterion":"Modular export, portability, and complete evidence","score":1.8,"max_score":2.0,
       "evidence":["Independent Blender 5.2.3 fresh reopen confirms Asset_neil_armstrong_hall has 445 objects/415 meshes and identity root.","Every mesh has a material; there are no null slots or missing external images.","R12.8 includes source review, validation, fresh renders, this independent probe and evaluator."],
       "limitations":["Evidence is visual/generalized rather than a dimensioned as-built drawing set."]}
    ]
    return {"building":"Neil Armstrong Hall","revision":"R12.8","asset_sha256":actual,
            "score":round(sum(c["score"] for c in criteria),2),"max_score":10,
            "pass_threshold":8.0,"passed":sum(c["score"] for c in criteria)>=8.0,
            "criteria":criteria,
            "evidence":{"asset":"modular/buildings/neil_armstrong_hall.blend",
             "independent_probe":"audit/neil_armstrong_hall_refine/independent_probe_r12_8.json",
             "builder_validation":"audit/neil_armstrong_hall_refine/validation_r12_8.json",
             "source_review":"audit/neil_armstrong_hall_refine/source_review_r12_8.md",
             "renders":"audit/neil_armstrong_hall_refine/renders_independent_r12_8/",
             "source_images":["audit/neil_armstrong_hall_refine/sources_r12/arms_2016_01.jpg",
                              "audit/neil_armstrong_hall_refine/sources_r12/arms_2016_02.jpg",
                              "audit/neil_armstrong_hall_refine/sources/wikimedia_neil_2016_03_r8.jpg"],
             "online_sources":["https://www.purdue.edu/operations/emergency-preparedness/arms/",
                               "https://www.kawneer.ca/projects/education/neil-armstrong-hall-of-engineering-purdue-university/",
                               "https://frpinc.com/projects/neil-armstrong-hall-of-engineering/",
                               "https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg",
                               "https://designandbuildwithmetal.com/featured-projects/neil-armstrong-hall-of-engineering"]},
            "findings":["R12.8 improves duplicate-face cleanup, canopy thinness, and soffit color, but does not resolve the two main fidelity gaps: structural wall plan and facade/canopy proportions.",
                        "Compared with the sourced 2016 photos, the model still under-represents the large curtain-wall zones and sunshade/outrigger cadence and over-simplifies the folded canopy wing.",
                        "The official footprint is not a verified wall outline and does not establish building height or roof geometry."],
            "limitations":["No public dimensioned as-built plan/elevation was found; roof/eaves and height evidence cannot validate structural walls or exact canopy profile."]}

if __name__ == "__main__":
    result=evaluate()
    out=Path(__file__).with_name("independent_grade_r12_8.json")
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"score":result["score"],"passed":result["passed"],"asset_sha256":result["asset_sha256"]},indent=2))
