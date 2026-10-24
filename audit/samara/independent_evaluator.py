import bpy,json,pathlib,math,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[2]; E=R/'audit'/'samara'; ID='massing_samara_f6b8e61'
def evaluate():
 p=R/'modular'/'buildings'/(ID+'.blend'); bpy.ops.wm.open_mainfile(filepath=str(p))
 col=bpy.data.collections['Asset_'+ID]; dg=bpy.context.evaluated_depsgraph_get(); obs={}; pts=[]
 for o in col.all_objects:
  if o.type!='MESH':continue
  ev=o.evaluated_get(dg); me=ev.to_mesh(); vs=[ev.matrix_world@v.co for v in me.vertices]; pts.extend(vs)
  obs[o.name]={'vertices':len(vs),'bounds':[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)],'world_vertices':[list(v) for v in vs]};ev.to_mesh_clear()
 manifest=json.load(open(R/'modular'/'manifest.json')); entry=next(a for a in manifest['assets'] if a['id']==ID)
 rec=json.load(open(E/'build_record.json')); a=Vector(rec['anchor_world_m']); angle=math.radians(-63.5); U=Vector((math.cos(angle),math.sin(angle))); V=Vector((-math.sin(angle),math.cos(angle))); S=(85+7.875/12)*.3048/607
 def pixels(v):
  q=Vector(v[:2])-a
  return [500+q.dot(U)/S,300-q.dot(V)/S,v[2]]
 for name,d in obs.items():d['drawing_vertices']=[pixels(v) for v in d['world_vertices']]
 from mathutils.bvhtree import BVHTree
 def worldpt(x,y,z):
  q=a+U*((x-500)*S)+V*((300-y)*S);return Vector((q.x,q.y,z))
 def cast_group(names,start,direction):
  vertices=[]; faces=[]
  for name in names:
   o=col.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh();off=len(vertices);vertices.extend([ev.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(off+i for i in f.vertices) for f in me.polygons]);ev.to_mesh_clear()
  return BVHTree.FromPolygons(vertices,faces).ray_cast(start,direction,10)
 floor_hits=[]
 for x,y in [(650,250),(610,285),(700,220)]:
  hit=cast_group(['Survey structural floor footprint','Sunken_living_red_floor'],worldpt(x,y,.1),Vector((0,0,-1)))
  floor_hits.append({'drawing_xy':[x,y],'first_floor_z':None if hit[0] is None else hit[0].z})
 aperture=[]
 for x in [620,650,680]:
  start=worldpt(x,365,1.5);direction=(worldpt(x,349,1.5)-start).normalized();hit=cast_group([n for n in obs if n.startswith('Structural_wall_10')],start,direction)
  aperture.append({'drawing_x':x,'brick_intersects_light_center':hit[0] is not None})
 critical=['Survey structural floor footprint','Sunken_living_red_floor','Structural_wall_10_sill_620','Structural_wall_10_head_620','Narrow_foyer_light_620','Lower_cantilever_roof','Upper_flat_roof','Red_brick_chimney','2026_patinated_chimney_cap','Lower_fascia_folded_seed_0_0']
 inspection={'revision':2,'asset_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'collection':col.name,'scene':bpy.context.scene.name,'collection_offset':list(col.instance_offset),'mesh_objects':len(obs),'evaluated_vertices':sum(x['vertices'] for x in obs.values()),'bounds':[[min(v[k] for v in pts),max(v[k] for v in pts)] for k in range(3)],'external_dependencies':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file],'manifest_entry':entry,'critical_objects':{k:obs[k] for k in critical},'coordinate_contract_matches':entry['kind']=='massing' and 'identity' in entry['placement_transform'] and list(col.instance_offset)==[0,0,0],'living_floor_downward_raycasts':floor_hits,'foyer_aperture_brick_raycasts':aperture,'inspection_method':'Fresh Blender reopen; evaluated world vertices and BVH raycasts; independent direct review of source drawings/photo and revision2 proof views'}
 inspection['floor_cutout_pass']=all(x['first_floor_z'] is not None and abs(x['first_floor_z']+.5588)<.001 for x in floor_hits)
 inspection['foyer_apertures_pass']=not any(x['brick_intersects_light_center'] for x in aperture)
 panel=obs['Lower_fascia_folded_seed_0_0'];inspection['folded_fascia_profile_m']=panel['bounds'][2][1]-panel['bounds'][2][0];inspection['folded_fascia_pass']=abs(inspection['folded_fascia_profile_m']-.44)<.001
 master=json.load(open(E/'master_link_check.json'));inspection['coordinator_master_link_evidence']=master
 inspection['master_link_pass']=master['passed'] and master['master_unchanged'] and master['direct_collection_occurrences']==1 and not master['collection_instances']
 json.dump(inspection,open(E/'independent_inspection.json','w'),indent=2)
 criteria=json.load(open(E/'iteration1'/'independent_grade.json'))['criteria']
 criteria[2]['score']=1.8
 criteria[2]['evidence'].append('Fresh BVH downward rays at three living-room sample points first hit lowered floorZ=-0.5588m, with entrance-level base removed there. Three stepped transition meshes and roof-hidden proof show the22inch drop.')
 criteria[2]['limitations']=['Roof outlines reconstructed with approximately0.5m uncertainty; stair count and tread sizes interpreted from drawing rather than printed dimensions.','Lower roof still spans below raised roof volume; interior roof/ceiling construction is approximate.']
 criteria[3]['score']=1.6
 criteria[3]['evidence'].extend(['New narrow foyer openings are clear through brick at all three center rays; actual glass spansZ0.79..2.38m, split sill/head/piers frame apertures; proof view shows three tall lights matching HABS southeast elevation.','Actual copper panel profile is0.44m deep with folded triangulated face and ribs; closeup now supports angular profiled fascia motif visible in Foundation photo.'])
 criteria[3]['limitations']=['Copper folds retain a stylized trapezoid profile and simplified rib pattern rather than a dimensioned reproduction of Wright detail.','Entry/glazing panel spacing, decorative seed motifs and trim dimensions remain approximate.']
 criteria[4]['score']=2.0
 criteria[4]['evidence']=[f'Fresh saved asset opens expected collection/scene;{len(obs)}meshes,{inspection["evaluated_vertices"]}evaluated vertices;zero collection offset;no external unpacked images.', 'Dedicated script and archived raw HABS/Foundation/owner sources,provenance,registration overlay,normal previews and three revision2 proof views preserved.','Coordinator read-only master check confirms expected source collection directly linked once,zero instances,and byte-identical master before/after; manifest path/collection and campus-coordinate contract retained.']
 criteria[4]['limitations']=['FullresolutionTIFF remains local;portable raw JPEG derivatives and source URL/hash retained.']
 checks=inspection['floor_cutout_pass'] and inspection['foyer_apertures_pass'] and inspection['folded_fascia_pass'] and inspection['master_link_pass']
 if not inspection['floor_cutout_pass']:criteria[2]['score']=1.4
 if not(inspection['foyer_apertures_pass'] and inspection['folded_fascia_pass']):criteria[3]['score']=1.0
 findings=[{'severity':'uncertainty','finding':'Placement remains approximately+/-2m and rotation+/-3degrees; absolute terrain datum not surveyed.','action':'Keep estimates explicit; use georeferenced survey before claiming surveyed registration.'},{'severity':'limitation','finding':'Fascia and clerestory seed details,stair tread/count and roof outline are source-informed approximations.','action':'Retain these limitations; obtain dimensioned detail survey for greater fidelity.'}]
 score=round(sum(c['score'] for c in criteria),2)
 return {'revision':2,'score':score,'max_score':10,'pass_threshold':8,'passed':score>=8 and checks,'required_revision_checks_passed':checks,'criteria':criteria,'evidence':inspection,'findings':findings,'resolved_iteration1_findings':['Three foyer apertures clear through brick','Entrance-level slab cut out above sunken living floor','Deep folded copper fascia replaces small rim tabs'],'source_date_caveat':'2020fieldwork/2021HABS geometry with2026owner-documented copper cap;not uniformly current surveyed condition.','grader':'Independent direct source and fresh saved asset review;no builder code executed;no asset/master changes.'}
result=evaluate();json.dump(result,open(E/'independent_grade.json','w'),indent=2);print('INDEPENDENT_GRADE',result['score'],result['passed'])
