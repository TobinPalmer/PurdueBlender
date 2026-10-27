from pathlib import Path
import json, hashlib

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'audit/utility_plant_office_facility'
OUT = AUDIT / 'independent_grade_r2'
ASSET = ROOT / 'modular/buildings/massing_utility_plant_office_facility_e219ef5.blend'
EXPECTED_SHA = '3d80ce9c7eb6c21ce21308da292e4bc7409acd7dc20875bd5a7c8e81fb0c7b28'

def evaluate():
    probe = json.loads((OUT / 'fresh_open_probe.json').read_text(encoding='utf-8'))
    provenance = json.loads((AUDIT / 'source_provenance.json').read_text(encoding='utf-8'))
    feature = json.loads((AUDIT / 'sources/arcgis_fid296_feature.json').read_text(encoding='utf-8'))['features'][0]
    attrs = feature['attributes']
    assert hashlib.sha256(ASSET.read_bytes()).hexdigest() == EXPECTED_SHA == probe['asset_sha256']
    assert probe['fresh_open'] and probe['passed']
    assert attrs['FID'] == 296 and attrs['BLDG_ABBR'] == 'UPOF'
    assert probe['max_vertex_error_against_raw_gis_ring_m'] < 1e-5
    assert abs(probe['long_axis_rotation_from_north_deg']) < 1.0
    assert probe['unsupported_large_roof_equipment_names'] == []
    criteria = [
      {'name':'Identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':['Raw ArcGIS feature is FID 296, code UPOF, name Utility Plant Office Facility.','Fresh Blender readback finds ten footprint vertices and maximum local-coordinate error 0.000000551 m against the source ring.','The z20 orthophoto overlay shows the magenta feature outline closely following the roof, including the east-side projection.'],
       'assessment':'Full credit. Stable identity and the non-rectangular footprint are verified numerically and visually.'},
      {'name':'Position, orientation, and scale','score':2.0,'max_score':2.0,
       'evidence':['Local footprint is 20.862 × 23.945 m; computed source area is 446.009 m² and model area is 446.006 m².','Longest-axis rotation is 0.441° from north.','Explicit campus placement_origin_xy_m is [105.20840981346892, -1052.103607498187].'],
       'assessment':'Full credit. Footprint and site anchor agree with supplied ArcGIS projection method to high precision.'},
      {'name':'Height, floors, and roof evidence','score':1.55,'max_score':2.0,
       'evidence':['ArcGIS attributes report NUM_LEVELS=2 and CountOfFLO=2.','Model shell height is 6.88 m and highest mesh is 7.32 m.','ArcGIS Extrution=24 has undocumented units; source provenance explicitly treats 7.3 m as an estimate, not verified survey height.','62 E-W oriented seam objects match the z20 orthophoto, whose roof appears bright and near-continuous. No large equipment/hatch objects remain.'],
       'assessment':'Strong two-floor low-profile roof treatment, but exact eave/parapet height and seam spacing remain estimates. Absence of HVAC/hatch is justified by the newer imagery, which does not substantiate them.'},
      {'name':'Facade, east entry, and distinctive details','score':1.05,'max_score':2.0,
       'evidence':['Official OEP page identifies the main entry on the east wall; asset includes a distinct entry projection and paired dark doors on that side.','OEP describes an administrative building, mostly cubicle workspace, with Utility Engineering/BAS staff upstairs; model has schematic interiors on both floors (30 objects each).','Oblique render shows light gray vertically ribbed walls, repetitive dark window/panel forms, floor divider, plinth, and east entry.','ECN camera is captioned “from UPOF” but the captured close wall is not conclusively identified as UPOF; source provenance correctly limits this to contextual support.'],
       'assessment':'Entry placement and restrained industrial material treatment are plausible and evidence-aware. Direct facade imagery is lacking: repeated window positions, glazing, wall panel system, and elevation composition are estimated; rendered window faces read nearly opaque and unusually dark. Interior is explicitly schematic/unverified.'},
      {'name':'Modular export, portability, and evidence','score':1.85,'max_score':2.0,
       'evidence':['Fresh Blender 5.2.3 process opened the asset and found expected scene and export collection.','Export collection has 361 objects (359 meshes); external image files and missing unpacked images are both absent. All 13 materials are procedural.','Separate evidence includes build/validation records, provenance, orthophoto overlay, raw imagery tiles, OEP snapshot, webcam page/image, and fresh-open render/probe.'],
       'assessment':'Portable self-contained asset with substantial evidence. Procedural, mostly monochrome surfaces are reliable and dependency-free but could use richer facade/window variation.'},
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    report = {
      'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),
      'stable_id':'massing_utility_plant_office_facility_e219ef5',
      'asset_sha256':EXPECTED_SHA,
      'independent_fresh_open_version':probe['blender_version'],
      'score':score,'max_score':10.0,'threshold':8.0,'passed_threshold':score >= 8.0,
      'criteria':criteria,
      'evidence':[
        'fresh_open_probe.json: current Blender 5.2.3 readback, geometry comparisons, dimensions, object/material/dependency counts.',
        'fresh_open_oblique.png: fresh render from opened asset; visual assessment of roof, facade, windows, entry and massing.',
        '../previews/utility_plant_office_facility_gis_orthophoto_overlay.png: z20 Esri roof/footprint comparison.',
        '../sources/arcgis_fid296_feature.json and ../source_provenance.json: raw GIS feature, projection method and stated uncertainty.',
        '../sources/purdue_oep_upof.html: official OEP program and east-entry source.',
        '../sources/purdue_ecn_webcam_from_upof_2026_05_18_11_00.jpg: contextual facade clue; not treated as confirmed elevation.'
      ],
      'findings':[
        {'severity':'positive','finding':'The roof equipment and hatch removal is a well-supported correction: the z20 outline overlays a largely uninterrupted roof and does not identify those objects.'},
        {'severity':'positive','finding':'E-W roof rib direction now agrees with the north-up orthophoto.'},
        {'severity':'limitation','finding':'Facade treatment remains uncertain because no direct UPOF elevation is provided by the available OEP, ECN, or overhead imagery.'},
        {'severity':'actionable','finding':'For a higher facade score, seek a clearly geolocated/direct UPOF street or ground-level facade image; then replace the estimated repeated dark panels with evidenced window sizes, spacing, glazing reflectance, and cladding breaks. Keep these marked estimated until direct imagery is found.'},
        {'severity':'limitation','finding':'The ArcGIS Extrution field unit is undocumented. Do not describe the 6.88 m shell / 7.32 m total as verified height; preserve as an estimate unless a reliable elevation source is found.'},
        {'severity':'limitation','finding':'Interior rooms are schematic because the OEP page gives limited program facts rather than a measured architectural plan.'}
      ],
      'source_facts_used':{'GIS_feature_id':attrs['FID'],'building_code':attrs['BLDG_ABBR'],'GIS_levels':attrs['NUM_LEVELS'],'GIS_extrution_raw':attrs['Extrution'],'height_units_documented':False},
      'method':'Independent criterion-based review of source snapshots, fresh-process Blender readback, numeric footprint comparison, and renders. No prior grader score was used to determine rubric points.'
    }
    (OUT/'evaluation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (OUT/'evaluation_report.md').write_text('# Independent UPOF grade r2\n\n**Score: '+str(score)+'/10 — '+('passes' if score>=8 else 'below')+' the 8.0 threshold.**\n\n'+ '\n'.join(f"- **{c['score']:.2f}/{c['max_score']:.2f} — {c['name']}:** {c['assessment']}" for c in criteria)+'\n\n## Findings\n\n'+'\n'.join(f"- **{f['severity'].title()}:** {f['finding']}" for f in report['findings'])+'\n\n## Evidence\n\n'+'\n'.join('- `'+e+'`' for e in report['evidence'])+'\n',encoding='utf-8')
    print(json.dumps({'score':score,'max_score':10,'passed_threshold':score>=8,'report':str(OUT/'evaluation.json')},indent=2))

if __name__ == '__main__': evaluate()
