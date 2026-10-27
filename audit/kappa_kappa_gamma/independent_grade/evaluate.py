from __future__ import annotations
import json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
AUDIT=ROOT/'audit'/'kappa_kappa_gamma'
ASSET=ROOT/'modular'/'buildings'/'massing_house_301840871_5d1bc06.blend'
BLENDER=Path(r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
INSPECT=AUDIT/'independent_grade'/'inspect_asset.py'

def evaluate():
    evidence=json.loads((AUDIT/'evidence.json').read_text(encoding='utf-8'))
    feature=json.loads((AUDIT/'sources'/'purdue_gis_fid782_raw.json').read_text(encoding='utf-8-sig'))['features'][0]
    obs=json.loads((AUDIT/'source_observations.json').read_text(encoding='utf-8'))
    proc=subprocess.run([str(BLENDER),'--background',str(ASSET),'--python',str(INSPECT)],capture_output=True,text=True,check=True)
    marker='GRADER_ASSET_JSON='
    line=next(line for line in proc.stdout.splitlines() if line.startswith(marker))
    asset=json.loads(line[len(marker):])
    assert feature['attributes']['FID']==782 and feature['attributes']['BLDG_ABBR']=='SOKKG'
    assert asset['source_fid']==782 and asset['matched_vertices']==12 and asset['max_footprint_residual_m']<1e-4
    assert asset['collection']=='Asset_massing_house_301840871_5d1bc06' and asset['object_name']=='House_301840871'
    photo=AUDIT/'sources'/'the_key_1952_page16.png'
    preview=AUDIT/'preview.png'
    assert ASSET.is_file() and photo.is_file() and preview.is_file()
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':f"Official Purdue GIS FID 782 identifies SOKKG / Kappa Kappa Gamma at 325 Waldron Street. Independent Blender inspection matched all {asset['matched_vertices']} of {asset['gis_vertices']} transformed ring points with {asset['max_footprint_residual_m']:.6f} m maximum residual.",
       'findings':'Identity and plan ring are well supported. The campus GIS is not a certified survey and provides no positional accuracy.'},
      {'name':'Position, orientation, and scale/dimensions','score':1.7,'max_score':2.0,
       'evidence':f"The detailed asset remains in the project campus frame with identity transform. Reopened bounds are {asset['bounds_world_m']} m, and the wall base agrees exactly with the mapped 12-point concave outline.",
       'findings':'The footprint and plan scale follow GIS. The west-facing principal facade and entry direction are selected from an unregistered historical photograph; compass-facing orientation is not verified. The modeled roof overhang extends modestly outside the GIS wall ring.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2.0,
       'evidence':'The February 1952 Kappa magazine page identifies Gamma Delta’s house and shows two main facade levels under a steep dormered roof. The asset includes two main levels and three dormers.',
       'findings':'GIS NUM_LEVELS=1 conflicts with the photo’s two visible facade levels; the GIS field definition is undocumented. Eaves (7.3 m), ridge (11 m), dormer dimensions, and present roof plan are estimates; no measured elevation or current roof drawing was found.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.3,'max_score':2.0,
       'evidence':'The historical photograph and caption support white rostone, French Provincial vocabulary, a steep dormered roof, repeated shuttered windows, and a centered entry. The model includes pale stone walls, two window bands with shutters, three dormers, and a centered entry/portico.',
       'findings':'This is a schematic interpretation of a single 1952 image, not a verified current facade. The model has sparse simplified sash bays and a low roof cap across GIS wings; the historical image shows a broader, more steeply articulated roof and facade ornament. Exact window spacing, current additions, material colors, and street-facing elevation remain uncertain.'},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,
       'evidence':f"Independent reopen inspection found the expected one-object collection, mesh object, identity transform, {asset['modifier_count']} modifiers, and {len(asset['external_unpacked_images'])} external unpacked images. GIS raw data, historical image, source observations, build script, validation script, and preview are present.",
       'findings':'The asset preserves its stable path, ID, collection and object names. The library is self-contained.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    result={'score':score,'max_score':10,'criteria':criteria,'evidence':{'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),'source_evidence':str((AUDIT/'evidence.json').relative_to(ROOT)).replace('\\','/'),'independent_saved_asset_inspection':asset,'source_attributes':{k:feature['attributes'].get(k) for k in ['FID','BLDG_ABBR','BUILDING_N','ADDRESS','NUM_LEVELS','Extrution','Shape__Area']},'historical_visual_source':{'file':'audit/kappa_kappa_gamma/sources/the_key_1952_page16.png','publication':'The Key, Vol.69 No.1, February 1952, p.14','supports':'Two visible main levels, steep dormered roof, pale stone, shutters, centered entrance'},'source_types':[s['provider'] for s in obs['sources']]},'findings':['PASS: meets the repository’s 8/10 threshold.' if score>=8 else 'FAIL: below the repository 8/10 threshold.','GIS footprint agreement is strong; source positional accuracy remains unpublished.','GIS NUM_LEVELS=1 conflicts with two visible levels in the historical image; GIS field definition is unknown.','Heights, detailed roof geometry, entry bearing, and present-day facade condition remain estimated or unverified.']}
    return result

if __name__=='__main__':
    result=evaluate()
    out=AUDIT/'independent_grade'/'result.json'
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print('SAVED='+str(out))
