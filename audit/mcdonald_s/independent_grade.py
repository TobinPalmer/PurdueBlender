"""Independent McDonald's massing grader. Run against the saved asset with Blender:
 blender --background modular/buildings/massing_mcdonald_s_ab77b70.blend --python audit/mcdonald_s/independent_grade.py
The evaluator reads the raw OSM way, independently measures the reopened mesh, and writes
independent_grade.json in this audit folder. Visual notes use the saved preview and raw
Esri World Imagery tiles; unsupported elevations/facade details are explicitly deducted.
"""
import json, math, xml.etree.ElementTree as ET
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'mcdonald_s'
ASSET_ID='massing_mcdonald_s_ab77b70'
OBJ_NAME="McDonald's"
COLL_NAME='Asset_'+ASSET_ID

def evaluate():
    xml=ET.parse(AUDIT/'sources'/'osm_way_256640455_full.xml').getroot()
    way=next((w for w in xml.findall('way') if w.get('id')=='256640455'),None)
    if way is None: raise RuntimeError('OSM way 256640455 missing from saved snapshot')
    tags={t.get('k'):t.get('v') for t in way.findall('tag')}
    nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in xml.findall('node')}
    ring=[nodes[nd.get('ref')] for nd in way.findall('nd')]
    if ring and ring[0]==ring[-1]: ring=ring[:-1]
    expected=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
    obj=bpy.data.objects.get(OBJ_NAME); col=bpy.data.collections.get(COLL_NAME)
    if obj is None or col is None: raise RuntimeError('Expected saved McDonald\'s object or collection missing')
    world=[obj.matrix_world@v.co for v in obj.data.vertices] if obj.type=='MESH' else []
    actual_base=[(float(p.x),float(p.y)) for p in world if abs(p.z)<1e-5]
    def d(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
    directed=lambda aa,bb:max((min(d(a,b) for b in bb) for a in aa),default=float('inf'))
    vertex_haus=max(directed(expected,actual_base),directed(actual_base,expected))
    # Verify every source structural edge against polygon faces with exactly two ground vertices.
    actual_edges=[]
    for poly in obj.data.polygons if obj.type=='MESH' else []:
        pts=[obj.matrix_world@obj.data.vertices[i].co for i in poly.vertices]
        base=[(float(p.x),float(p.y)) for p in pts if abs(p.z)<1e-5]
        if len(base)==2: actual_edges.append(base)
    def edge_err(a,b):
        return min(max(d(a[0],b[0]),d(a[1],b[1])),max(d(a[0],b[1]),d(a[1],b[0])))
    edges=[(expected[i],expected[(i+1)%len(expected)]) for i in range(len(expected))]
    edge_errors=[]; matched_wall_vertices=[]
    for e in edges:
        best=min(actual_edges,key=lambda a:edge_err(e,a),default=None)
        err=edge_err(e,best) if best else float('inf')
        edge_errors.append(err)
        if best and err<.002:
            matched_wall_vertices.extend(best)
    max_edge=max(edge_errors,default=float('inf'))
    wall_vertex_haus=max(directed(expected,matched_wall_vertices),directed(matched_wall_vertices,expected))
    source_area2=sum(expected[i][0]*expected[(i+1)%len(expected)][1]-expected[(i+1)%len(expected)][0]*expected[i][1] for i in range(len(expected)))
    lo=[min(p[i] for p in world) for i in range(3)]; hi=[max(p[i] for p in world) for i in range(3)]
    identity=tags.get('name')=="McDonald's" and tags.get('brand')=="McDonald's" and tags.get('addr:housenumber')=='605' and tags.get('addr:street')=='Stadium Avenue'
    manifest=json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8'))
    m=next(x for x in manifest['assets'] if x.get('id')==ASSET_ID)
    external=[im.filepath for im in bpy.data.images if im.source=='FILE']
    # Criterion scores weigh direct evidence rather than model appearance alone.
    criteria=[
      {'criterion':'Identity and source-backed footprint','score':2.0 if identity and len(ring)==16 and max_edge<.002 else 0.0,'max_score':2.0,
       'status':'verified with community-map accuracy limitation' if identity and len(ring)==16 and max_edge<.002 else 'fail',
       'evidence':'OSM way 256640455 explicitly tags McDonald\'s name/brand, 605 Stadium Avenue, fast-food amenity, and official store URL. Reopened model structural edges are independently compared to all source edges.',
       'metrics':{'osm_way_id':256640455,'name':tags.get('name'),'brand':tags.get('brand'),'address':f"{tags.get('addr:housenumber')} {tags.get('addr:street')}",'source_vertices':len(ring),'matched_edges':sum(e<.002 for e in edge_errors),'max_edge_error_m':max_edge,'matched_structural_wall_vertex_symmetric_hausdorff_m':wall_vertex_haus,'source_area_m2':abs(source_area2)/2}},
      {'criterion':'Position, orientation, and dimensions','score':2.0 if max_edge<.002 and len(ring)==16 else 0.0,'max_score':2.0,
       'status':'verified against OSM outline; survey limitation retained' if max_edge<.002 else 'fail',
       'evidence':'Structural perimeter coordinates, rotation, and plan dimensions independently match the georeferenced OSM ring in the manifest campus frame. Purdue GIS name inventory has no McDonald\'s record; no separate official building footprint is available.',
       'metrics':{'model_identity_transform':list(obj.location)==[0.0,0.0,0.0] and list(obj.rotation_euler)==[0.0,0.0,0.0] and list(obj.scale)==[1.0,1.0,1.0],'source_bbox_xy_m':{'min':[min(p[0] for p in expected),min(p[1] for p in expected)],'max':[max(p[0] for p in expected),max(p[1] for p in expected)]},'model_bounds_xyz_m':{'min':lo,'max':hi},'source_bbox_dimensions_m':[max(p[0] for p in expected)-min(p[0] for p in expected),max(p[1] for p in expected)-min(p[1] for p in expected)]}},
      {'criterion':'Height, floors, and roof form','score':1.0,'max_score':2.0,'status':'partly supported; height unverified',
       'evidence':'Esri aerial tiles support a low, broad roof plan. The reopened model is 4.70 m tall with a single low parapet mass, but neither OSM nor another captured source supplies measured height, floors, or roof elevation.',
       'metrics':{'model_roof_top_m':hi[2],'published_height_m':None,'published_floor_count':None,'aerial_supports_roof_plan_only':True}},
      {'criterion':'Facade, entrances, and distinctive architecture','score':0.5,'max_score':2.0,'status':'mostly illustrative',
       'evidence':'The model preview shows red/gold fascia, an arches mark, windows, door, and canopy. Store identity supports brand context only; no store-specific exterior photograph, entrance bearing, elevation, or facade measurement is present in the saved evidence. Those architectural details are therefore not source-verified.',
       'metrics':{'store_specific_facade_photo_present':False,'store_specific_elevation_present':False,'entrance_bearing_verified':False}},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0 if obj.type=='MESH' and len(col.objects)==1 and m.get('file')=='buildings/'+ASSET_ID+'.blend' and not external else 0.0,'max_score':2.0,
       'status':'pass' if obj.type=='MESH' and len(col.objects)==1 and m.get('file')=='buildings/'+ASSET_ID+'.blend' and not external else 'fail',
       'evidence':'Saved file reopens with one mesh in the expected manifest collection/path, no modifiers, no file-backed image dependencies, and source snapshots plus preview/reopen record in the dedicated audit folder.',
       'metrics':{'asset_path':bpy.data.filepath,'manifest_path':m.get('file'),'collection_object_count':len(col.objects),'object_type':obj.type,'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),'modifiers':[mod.name for mod in obj.modifiers],'external_file_images':external}}
    ]
    score=sum(c['score'] for c in criteria)
    findings=[
      f"Score {score:.1f}/10; {'PASS' if score>=8 else 'FAIL'} against the required 8/10 minimum.",
      f"Identity and 16-edge structural footprint match OSM way 256640455 within {max_edge:.6f} m; Purdue BuildingShapes has no separate named McDonald's footprint.",
      'The source set supports plan geometry and approximate flat-roof context but has no building height/floor source; 4.70 m remains an estimate.',
      'Facade, windows, entrance, fascia, and arches are illustrative. Add a current photograph or elevation for this exact 605 Stadium Avenue store and verify entrance side before claiming architectural accuracy.'
    ]
    return {'score':score,'max_score':10,'pass':score>=8,'passing_standard':8,'criteria':criteria,
       'evidence':{'asset_id':ASSET_ID,'saved_blend_reopened':bool(bpy.data.filepath),'osm_snapshot':'audit/mcdonald_s/sources/osm_way_256640455_full.xml','aerial_snapshots':['audit/mcdonald_s/sources/esri_world_imagery_tile_z20_y395324_x271135.jpg','audit/mcdonald_s/sources/esri_world_imagery_tile_z19_y197662_x135567.jpg'],'preview':'audit/mcdonald_s/preview_exterior.png','purdue_gis_name_inventory':'audit/mcdonald_s/sources/purdue_gis_building_name_inventory.json','measurement_tolerance_m':0.002},
       'findings':findings}
result=evaluate()
(AUDIT/'independent_grade.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('MCDONALDS_INDEPENDENT_GRADE='+json.dumps(result))
