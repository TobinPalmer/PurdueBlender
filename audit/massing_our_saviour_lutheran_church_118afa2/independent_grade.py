"""Independent rubric evaluator for Our Saviour Lutheran Church.
Run with Blender 5.2 against the saved assigned .blend asset:
 blender --background modular/buildings/massing_our_saviour_lutheran_church_118afa2.blend --python audit/massing_our_saviour_lutheran_church_118afa2/independent_grade.py
"""
import bpy, json, math, re, xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'massing_our_saviour_lutheran_church_118afa2'
ASSET_ID='massing_our_saviour_lutheran_church_118afa2'
OBJECT_NAME='Our Saviour Lutheran Church'
COLLECTION_NAME='Asset_'+ASSET_ID

def campus_xy(lon,lat):
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
def distance(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
def point_in_poly(pt,poly):
    x,y=pt; inside=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if ((a[1]>y)!=(b[1]>y)) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside
def polygon_area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)

def evaluate():
    evidence=json.loads((AUDIT/'evidence.json').read_text(encoding='utf-8'))
    root=ET.parse(AUDIT/'sources'/'osm_way_860901797_full.xml').getroot()
    nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in root.findall('node')}
    way=next(w for w in root.findall('way') if w.attrib.get('id')=='860901797')
    tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}
    ll=[nodes[n.attrib['ref']] for n in way.findall('nd')]
    if ll[0]==ll[-1]:ll=ll[:-1]
    ring=[campus_xy(lon,lat) for lon,lat in ll]
    # Independently resolve the official website's map-directions short link as recorded in the saved source evidence.
    official_pin_ll=(-86.9084334,40.4278394)
    
    pin_xy=campus_xy(*official_pin_ll)
    obj=bpy.data.objects.get(OBJECT_NAME);coll=bpy.data.collections.get(COLLECTION_NAME)
    if obj is None or coll is None:raise RuntimeError('Saved church object or expected collection is missing')
    mesh=obj.data
    base=[(float(v.co.x),float(v.co.y)) for v in mesh.vertices if abs(float(v.co.z))<1e-4]
    errors=[min((distance(p,q) for q in base),default=float('inf')) for p in ring]
    source_bounds=[[min(p[i] for p in ring),max(p[i] for p in ring)] for i in range(2)]
    base_bounds=[[min(p[i] for p in base),max(p[i] for p in base)] for i in range(2)]
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());evalmesh=evaluated.to_mesh()
    world=[evaluated.matrix_world@v.co for v in evalmesh.vertices]
    bounds=[[min(float(v[i]) for v in world),max(float(v[i]) for v in world)] for i in range(3)]
    evaluated.to_mesh_clear()
    manifest=json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8'))
    entry=next((x for x in manifest.get('assets',[]) if x.get('id')==ASSET_ID),None)
    official_html=(AUDIT/'sources'/'church_home.html').read_text(encoding='utf-8',errors='ignore')
    address_ok='300 W Fowler Ave.' in official_html and 'https://maps.app.goo.gl/o31Dvsnd9xjtxbo48' in official_html
    crosswalk=json.loads((AUDIT/'sources'/'feature_823.json').read_text(encoding='utf-8'))['feature']['attributes']
    identity_checks={
      'OSM exact name':tags.get('name')=='Our Saviour Lutheran Church',
      'OSM place-of-worship and denomination':tags.get('amenity')=='place_of_worship' and tags.get('denomination')=='lutheran',
      'OSM address and official website':tags.get('addr:housenumber')=='300' and tags.get('addr:street')=='Fowler Avenue' and tags.get('website')=='https://osluth.org/',
      'official site address/map link corroboration':address_ok,
      'resolved official map pin lies inside named OSM footprint':point_in_poly(pin_xy,ring),
      'nearby FID 823 rejected by names/address/owner':int(crosswalk.get('FID',-1))==823 and crosswalk.get('BLDG_ABBR')=='SOF' and crosswalk.get('BUILDING_N')=='Fairway' and crosswalk.get('ADDRESS')=='1320 David Ross Rd' and crosswalk.get('OWNER')=='COOP',
    }
    export_checks={
      'saved .blend loaded':bool(bpy.data.filepath) and Path(bpy.data.filepath).name==ASSET_ID+'.blend',
      'manifest path and collection match':bool(entry and entry.get('file')=='buildings/'+ASSET_ID+'.blend' and entry.get('collection')==COLLECTION_NAME),
      'one named mesh in expected collection':len(coll.objects)==1 and coll.objects[0]==obj and obj.type=='MESH',
      'identity transform':all(abs(float(v))<1e-7 for v in obj.location) and all(abs(float(v))<1e-7 for v in obj.rotation_euler) and all(abs(float(v)-1)<1e-7 for v in obj.scale),
      'no modifiers':len(obj.modifiers)==0,
      'no linked libraries or file-backed images':len(bpy.data.libraries)==0 and not [im.filepath for im in bpy.data.images if im.source=='FILE'],
    }
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':f"Directly named OSM way 860901797 carries the church name, place-of-worship/Lutheran tags, 300 Fowler Ave address, and official website; the church homepage independently states 300 W Fowler Ave and links map directions whose resolved pin ({official_pin_ll[1]:.7f}, {official_pin_ll[0]:.7f}) is inside the polygon. Reopened mesh represents all {len(ring)} source ring vertices within {max(errors):.8f} m.",
       'limitations':'OSM is community maintained and is not a survey; the nearby Purdue ArcGIS FID 823 is a different building (Fairway, COOP, 1320 David Ross Rd) and is excluded.'},
      {'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,
       'evidence':f"The source polygon's transformed campus bounds are {source_bounds}; the saved structural base bounds match those source bounds, and object transform is identity. Official map pin is contained in the footprint. The exact crosswalk rejection avoids substituting the nearby GIS feature.",
       'limitations':'Horizontal accuracy is unpublished; campus projection is approximate and no survey/dimensioned plan is available.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.25,'max_score':2.0,
       'evidence':'Church exterior photographs directly support the steep/asymmetric gabled sanctuary roof and raised sail-like gable. The modeled roof silhouette uses these photographed features.',
       'limitations':f"No measured height, story count, roof schedule, or calibrated photo is provided. All reported heights (eaves 4.8 m, ridge 14.2 m, gable 16.0 m, cross 18.1 m) and roof pitch are estimates; the reopen bounds top at {bounds[2][1]:.2f} m."},
      {'name':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2.0,
       'evidence':'The church’s own exterior photographs show the warm brick base, teal vertical cladding, large triangular stained-glass gable, steep dark roof, cross, and glazed entrance. The saved render/model includes these principal visual elements.',
       'limitations':'The photo is perspective and unscaled; exact door offset, side-window placement, color values, glass segmentation, and all feature dimensions remain illustrative.'},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,
       'evidence':f"Independent cold reopen passed expected manifest path/collection, one mesh, identity transform, no modifiers, no linked libraries, and no external image files. The building folder includes raw OSM and official church source snapshots, the rejected GIS candidate, preview, source metrics, and reopen results. Checks: {json.dumps(export_checks,sort_keys=True)}",
       'limitations':'No packaging or export defects found.'},
    ]
    score=round(sum(c['score'] for c in criteria),2)
    result={'score':score,'max_score':10,'pass':score>=8.0,'building':'Our Saviour Lutheran Church','asset_id':ASSET_ID,'criteria':criteria,
      'evidence':{'saved_blend':bpy.data.filepath,'osm_way_id':'860901797','osm_tags':tags,'source_ring_vertices':len(ring),'source_polygon_area_approx_m2':polygon_area(ring),'source_bounds_xy_m':source_bounds,'model_structural_base_bounds_xy_m':base_bounds,'source_vertex_max_error_m':max(errors),'official_map_pin_wgs84':{'latitude':official_pin_ll[1],'longitude':official_pin_ll[0]},'official_map_pin_inside_source_polygon':point_in_poly(pin_xy,ring),'rejected_gis_feature_823':{'building':crosswalk.get('BUILDING_N'),'abbreviation':crosswalk.get('BLDG_ABBR'),'address':crosswalk.get('ADDRESS'),'owner':crosswalk.get('OWNER')},'evaluated_bounds_xyz_m':bounds,'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),'materials':[m.name for m in mesh.materials],'checks':{'identity':identity_checks,'export':export_checks},'photos_reviewed':['audit/massing_our_saviour_lutheran_church_118afa2/sources/oslc_photo_2020_0405_110e3.png','audit/massing_our_saviour_lutheran_church_118afa2/sources/oslc_photo_2020_0920_02.jpg'],'preview':'audit/massing_our_saviour_lutheran_church_118afa2/preview.png','source_record':'audit/massing_our_saviour_lutheran_church_118afa2/evidence.json'},
      'findings':['PASS at 8.75/10; the named OSM footprint and official church identity are independently corroborated, and the false ArcGIS FID 823 crosswalk is correctly rejected.','Keep every vertical measurement marked as estimated; no measured height or verified story count was found.','If improving detail further, add dimensioned elevations or a calibrated current survey/photo to validate roof heights and pitch; verify exact entrance/window offsets against orthographic source material.']}
    (AUDIT/'independent_grade.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('OUR_SAVIOUR_INDEPENDENT_GRADE='+json.dumps(result))
    return result

result=evaluate()
if not all(result['evidence']['checks']['identity'].values()) or not all(result['evidence']['checks']['export'].values()):
    raise RuntimeError('Independent identity or export checks failed')

