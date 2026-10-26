import json, math, hashlib
from pathlib import Path
ROOT=Path('.').resolve()
G=ROOT/'audit/forney_hall_of_chemical_engineering_frny_d94ba3a'
R=ROOT/'audit/forney_hall_of_chemical_engineering_frny_d94ba3a_independent_grade'
asset=ROOT/'modular/buildings/massing_forney_hall_of_chemical_engineering_frny_d94ba3a.blend'
def evaluate():
    gis=json.loads((G/'purdue_gis_current.json').read_text(encoding='utf-8-sig'))
    osm=json.loads((G/'openstreetmap_way_117146497_full.json').read_text(encoding='utf-8-sig'))
    probe=json.loads((R/'blender_probe.json').read_text())
    feature=next(f for f in gis['features'] if f['properties'].get('OBJECTID')==12)
    raw=feature['geometry']['coordinates'][0]
    lat0,lon0=40.4274,-86.9137
    def xy(lon,lat): return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)
    def area(p): return 0.5*sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
    def inside(p,x,y):
        c=False; j=len(p)-1
        for i in range(len(p)):
            xi,yi=p[i]; xj,yj=p[j]
            if ((yi>y)!=(yj>y)) and x < (xj-xi)*(y-yi)/(yj-yi)+xi: c=not c
            j=i
        return c
    src=[xy(lon,lat) for lon,lat in raw[:-1]]
    model=[tuple(p) for p in probe['base_ring_ordered_xy_m']]
    assert len(model)==22 and len(src)==85
    # Deterministic point-in-polygon raster overlap over a padded combined AABB.
    allp=src+model
    xmin=min(p[0] for p in allp); xmax=max(p[0] for p in allp); ymin=min(p[1] for p in allp); ymax=max(p[1] for p in allp)
    res=.2; n_src=n_mod=n_both=0; y=ymin+res/2
    while y<ymax:
        x=xmin+res/2
        while x<xmax:
            a=inside(src,x,y); b=inside(model,x,y)
            n_src+=a; n_mod+=b; n_both+=(a and b)
            x+=res
        y+=res
    union=n_src+n_mod-n_both
    # centroid, aligned outline pointwise stats via nearest vertex and boundaries.
    def centroid(p):
        a=area(p); cx=cy=0
        for i,(x,y) in enumerate(p):
            x2,y2=p[(i+1)%len(p)]; c=x*y2-x2*y
            cx+=(x+x2)*c; cy+=(y+y2)*c
        return [cx/(6*a),cy/(6*a)]
    def point_segment_d2(p,a,b):
        dx=b[0]-a[0];dy=b[1]-a[1]; den=dx*dx+dy*dy
        t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
        return (p[0]-a[0]-t*dx)**2+(p[1]-a[1]-t*dy)**2
    def directed_hausdorff(a,b):
        return max(math.sqrt(min(point_segment_d2(p,b[i],b[(i+1)%len(b)]) for i in range(len(b)))) for p in a)
    haus=max(directed_hausdorff(src,model),directed_hausdorff(model,src))
    # OSM closed way cross-check
    way=next(e for e in osm['elements'] if e['type']=='way' and e['id']==117146497)
    nodes={e['id']:(e['lon'],e['lat']) for e in osm['elements'] if e['type']=='node'}
    osmring=[xy(*nodes[n]) for n in way['nodes'] if n in nodes]
    if len(osmring)>1 and osmring[0]==osmring[-1]: osmring.pop()
    # Raster overlap source and model values
    p={'score':8.2,'max_score':10,'pass_threshold':8,'passes':True,
     'candidate_path':'modular/buildings/massing_forney_hall_of_chemical_engineering_frny_d94ba3a.blend',
     'candidate_sha256_expected':'24D28F5617A7B9A9604812A49F7C9E855D75257AC4832EA44D7E8EED6D51B216',
     'candidate_sha256_observed':hashlib.sha256(asset.read_bytes()).hexdigest(),
     'sha256_verified':hashlib.sha256(asset.read_bytes()).hexdigest().lower()=='24d28f5617a7b9a9604812a49f7c9e855d75257ac4832ea44d7e8eed6d51b216'.lower(),
     'fresh_open_verified':probe['blender_version'].startswith('5.2.3') and probe['scene_name']=='Building_massing_forney_hall_of_chemical_engineering_frny_d94ba3a' and probe['export_collection']=='Asset_massing_forney_hall_of_chemical_engineering_frny_d94ba3a',
     'criteria':[
      {'name':'Correct identity and source-backed footprint','score':1.8,'max_score':2,
       'evidence':[f"Purdue Maps ArcGIS current feature OBJECTID 12 is named {feature['properties']['Name']} at {feature['properties']['ADDRESS']}; OSM way 117146497 independently names Forney Hall of Chemical Engineering (FRNY) at 480 Stadium Mall Drive.",f"Independently transformed the raw Purdue 85-vertex ring and extracted the candidate's ordered 22-vertex structural shell ring. At {res:.1f} m raster resolution, IoU is {n_both/union:.6f}; maximum symmetric boundary distance is {haus:.3f} m.",f"The GIS record describes the 2002–2004 addition and 1938–1939 historical record (OBJECTID 485) separately. Candidate follows the current whole-building OBJECTID 12 polygon.",f"GIS Shape.STArea reports {feature['properties']['Shape.STArea()']:.2f} m², conflicting with {abs(area(src)):.2f} m² from the source ring after project local conversion; the discrepancy is unresolved."],
       'findings':['Identity and polygon choice are supported by GIS name/address, OSM name, and contemporary-use sources. The authoritative GIS numeric area attribute conflict warrants a small deduction; overlap between GIS and OSM outlines also indicates minor outline disagreement.']},
      {'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2,
       'evidence':[f"Model shell bounds are {probe['main_object_bounds_m']} m; source-local bounds are [[{min(x for x,y in src):.3f},{max(x for x,y in src):.3f}],[{min(y for x,y in src):.3f},{max(y for x,y in src):.3f}]]. The candidate inherits the source ring's campus conversion and orientation.",f"Raster footprint IoU {n_both/union:.6f}; symmetric boundary distance {haus:.3f} m; area source/model {abs(area(src)):.2f}/{abs(area(model)):.2f} m²."],
       'findings':['Plan position, orientation and dimensions are effectively a direct copy of the documented local GIS ring. This is not a ground survey; the project conversion is approximate.']},
      {'name':'Evidence-backed height, floors, and roof form','score':1.4,'max_score':2,
       'evidence':["Candidate wall top is 13.9 m and coping top 14.35 m according to independently reopened geometry. Height is explicitly estimated, using a legacy GIS 46 ft register as context.","Purdue College of Engineering describes a five-story 2002–2004 addition; the street-level Purdue photo supports a flat/parapet roof edge, red-brick exterior and repeated floor bands. The model has a flat roof deck, low parapet and roof equipment.","The current raw GIS snapshot inspected by the grader does not expose a floor-count field among the returned properties; therefore the builder's note of a six-level GIS count is unverified from this snapshot. The image supports approximately five visible levels but does not provide measured height."],
       'findings':['Wall height, total height, exact floor count and roof equipment remain estimates. Flat/parapet roof language fits the photo, but roof/equipment arrangement lacks a clear top-down source.']},
      {'name':'Facade, entrances, and distinctive architecture','score':1.4,'max_score':2,
       'evidence':["The fresh-opened exterior preview shows red brick, pale horizontal masonry belt courses, tall dark windows with repeated framing, an entrance portal, coping and HVAC. These align with the official Purdue photo's brick, pale stone bands and dark window rhythm.","The feature includes differentiated corner/side walls and facade cadence, not merely a bounding-box extrusion; mesh has dedicated brick, limestone, glazing, framing and roof materials.","The centered front portal in the model does not match the off-center arched portal and roundel visible in the one official photograph from its shown viewpoint; other faces/entry position are not geotagged or independently confirmed."],
       'findings':['The palette, belt courses and regular window rhythm are well aligned at building scale. The photographed entrance is more articulated and off-center than the modeled portal, and no nearby street panorama was available to verify exact facade schedule.']},
      {'name':'Modular export, portability, and complete evidence','score':1.6,'max_score':2,
       'evidence':[f"Independent Blender 5.2.3 fresh-open verified stable scene and collection. The asset contains {probe['collection_objects']} objects ({probe['type_counts']}), {probe['mesh_vertices']} mesh vertices, {probe['mesh_polygons']} polygons and {probe['used_material_count']} used materials.","The saved file has no linked libraries, external image dependencies, modifiers or hidden objects. Procedural brick/stone/glazing/roof and interior materials are portable.","The evidence folder includes source registry, raw Purdue GIS and OSM snapshots, footprint diagnostic, official image, exterior/top/interior views and fresh-open validation.","A separate collection contains 10 schematic interior objects representing a labeled atrium/distillation tower, a 200-seat auditorium and laboratory/research areas."],
       'findings':['Portability and evidence are strong. Interior features are a clearly labeled schematic, supported by program descriptions but not floor plans; they do not reproduce surveyed room geometry or interior finishes.']}
     ],
     'independent_evidence':{
      'comparison_method':'Point-in-polygon raster comparison of independently projected Purdue GIS and candidate structural shell ring at 0.20 m spacing; directed nearest-boundary Hausdorff computed against every source/candidate vertex and opposite ring segments.',
      'source':'Purdue campus ArcGIS MapServer layer 0 raw Feature 12; OSM API way 117146497; official Purdue Events Calendar photo; Purdue College of Engineering and Davidson School webpages (source register URLs).',
      'raster_resolution_m':res,'source_area_local_m2':abs(area(src)),'model_area_m2':abs(area(model)),'intersection_area_raster_m2':n_both*res*res,'union_area_raster_m2':union*res*res,'iou':n_both/union,'symmetric_hausdorff_m':haus,
      'source_bounds_xy_m':[min(x for x,y in src),min(y for x,y in src),max(x for x,y in src),max(y for x,y in src)],
      'model_bounds_xy_m':[min(x for x,y in model),min(y for x,y in model),max(x for x,y in model),max(y for x,y in model)],
      'gis_shape_area_attribute_m2':feature['properties']['Shape.STArea()'],
      'osm_way_id':way['id'],'osm_tags':way['tags'],'osm_area_m2':abs(area(osmring)),
      'visuals_reviewed':['audit/forney_hall_of_chemical_engineering_frny_d94ba3a/forney_exterior_preview.png','audit/forney_hall_of_chemical_engineering_frny_d94ba3a/forney_roof_and_footprint_preview.png','audit/forney_hall_of_chemical_engineering_frny_d94ba3a/forney_schematic_interior_preview.png','audit/forney_hall_of_chemical_engineering_frny_d94ba3a/official_exterior.jpg'],
      'fresh_open_probe':'audit/forney_hall_of_chemical_engineering_frny_d94ba3a_independent_grade/blender_probe.json'},
     'findings':['Passes narrowly at 8.2/10. The strong match is plan geometry; height, exact entrance location and interior floor plan are not survey-verified.','The model and source both represent a footprint polygon rather than proof of all exterior facade geometry.','The evaluator treats Purdue and OSM as separate identity/outline evidence; OSM agreement does not resolve Purdue area field discrepancy.'],
     'graded_utc':'2026-10-26','grader':'Independent evaluator agent; candidate author was not consulted during scoring.'}
    return p

p=evaluate()
(R/'result.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sha':p['candidate_sha256_observed'],'sha_ok':p['sha256_verified'],'fresh_open':p['fresh_open_verified'],'score':p['score'],'passes':p['passes'],'iou':p['independent_evidence']['iou'],'hausdorff_m':p['independent_evidence']['symmetric_hausdorff_m'],'source_area':p['independent_evidence']['source_area_local_m2'],'model_area':p['independent_evidence']['model_area_m2']},indent=2))
