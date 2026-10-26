"""Independent r4 regrade after shared manifest bounds correction.

Uses a fresh Blender 5.2.3 reopen through the prior self-contained evaluator,
then independently checks the current manifest against reopened dimensions.
Only the corrected manifest changes the r3 rubric assessment.
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ID = "massing_provenance_apartments_005_960f6b0"
BASE_PATH = HERE / "independent_evaluator_r3.py"


def evaluate():
    spec = importlib.util.spec_from_file_location("provenance_r3_reopen", BASE_PATH)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)

    # This performs a new separate-process Blender reopen and rechecks the
    # GIS ring, evidence package, names, mesh, dependencies and source files.
    result = base.evaluate()
    bounds = result["evidence"]["direct_reopen_measurements"]["bounds"]
    manifest = result["evidence"]["manifest_bounds_m"]
    delta = [[bounds[i][j] - manifest[i][j] for j in range(2)] for i in range(3)]
    max_delta = max(abs(v) for row in delta for v in row)
    assert max_delta <= 0.001, f"Manifest/reopened bounds differ by {max_delta} m"
    assert result["evidence"]["blender"].startswith("5.2.3")

    modular = result["criteria"][4]
    modular["score"] = 2.0
    modular["status"] = "Asset reopens cleanly; manifest bounds match the saved asset and the evidence package is complete"
    modular["evidence"] = [
        f"Fresh separate-process Blender {result['evidence']['blender']} reopen confirms scene/collection identity, one mesh ({result['evidence']['direct_reopen_measurements']['vertices']} vertices, {result['evidence']['direct_reopen_measurements']['faces']} faces), no modifiers, no unpacked images, and no linked libraries.",
        "The dedicated audit contains the raw Purdue GIS snapshot, C1.4 plan/crop, raw and overlaid 2025 orthophoto, exact-block source search/register, revision summary, reopen validation, and top/oblique renders. The mesh has two neutral material slots and no external image dependencies.",
        f"The coordinator-updated shared manifest bounds match the Blender-reopened mesh bounds componentwise within {max_delta:.6f} m: {bounds}. This resolves the prior integration-bounds mismatch."
    ]
    modular["findings"] = []
    result["score"] = round(sum(c["score"] for c in result["criteria"]), 2)
    result["reviewer"] = "independent r4 evaluator; fresh Blender 5.2.3 reopen and direct check of corrected manifest, GIS crosswalk, source evidence, and renders"
    result["evidence"]["manifest_delta_m"] = delta
    result["evidence"]["manifest_bounds_match_tolerance_m"] = 0.001
    result["evidence"]["reviewed_files"].append(str((HERE / "independent_evaluator_r4.py").relative_to(ROOT)))
    result["evidence"]["limitations"] = [
        "Purdue GIS FID 506 is a pre-planning feature, not an as-built wall survey.",
        "C1.4 is an un-georeferenced site/construction plan and not a vertical elevation.",
        "Orthophoto supports roof outline and approximate breaks, not roof height, pitch, or facade layout.",
        "Three-story evidence is development-wide; eaves, ridge, and roof segmentation remain estimates.",
        "No exact-block facade image/elevation was located; entrances and opening pattern remain unknown."
    ]
    result["findings"] = [f for c in result["criteria"] for f in c["findings"]]
    result["recommendation"] = (
        f"The r4 asset scores {result['score']}/10 and passes the 8/10 standard. "
        "Identity and approximate footprint are well supported by C1.4, FID 506, and the current orthophoto. "
        "Manifest bounds now match the reopened asset. Height and the five-break roof rhythm remain estimates; "
        "facade and entrance character remain undocumented and intentionally unmodeled."
    )
    return result


if __name__ == "__main__":
    grade = evaluate()
    (HERE / "independent_grade_r4.json").write_text(json.dumps(grade, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(grade, indent=2))
