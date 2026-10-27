import bpy, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(bpy.path.abspath('//')); MOD=ROOT/'modular'; AID='massing_house_301841253_f0b3be3'
manifest=json.loads((MOD/'manifest.json').read_text(encoding='utf-8')); record=next(a for a in manifest['assets'] if a['id']==AID)
scene=bpy.context.scene; root_col=scene.collection; marker_name='Placement_'+AID
markers=[o for o in bpy.data.objects if o.name==marker_name]; marker=markers[0] if markers else None
col=bpy.data.collections.get(record['collection']); libpath=Path(bpy.path.abspath(col.library.filepath)).resolve() if col and col.library else None; expected=(MOD/record['file']).resolve()
root_linked=bool(col and col in list(root_col.children)); source_objs=list(col.all_objects) if col else []; geo=[o for o in source_objs if o.type in {'MESH','CURVE','FONT','SURFACE','META'}]
def local_matrix(obj,cache):
 if obj in cache:return cache[obj]
 m=obj.matrix_local.copy()
 if obj.parent is not None:m=local_matrix(obj.parent,cache)@m
 cache[obj]=m;return m
points=[];cache={}
for obj in geo:
 m=local_matrix(obj,cache)
 points.extend(m@Vector(c) for c in obj.bound_box)
local_bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
world=[marker.matrix_world@p for p in points] if marker else []
world_bounds=[[min(p[i] for p in world),max(p[i] for p in world)] for i in range(3)] if world else None
instances=[];dg=bpy.context.evaluated_depsgraph_get()
for inst in dg.object_instances:
 if inst.is_instance and inst.parent and inst.parent.original.name==marker_name:
  instances.append({'object':inst.object.original.name,'type':inst.object.original.type})
root_obj=bpy.data.objects.get('AssetRoot_'+AID)
result={'master':str(Path(bpy.data.filepath).resolve()),'asset_id':AID,'kind':record.get('kind'),'marker_count':len(markers),'marker':({'name':marker.name,'location':list(marker.location),'rotation_euler':list(marker.rotation_euler),'scale':list(marker.scale),'instance_type':marker.instance_type,'instance_collection':marker.instance_collection.name if marker.instance_collection else None}if marker else None),'collection_exists':bool(col),'collection_name':col.name if col else None,'collection_library_path':str(libpath)if libpath else None,'expected_library_path':str(expected),'library_path_matches':bool(libpath==expected),'collection_directly_linked_under_scene_root':root_linked,'source_collection_object_count':len(source_objs),'source_geometry_object_count':len(geo),'collection_local_bounds_m':local_bounds,'reconstructed_world_bounds_m':world_bounds,'asset_root':({'name':root_obj.name,'location':list(root_obj.location),'parent':root_obj.parent.name if root_obj.parent else None}if root_obj else None),'instance_evaluated_object_count_for_marker':len(instances),'instance_evaluated_types':{t:sum(1 for x in instances if x['type']==t)for t in sorted(set(x['type'] for x in instances))},'external_unpacked_images_from_asset_library':[],'manifest_object_count':record.get('object_count'),'manifest_bounds_world_m':record.get('bounds_world_m'),'manifest_local_bounds_m':record.get('local_bounds_m'),'errors':[]}
if len(markers)!=1:result['errors'].append(f'expected 1 placement marker, found {len(markers)}')
if not marker or marker.instance_type!='COLLECTION' or not marker.instance_collection:result['errors'].append('placement marker is not a collection instance')
if not col or not col.library:result['errors'].append('asset collection missing library link')
if libpath!=expected:result['errors'].append('library path differs from manifest asset path')
if root_linked:result['errors'].append('asset collection is also directly linked under scene root; duplicate risk')
if marker and marker.instance_collection!=col:result['errors'].append('marker references a different collection')
if marker and (max(abs(float(marker.scale[i])-1)for i in range(3))>1e-8 or max(abs(float(marker.rotation_euler[i]))for i in range(3))>1e-8):result['errors'].append('marker scale/rotation is not identity')
if record.get('kind')!='detailed' or not record.get('local_coordinates'):result['errors'].append('manifest does not classify this as local detailed asset')
out=Path(__file__).resolve().parent/'master_inspection.json';out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
