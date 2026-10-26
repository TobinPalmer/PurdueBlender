import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd(); MASTER=ROOT/'purdue_campus_master.blend'; MOD=ROOT/'modular'; MAN=json.loads((MOD/'manifest.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(MASTER)); scene=bpy.context.scene; root=scene.collection
pgid='massing_purdue_graduate_student_center_af9c5c7'; garageid='massing_northwestern_parking_garage_979f1a2'; pg=next(a for a in MAN['assets'] if a['id']==pgid); gr=next(a for a in MAN['assets'] if a['id']==garageid)
marker=bpy.data.objects.get('Placement_'+pgid); ov=bpy.data.collections.get('MasterOverride_NorthwesternParkingGarage_PGSC'); gsrc=bpy.data.collections.get(gr['collection']); errors=[]
if pg.get('kind')!='detailed':errors.append('PGSC manifest kind is not detailed')
if marker is None or marker.instance_collection is None:errors.append('PGSC placement marker missing')
else:
 if marker.instance_collection.name!=pg['collection']:errors.append('PGSC marker links wrong collection')
 if any(abs(float(marker.location[i])-float(pg['placement_origin_xy_m'][i]))>0.001 for i in range(2)):errors.append('PGSC marker XY does not match manifest')
 if marker.instance_type!='COLLECTION':errors.append('PGSC marker is not collection instance')
if ov is None or ov not in list(root.children):errors.append('Garage master override collection not root-linked')
if gsrc is not None and gsrc in list(root.children):errors.append('Uncut garage source collection still root-linked')
obj=bpy.data.objects.get('Northwestern Parking Garage — master PGSC cutout proxy')
if obj is None:errors.append('Garage cutout proxy object missing')
else:
 bm=bmesh.new();bm.from_mesh(obj.data);bm.normal_update();nonman=sum(not e.is_manifold for e in bm.edges);boundary=sum(e.is_boundary for e in bm.edges);bm.free()
 if nonman or boundary:errors.append(f'Garage proxy not watertight: {nonman}/{boundary}')
 points=[]
 if pg.get('local_bounds_m') and marker:
  for objp in marker.instance_collection.all_objects:
   if objp.type not in {'MESH','CURVE','FONT'}:continue
   # Current PGSC asset collection objects are root-level local geometry.
   for corner in objp.bound_box:points.append(marker.matrix_world @ objp.matrix_local @ Vector(corner))
 if points:
  actual=[[min(float(p[i]) for p in points),max(float(p[i]) for p in points)] for i in range(3)]
  expected=pg['bounds_world_m'];err=max(abs(actual[i][j]-expected[i][j]) for i in range(3) for j in range(2))
  if err>0.01:errors.append(f'PGSC world bounds mismatch {err}')
 # Test a representative point inside the GIS PGSC footprint; the cutout roof
 # should be above the 3.65 m PGSC roof and no garage surface may occur below.
 world=Vector((153.0099342,261.436409, -0.5)); direction=Vector((0,0,1)); inv=obj.matrix_world.inverted(); origin=inv@world; local_dir=(inv.to_3x3()@direction).normalized(); hit,loc,norm,fi=obj.ray_cast(origin,local_dir,distance=20)
 if not hit or loc.z<4.45:errors.append(f'Garage cutout clearance ray did not pass PGSC volume: hit={hit}, local_z={loc.z if hit else None}')
sha=hashlib.sha256(MASTER.read_bytes()).hexdigest();res={'status':'PASS' if not errors else 'FAIL','master_sha256':sha,'scene':scene.name,'scene_object_count':len(scene.objects),'manifest_detailed_count':MAN.get('detailed_asset_count'),'placement_marker_count':sum(o.name.startswith('Placement_') for o in scene.objects),'pgsc':{'id':pgid,'kind':pg.get('kind'),'placement_origin_xy_m':pg.get('placement_origin_xy_m'),'bounds_world_m':pg.get('bounds_world_m'),'actual_bounds_world_m':[[round(float(p[i]),6) for p in (min(points,key=lambda x:x[i]),max(points,key=lambda x:x[i]))] for i in range(0)] if False else None},'garage_override':{'collection':ov.name if ov else None,'nonmanifold_edges':nonman if obj else None,'boundary_edges':boundary if obj else None,'clearance_ray_hit':bool(hit) if obj else None,'clearance_roof_z_m':float(loc.z) if obj and hit else None},'errors':errors}
if points:res['pgsc']['actual_bounds_world_m']=[[min(float(p[i]) for p in points),max(float(p[i]) for p in points)] for i in range(3)]
(ROOT/'audit/master_sync_pgsc_2026-10-26.json').write_text(json.dumps(res,indent=2),encoding='utf-8');print(json.dumps(res,indent=2))
if errors:raise RuntimeError('; '.join(errors))
