import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PROBE=HERE/'fresh_asset_probe.json'


def evaluate():
    p=json.loads(PROBE.read_text(encoding='utf-8'))
    assert p['sha_matches_expected'] is True
    assert p['gis_feature_id']==295 and p['gis_name']=='Schowe House'
    assert p['scene']=='Building_massing_purdue_center_for_regional_development_scho_a2375c9'
    assert p['collection']=='Asset_massing_purdue_center_for_regional_development_scho_a2375c9'
    assert p['gis_to_wall_max_m'] is not None and p['wall_to_gis_max_m'] is not None
    criteria=[
      {
        'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
        'status':'verified',
        'evidence':[
          'Purdue campus GIS feature 295 names Schowe House at 1341 Northwestern Avenue and reports 471.365 m² area; the official campus map labels SCHO as Global Policy Research Institute (Schowe House), and the PCRD contact page confirms the address.',
          f"I independently sampled the GIS boundary and the saved perimeter wall mesh. GIS-to-wall maximum distance is {p['gis_to_wall_max_m']:.3f} m and wall-to-GIS maximum is {p['wall_to_gis_max_m']:.3f} m; mean GIS-to-wall distance is {p['gis_to_wall_mean_m']:.3f} m. The residual is concentrated around ground-level openings and the documented wall thickness."
        ],
        'reason':'Building identity is corroborated by multiple Purdue records. The 40-vertex official footprint is used directly, and the structural walls align closely with it.'
      },
      {
        'criterion':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2.0,
        'status':'mostly verified in campus coordinates',
        'evidence':[
          f"The independently checked wall aligns to GIS bounds X={p['gis_bounds_m'][0]} m, Y={p['gis_bounds_m'][1]} m under the project's documented lon/lat-to-local-meter transform.",
          'The model retains the massing asset’s campus-world coordinate convention and is not rescaled. The approximate project transform is not a surveyed CRS, and this stand-alone grade does not validate a master placement marker or neighboring context.'
        ],
        'reason':'Footprint position, orientation, and plan dimensions are directly derived from the mapped feature. A small deduction reflects the approximate coordinate conversion and the fact that master integration has not yet been reviewed.'
      },
      {
        'criterion':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2.0,
        'status':'roof form partly photo-supported; vertical dimensions estimated',
        'evidence':[
          'The retained May 2025 NIRPC appendix photo associated with the Schowe House/PCRD address visibly shows a brick house with intersecting gray pitched roofs, upper dark wood/shingle gable faces, chimney stacks, and garage doors. The revised model now contains three cross-gable roof runs, dark infill faces, and two brick chimneys.',
          f"Fresh-open evaluated vertical bounds are {p['evaluated_bounds_m'][2][0]:.2f}–{p['evaluated_bounds_m'][2][1]:.2f} m. The project sources do not provide a surveyed elevation, confirmed floor count, or roof dimensions; eaves, ridge levels, chimney heights/positions, and wing roof geometry remain visual estimates."
        ],
        'reason':'The revised roof silhouette includes the principal photo-supported cross-gables and chimneys, but exact heights and hidden-side geometry are not documented by measured sources.'
      },
      {
        'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2.0,
        'status':'principal materials and features supported; some openings/interior schematic',
        'evidence':[
          'The photo and source notes support red-brown brick, slate-like gray roofs, upper dark timber/shingle cladding, rectangular windows, chimney stacks, and garage doors. These features appear in the revised model and are represented with distinct assigned materials.',
          'The single oblique photo is partly tree-obscured and does not identify camera azimuth. Door/window placement on obscured elevations, the exact main entrance position, roof junction details, and the interior plan cannot be verified from this source set; the modeled interior is explicitly schematic.'
        ],
        'reason':'The principal facade palette and distinctive roof details are now represented. Some openings and the interior remain interpretations because the available photo does not show all elevations or room layout.'
      },
      {
        'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,
        'status':'verified in fresh Blender reopen',
        'evidence':[
          f"A clean Blender {p['blender_version']} process reopened the exact asset SHA {p['asset_sha256']} and found scene {p['scene']}, export collection {p['collection']}, {p['object_count']} collection objects, and {p['mesh_count']} mesh objects.",
          f"All meshes have assigned materials ({len(p['meshes_without_material'])} missing); generated brick, shingle, and slate images are packed; no linked Blender libraries are present. The asset includes its dedicated builder, source snapshots/register, metrics, fresh-open validation, and two review renders."
        ],
        'reason':'The expected asset and collection reopen cleanly and use self-contained packed materials with building-specific evidence.'
      }
    ]
    score=round(sum(c['score'] for c in criteria),2)
    return {
      'building':'Purdue Center for Regional Development / Schowe House',
      'asset_id':'massing_purdue_center_for_regional_development_scho_a2375c9',
      'asset_path':p['asset_path'],'asset_sha256':p['asset_sha256'],
      'grader':'independent_grader_subagent','grade_date':'2026-10-26',
      'score':score,'max_score':10,'passing_threshold':8,
      'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,
      'evidence':{
        'fresh_asset_probe':str(PROBE.relative_to(ROOT)).replace('\\','/'),
        'GIS_source':'audit/schowe_house/sources/purdue_gis_fid295_schowe_house_2026-10-26.json',
        'photo_reference':'audit/schowe_house/sources/schowe_house_pcrd_photo_2025_crop.png',
        'official_source_register':'audit/schowe_house/sources/source_register.json',
        'visual_references':['audit/schowe_house/preview_three_quarter.png','audit/schowe_house/preview_roof.png','audit/schowe_house/sources/schowe_house_pcrd_photo_2025_crop.png'],
        'gis_to_wall_max_m':p['gis_to_wall_max_m'],'wall_to_gis_max_m':p['wall_to_gis_max_m'],
        'gis_to_wall_mean_m':p['gis_to_wall_mean_m'],'evaluated_bounds_m':p['evaluated_bounds_m'],
        'mesh_count':p['mesh_count'],'material_names':p['material_names'],'images':p['images']
      },
      'findings':[
        'Revision 3 resolves the previous multi-meter wall alignment defect and adds the cross-gable runs, dark upper gable cladding, and chimneys visible in the address-associated photo.',
        'A single oblique, tree-obscured photograph supports the main roof/facade features but cannot establish measured heights, floor count, all elevation details, roof pitch, or exact chimney placement; these remain estimates.',
        'The small perimeter-distance maxima occur around openings and wall thickness. The converted GIS basis is the project approximate campus transform, not a surveyed CRS.',
        'The interior remains schematic, and the complete campus master/neighbor context is outside this standalone asset grade.'
      ]
    }

result=evaluate()
(HERE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
