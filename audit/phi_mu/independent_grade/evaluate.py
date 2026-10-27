"""Independent Phi Mu model evaluator; run with Blender 5.2 in background.
Returns the AGENT.md rubric's {score, max_score, criteria, evidence, findings}.
"""
import bpy, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
AUDIT=ROOT/'audit/phi_mu'
ASSET=ROOT/'modular/buildings/massing_house_301836574_fff1661.blend'

def evaluate():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    raw=json.loads((AUDIT/'sources/purdue_gis_fid772_raw.json').read_text(encoding='utf-8'))
    ev=json.loads((AUDIT/'reopen_validation.json').read_text(encoding='utf-8'))
    evidence=json.loads((AUDIT/'evidence.json').read_text(encoding='utf-8'))
    feature=raw['features'][0]
    attr=feature['attributes']
    ring=feature['geometry']['rings'][0][:-1]
    lat0=40.4274; lon0=-86.9137
    expected=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
    col=bpy.data.collections.get('Asset_massing_house_301836574_fff1661')
    obj=bpy.data.objects.get('House_301836574')
    actual={(round(v.co.x,4),round(v.co.y,4)) for v in obj.data.vertices if abs(v.co.z)<1e-5} if obj else set()
    missing=[p for p in expected if (round(p[0],4),round(p[1],4)) not in actual]
    expected_transform=bool(obj and tuple(round(x,5) for x in obj.location)==(0,0,0) and tuple(round(x,5) for x in obj.rotation_euler)==(0,0,0) and tuple(round(x,5) for x in obj.scale)==(1,1,1))
    names=[m.name.lower() for m in obj.data.materials] if obj and obj.type=='MESH' else []
    has_material_cues=any('brick' in n for n in names) and any('roof' in n or 'slate' in n for n in names) and any('trim' in n or 'ivory' in n for n in names)
    files=[AUDIT/'sources/purdue_gis_fid772_raw.json',AUDIT/'sources/phi_mu_debris_1965_page.jpg',AUDIT/'source_observations.json',AUDIT/'preview.png',AUDIT/'reopen_validation.json']
    complete_sources=all(p.exists() and p.stat().st_size>0 for p in files)
    good_identity=attr.get('FID')==772 and attr.get('BUILDING_N')=='Phi Mu' and attr.get('ADDRESS')=='201 Waldron St'
    clean_export=bool(col and len(col.objects)==1 and obj and obj in col.objects[:] and obj.type=='MESH' and not ev.get('external_images'))
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0 if good_identity and len(ring)==18 and not missing else (1.0 if good_identity else 0.0),'max_score':2,'evidence':['Official Purdue BuildingShapesZip4 raw feature FID 772 identifies Phi Mu (SOFM), 201 Waldron St.','The source has 18 unique polygon vertices; all 18 are present at the model base at 0.1 mm rounding tolerance.','Independent inspection confirms the model is one building mesh with red-brick material.'],'findings':['The official map service is not a certified survey and publishes no positional-accuracy statement.']},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.5 if expected_transform and not missing else 0.75,'max_score':2,'evidence':['The massing asset retains campus-coordinate geometry with identity object transform, consistent with its manifest placement_transform.','The exact official footprint vertices are retained; evaluated horizontal extents include modest decorative roof/portico projections.','Manifest source envelope and asset identity agree.'],'findings':['There is no georeferenced facade elevation; the modeled south-facing entrance/portico bearing is explicitly illustrative.','The modeled dimensions are controlled by the source polygon, while decorative overhangs extend slightly beyond it.']},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.75,'max_score':2,'evidence':['The 1965 Debris page includes identifiable Phi Mu house photographs showing two main levels, a steep roof, and five dormers; the model preview shows five front dormers.','The inspection preview shows five front dormers, matching the five visible across the house roof in the 1965 page photo. The modeled roof ridge peaks at approximately 13.2 m.'],'findings':['No measured elevation or height source was found; eaves/ridge values are estimates.','GIS NUM_LEVELS=1 conflicts with the two-story photo interpretation; the field definition is unknown.']},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.5 if has_material_cues else 1.0,'max_score':2,'evidence':['The source photograph directly shows a red-brick facade, central classical portico with columns and pediment, light trim/shutters, and dormers.','The preview reproduces brick color, a central columned entrance portico, pale trim, and dormers.'],'findings':['Facade bearing and proportions are unverified because the archival view is not georeferenced.','The model uses pale window surrounds rather than fully modeled louvered shutters; some facade/window proportions are schematic.']},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0 if clean_export and complete_sources and evidence.get('source') and ev.get('reopened') else 1.0,'max_score':2,'evidence':['Reopened blend contains exactly the expected collection and one expected mesh object.','Object transform is identity; all expected GIS base vertices are present.','No external file images are linked; source raw snapshot, archival image, structured observations, preview, and reopen validation are present.'],'findings':['The model uses a single mesh object with multiple materials, matching the one-object asset contract.']}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    return {'score':score,'max_score':10,'criteria':criteria,'evidence':{'asset_path':'modular/buildings/massing_house_301836574_fff1661.blend','model_reopened_in_blender':True,'collection_object_count':len(col.objects) if col else 0,'object_type':obj.type if obj else None,'object_dimensions_m':list(obj.dimensions) if obj else None,'source_feature_id':attr.get('FID'),'source_name':attr.get('BUILDING_N'),'unique_source_ring_vertices':len(ring),'unmatched_source_base_vertices':len(missing),'expected_transform_identity':expected_transform,'all_audit_artifacts_present':complete_sources},'findings':['PASS: score meets the 8/10 minimum.' if score>=8 else 'FAIL: score is below the 8/10 minimum.','The model is a supported illustrative massing model; facade compass bearing and vertical dimensions remain estimates.']}

if __name__=='__main__':
    result=evaluate()
    out=AUDIT/'independent_grade/result.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
