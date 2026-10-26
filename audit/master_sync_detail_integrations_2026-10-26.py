import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd();MASTER=ROOT/'purdue_campus_master.blend';MOD=ROOT/'modular';MAN=json.loads((MOD/'manifest.json').read_text(encoding='utf-8'))
IDS=['massing_purdue_fire_department_520430b','massing_purdue_drug_discovery_facility_fc72a4a','massing_purdue_center_for_regional_development_scho_a2375c9','massing_purdue_football_performance_complex_f106c29','massing_purdue_graduate_student_center_af9c5c7','massing_purdue_lutheran_ministry_5425b3c','massing_wood_street_garage_pgw_2fa056e','massing_university_book_store_717bf2c','massing_university_church_84b2a1b','massing_university_lutheran_church_20903f1','massing_wang_hall_wang_0dac5ab']
bpy.ops.wm.open_mainfile(filepath=str(MASTER));scene=bpy.context.scene;root=scene.collection;by_id={a['id']:a for a in MAN['assets']};errors=[];records=[]
def library_path(c):return Path(bpy.path.abspath(c.library.filepath)).resolve() if c.library else None
def local_matrix(o,members,cache):
 if o in cache:return cache[o]
 mat=o.matrix_local.copy()
 if o.parent in members:mat=local_matrix(o.parent,members,cache)@mat
 cache[o]=mat;return mat
for aid in IDS:
 rec=by_id[aid];name='Placement_'+aid;marker=bpy.data.objects.get(name)
 if rec.get('kind')!='detailed':errors.append(f'{aid}: manifest kind is {rec.get("kind")}')
 if marker is None or marker.instance_collection is None:errors.append(f'{aid}: placement marker missing');continue
 if marker.instance_collection.name!=rec['collection']:errors.append(f'{aid}: wrong collection {marker.instance_collection.name}')
 if library_path(marker.instance_collection)!=(MOD/rec['file']).resolve():errors.append(f'{aid}: wrong linked library')
 anchor=rec['placement_origin_xy_m'];pos=list(marker.location)
 poserr=max(abs(float(pos[i])-float(anchor[i])) for i in range(2))
 if poserr>0.001:errors.append(f'{aid}: marker position error {poserr}')
 if max(abs(float(v)) for v in marker.rotation_euler)>1e-6:errors.append(f'{aid}: nonzero marker rotation')
 if max(abs(float(marker.scale[i])-1) for i in range(3))>1e-6:errors.append(f'{aid}: nonunit scale')
 col=marker.instance_collection;members=set(col.all_objects);cache={};pts=[]
 for obj in members:
  if obj.type not in {'MESH','CURVE','FONT'}:continue
  mat=local_matrix(obj,members,cache)
  for corner in obj.bound_box:pts.append(marker.matrix_world@mat@Vector(corner))
 actual=[[min(float(p[i]) for p in pts),max(float(p[i]) for p in pts)] for i in range(3)]
 exp=rec['bounds_world_m'];berr=max(abs(actual[i][j]-exp[i][j]) for i in range(3) for j in range(2))
 if berr>0.001:errors.append(f'{aid}: exterior bounds error {berr}')
 records.append({'id':aid,'marker':name,'anchor_xy_m':pos[:2],'placement_error_m':poserr,'bounds_error_m':berr,'object_count':len(col.all_objects),'library':str(library_path(col))})
old_ids=['massing_purdue_fire_department_520430b','massing_purdue_drug_discovery_facility_fc72a4a','massing_purdue_center_for_regional_development_scho_a2375c9','massing_purdue_football_performance_complex_f106c29','massing_purdue_lutheran_ministry_5425b3c','massing_wood_street_garage_pgw_2fa056e','massing_university_book_store_717bf2c','massing_university_church_84b2a1b','massing_university_lutheran_church_20903f1','massing_wang_hall_wang_0dac5ab','massing_northwestern_parking_garage_979f1a2']
for aid in old_ids:
 rec=by_id[aid];col=bpy.data.collections.get(rec['collection'])
 if col is not None and col in list(root.children):errors.append(f'{aid}: superseded source collection still root-linked')
ov=bpy.data.collections.get('MasterOverride_NorthwesternParkingGarage_PGSC')
override=next((o for o in ov.objects if o.type=='MESH'),None) if ov else None
if ov is None or ov not in list(root.children):errors.append('PGSC garage override collection missing')
if override is None:errors.append('PGSC garage override mesh missing')
else:
 bm=bmesh.new();bm.from_mesh(override.data);bm.normal_update();nonman=sum(not e.is_manifold for e in bm.edges);boundary=sum(e.is_boundary for e in bm.edges);bm.free()
 if nonman or boundary:errors.append(f'PGSC garage override topology {nonman}/{boundary}')
 # The source library is deliberately not linked into the saved master; its
 # hash must still match the independent grader's Git LFS object probe.
 garage_file=MOD/by_id['massing_northwestern_parking_garage_979f1a2']['file']
 garage_path=MOD/garage_file
 garage_probe=json.loads((ROOT/'audit/purdue_graduate_student_center/independent_grade_master/garage_source_probe.json').read_text(encoding='utf-8'))
 source_sha=hashlib.sha256(garage_path.read_bytes()).hexdigest() if garage_path.exists() else None
 if source_sha!=garage_probe.get('head_lfs_sha256'):errors.append('Northwestern Garage source file differs from the independently recorded Git LFS object')
sha=hashlib.sha256(MASTER.read_bytes()).hexdigest();res={'status':'PASS' if not errors else 'FAIL','master_sha256':sha,'scene':scene.name,'scene_object_count':len(scene.objects),'manifest_detailed_count':MAN.get('detailed_asset_count'),'placement_marker_count':sum(o.name.startswith('Placement_') for o in scene.objects),'integrated_assets':records,'garage_override':{'collection':ov.name if ov else None,'nonmanifold_edges':nonman if override else None,'boundary_edges':boundary if override else None,'source_collection_unlinked_from_root':True,'source_asset_sha256':source_sha,'source_matches_independent_git_lfs_probe':source_sha==garage_probe.get('head_lfs_sha256')},'errors':errors}
(ROOT/'audit/master_sync_detail_integrations_2026-10-26.json').write_text(json.dumps(res,indent=2),encoding='utf-8');print(json.dumps(res,indent=2))
if errors:raise RuntimeError('; '.join(errors))
