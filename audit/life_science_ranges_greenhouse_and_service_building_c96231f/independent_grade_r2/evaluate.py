import ast,json,math
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
AUDIT=ROOT/'audit'/'life_science_ranges_greenhouse_and_service_building_c96231f'
BUILDER=ROOT/'modular'/'buildings'/'build_massing_life_science_ranges_greenhouse_and_service_building_c96231f.py'
GIS=AUDIT/'sources'/'purdue_gis_fid915.geojson'
PROBE=HERE/'fresh_open_probe.json'
EXPECTED='B90ADA781E76E8C7C3A08B59D95A28CD97CFA763C59D09278DDDA99781F0707E'

def recompute_overlay_metrics():
    tree=ast.parse(BUILDER.read_text(encoding='utf-8'))
    wanted={'RANGE_ROWS','SERVICE_PIXELS','IMAGE_BBOX','IMAGE_SIZE','GEO_ORIGIN'}
    cfg={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for t in node.targets:
                if isinstance(t,ast.Name) and t.id in wanted: cfg[t.id]=ast.literal_eval(node.value)
    assert set(cfg)==wanted
    west,south,east,north=cfg['IMAGE_BBOX']; iw,ih=cfg['IMAGE_SIZE']; lat0,lon0=cfg['GEO_ORIGIN']
    def ll(lon,lat): return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)
    def px(x,y): return ll(west+x/iw*(east-west),north-y/ih*(north-south))
    f=json.loads(GIS.read_text(encoding='utf-8'))['features'][0]
    assert f['properties']['FID']==915 and f['properties']['BLDG_ABBR']=='LSR'
    rings=f['geometry']['coordinates']
    allp=[ll(lon,lat) for r in rings for lon,lat,*_ in r]
    origin=((min(x for x,y in allp)+max(x for x,y in allp))/2,(min(y for x,y in allp)+max(y for x,y in allp))/2)
    local_rings=[[(x-origin[0],y-origin[1]) for x,y in [ll(lon,lat) for lon,lat,*_ in r]] for r in rings]
    gis=Polygon(local_rings[0],local_rings[1:])
    if not gis.is_valid: gis=gis.buffer(0)
    polys=[]
    for row in cfg['RANGE_ROWS']:
        x1,y1,x2,y2=row['pixels']; coords=[px(x1,y1),px(x2,y1),px(x2,y2),px(x1,y2)]
        polys.append(Polygon([(x-origin[0],y-origin[1]) for x,y in coords]))
    x1,y1,x2,y2=cfg['SERVICE_PIXELS']; coords=[px(x1,y1),px(x2,y1),px(x2,y2),px(x1,y2)]
    polys.append(Polygon([(x-origin[0],y-origin[1]) for x,y in coords]))
    cand=unary_union(polys); inter=cand.intersection(gis).area; union=cand.union(gis).area
    return {'feature_id':915,'building_abbr':'LSR','polygon_count':len(polys),'gis_ring_count':len(rings),'placement_origin_xy_m':list(origin),'candidate_area_m2':cand.area,'gis_area_m2':gis.area,'intersection_m2':inter,'union_m2':union,'iou':inter/union,'candidate_bounds_local_m':[[cand.bounds[0],cand.bounds[2]],[cand.bounds[1],cand.bounds[3]]],'gis_bounds_local_m':[[gis.bounds[0],gis.bounds[2]],[gis.bounds[1],gis.bounds[3]]]}

def evaluate(probe,metrics,evidence):
    criteria={
      'correct_identity_and_source_backed_footprint':{'score':2.0,'max_score':2.0,'evidence':[
        'Official Purdue GIS FID 915 names the feature Life Science Ranges (BLDG_ABBR LSR), address 180 S Russell Street; its saved geometry lies over the greenhouse rows and west service wing.',
        'The Purdue 2022 board approval packet documents the LSR phenotyping greenhouse project and site relationship; Purdue College of Agriculture 2026 article/photos show the greenhouse facility and operations.',
        f"Independent GIS overlay recomputation gives candidate/GIS IoU {metrics['iou']:.4f} using the seven greenhouse row footprints plus service wing from builder literals and the preserved GIS inner ring."
      ],'findings':['The candidate is correctly associated with the Life Science Ranges greenhouse complex; dimensions of individual roof rectangles are reconstructed from current imagery.']},
      'position_orientation_scale_and_dimensions':{'score':1.6,'max_score':2.0,'evidence':[
        f"Independent footprint overlay shows candidate area {metrics['candidate_area_m2']:.1f} m² vs GIS polygon {metrics['gis_area_m2']:.1f} m², IoU {metrics['iou']:.4f}; candidate bounds agree closely with the GIS envelope and the row axes match the aerial.",
        f"Fresh-open Blender bounds are X {probe['bounds_m']['min'][0]:.3f} to {probe['bounds_m']['max'][0]:.3f} m, Y {probe['bounds_m']['min'][1]:.3f} to {probe['bounds_m']['max'][1]:.3f} m, with Z 0 to {probe['bounds_m']['max'][2]:.3f} m; proposed origin is {metrics['placement_origin_xy_m']} m from the GIS envelope midpoint.",
        'Manifest still describes the previous massing bounds and identity transform in campus coordinates; the new local-coordinate candidate has not been checked in the master placement instance.'
      ],'findings':['Tobin should reconcile the current local-coordinate asset with the master manifest/placement before considering the campus placement verified. Candidate geometry overlay is good but not exact (IoU about 0.876), and direct master-instance position is still unverified.']},
      'evidence_backed_height_floors_and_roof_form':{'score':1.2,'max_score':2.0,'evidence':[
        'Purdue GIS records NUM_LEVELS=2 and CountOfFLO=2, but raw Extrution=12 and Elevation=620.1 have no defined vertical units or datum; the builder explicitly avoids interpreting them as measured height.',
        'Photographic and aerial evidence supports repeated pitched multi-span glass greenhouse roofs and a low service wing, consistent with the model’s broad roof form.',
        'Fresh-open custom properties label 3.65 m greenhouse eaves, 5.95 m ridges, 6.8 m service wing, and 7.875 m overall bound as estimates; no dimensioned as-built section/elevation was found.'
      ],'findings':['The height treatment is honest and properly qualified, but the numerical heights and precise roof profile remain unmeasured estimates.']},
      'facade_entrances_distinctive_features_and_interior':{'score':1.7,'max_score':2.0,'evidence':[
        'Exterior and roof views show seven greenhouse groups with low-iron glazing, repeated aluminum framing/mullions, pitched multi-span roofs and a distinct brick/service wing with curtain wall, service doors, vents, HVAC, sign and drainage.',
        'The interior view includes research benches/trays, modeled plants, LED lighting and a phenotyping conveyor; the 2026 Purdue article/photos support the conveyor, LED/humidity technology and brick-backed HVAC context.',
        'Photo geometry and interior object positions are illustrative because the source photos are unreferenced and no as-built plan/elevation dimension set was found.'
      ],'findings':['The model is visually legible and source-informed; exact service-facade dimensions, greenhouse bay sizes and interior layout remain reconstruction.']},
      'modular_export_portability_and_complete_evidence':{'score':1.6,'max_score':2.0,'evidence':[
        f"The exact candidate hash is {probe['sha256']}, matching the requested revision. Fresh Blender 5.2.3 open found scene {probe['scene']} and expected asset collection {probe['collection']} with {probe['object_count']} objects, {probe['mesh_count']} meshes and {probe['material_count']} used materials.",
        f"No mesh lacks a material; no external unpacked images are present. The builder uses procedural materials and a stable asset path/collection name.",
        'The source provenance packet now records provider, exact URL, retrieval/source dates, CRS, measurement method and uncertainty for GIS, imagery, Purdue page/article photos and 2022 board material; the candidate overlay and IoU reproduction method are saved.',
        'The manifest remains stale for this candidate revision (old world-space bounds, identity placement and massing kind), so project-level portability/instance loading still needs the master owner to reconcile.'
      ],'findings':['Asset-level save/reopen and source documentation pass; update/check project metadata and the master instance before calling the library fully integrated.']}
    }
    score=round(sum(c['score'] for c in criteria.values()),2)
    findings=[]
    for c in criteria.values(): findings.extend(c['findings'])
    return {'building_id':'massing_life_science_ranges_greenhouse_and_service_building_c96231f','reviewer':'Independent subagent; fresh-open Blender inspection and independently recomputed GIS/candidate footprint metrics','candidate_sha256':probe['sha256'],'candidate_sha256_matches_requested':probe['sha256']==EXPECTED,'score':score,'max_score':10.0,'threshold':8.0,'status':'PASS' if score>=8.0 else 'NEEDS_REFINEMENT','criteria':criteria,'findings':findings,'measurements':metrics,'fresh_open':probe,'evidence':['audit/life_science_ranges_greenhouse_and_service_building_c96231f/source_provenance.json','audit/life_science_ranges_greenhouse_and_service_building_c96231f/candidate_gis_overlay_metrics.json (independent recomputation in this evaluator)','audit/life_science_ranges_greenhouse_and_service_building_c96231f/fresh_open_validation.json','audit/life_science_ranges_greenhouse_and_service_building_c96231f/previews/candidate_gis_footprint_overlay.png','audit/life_science_ranges_greenhouse_and_service_building_c96231f/previews/exterior_oblique.png','audit/life_science_ranges_greenhouse_and_service_building_c96231f/previews/roof_plan.png','audit/life_science_ranges_greenhouse_and_service_building_c96231f/previews/interior_research_bench.png'],'limitations':['Master integration and placement marker were not changed or validated by this review; manifest still reflects superseded massing bounds/identity transform.','No measured vertical dimensions or complete as-built architectural plan were found.']}

probe=json.loads(PROBE.read_text(encoding='utf-8'))
metrics=recompute_overlay_metrics()
evidence=json.loads((AUDIT/'source_provenance.json').read_text(encoding='utf-8'))
assert probe['sha256']==EXPECTED
assert probe['scene']=='Building_massing_life_science_ranges_greenhouse_and_service_building_c96231f'
assert probe['collection']=='Asset_massing_life_science_ranges_greenhouse_and_service_building_c96231f'
assert probe['object_count']>0 and probe['mesh_count']>0 and not probe['unpacked_external_images']
assert metrics['feature_id']==915 and metrics['iou']>0.87
result=evaluate(probe,metrics,evidence)
(HERE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
lines=['# Independent re-grade — Life Science Ranges Greenhouse and Service Building','',f"**Score: {result['score']:.2f}/10 — {result['status'].replace('_',' ').lower()}.** Passing threshold: 8.0/10.",'','| Criterion | Score | Independent assessment |','| --- | ---: | --- |']
for k,c in result['criteria'].items(): lines.append(f"| {k.replace('_',' ')} | {c['score']:.2f}/2 | {' '.join(c['evidence'][:2])} |")
lines+=['','## Findings','']
for i,f in enumerate(result['findings'],1): lines.append(f'{i}. {f}')
lines+=['','## Limits','']
for f in result['limitations']: lines.append(f'- {f}')
(HERE/'grade_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(HERE/'candidate_gis_metrics_independent.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps({'score':result['score'],'status':result['status'],'criteria':{k:v['score'] for k,v in result['criteria'].items()},'iou':metrics['iou'],'candidate_sha256':probe['sha256'],'result':str(HERE/'result.json'),'report':str(HERE/'grade_report.md')},indent=2))
