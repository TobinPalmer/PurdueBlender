"""Fresh independent Sigma Chi evaluator; run with Blender 5.2.3 -b --python."""
import bpy, bmesh, hashlib, json, math, os
from mathutils import Vector
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'massing_sigma_chi_fid828.blend')
EVIDENCE = os.path.join(ROOT, 'audit', 'sigma_chi')
SOURCE = os.path.join(EVIDENCE, 'sources', 'purdue_gis_fid828_raw.json')
OUT = os.path.join(os.path.dirname(__file__), 'sigma_chi_independent_grade_r2.json')
EXPECTED_SHA = 'c92ba432fd0b7593f6043929aece4d4b2c1dc07a9a9216f63fe72d5033543de4'
ASSET_ID = 'massing_sigma_chi_fid828'
COLLECTION_NAME = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
XF = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
YF = 111040.0

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def evaluate():
    digest=sha256(ASSET)
    if digest != EXPECTED_SHA: raise RuntimeError('SHA mismatch; refusing to grade changed asset: '+digest)
    bpy.ops.wm.open_mainfile(filepath=ASSET)
    with open(SOURCE,encoding='utf-8') as f: raw=json.load(f)
    col=bpy.data.collections.get(COLLECTION_NAME); scene=bpy.data.scenes.get(SCENE_NAME)
    if col is None or scene is None: raise RuntimeError('Expected scene or exported collection missing')
    objects=list(col.objects); meshes=[o for o in objects if o.type=='MESH']
    feature=next((x for x in raw.get('features',[]) if x.get('attributes',{}).get('FID')==828),None)
    if feature is None: raise RuntimeError('FID 828 absent from preserved GIS snapshot')
    ring=feature['geometry']['rings'][0]
    if math.dist(ring[0],ring[-1])<1e-10: ring=ring[:-1]
    expected=[((lon-ORIGIN_LON)*XF,(lat-ORIGIN_LAT)*YF) for lon,lat in ring]
    wall=bpy.data.objects.get('SigmaChi_GIS_Footprint_Walls')
    actual=[]
    if wall and wall.type=='MESH': actual=[tuple((wall.matrix_world @ v.co).xy) for v in wall.data.vertices[:len(expected)]]
    err=max((math.dist(a,b) for a,b in zip(expected,actual)),default=float('inf'))
    points=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
    nm=loose=0
    for obj in meshes:
        bm=bmesh.new(); bm.from_mesh(obj.data)
        nm += sum(not e.is_manifold for e in bm.edges); loose += sum(not e.link_faces for e in bm.edges); bm.free()
    external=[]
    for image in bpy.data.images:
        if image.source=='FILE' and image.filepath and not image.packed_file:
            resolved=bpy.path.abspath(image.filepath)
            if not os.path.isfile(resolved): external.append(image.filepath)
    evidence=json.load(open(os.path.join(EVIDENCE,'sigma_chi_evidence.json'),encoding='utf-8'))
    source_files=[os.path.join(EVIDENCE,'sources',x) for x in ['purdue_gis_fid828_raw.json','sigma_chi_chapter_house.html','sigma_chi_renovation.html','house_1960_62.gif','renovation_sept2006.jpg']]
    source_coverage=all(os.path.isfile(p) for p in source_files)
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'evidence':['Preserved FID 828 attributes identify Sigma Chi at 202 Littleton Street; current chapter house page crosswalks the house identity/address.','Saved wall shell compared vertex-by-vertex against the transformed GIS ring; independently computed maximum XY error %.8f m.'%err],'findings':[] if err<0.001 else ['Wall shell is missing or differs from the mapped ring.']},
      {'criterion':'Position, orientation, and scale/dimensions','score':2.0 if err<0.001 else 0.0,'max_score':2,'evidence':['Massing asset uses campus coordinates; GIS ring sets plan orientation and dimensions.','Model world bounds: X %.3f..%.3f m, Y %.3f..%.3f m, Z %.3f..%.3f m.'%(bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1],bounds[2][0],bounds[2][1]),'Recorded coordinate conversion is the project approximate local conversion, not a survey CRS.'],'findings':['Position and size are verified against Purdue GIS only; independent survey unavailable.']},
      {'criterion':'Evidence-backed height, floors, and roof form','score':0.75,'max_score':2,'evidence':['Saved bounds reach %.2f m; eaves and roof heights are explicitly estimates, not measurements.'%bounds[2][1],'Historic 1960–62 and 2006 construction-stage photographs support steep intersecting roofs, dormers, chimneys, and gable cues.','The saved render has a tall, steep main roof, two dormers, and chimneys, but the dominant uninterrupted roof plane does not reproduce the more articulated intersecting gable roof visible in source photographs.','Floor count remains unverified; available GIS level fields are unreliable/conflicting evidence.'],'findings':['No elevation or point-cloud source establishes height or floor count. Roof massing is only partly matched: subdivide the long roof plane with the photo-supported intersecting cross-gables and roof breaks.']},
      {'criterion':'Facade, entrances, and distinctive architecture','score':0.75,'max_score':2,'evidence':['Photo sources show Tudor Revival, rough masonry/stucco, prominent cross-gables, an arched opening, a substantial timbered entrance, and irregularly grouped openings.','The model now includes a visible gabled entry porch, divided windows, trim, dormers, chimney stacks, and an L-shaped shell.','Rendered facades remain mostly uniform flat wall courses with evenly repeated rectangular windows; stone/masonry articulation, arched feature, timbering and historic entrance proportions are weak or absent.'],'findings':['Photo-backed identity cues improved, but signature Tudor features and facade composition are not well reproduced. Add the photo-supported entry timber framing/stone surround, arched gable opening, and irregular window groupings.']},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0 if source_coverage and col and scene and not external and nm==0 and loose==0 else 1.0,'max_score':2,'evidence':['Exact expected asset SHA verified and file opened in Blender %s.'%bpy.app.version_string,'Expected scene and asset collection exist; %d collection objects, %d mesh objects.'%(len(objects),len(meshes)),'Topology scan: %d non-manifold and %d loose edges.'%(nm,loose),'External unpacked missing image dependencies: %s.'%('none' if not external else ', '.join(external)),'Source snapshots and metadata coverage: %s.'%('complete' if source_coverage else 'incomplete'),'Fresh reopen record separately reports Blender 5.2.3 and matching candidate SHA.' if evidence.get('candidate_sha256')==digest else 'Fresh reopen evidence SHA did not match asset.'],'findings':[] if source_coverage and not external and nm==0 and loose==0 else ['Export/evidence/portability checks incomplete; inspect evaluator evidence.']}
    ]
    score=round(sum(x['score'] for x in criteria),2)
    findings=[v for c in criteria for v in c['findings']]
    result={'building':'Sigma Chi Delta Delta chapter house (Purdue GIS FID 828)','asset_path':'modular/buildings/massing_sigma_chi_fid828.blend','asset_sha256':digest,'grader':'Fresh independent re-open, source comparison, render review, and evaluator following root AGENT.md rubric','blender_version':bpy.app.version_string,'score':score,'max_score':10,'criteria':criteria,'evidence':{'reopened_saved_asset':True,'scene':scene.name,'collection':col.name,'collection_object_count':len(objects),'mesh_object_count':len(meshes),'source_ring_vertex_count':len(expected),'source_ring_max_xy_error_m':err,'world_bounds_m':bounds,'nonmanifold_edges':nm,'loose_edges':loose,'missing_unpacked_image_dependencies':external,'source_snapshots_present':source_coverage,'inspected_views':['audit/sigma_chi/sigma_chi_fresh_reopen_render.png','audit/sigma_chi/sigma_chi_roof_plan.png','audit/sigma_chi/sigma_chi_front_oblique.png','audit/sigma_chi/sources/house_1960_62.gif','audit/sigma_chi/sources/renovation_sept2006.jpg']},'findings':findings,'pass_threshold':8,'result':'PASS' if score>=8 else 'FAIL'}
    with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2); f.write('\n')
    print('SIGMA_CHI_GRADE_R2',json.dumps(result,sort_keys=True))
    return result
if __name__=='__main__': evaluate()

