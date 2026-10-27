"""Independent rubric evaluator for frozen Purdue SAE FID 849 massing asset."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "sae_fid849"
EXPECTED_SHA256 = "9756B5AE39B3070918DEBBE6E3F0A07913F79E1EAB04B956BA4F1D0AAEBDD20D"


def evaluate():
    validation = json.loads((AUDIT / "independent_fresh_open.json").read_text(encoding="utf-8"))
    evidence = {
        "frozen_candidate": {
            "asset": "modular/buildings/massing_sigma_alpha_epsilon_fid849.blend",
            "expected_sha256": EXPECTED_SHA256,
            "independently_reopened_sha256": validation["asset_sha256"],
            "hash_match": validation["asset_sha256"] == EXPECTED_SHA256,
            "fresh_open": validation["fresh_open"],
            "blender_version": validation["blender_version"],
        },
        "identity_and_footprint": [
            "Purdue FID 849 source snapshot names Sigma Alpha Epsilon and address 406 N Littleton St.",
            "Chapter homepage independently gives 406 Littleton St; Tippecanoe parcel key matches that address.",
            "FID outline overlays the visible house roof inside the address-matched parcel; parcel is correctly treated as site boundary, not wall footprint.",
            "Independent reopen compared all 16 source ring vertices to facade base corners: max nearest error 0.000029 m; mean 0.000014 m.",
            "Overlay imagery date is unavailable; orthophoto is used for identity reconciliation, not survey precision.",
        ],
        "position_dimensions": [
            "Footprint uses the project's stated local geographic approximation and campus-coordinate frame.",
            "Reopened XY bounds agree with projected GIS ring bounds, apart from the explicitly modeled small entry projection.",
            "Orientation is retained directly from the official GIS ring; no independent survey or georeferenced elevation is supplied.",
        ],
        "vertical_and_roof": [
            "Architect portfolio renderings show three facade bands / visible storeys and multiple low-pitched roof masses with a raised central volume.",
            "Purdue GIS attributes NUM_LEVELS=1 and Extrution=12 are conflicting/underspecified vertical metadata; modeled 3-level layout and 11.95 m top are estimates, not verified measurements.",
            "Candidate represents roof primarily with a broad flat plate and small raised hip cap; it omits the reference's distinct sloped wing roof masses and gabled entry silhouette is simplified.",
        ],
        "facade_and_entry": [
            "Architect renderings support brick lower facade, light upper walls, repeated window rhythm and a prominent gabled/arched entry.",
            "Candidate includes brick/light bands, repeated framed windows and an entry projection, but details are schematic: rendered entrance surround is simplified, and actual openings / as-built window counts are not established.",
        ],
        "modularity_and_portability": [
            f"Reopened expected collection {validation['expected_collection']} contains {validation['collection_object_count']} mesh objects and all have materials.",
            "No linked libraries, modifiers, or unpacked external image dependencies were found.",
            "Audit includes the raw FID, parcel, imagery, architect portfolio and chapter newsletter snapshots, source register, render, and orthophoto overlay.",
            "This is a newly proposed stable ID and shared manifest registration remains coordinator-owned.",
        ],
    }
    criteria = [
        {"name": "Correct identity and source-backed footprint", "score": 2, "max_score": 2,
         "assessment": "Pass. Purdue GIS identity, chapter address and parcel reconcile; footprint is aligned to the GIS ring within 0.000029 m at the facade base. Orthophoto supports identity but is undated."},
        {"name": "Position, orientation, and scale/dimensions", "score": 2, "max_score": 2,
         "assessment": "Pass for source-derived massing. The GIS polygon is transformed with the project's prescribed local approximation and retained directly; dimensions are approximately 32.35 by 50.01 m. No independent survey is available."},
        {"name": "Evidence-backed height, floors, and roof form", "score": 1, "max_score": 2,
         "assessment": "Partial. Architect renderings support three visible facade bands and a raised central volume, but vertical metrics are estimates and the modeled broad flat roof omits the reference's low-pitched wing roof forms."},
        {"name": "Facade, entrances, and distinctive architecture", "score": 1, "max_score": 2,
         "assessment": "Partial. Brick/light facade bands, repeated windows and an entry projection are supported in broad terms; the gabled/arched entry and facade details are simplified and window counts are not as-built verified."},
        {"name": "Modular export, portability, and complete evidence", "score": 2, "max_score": 2,
         "assessment": "Pass. Exact named collection reopens with all mesh objects materialized, no external image dependencies, linked objects or modifiers; source snapshots and visual evidence are preserved. Shared manifest registration is pending coordinator action."},
    ]
    score = sum(c["score"] for c in criteria)
    return {"building": "Sigma Alpha Epsilon, Purdue FID 849", "score": score, "max_score": 10,
            "result": "PASS" if score >= 8 else "FAIL", "criteria": criteria,
            "evidence": evidence,
            "findings": [
                "The asset faithfully carries the authoritative plan outline and campus frame, but vertical dimensions remain estimates.",
                "Revise roof treatment toward the architect portfolio's distinct low-pitch wing masses and strengthen the gabled entry if the builder continues iteration; these are the two principal fidelity gaps.",
                "The 1-level Purdue GIS attribute conflicts with the three-level visual rendering. Preserve this source conflict in documentation; do not present the modeled levels or 11.95 m cap as measured.",
                "Coordinator should register the proposed asset ID in shared manifest/indexes and track master-blend integration after this pass.",
            ],
            "asset_sha256": validation["asset_sha256"],
            "fresh_open_validation": "independent_fresh_open.json"}

if __name__ == "__main__":
    result = evaluate()
    out = AUDIT / "independent_grade_result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
