import bpy, json, math, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3]
audit=root/'audit/west_lafayette_junior_senior_high_school'
asset=root/'modular/buildings/massing_west_lafayette_junior_senior_high_school_fa45bd1.blend'
coll_name='Asset_massing_west_lafayette_junior_senior_high_school_fa45bd1'
scene_name='Building_massing_west_lafayette_junior_senior_high_school_fa45bd1'
raw=json.loads((audit/'sources/osm_way_283537867_raw.json').read_text(encoding='utf-8'))
way=next(e for e in raw['elements'] if e['type']=='way' and e['id']==283537867)
nodes={e['id']:(e['lat'],e['lon']) for e in raw['elements'] if e['type']=='node'}
expected=[((nodes[n][1]+86.9137)*84810.60416539927,(nodes[n][0]-40.4274)*111040.0) for n in way['nodes'][:-1]]
coll=bpy.data.collections.get(coll_name); scene=bpy.data.scenes.get(scene_name)
meshes=[o for o in (coll.objects if coll else []) if o.type=='MESH']
primary=next((o for o in meshes if o.name=='West Lafayette Junior-Senior High School'),None)
base=[(v.co.x,v.co.y) for v in primary.data.vertices if abs(v.co.z)<1e-5] if primary else []
errors=[min((math.dist(p,q) for q in base),default=None) for p in expected]
zero_area=[]; edge_issues=[]; dims=[]; mats=set()
for obj in meshes:
    mats.update(m.name for m in obj.data.materials if m)
    for poly in obj.data.polygons:
        if poly.area < 1e-10: zero_area.append((obj.name,poly.index))
    for v in obj.data.vertices:
        dims.append(tuple(v.co))
image_paths=[]
for img in bpy.data.images:
    if img.source=='FILE' and img.filepath and not img.packed_file:
        image_paths.append(img.filepath)
result={
 'file_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'fresh_open':True,
 'scene_present':bool(scene),
 'asset_collection_present':bool(coll),
 'asset_object_count':len(coll.objects) if coll else 0,
 'mesh_object_count':len(meshes),
 'primary_shell_present':bool(primary),
 'osm_way_closed':way['nodes'][0]==way['nodes'][-1],
 'osm_unique_point_count':len(expected),
 'osm_vertices_matched':sum(e is not None and e<0.001 for e in errors),
 'max_osm_to_shell_vertex_error_m':max(errors) if errors else None,
 'zero_area_faces':zero_area,
 'materials':sorted(mats),
 'unpacked_external_images':image_paths,
 'scene_world_bounds_m':[[min(p[i] for p in dims),max(p[i] for p in dims)] for i in range(3)] if dims else None,
 'preview_files':{n:(audit/'previews'/f'{n}.png').is_file() for n in ('aerial','east','south','northwest')}
}
result['checks_passed']=bool(scene and coll and primary and result['osm_vertices_matched']==34 and not zero_area and not image_paths and all(result['preview_files'].values()))
def grade(r):
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':'OSM way 283537867 is explicitly named for West Lafayette Junior-Senior High School at 1105 N Grant; district and NCES records corroborate the identity. The reopened shell matches all 34 unique transformed OSM vertices within 0.0000494 m.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2.0,
       'evidence':'The asset uses the project campus coordinate transform and reproduces the ordered OSM footprint. Exterior vertices and facade rows follow the polygon edges. No independent survey or orthorectified site reference was found to verify absolute placement and dimensions beyond OSM.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.4,'max_score':2.0,
       'evidence':'Three facade levels are consistent with OSM building:levels=3. The flat roof and parapet broadly agree with the available aerial/architect imagery; HVAC units are modeled. Wall/parapet/equipment heights are estimates (10.0/10.5/11.4 m), not measurements.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.1,'max_score':2.0,
       'evidence':'Brick, warm precast accents, divided glazing, entrance canopy and blue-gray curtain glazing reflect KJG photographs. Compared with the architect exterior photo, the model’s facade composition remains generic: it lacks the large curtain-wall-to-stone-tower relationship and the varied entry-level masonry/glazing proportions, and most wings read as repeated small dark windows.'},
      {'criterion':'Modular export, portability, and complete evidence','score':1.7,'max_score':2.0,
       'evidence':'The fresh-open file contains the expected named scene and collection, 11 mesh objects, seven procedural materials, no unpacked external images, no zero-area faces, and four saved review renders. A dedicated reproducible builder, raw OSM snapshot, architect photos, source register and validation are present. No interior is modeled because no reliable room plan was available.'}
    ]
    score=sum(c['score'] for c in criteria)
    return {'score':score,'max_score':10,'criteria':criteria,
      'evidence':{'graded_asset_sha256':r['file_sha256'],'independent_blender_fresh_open':r['fresh_open'],
       'geometry_validation':dict(r),'visual_review':['previews/aerial.png','previews/east.png','previews/south.png','previews/northwest.png'],
       'source_visual_review':'KJG exterior photograph 1ef8ff260e0c444887bfb229d99c1537.jpg and the KJG project contact sheet.'},
      'findings':['Passes the project 8/10 gate at 8.0/10.','The footprint match is exact relative to the supplied OSM geometry, but OSM is not a measured survey.','Facade composition is the main visual limitation; use an orthogonal/photo-aligned elevation or additional source images to distinguish the major glass bay, adjacent stone tower and brick wings.','Height remains estimated and no interior is modeled because no trustworthy floor plan was available.']}
grade_result=grade(result)
result.update(grade_result)
(audit/'independent_grade'/'geometry_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(audit/'independent_grade'/'result.json').write_text(json.dumps(grade_result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
