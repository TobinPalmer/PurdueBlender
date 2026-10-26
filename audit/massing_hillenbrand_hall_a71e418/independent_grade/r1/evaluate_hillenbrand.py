import json
from pathlib import Path

ROOT = Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
ASSET_ID = 'massing_hillenbrand_hall_a71e418'
AUDIT = ROOT / 'audit' / ASSET_ID
GRADE = AUDIT / 'independent_grade' / 'r1'


def evaluate():
    source_path = AUDIT / 'sources' / 'source_record.json'
    direct_path = GRADE / 'direct_model_check.json'
    imagery_path = AUDIT / 'review' / 'gis_aerial_overlay.png'
    preview_path = AUDIT / 'review' / 'preview_r1.png'
    validation_path = AUDIT / 'review' / 'validation_r1.json'
    model_path = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'

    source = json.loads(source_path.read_text(encoding='utf-8'))
    direct = json.loads(direct_path.read_text(encoding='utf-8'))
    validation = json.loads(validation_path.read_text(encoding='utf-8'))
    shell_bounds = source['transformed_gis_shell']['bounds_xy_m']
    model = direct['objects'][0]
    model_bounds = model['world_bounds']
    xy_delta = [
        [round(model_bounds[i][j] - shell_bounds[i][j], 4) for j in (0, 1)]
        for i in (0, 1)
    ]
    max_shell_delta = max(abs(x) for axis in xy_delta for x in axis)
    raw_sources = [AUDIT / p for p in source.get('raw_snapshots', [])]
    raw_sources_present = all(p.is_file() and p.stat().st_size > 0 for p in raw_sources)

    criteria = [
        {
            'criterion': 'Correct identity and source-backed footprint',
            'score': 2.0,
            'max_score': 2,
            'evidence': [
                'Purdue Facilities GIS BuildingShapesZip4 feature FID 259 explicitly names Hillenbrand Residence Hall at 1301 3rd Street.',
                'The source GIS polygon has 62 vertices and directly drives the mesh plan shell.',
                f'Independent saved-blend check compared its XY bounds with the transformed GIS shell; max bound delta is {max_shell_delta:.3f} m. The aerial overlay visually aligns the polygon with the building roof.',
            ],
            'limitations': ['The polygon-to-mesh correspondence is by construction, and the aerial image is not survey control.'],
        },
        {
            'criterion': 'Position, orientation, and scale/dimensions',
            'score': 2.0,
            'max_score': 2,
            'evidence': [
                'Directly reopened blend stores the asset in the expected campus-coordinate frame with identity object transform.',
                f'Model bounds are X {model_bounds[0][0]:.3f}..{model_bounds[0][1]:.3f} m, Y {model_bounds[1][0]:.3f}..{model_bounds[1][1]:.3f} m; transformed GIS bounds agree within {max_shell_delta:.3f} m.',
                'Polygon vertex order and edge direction are inherited from the GIS source; aerial overlay provides a visual alignment check.',
            ],
            'limitations': ['Coordinates use the project approximate local lon/lat conversion, not a survey-grade projection. Small facade details extend beyond the shell.'],
        },
        {
            'criterion': 'Evidence-backed height, floors, and roof form',
            'score': 0.6,
            'max_score': 2,
            'evidence': [
                'GIS/aerial evidence supports the irregular roof plan perimeter and the model reproduces it.',
                'The saved model is 30.4 m tall; its source record labels this as an unverified visual estimate retained from the prior asset.',
                'Facade divisions imply eight schematic levels, while the GIS attributes mention 10 levels/floors and are described as inconsistent; neither establishes the actual floor count.',
                'The preview and aerial show a simplified flat roof with no measured roof heights or rooftop articulation.',
            ],
            'limitations': ['Height and floor count remain unverified; roof profile and rooftop volumes are materially simplified.'],
        },
        {
            'criterion': 'Facade, entrances, and distinctive architecture',
            'score': 0.9,
            'max_score': 2,
            'evidence': [
                'Official Purdue 2018 photo directly supports red brick, glazing, and a green standing-seam entrance pavilion.',
                'The asset has schematic brick, dark window bays, belt courses, and an approximate green canopy material; the saved preview shows repeated window bays and brick massing.',
                'The source photo is a close view without compass location or dimensions, so the builder itself describes canopy location as estimated.',
            ],
            'limitations': ['Window count/size, floor rhythm, entrance wall/location and canopy dimensions are not measured; the preview does not clearly resolve entry details.'],
        },
        {
            'criterion': 'Modular export, portability, and complete evidence',
            'score': 2.0,
            'max_score': 2,
            'evidence': [
                f'Independent Blender 5.2.0 reopen found scene {direct["scene_name"]}, collection {direct["collection_name"]}, one mesh ({model["vertex_count"]} vertices / {model["face_count"]} faces), no modifiers, and no file-backed image dependencies.',
                f'All direct model checks passed: {direct["checks"]}.',
                f'Preview and GIS aerial overlay exist ({preview_path.stat().st_size:,} and {imagery_path.stat().st_size:,} bytes); {sum(p.is_file() and p.stat().st_size > 0 for p in raw_sources)}/{len(raw_sources)} listed raw source snapshots exist.',
                'Source record documents URLs, providers, feature IDs, retrieval dates, CRS/methods where applicable, and uncertainty; validation records the Blender version warning and remaining unknowns.',
            ],
            'limitations': ['The bundled Blender 5.2.0 emitted startup warnings for omitted fonts/add-on operators, though the model opened and the independent checks completed.'],
        },
    ]
    score = round(sum(c['score'] for c in criteria), 1)
    findings = [
        'FAIL: overall score is below the repository minimum of 8/10.',
        'The 30.4 m height is unsupported by measured elevation evidence, and the floor-count depiction conflicts with the source GIS level attribute.',
        'Roof articulation, rooftop volumes, and distinct entry geometry need more source-backed modeling.',
        'The facade uses source-informed materials but schematic window rhythm and unverified entry orientation/dimensions.',
        'The outline/placement is strongly supported by the named Purdue GIS feature and the imagery overlay.',
    ]
    evidence = {
        'asset': str(model_path),
        'preview': str(preview_path),
        'gis_aerial_overlay': str(imagery_path),
        'official_entrance_photo': str(AUDIT / 'sources' / 'hillenbrand_entrance_official.jpg'),
        'source_record': str(source_path),
        'independent_direct_model_check': str(direct_path),
        'independent_visual_inspection': 'Reviewed the saved oblique preview, red GIS-on-aerial overlay, and the official Purdue entrance photograph.',
        'model_xy_bounds_minus_gis_xy_bounds_m': xy_delta,
        'max_absolute_xy_bound_delta_m': round(max_shell_delta, 4),
        'all_listed_raw_snapshots_present': raw_sources_present,
        'raw_snapshot_paths': [str(p) for p in raw_sources],
    }
    return {'score': score, 'max_score': 10, 'pass_threshold': 8, 'passed': score >= 8, 'criteria': criteria, 'evidence': evidence, 'findings': findings}


if __name__ == '__main__':
    result = evaluate()
    (GRADE / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
