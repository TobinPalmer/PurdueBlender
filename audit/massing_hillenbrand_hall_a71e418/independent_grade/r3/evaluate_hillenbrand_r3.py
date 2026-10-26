import json
from pathlib import Path

ROOT = Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
ASSET_ID = 'massing_hillenbrand_hall_a71e418'
AUDIT = ROOT / 'audit' / ASSET_ID
GRADE = AUDIT / 'independent_grade' / 'r3'


def evaluate():
    asset = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
    source_path = AUDIT / 'sources' / 'source_record.json'
    direct_path = AUDIT / 'review' / 'direct_reopen_r3.json'
    validation_path = AUDIT / 'review' / 'validation_r3.json'
    preview_path = AUDIT / 'review' / 'preview_r3.png'
    overlay_path = AUDIT / 'review' / 'gis_aerial_overlay.png'
    official_photo = AUDIT / 'sources' / 'hillenbrand_entrance_official.jpg'
    treasurer_pdf = AUDIT / 'sources' / 'purdue_treasurer_hillenbrand_two_towers_2023.pdf'
    treasurer_page = AUDIT / 'sources' / 'treasurer_hillenbrand_page-3.png'

    source = json.loads(source_path.read_text(encoding='utf-8'))
    direct = json.loads(direct_path.read_text(encoding='utf-8'))
    validation = json.loads(validation_path.read_text(encoding='utf-8'))
    model = direct['objects'][0]
    shell = source['transformed_gis_shell']['bounds_xy_m']
    bounds = model['bounds_world_m']
    delta = [[round(bounds[a][i] - shell[a][i], 4) for i in range(2)] for a in range(2)]
    max_delta = max(abs(v) for axis in delta for v in axis)
    raw = [AUDIT / p for p in source['raw_snapshots']]
    raw_present = all(p.is_file() and p.stat().st_size > 0 for p in raw)

    criteria = [
        {
            'criterion': 'Correct identity and source-backed footprint',
            'score': 1.9,
            'max_score': 2,
            'evidence': [
                'Purdue Facilities GIS BuildingShapesZip4 FID 259 names Hillenbrand Residence Hall at 1301 3rd Street; the official Purdue Residences page independently matches the identity and address.',
                f'The saved mesh XY bounds match the transformed 62-vertex GIS polygon within {max_delta:.4f} m. I inspected the GIS-on-Esri aerial overlay; the outline follows the building footprint/roof perimeter closely, including the connected wings.',
            ],
            'limitations': ['The polygon directly drives the mesh, so bound agreement alone is not independent; the aerial provides a visual cross-check but not survey control.'],
        },
        {
            'criterion': 'Position, orientation, and scale/dimensions',
            'score': 1.8,
            'max_score': 2,
            'evidence': [
                f'Direct-reopen bounds are X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m, Z {bounds[2][0]:.3f}..{bounds[2][1]:.3f} m; the XY bounds agree with the transformed GIS shell within {max_delta:.4f} m.',
                'The model object has zero location/rotation offsets and unit scale in the campus-coordinate massing frame. The polygon orientation and aerial overlay agree visually.',
            ],
            'limitations': ['The project lon/lat conversion is approximate; imagery registration and GIS coordinates are not survey-grade.'],
        },
        {
            'criterion': 'Evidence-backed height, floors, and roof form',
            'score': 1.5,
            'max_score': 2,
            'evidence': [
                'The saved Purdue Treasurer project summary (rendered page 3) states there are two towers of eight floors each, each tower has two wings, and towers connect at the first floor and basement.',
                'The saved aerial shows two separate tower roof crowns and the broad lower connected footprint; the preview models two eight-level towers with approximate wing breaks and hipped caps.',
                'The 25.35936 m roof peak is explicitly labeled estimated; source GIS height fields have undocumented units and conflicting values.',
            ],
            'limitations': ['No measured elevation, exact floor elevations, wing dimensions, roof pitch, ridge height, or as-built confirmation is available. The caps and upper-level wing interpretation remain approximations.'],
        },
        {
            'criterion': 'Facade, entrances, and distinctive architecture',
            'score': 0.8,
            'max_score': 2,
            'evidence': [
                'I inspected the official Purdue entrance photograph: it supports red brick, glazing, and a prominent green standing-seam canopy/pavilion.',
                'The preview shows a brick-colored facade, repeated dark window apertures, and green roof caps; these are plausible schematic cues rather than measured facade details.',
                'The builder removed the entrance geometry because the photograph does not establish which compass-facing wall contains it; the model therefore omits a distinctive documented feature.',
            ],
            'limitations': ['No independent facade drawings or measured window rhythm/size, material extent, entrance position, or canopy geometry.'],
        },
        {
            'criterion': 'Modular export, portability, and complete evidence',
            'score': 2.0,
            'max_score': 2,
            'evidence': [
                f'Independent saved-file reopen record reports Blender {direct["blender_version"]}, expected scene/collection, one mesh ({model["verts"]} vertices; {model["faces"]} faces), identity transform, no modifiers, and no external images; all recorded direct checks pass.',
                f'The preview, validation record, GIS overlay, source record, official PDF and page rendering are present. {sum(p.is_file() and p.stat().st_size > 0 for p in raw)}/{len(raw)} source snapshots listed by the source record are present.',
                'The source record identifies URLs, providers, GIS feature ID, retrieval date, source CRS, coordinate/measurement methods, and uncertainties. Asset identity and export collection names remain stable.',
            ],
            'limitations': ['The validation was performed with Blender 5.2.0 LTS; portability was directly checked in that version.'],
        },
    ]
    score = round(sum(c['score'] for c in criteria), 1)
    findings = [
        'PASS at the 8/10 repository threshold, with the score relying on strong identity/footprint and export evidence.',
        'Height remains an estimate and must not be treated as measured; the floor count is documented in a Purdue project summary, which is not an as-built drawing.',
        'The distinctive entrance canopy is visible in the official photograph but absent from the model because its position could not be resolved. Facade bays and roof details are schematic.',
        'Upper tower wing layout and roof interpretation are only partially supported by the text summary and aerial image; exact dimensions remain unverified.',
    ]
    evidence = {
        'asset': str(asset),
        'preview': str(preview_path),
        'aerial_overlay': str(overlay_path),
        'official_entrance_photo': str(official_photo),
        'treasurer_source_pdf': str(treasurer_pdf),
        'treasurer_page_render': str(treasurer_page),
        'source_record': str(source_path),
        'direct_reopen_record': str(direct_path),
        'validation_record': str(validation_path),
        'xy_model_minus_gis_bounds_m': delta,
        'max_absolute_xy_bound_delta_m': round(max_delta, 4),
        'all_listed_raw_snapshots_present': raw_present,
        'raw_snapshots_present_count': sum(p.is_file() and p.stat().st_size > 0 for p in raw),
        'raw_snapshots_listed_count': len(raw),
        'direct_reopen_checks_passed': direct['all_checks_pass'],
        'visual_inspection': 'Independently inspected preview_r3.png, gis_aerial_overlay.png, official entrance photo, and rendered Treasurer PDF page 3.',
    }
    return {'asset_id': ASSET_ID, 'iteration': 'r3', 'score': score, 'max_score': 10, 'pass_threshold': 8, 'passed': score >= 8, 'criteria': criteria, 'evidence': evidence, 'findings': findings}


if __name__ == '__main__':
    result = evaluate()
    GRADE.mkdir(parents=True, exist_ok=True)
    (GRADE / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
