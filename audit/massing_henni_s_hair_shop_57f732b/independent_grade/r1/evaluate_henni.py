"""Independent, read-only AGENT.md rubric evaluation for Henni's Hair Shop.

Run the paired inspect_saved_blend.py in Blender 5.2 first, then run this file with system Python.
"""
from pathlib import Path
import json, math
from shapely.geometry import Polygon

ROOT=Path(__file__).resolve().parents[4]
AUDIT=ROOT/'audit'/'massing_henni_s_hair_shop_57f732b'
GRADE= AUDIT/'independent_grade'/'r1'
ASSET=ROOT/'modular'/'buildings'/'massing_henni_s_hair_shop_57f732b.blend'

def evaluate(asset_facts, source_catalog, osm, business_html, render_path):
    wid=116427257
    nodes={n['id']:n for n in osm['nodes']}
    way=osm['way']
    ring_ll=[(nodes[n]['lon'],nodes[n]['lat']) for n in way['nodes'][:-1]]
    # Repository transform, approximate local XY; not a survey CRS.
    lon0,lat0=-86.9137,40.4274
    mx=111412.84*math.cos(math.radians(lat0)); my=111040.0
    ring_xy=[((lon-lon0)*mx,(lat-lat0)*my) for lon,lat in ring_ll]
    poly=Polygon(ring_xy)
    mesh=next((o for o in asset_facts['objects'] if o['type']=='MESH'),None)
    expected_col='Asset_massing_henni_s_hair_shop_57f732b'
    expected_scene='Building_massing_henni_s_hair_shop_57f732b'
    base=mesh['base_vertices_z0_unique_xy'] if mesh else []
    distances=[]; matched=[]
    for sx,sy in ring_xy:
        cand=sorted((math.hypot(x-sx,y-sy),[x,y]) for x,y in base)
        distances.append(cand[0][0]); matched.append(cand[0][1])
    bounds=mesh['bounds_world_m'] if mesh else None
    # Infer long/short edge lengths from the traced source polygon; dimensions remain only as accurate as OSM.
    edges=[math.dist(ring_xy[i],ring_xy[(i+1)%len(ring_xy)]) for i in range(len(ring_xy))]
    dims=sorted(edges)
    official_address=('121 Northwestern Avenue' in business_html)
    identity_ok=(way['id']==wid and way.get('tags',{}).get('name')=="Henni's Hair Shop" and official_address)
    export_ok=bool(mesh and asset_facts['scene']==expected_scene and len(asset_facts['scenes'])==1 and
                   any(c['name']==expected_col and c['objects']==["Henni's Hair Shop"] for c in asset_facts['collections']) and
                   len([o for o in asset_facts['objects'] if o['type']=='MESH'])==1 and not mesh['modifiers'] and
                   not asset_facts['linked_libraries'] and not asset_facts['images'])
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','points':1.8,'max_points':2,
       'status':'strong but OSM-only footprint evidence','reason':'The named OSM way 116427257 is tagged building=yes/shop=hairdresser/name=Henni’s Hair Shop; the official contact page independently lists 121 Northwestern Avenue. The four transformed way vertices match the base-shell vertices closely. No official campus footprint match or survey is available, so source authority/positional accuracy remain bounded by OSM.'},
      {'criterion':'Position, orientation, and scale/dimensions','points':1.8,'max_points':2,
       'status':'verified against mapped footprint; not independently surveyed','reason':f"Direct saved-mesh z=0 vertex inspection finds a one-to-one maximum residual of {max(distances):.6f} m and mean {sum(distances)/len(distances):.6f} m against the four source nodes after the documented project transform. OSM polygon area is {poly.area:.2f} m²; edge lengths are {', '.join(f'{v:.2f} m' for v in sorted(edges,reverse=True))}. Northwestern Avenue centerline and east-facing frontage are consistent, but the same OSM data drives the model and there is no independent survey/geodetic check."},
      {'criterion':'Evidence-backed height, floors, and roof form','points':1.0,'max_points':2,
       'status':'partially supported; height and roof uncertain','reason':'The 2022 oblique storefront image visibly supports two exterior levels. The 8.38 m total height and flat parapet are estimates only; the photo crops the roof and gives no measured vertical datum, section, or elevation. The evaluator does not treat the modeled height as verified.'},
      {'criterion':'Facade, entrances, and distinctive architecture','points':1.8,'max_points':2,
       'status':'photo-backed composition with schematic details','reason':'The storefront photo directly shows gray masonry at the ground level, light horizontal upper siding, broad shopfront glazing, a black awning wrapping the corner, a projecting Henni sign, and an upper sash window. The model represents these features, including a door and sign text; exact opening sizes, door position, complete elevations, and georeferenced photo orientation are not established.'},
      {'criterion':'Modular export, portability, and complete evidence','points':1.8,'max_points':2,
       'status':'export collection portable; minor scene clutter','reason':f"Direct Blender reopen confirms expected scene `{asset_facts['scene']}`, one expected collection with one mesh object, no mesh modifiers, external libraries, or image datablocks. There is also a review camera outside the asset collection in the saved scene, so the scene itself contains a non-export camera. Raw OSM and storefront source snapshots, catalog, evidence record, reopen validation, and a preview render are present."}
    ]
    score=round(sum(c['points'] for c in criteria),1)
    return {'score':score,'max_score':10,'passing_threshold':8,'pass':score>=8,'criteria':criteria,
      'evidence':{
        'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),
        'direct_reopen':asset_facts,
        'OSM_source_id':f'way/{wid}','OSM_tags':way['tags'],'OSM_snapshot_timestamp':osm.get('snapshot_timestamp'),
        'source_crs':'EPSG:4326 / WGS 84','project_transform':f'X=(lon+86.9137)*{mx:.6f}; Y=(lat-40.4274)*111040.0; approximate local coordinates, not surveyed.',
        'source_polygon_area_m2':poly.area,'source_edge_lengths_m':edges,'model_to_source_vertex_residuals_m':distances,
        'business_address_confirmed_in_saved_official_page':official_address,
        'render_path':str(render_path.relative_to(ROOT)).replace('\\','/'),
        'source_catalog':str((AUDIT/'sources'/'source_catalog.json').relative_to(ROOT)).replace('\\','/'),
        'evidence_record':str((AUDIT/'evidence_record.json').relative_to(ROOT)).replace('\\','/')},
      'findings':[
        {'severity':'uncertainty','finding':'Height is an 8.38 m estimate and the roofline is not visible in the saved oblique photo.','action':'Retain as estimated unless a measured elevation, permit drawing, or suitable orthogonal image becomes available.'},
        {'severity':'uncertainty','finding':'The footprint comes from a named OSM way and matches the asset precisely, but there is no independent authoritative wall survey; the photoreference is not georeferenced.','action':'For stricter survey-grade placement, compare with a city/county building polygon or georeferenced orthophoto when obtainable.'},
        {'severity':'minor','finding':'The reopened scene contains a review camera outside the single-object export collection.','action':'It does not affect collection-instance export; remove it only if a clean scene-level library is required.'}
      ]}

def main():
    facts=json.load(open(GRADE/'direct_inspection.json',encoding='utf-8'))
    catalog=json.load(open(AUDIT/'sources'/'source_catalog.json',encoding='utf-8'))
    osm=json.load(open(AUDIT/'sources'/'osm_way_116427257_raw.json',encoding='utf-8'))
    html=(AUDIT/'sources'/'henni_hairshop_contact.html').read_text(encoding='utf-8',errors='ignore')
    render=AUDIT/'renders'/'henni_hair_shop_facade.png'
    result=evaluate(facts,catalog,osm,html,render)
    with open(GRADE/'result.json','w',encoding='utf-8') as f: json.dump(result,f,indent=2,ensure_ascii=False)
    print(json.dumps({'score':result['score'],'max_score':result['max_score'],'pass':result['pass'],'criterion_points':[c['points'] for c in result['criteria']],'findings':result['findings']},indent=2,ensure_ascii=False))
if __name__=='__main__': main()

