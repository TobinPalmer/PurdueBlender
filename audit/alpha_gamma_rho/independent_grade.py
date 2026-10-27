"""Independent Alpha Gamma Rho asset evaluator.

Run from the repository root with standard Python. It reads the raw OSM snapshot,
source-page snapshots, render evidence, saved Blender asset, and fresh-open report.
Visual observations are explicitly recorded as evaluator findings; unsupported
measured height and plan details are not treated as confirmed facts.
"""
from __future__ import annotations
import json, math, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=Path(__file__).resolve().parent
ASSET=ROOT/'modular'/'buildings'/'massing_house_301841253_f0b3be3.blend'

def evaluate():
    e=json.loads((EVIDENCE/'evidence.json').read_text(encoding='utf-8-sig'))
    osm=json.loads((EVIDENCE/'sources'/'osm_way_301841253_2026-10-26.json').read_text(encoding='utf-8-sig'))
    way=next(x for x in osm['elements'] if x.get('type')=='way' and x.get('id')==301841253)
    nodes={x['id']:x for x in osm['elements'] if x.get('type')=='node'}
    pts=[]
    for n in way['nodes'][:-1]:
        p=nodes[n]
        pts.append(((p['lon']+86.9137)*111412.84*math.cos(math.radians(40.4274)),(p['lat']-40.4274)*111040.0))
    bounds=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
    area=abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2)
    chapter=(EVIDENCE/'sources'/'agr_delta_official_site_2026-10-26.html').read_text(encoding='utf-8-sig').lower()
    purdue=(EVIDENCE/'sources'/'purdue_ag_greek_life_page_2026-10-26.html').read_text(encoding='utf-8-sig').lower()
    kjg=(EVIDENCE/'sources'/'kjg_agr_project_page_2026-10-26.html').read_text(encoding='utf-8-sig').lower()
    gis=json.loads((EVIDENCE/'sources'/'purdue_campus_607_address_query_2026-10-26.json').read_text(encoding='utf-8-sig'))
    reopen=json.loads((EVIDENCE/'reopen_validation_2026-10-26.json').read_text(encoding='utf-8-sig'))
    renders=[EVIDENCE/'renders'/'alpha_gamma_rho_hero.png',EVIDENCE/'renders'/'alpha_gamma_rho_first_floor_interior.png']
    assert way.get('tags',{}).get('addr:housenumber')=='607'
    assert all(s in chapter for s in ('607','university'))
    assert 'alpha gamma rho' in purdue and 'alpha gamma rho fraternity' in kjg
    assert round(bounds[2]-bounds[0],3)==round(e['source_footprint']['dimensions_xy_m'][0],3)
    assert round(bounds[3]-bounds[1],3)==round(e['source_footprint']['dimensions_xy_m'][1],3)
    assert round(area,2)==round(e['source_footprint']['polygon_area_m2'],2)
    assert ASSET.is_file() and all(p.is_file() for p in renders)
    assert reopen['status']=='passed' and reopen['collection']=='Asset_massing_house_301841253_f0b3be3'
    assert gis.get('features')==[]
    # Direct visual inspection: brick walls, sash windows/blue shutters, the
    # east portico with white columns, blue fascia, ΑΓΡ sign, and gable dormers
    # are visible in the hero render. The overhead preview shows interior
    # dining/common areas, partitions and stairs, but the room arrangement is
    # schematic and not sourced from plans.
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','points':1.8,'max_points':2,
       'evidence':f"OSM way 301841253 has addr:housenumber=607; the official chapter page lists 607 N University; Purdue Agriculture identifies Alpha Gamma Rho and provides a chapter-house image; shell polygon has {len(pts)} source vertices, {area:.2f} m² area, and OSM-aligned bounds.",
       'finding':'Identity and plan trace are strongly cross-checked, but the polygon is a community-mapped 2022 trace and is not an official measured survey.'},
      {'criterion':'Position, orientation, scale/dimensions','points':1.6,'max_points':2,
       'evidence':f"The raw ring maps to {bounds[2]-bounds[0]:.3f} m E-W by {bounds[3]-bounds[1]:.3f} m N-S; the shell geometry is built from that same ring in the documented project conversion, with north-south long axis and east-facing address frontage.",
       'finding':'No independent Purdue GIS feature for 607 or survey control was returned; the GIS address query is empty. Campus-world horizontal registration beyond the OSM transform remains unverified.'},
      {'criterion':'Evidence-backed height, floors, and roof form','points':1.4,'max_points':2,
       'evidence':'KJG Architecture describes the Purdue project as four levels and approximately 24,100 sq ft; its saved project render depicts a dark pitched roof, dormers, and brick/portico composition, corroborated by Purdue Agriculture photograph.',
       'finding':'The model uses a 10.35 m wall top and 13.8 m ridge by estimate. The source says four levels but does not clarify which are above grade; roof heights and exact roof geometry are not measured.'},
      {'criterion':'Facade, entrances, and distinctive architecture','points':1.7,'max_points':2,
       'evidence':'Purdue Agriculture photo and KJG project image directly show red brick, blue shutters/fascia, white columned portico, arched transom, and green ΑΓΡ pediment lettering. Exterior hero includes those features and four dormers.',
       'finding':'The modeled gable/roof and entrance proportions are stylized and the roof reads as a broad, simplified plane; no elevation drawing was supplied for exact bay spacing or proportions.'},
      {'criterion':'Modular export, portability, complete evidence','points':1.7,'max_points':2,
       'evidence':f"Saved asset reopens with scene and collection names intact; {reopen['object_count']} collection objects and {reopen['mesh_count']} meshes evaluate; no external file images; exterior/interior renders and source snapshots are present.",
       'finding':'Manifest path/collection are preserved, but shared manifest still reports the old one-object count while the exported collection is now detailed multi-object geometry; coordinator review is needed.'}
    ]
    score=round(sum(c['points'] for c in criteria),1)
    return {'score':score,'max_score':10,'criteria':criteria,
            'evidence':{'asset_path':str(ASSET),'sources_folder':str(EVIDENCE/'sources'),'renders':[str(p) for p in renders],
                        'footprint_measurement':{'osm_way_id':301841253,'area_m2':area,'bounds_xy_m':bounds,'long_axis':'north-south'},
                        'fresh_open':reopen,'purdue_gis_address_query_features':len(gis.get('features',[]))},
            'findings':['Current identity/address match is strong despite no direct OSM name tag.','Footprint match is exact by construction and dimensions; position is only as trustworthy as the community mapping and local conversion.','Vertical dimensions and interior room layout remain estimates.','The manifest object-count field is stale and needs a coordinator update during integration.'],
            'grader':'independent evidence review', 'date':'2026-10-26'}

if __name__=='__main__':
    result=evaluate()
    out=EVIDENCE/'independent_grade_2026-10-26.json'
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
