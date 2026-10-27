"""Independent, evidence-first rubric for the Veterinary Pathology Building."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GRADE_DIR = Path(__file__).resolve().parent


def evaluate():
    probe = json.loads((GRADE_DIR / "fresh_open_probe.json").read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / "audit/veterinary_pathology_building/evidence.json").read_text(encoding="utf-8"))

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "Purdue Libraries GIS feature OBJECTID 165 identifies VPTH / Veterinary Pathology Building at 725 Harrison Street.",
                "An independent Blender reopen compared every converted GIS ring point to the asset's base-level vertices; the two-way Hausdorff difference is 0.000031 m.",
                "The saved polygon area and perimeter are preserved in the raw GIS snapshot; the footprint was not rescaled."
            ],
            "limits": ["The source service does not publish survey positional accuracy; the project uses a local tangent coordinate approximation."]
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "The asset is saved in the campus coordinate frame and the footprint retains the source GIS polygon's orientation and dimensions.",
                "Model base vertices match the GIS ring to about 0.03 mm; total bounding box is about 54.97 x 42.74 m, with small exterior trims extending past the GIS wall line.",
                "The historical GIS map and emergency plan identify the same Harrison Street site."
            ],
            "limits": ["This asset-only grade does not verify a master placement marker or neighboring master context."]
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.2,
            "max_score": 2.0,
            "evidence": [
                "Purdue's current 2026 emergency plan lists basement, first, second, third floors, and an attic; the model presents three occupied-looking levels over a basement with a raised attic/service volume.",
                "The 1916 Purdue GIS description independently records a basement and attic, and states that the original building was two stories.",
                "The model tags its vertical extent as estimated and uses a 15.925 m top based on the prior massing envelope."
            ],
            "limits": ["No measured elevations or floor-to-floor heights support the 15.925 m height. The model's roof and raised attic/service shape are not established by the available plan or historic description."]
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.0,
            "max_score": 2.0,
            "evidence": [
                "The mesh includes coherent brick-like wall texture, pale story bands, window surrounds, glazing, and entry portals; the GIS-derived outline preserves the building's distinctive plan shape.",
                "Purdue's historical record establishes the building's 1916 origin and former use, which gives broad architectural context.",
                "The independent preview shows a complete, legible exterior with repeated window bays and three visible entry locations."
            ],
            "limits": ["The local evidence set contains no usable exterior elevation or facade photograph. Brick color, stone trim, window rhythm, portal designs, and exact entrance positions remain visual estimates; they should not be treated as verified historic details."]
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.5,
            "max_score": 2.0,
            "evidence": [
                "A fresh Blender 5.2.3 process opened the asset and found the expected scene, collection, stable ID, and one named building mesh.",
                "The mesh has 5,858 vertices, 4,152 polygons, and 8 material slots; brick and stone shaders use procedural nodes.",
                "No file-image dependencies or linked libraries were found, and builder evidence includes the source GIS snapshot, current emergency plan, preview, and validation report."
            ],
            "limits": ["Geometry vertices are still stored in the campus-wide coordinate frame rather than a local building frame, so a master placement marker would double-translate the building unless the source is converted before linking. One material slot is unused, and the interior is only represented by generic floor plates."]
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        {"severity":"uncertainty","finding":"The asset footprint and campus coordinates are unusually well-supported, but the roof/attic height and facade language remain estimates without a measured elevation or a usable exterior photograph."},
        {"severity":"minor modeling issue","finding":"The darker brick material slot has no polygons assigned; it does not currently affect the preview."},
        {"severity":"scope limit","finding":"The model contains generic floor plates only. Interior rooms, corridors, and connections to Lynn Hall/VPRB tunnels are not represented or independently validated."}
    ]
    return {
        "building":"Veterinary Pathology Building (VPTH)",
        "asset_sha256":probe["asset_sha256"],
        "score":score,
        "max_score":10,
        "passing_threshold":8,
        "pass":score >= 8,
        "criteria":criteria,
        "evidence":{
            "independent_fresh_open_probe":"fresh_open_probe.json",
            "source_evidence":"../evidence.json",
            "source_gis_snapshot":"../purdue_campus_building_vpth_raw.geojson",
            "exterior_preview":"../preview_exterior.png",
            "builder_validation":"../validation.json",
            "rubric":"AGENT.md five-criterion rubric"
        },
        "findings":findings
    }


if __name__ == "__main__":
    result=evaluate()
    (GRADE_DIR / "grade_result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
