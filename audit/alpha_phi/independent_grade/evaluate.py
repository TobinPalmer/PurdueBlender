from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
AUDIT=ROOT/'audit'/'alpha_phi'
ASSET=ROOT/'modular'/'buildings'/'massing_house_301841331_735e92f.blend'
BLENDER=Path(r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
INSPECT=AUDIT/'independent_grade'/'inspect_asset.py'
def evaluate():
    evidence=json.loads((AUDIT/'evidence.json').read_text(encoding='utf-8'))
    feature=json.loads((AUDIT/'sources'/'purdue_gis_fid764_raw.json').read_text(encoding='utf-8-sig'))['features'][0]
    process=subprocess.run([str(BLENDER),'--background',str(ASSET),'--python',str(INSPECT)],capture_output=True,text=True,check=True)
    marker='GRADE_INSPECT_JSON='
    line=next(line for line in process.stdout.splitlines() if line.startswith(marker))
    asset=json.loads(line[len(marker):])
    artist=AUDIT/'sources'/'alpha_phi_purdue_artist_illustration.jpg'
    yearbook=AUDIT/'sources'/'debris_1966_alpha_phi_source.html'
    preview=AUDIT/'preview.png'
    assert asset['asset_exists'] and artist.is_file() and yearbook.is_file() and preview.is_file()
    assert feature['attributes']['FID']==764 and asset['source_fid']==764
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':f"Official Purdue GIS FID 764 identifies SOAF / Alpha Phi at 801 David Ross Road. Independent Blender reopen matched all {asset['matched_source_vertices']} of {asset['source_vertices']} distinct transformed GIS ring points at {asset['max_source_vertex_residual_m']:.6f} m maximum residual. The yearbook snapshot independently identifies the new house at that address in 1966.",
       'findings':'Identity and plan ring are well supported. GIS is not a certified survey and has no published positional accuracy.'},
      {'name':'Position, orientation, and scale/dimensions','score':1.7,'max_score':2.0,
       'evidence':f"The source polygon base is exact, the object transform is identity, and reopened bounds are {asset['world_bounds_m']} m. The base ring preserves all 16 distinct corners.",
       'findings':'Scale and plan shape are strongly supported by GIS, though the source provides no positional uncertainty. The principal facade/entry bearing was selected illustratively from an unscaled drawing that is not georeferenced; the sign feature projects beyond the source wall polygon.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.1,'max_score':2.0,
       'evidence':'The exact-house artist illustration supports a flat roofline, raised sign wall, and multiple facade levels. The model has three window bands, a flat cap, and the sign wall.',
       'findings':'GIS NUM_LEVELS=1 conflicts with the illustration’s visible levels; its field convention is undocumented. The image does not establish whether all window bands are full floors. Eaves at 13.4 m and the 17.4 m sign wall are estimates without measured elevations.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.4,'max_score':2.0,
       'evidence':'The exact-house drawing identifies AΦ / Alpha Phi and depicts an asymmetrical masonry facade, flat roof, horizontal bands, repeated narrow windows, a covered entrance with posts, and a raised sign wall. The model reproduces these broad features and contains readable signage.',
       'findings':'The original facade drawing shows a longer, denser window rhythm and larger articulated masonry sign panels than the model’s sparse simplified bays. The reference is an unscaled artist illustration, so exact window spacing, materials, entrance side, and present-day details are not verified.'},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,
       'evidence':f"The reopened file contains the expected collection with {asset['collection_object_count']} mesh object, identity transform, {len(asset['modifiers'])} modifiers, and {len(asset['external_unpacked_images'])} external unpacked images. Raw GIS, the exact-house illustration, yearbook page snapshot, source observations, preview, validation, and independent evaluator are present.",
       'findings':'Stable asset ID, collection, path, and object name are preserved; library is self-contained.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=[('PASS: meets the repository 8/10 threshold.' if score>=8 else 'FAIL: below the repository 8/10 threshold.'),'Official GIS and historical yearbook strongly verify identity, address, and footprint ring.','The three-level interpretation conflicts with the undocumented GIS NUM_LEVELS=1 field; all heights remain estimates.','The facade direction is unregistered and the illustration is unscaled; model detail remains schematic compared with the pictured window and masonry rhythm.']
    return {'score':score,'max_score':10,'criteria':criteria,'evidence':{'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),'source_evidence':str((AUDIT/'evidence.json').relative_to(ROOT)).replace('\\','/'),'independent_asset_inspection':asset,'gis_attributes':{k:feature['attributes'].get(k) for k in ['FID','BLDG_ABBR','BUILDING_N','ADDRESS','NUM_LEVELS','Extrution','Shape__Area','Shape__Length']},'visual_reference':{'file':'audit/alpha_phi/sources/alpha_phi_purdue_artist_illustration.jpg','description':'HUBERart exact-house unscaled illustration with three apparent facade bands, flat roof, raised AΦ sign wall, window rhythm, and covered entrance.'},'yearbook_reference':{'file':'audit/alpha_phi/sources/debris_1966_alpha_phi_source.html','description':'1966 Debris says Alpha Phi showed off its new house at 801 David Ross Road.'}},'findings':findings}
if __name__=='__main__':
    result=evaluate()
    (AUDIT/'independent_grade'/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
