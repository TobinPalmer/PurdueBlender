from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRITERIA = [
    {"name":"Identity and source-backed footprint","score":1.8,"max_score":2.0,"evidence":"The asset remains recognizable as PMU's tower-and-wings complex. The historic Purdue Libraries GIS phase context and immutable original bounds support the main shell. R3 freshly reopened with all 18 original wall/base bounds unchanged at 0.0 m delta; three new bases are documented as additive."},
    {"name":"Placement, orientation, and scale","score":1.9,"max_score":2.0,"evidence":"Fresh reopen confirms identity transform on AssetRoot_purdue_memorial_union. Existing read-only master marker records the expected placement at (205.75, -271.65, 0), zero rotation, unit scale. The live master was not reopened as part of this asset-only grading pass."},
    {"name":"Evidence-backed height, floors, and roof form","score":1.2,"max_score":2.0,"evidence":"R3 makes the wing roofs more legible as separate gables and adds three source-supported south-west dormers, restrained slate texture, and caps. The roof render still reads as very broad continuous planes around an oversized open courtyard, with abrupt central junctions and roof planes that compete with the tower silhouette. Height (29.5 m), floor spacing, and roof elevations remain explicitly estimated; the dated images are not measured elevations."},
    {"name":"Facade rhythm, entrance, and distinctive architecture","score":1.5,"max_score":2.0,"evidence":"The south facade now has seven arched openings with stone surrounds, a more articulated entry, multi-tier tower glazing, and a documented 4+3 window rhythm. Brick and slate are visibly textured. However, the tower's window proportions and stone field remain schematic compared with the Purdue references; relief fields are blank, repeated wing openings are sparse, and oblique renders show large unarticulated side walls."},
    {"name":"Modular portability and evidence/validation","score":1.5,"max_score":2.0,"evidence":"Independent fresh reopen confirms 630 objects, 588 meshes, identity root, no mesh without a material, and no unpacked image dependencies. R3 validation records the exact asset SHA and structural comparison. The shared manifest still describes PMU as unverified with object_count 414 and no asset hash or grade record, and master reload/integration remains pending."},
]

def evaluate() -> dict:
    score = round(sum(x['score'] for x in CRITERIA), 1)
    return {
      "asset":"modular/buildings/purdue_memorial_union.blend",
      "sha256":"a53a451a998085af0ae765fdae2c364bd709e02bd03b7169a412b181ada547cd",
      "score":score,"max_score":10.0,"pass_threshold":8.0,"passed":score>=8.0,
      "criteria":CRITERIA,
      "evidence":{
        "fresh_reopen":"audit/purdue_memorial_union_independent_grade/independent_reopen_r3.json",
        "builder_validation":"audit/purdue_memorial_union_refine/validation_r3.json",
        "source_and_method":"audit/purdue_memorial_union_refine/build_evidence.md",
        "r3_rendered_views":[
          "audit/purdue_memorial_union_refine/grader_south_oblique_r3.png",
          "audit/purdue_memorial_union_refine/grader_west_oblique_r3.png",
          "audit/purdue_memorial_union_refine/grader_roof_r3.png",
          "audit/purdue_memorial_union_refine/south_facade_detail_r3.png"
        ],
        "source_images":[
          "audit/purdue_memorial_union_refine/archives_postconstruction_1924.jpg",
          "audit/purdue_memorial_union_refine/official_centenary_exterior_2024.jpg"
        ],
        "shared_manifest":"modular/manifest.json; PMU object_count is 414 and status remains unverified"
      },
      "findings":[
        "Score: 7.9/10, below the 8.0 pass threshold. R3 improves facade rhythm and source-specific detail over R2 but does not resolve the roof silhouette/junction problem enough to pass.",
        "Break up the broad roof planes and make the individual wing gables/eaves and courtyard transitions read cleanly from south-west and west oblique views. Preserve the footprint and identify any roof dimensions as estimates.",
        "Bring tower glazing and limestone surround closer to the 2024 reference proportions; add supported articulation to the currently blank side relief panels and increase facade rhythm where supported by the 1924 photo.",
        "After a passing grade, synchronize the PMU manifest object count/hash and verify the master placement on a fresh reopen. Do not treat the manifest's current count 414 as the actual R3 count of 630."
      ],
      "limitations":[
        "Historical GIS is approximate and phase-specific; it does not prove present-day dimensions or detailed roof geometry.",
        "The 1924 archival and 2024 university images differ in date and viewpoint, so comparisons support qualitative facade and massing review only.",
        "This reviewer did not modify the PMU asset, manifest, or master file."
      ]
    }

if __name__ == '__main__':
    result=evaluate()
    (HERE/'independent_grade_r3.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    lines=[
      '# Independent grade — Purdue Memorial Union R3','',
      f"**Score: {result['score']:.1f}/10 — {'passes' if result['passed'] else 'below'} the 8.0 pass threshold.**",'',
      f"Reviewed asset SHA-256: `{result['sha256']}`. The saved asset was reopened independently in Blender 5.2.3; reopen evidence is `independent_reopen_r3.json`. This review compares the R3 render set with the cited Purdue Archives 1924 and Purdue University 2024 images and the source record in `audit/purdue_memorial_union_refine/build_evidence.md`.",'',
      '| Criterion | Score | Finding |','|---|---:|---|'
    ]
    for c in CRITERIA:
      lines.append(f"| {c['name']} | {c['score']:.1f}/{c['max_score']:.1f} | {c['evidence']} |")
    lines += ['', '## Findings', ''] + [f"{i}. {v}" for i,v in enumerate(result['findings'],1)] + ['', '## Review limits', ''] + [f"- {v}" for v in result['limitations']] + ['', 'Machine-readable result: `independent_grade_r3.json`. Scoring function: `independent_evaluator_r3.py`.', '']
    (HERE/'independent_grade_r3.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'score':result['score'],'passed':result['passed'],'criteria':[(c['name'],c['score']) for c in CRITERIA]},indent=2))
