import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/black_cultural_center.blend'; GIS=HERE/'sources/purdue_gis_fid_645.json'; MANIFEST=HERE/'sources/manifest_snapshot.json'; EXPORT=HERE/'black_cultural_center_independent_export.blend'
def bounds(points): return [[float(min(p[i] for p in points)),float(max(p[i] for p in points))] for i in range(3)]
def evaluated_points(obj,deps):
 ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
 try: return [ev.matrix_world @ v.co for v in mesh.vertices]
 finally: ev.to_mesh_clear()
def nearest(a,points): return min(math.hypot(a[0]-b[0],a[1]-b[1]) for b in points)
manifest=json.loads(MANIFEST.read_text(encoding='utf-8-sig')); entry=next(a for a in manifest['assets'] if a.get('id')=='black_cultural_center')
gis=json.loads(GIS.read_text(encoding='utf-8-sig')); feature=gis['features'][0]; attrs=feature['attributes']; ring=feature['geometry']['rings'][0]
LON_M=84810.60416539927; LAT_M=111040.0
cx=(min(p[0] for p in ring[:-1])+max(p[0] for p in ring[:-1]))/2; cy=(min(p[1] for p in ring[:-1])+max(p[1] for p in ring[:-1]))/2
src=[((p[0]-cx)*LON_M,(p[1]-cy)*LAT_M) for p in ring[:-1]]
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); col=bpy.data.collections.get(entry['collection']); scene=bpy.data.scenes.get(entry['scene']); assert col and scene
objs=list(col.all_objects); types={}
for o in objs: types[o.type]=types.get(o.type,0)+1
names=sorted(o.name for o in objs); manifest_names=sorted(entry.get('objects',[]))
deps=bpy.context.evaluated_depsgraph_get(); mesh_objs=[o for o in objs if o.type=='MESH']
pts=[p for o in mesh_objs for p in evaluated_points(o,deps)]; asset_bounds=bounds(pts)
shell=bpy.data.objects.get('BCC | first-floor brick envelope'); assert shell and shell in objs
shellpts=evaluated_points(shell,deps); shell_xy=[(float(p.x),float(p.y)) for p in shellpts]
# For direct geometric outline checks, retain only shell vertices at lower and upper structural levels, then deduplicate XY.
shell_xy_unique=sorted(set((round(x,7),round(y,7)) for x,y in shell_xy))
src_to_shell=[nearest(p,shell_xy_unique) for p in src]; shell_to_src=[nearest(p,src) for p in shell_xy_unique]
shell_bbox=[[min(p[i] for p in shell_xy_unique),max(p[i] for p in shell_xy_unique)] for i in (0,1)]
gis_bbox=[[min(p[i] for p in src),max(p[i] for p in src)] for i in (0,1)]
libs=[l.filepath for l in bpy.data.libraries]
imgs=[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
materials={m for o in mesh_objs for m in o.data.materials if m}; no_mat=[o.name for o in mesh_objs if not o.data.materials or all(m is None for m in o.data.materials)]
report={'asset_path':'modular/buildings/black_cultural_center.blend','asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'asset_bytes':ASSET.stat().st_size,'blender_version':bpy.app.version_string,'scene':scene.name,'collection':col.name,'object_count':len(objs),'type_counts':types,'manifest_object_count':entry['object_count'],'manifest_names_match':names==manifest_names,'manifest_count_match':len(objs)==entry['object_count'],'evaluated_bounds_local_m':asset_bounds,'manifest_bounds_local_m':entry.get('local_bounds_m'),'manifest_placement_origin_xy_m':entry['placement_origin_xy_m'],'source_feature':{'fid':attrs.get('FID'),'code':attrs.get('BLDG_ABBR'),'name':attrs.get('BUILDING_N'),'address':attrs.get('ADDRESS'),'crs':gis.get('spatialReference'),'ring_vertex_count_unique':len(src),'num_levels':attrs.get('NUM_LEVELS'),'extrution':attrs.get('Extrution')},'structural_shell':shell.name,'structural_shell_local_xy_bounds_m':shell_bbox,'gis_local_xy_bounds_m':gis_bbox,'source_to_shell_nearest_avg_m':sum(src_to_shell)/len(src_to_shell),'source_to_shell_nearest_max_m':max(src_to_shell),'shell_to_source_nearest_avg_m':sum(shell_to_src)/len(shell_to_src),'shell_to_source_nearest_max_m':max(shell_to_src),'unmaterialed_mesh_count':len(no_mat),'unmaterialed_meshes':no_mat,'material_count':len(materials),'external_libraries':libs,'unpacked_file_images':imgs,'asset_camera_light_count':sum(o.type in {'CAMERA','LIGHT'} for o in objs),'modifier_count':sum(len(o.modifiers) for o in objs)}
(HERE/'blender_asset_probe.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
bpy.data.libraries.write(str(EXPORT),{col},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
print(json.dumps(report,indent=2)); print('EXPORT',EXPORT,'COUNT',len(objs))
