from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'modular/buildings/felix_haas_hall.blend'
VALIDATION = ROOT / 'audit/batch3_haas/round11_validation.json'
INTERSECTIONS = ROOT / 'audit/batch3_haas/round11_intersections.json'
MANIFEST = ROOT / 'modular/manifest.json'
EXPECTED_SHA = 'e333a99e9b7bbb3288329afad7af177be62d73d9077146a4a579c4b123cb1ec1'


def evaluate():
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    validation = json.loads(VALIDATION.read_text(encoding='utf-8'))
    intersections = json.loads(INTERSECTIONS.read_text(encoding='utf-8'))
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    row = next(a for a in manifest['assets'] if a['id'] == 'felix_haas_hall')
    assert sha == EXPECTED_SHA, f'Asset changed during grading: {sha}'
    assert validation['asset_sha256'] == sha and validation['reopened']

    criteria = [
      {
        'name': 'identity and source-backed footprint', 'score': 1.8, 'max_score': 2.0,
        'evidence': 'Official Purdue Events imagery identifies Felix Haas Hall and supports its red roof and signature front; Purdue Archives dates the former Memorial Gymnasium to 1908. The GIS shell was unchanged from the earlier shell review. Round-11 evidence still treats photo-derived form as qualitative.',
        'findings': 'Identity and plan envelope are well supported; no new round-11 pointwise GIS overlay was run.'
      },
      {
        'name': 'position, orientation, and dimensions', 'score': 1.5, 'max_score': 2.0,
        'evidence': 'The saved local frame and placement origin are reported unchanged; the existing shell bounds are retained. The round-11 exported extent reaches X=19.136 m while the cited shell reaches X=12.981 m, so roof projection extends about 6.15 m beyond the shell on that side.',
        'findings': 'Location continuity is supported, but facade bearing/dimensions are estimates and the roof overhang/projection is conspicuously large relative to the unchanged wall envelope.'
      },
      {
        'name': 'height, floors, and roof', 'score': 1.1, 'max_score': 2.0,
        'evidence': 'The historical Purdue timeline supports 17 entrance steps. The official photo supports a red-clay roof, but has no calibration. The round-11 edit raised roof rise by 1.8x; export top is Z=15.84 m versus cited shell top Z=11.5 m.',
        'findings': 'The roof reads much taller and broader than its facade in the saved overview. Roof rise/profile and upper floor heights lack measurable source evidence; the increase is explicitly estimated.'
      },
      {
        'name': 'facade, entrance, and distinctive architecture', 'score': 1.6, 'max_score': 2.0,
        'evidence': 'Round 11 adds segmented stone portal voussoirs, pilasters/capitals, an arched transom, and two lower arched window surrounds. These address signature arches visible in the official exterior photo; brick/stone palette and roof tile color are improved.',
        'findings': 'The render remains simplified and heavily planar compared with the photo; masonry hierarchy and the roof-to-facade proportion still need refinement. Opening dimensions and detailing are estimated from perspective imagery.'
      },
      {
        'name': 'modular export, portability, and evidence', 'score': 1.7, 'max_score': 2.0,
        'evidence': 'Exact SHA matched; the exact asset reopened in Blender 5.2.3. Stable export collection is Asset_felix_haas_hall with 919 objects / 879 meshes; round-11 BVH report found no new-to-existing surface intersections; no external images or image-texture nodes were reported. Builder provides official source links, uncertainty, renders, and intersection evidence.',
        'findings': f'The shared manifest is stale: it still records {row["object_count"]} objects and local max Z={row["local_bounds_m"][2][1]}, versus reopened export {validation["object_count"]} objects and max Z={validation["bounds_local_mesh_m"][1][2]}. Interior is explicitly schematic.'
      }
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    return {
      'building': 'Felix Haas Hall', 'round': 11, 'score': score, 'max_score': 10.0,
      'threshold_8_met': score >= 8.0,
      'asset_path': str(ASSET.relative_to(ROOT)).replace('\\','/'), 'evaluated_sha256': sha,
      'criteria': criteria,
      'evidence_reviewed': [
        'audit/batch3_haas/round11_evidence.md',
        'audit/batch3_haas/round11_validation.json',
        'audit/batch3_haas/round11_intersections.json',
        'audit/batch3_haas/exterior_round11.png',
        'audit/batch3_haas/entrance_round11.png',
        'audit/batch3_haas/interior_plan_round11.png',
        'audit/batch3_haas/exterior_reference.jpg',
        'audit/batch3_haas/independent_review_round10.md',
        'modular/manifest.json'
      ],
      'findings': [
        'The new arches and stone surround improve the signature facade compared with round 10.',
        'The red tile material is more legible, but the roof dominates the saved overview; its rise was increased without calibrated height evidence.',
        'The roof projection extends about 6.15 m beyond the unchanged shell in the X-positive direction; validate the overhang against source evidence.',
        f'Manifest object count is stale ({row["object_count"]} vs {validation["object_count"]}); round-11 master integration must refresh the shared count/bounds.',
        'Interior plan is schematic and correctly labeled as nondimensional; no evidence supports treating it as a verified interior.'
      ],
      'priority_fixes': [
        'Recheck the broad/tall roof silhouette and X-positive overhang using additional elevations, aerial/LiDAR, or a better-calibrated source; reduce unsupported projection/height if evidence warrants.',
        'Refine the large facade fields and stone/brick hierarchy to better match the official photograph without inventing unsupported dimensions.',
        'Update manifest count/bounds only after this exact asset version is accepted and integrated.'
      ],
      'master_or_asset_edited': False,
      'independent_grade': True
    }

if __name__ == '__main__':
    result = evaluate()
    out = Path(__file__).resolve().parent / 'result.json'
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'score': result['score'], 'threshold_8_met': result['threshold_8_met'], 'evaluated_sha256': result['evaluated_sha256'], 'result': str(out)}, indent=2))
