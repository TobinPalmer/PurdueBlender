import bpy,bmesh,hashlib,json,math,os
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd(); EVID=ROOT/'audit/purdue_graduate_student_center'; OUT=EVID/'independent_grade_master'/'model_probe.json'
asset=ROOT/'modular/buildings/massing_purdue_graduate_student_center_af9c5c7.blend'; master=ROOT/'purdue_campus_master.blend'; asset_sha=hashlib.sha256(asset.read_bytes()).hexdigest(); gis=json.loads((EVID/'sources'/'purdue_gis_pgsc_fid526_2026-10-26.geojson').read_text(encoding='utf-8')); evidence=json.loads((EVID/'evidence.json').read_text(encoding='utf-8')); anchor=evidence['modeling_method']['placement_origin_xy_m']
asset_result={'sha256':asset_sha,'fresh_open':False,'scene':None,'collection':None,'object_count':None,'mesh_count':None,'used_material_count':None,'external_image_paths':[],'shell_footprint_vertices_local':None,'gis_vertex_count':None,'source_model_symmetric_max_vertex_error_m':None}
bpy.ops.wm.open_mainfile(filepath=str(asset)); sc=bpy.data.scenes.get('Building_massing_purdue_graduate_student_center_af9c5c7'); col=bpy.data.collections.get('Asset_massing_purdue_graduate_student_center_af9c5c7')
asset_result.update({'fresh_open':True,'scene':sc.name if sc else None,'collection':col.name if col else None,'object_count':len(list(col.all_objects)) if col else 0,'mesh_count':sum(o.type=='MESH' for o in col.all_objects) if col else 0})
used={m.name for o in col.all_objects if o.type=='MESH' for m in o.data.materials if m} if col else set();asset_result['used_material_count']=len(used)
asset_result['external_image_paths']=sorted({str(Path(i.filepath).as_posix()) for i in bpy.data.images if i.source=='FILE' and i.filepath and i.packed_file is None})
shell=bpy.data.objects.get('PGSC source-footprint brick volume (garage office portion)');gisring=gis['features'][0]['geometry']['coordinates'][0]
def xy_from_lonlat(lon,lat):return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
src=[(xy_from_lonlat(ll[0],ll[1])[0]-anchor[0],xy_from_lonlat(ll[0],ll[1])[1]-anchor[1]) for ll in gisring[:-1]]
if shell:
 model=[]
 for v in shell.data.vertices:
  co=shell.matrix_world@v.co
  if abs(float(co.z))<1e-5:
   pt=(round(float(co.x),7),round(float(co.y),7))
   if pt not in model:model.append(pt)
 distances=[min(math.dist(a,b) for b in model) for a in src] if model else []
 reverse=[min(math.dist(a,b) for b in src) for a in model] if src else []
 asset_result.update({'shell_name':shell.name,'shell_footprint_vertices_local':len(model),'gis_vertex_count':len(src),'source_to_model_max_vertex_error_m':max(distances,default=None),'model_to_source_max_vertex_error_m':max(reverse,default=None),'source_model_symmetric_max_vertex_error_m':max(distances+reverse,default=None),'shell_matrix_world':[[float(x) for x in row] for row in shell.matrix_world]})
# Now open the actual master from disk in the same fresh Blender process.
bpy.ops.wm.open_mainfile(filepath=str(master)); scene=bpy.context.scene; root=scene.collection; manifest=json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8'))
pgid='massing_purdue_graduate_student_center_af9c5c7';gid='massing_northwestern_parking_garage_979f1a2';pg=next(a for a in manifest['assets'] if a['id']==pgid); garage=next(a for a in manifest['assets'] if a['id']==gid)
marker=bpy.data.objects.get('Placement_'+pgid); markers=[o for o in scene.objects if o.name=='Placement_'+pgid]; override=bpy.data.collections.get('MasterOverride_NorthwesternParkingGarage_PGSC'); override_obj=bpy.data.objects.get('Northwestern Parking Garage — master PGSC cutout proxy'); garage_source=bpy.data.collections.get(garage['collection'])
master_result={'fresh_open':True,'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'scene':scene.name,'pgsc_marker_count':len(markers),'marker_exists':marker is not None,'marker_instance_type':marker.instance_type if marker else None,'marker_collection':marker.instance_collection.name if marker and marker.instance_collection else None,'marker_library_path':bpy.path.abspath(marker.instance_collection.library.filepath) if marker and marker.instance_collection and marker.instance_collection.library else None,'expected_library_path':str(asset.resolve()),'marker_location':list(marker.location) if marker else None,'marker_rotation':list(marker.rotation_euler) if marker else None,'marker_scale':list(marker.scale) if marker else None,'manifest_anchor':pg.get('placement_origin_xy_m'),'garage_override_root_linked':bool(override and override in list(root.children)),'source_garage_collection_root_linked':bool(garage_source and garage_source in list(root.children)),'garage_override_object_exists':override_obj is not None,'garage_override_nonmanifold_edges':None,'garage_override_boundary_edges':None,'garage_clearance_rays':[],'pgsc_world_bounds_m':None,'manifest_world_bounds_m':pg.get('bounds_world_m')}
points=[]
if marker and marker.instance_collection:
 for o in marker.instance_collection.all_objects:
  if o.type not in {'MESH','CURVE','FONT'}:continue
  if o.parent is not None:continue
  for corner in o.bound_box:points.append(marker.matrix_world@o.matrix_local@Vector(corner))
if points:master_result['pgsc_world_bounds_m']=[[min(float(p[i]) for p in points),max(float(p[i]) for p in points)] for i in range(3)]
if override_obj:
 bm=bmesh.new();bm.from_mesh(override_obj.data);bm.normal_update();master_result['garage_override_nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges);master_result['garage_override_boundary_edges']=sum(e.is_boundary for e in bm.edges);bm.free()
 inv=override_obj.matrix_world.inverted()
 for x,y in ((153.0099342,261.43640895),(150.0,260.0),(160.0,260.0),(145.0,252.0)):
  origin=inv@Vector((x,y,-0.5));direction=(inv.to_3x3()@Vector((0,0,1))).normalized();hit,loc,norm,idx=override_obj.ray_cast(origin,direction,distance=20);hit_world=override_obj.matrix_world@loc if hit else None
  master_result['garage_clearance_rays'].append({'xy_m':[x,y],'hit':hit,'hit_z_m':float(hit_world.z) if hit else None})
asset_result['expected_hash_match']=asset_sha=='f3133fc447a1d9cc29db970dd286e417ac08b9ced6cdcb07c031bba1d878b25b';master_result['expected_hash_match']=master_result['master_sha256']=='6aa50f651ad35d138d73cece4cabd0139413fb35326649ad3f7471495b85941d'
errors=[]
if not asset_result['expected_hash_match']:errors.append('asset SHA differs from graded asset')
if not asset_result['fresh_open'] or asset_result['scene']!='Building_massing_purdue_graduate_student_center_af9c5c7' or asset_result['collection']!='Asset_massing_purdue_graduate_student_center_af9c5c7':errors.append('asset scene or collection missing')
if asset_result['source_model_symmetric_max_vertex_error_m'] is None or asset_result['source_model_symmetric_max_vertex_error_m']>0.001:errors.append('structural shell does not match GIS ring within 1mm')
if asset_result['external_image_paths']:errors.append('asset has unpacked external image dependencies')
if not master_result['expected_hash_match']:errors.append('master SHA differs from opened master')
if master_result['pgsc_marker_count']!=1 or not master_result['marker_exists']:errors.append('PGSC placement marker count not exactly one')
if master_result['marker_instance_type']!='COLLECTION' or master_result['marker_collection']!=pg['collection']:errors.append('PGSC marker uses wrong collection')
if not master_result['marker_library_path'] or Path(master_result['marker_library_path']).resolve()!=asset.resolve():errors.append('PGSC marker points to wrong source file')
if not marker or any(abs(float(marker.location[i])-float(pg['placement_origin_xy_m'][i]))>0.001 for i in range(2)):errors.append('PGSC marker position differs from manifest')
if not master_result['garage_override_root_linked'] or master_result['source_garage_collection_root_linked']:errors.append('garage override/source root-link arrangement incorrect')
if master_result['garage_override_nonmanifold_edges']!=0 or master_result['garage_override_boundary_edges']!=0:errors.append('garage override not watertight')
if points and max(abs(master_result['pgsc_world_bounds_m'][i][j]-pg['bounds_world_m'][i][j]) for i in range(3) for j in range(2))>0.001:errors.append('PGSC transformed bounds do not match manifest')
for ray in master_result['garage_clearance_rays']:
 if ray['xy_m'] in ([153.0099342,261.43640895],[150.0,260.0],[160.0,260.0]) and (not ray['hit'] or abs(ray['hit_z_m']-4.5)>0.01):errors.append('garage ray does not clear model volume to upper slab')
result={'status':'PASS' if not errors else 'FAIL','asset':asset_result,'master':master_result,'errors':errors}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if errors:raise RuntimeError('; '.join(errors))
