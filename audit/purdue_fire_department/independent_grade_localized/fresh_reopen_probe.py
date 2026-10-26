import bpy, json, math, os, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
MOD=ROOT/'modular'; ASSET_ID='massing_purdue_fire_department_520430b'
ASSET=MOD/'buildings'/f'{ASSET_ID}.blend'; MASTER=ROOT/'purdue_campus_master.blend'
MANIFEST=json.loads((MOD/'manifest.json').read_text(encoding='utf-8'))
REC=next(a for a in MANIFEST['assets'] if a['id']==ASSET_ID)
MARKER_NAME='Placement_'+ASSET_ID

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def bounds(points):return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
asset_sha=sha(ASSET); assert asset_sha=='6a20209ae3db99c028a16d7df11e42a87577b8bee29afc5e0ead98a779b03817',asset_sha
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections.get(REC['collection']); assert col and bpy.context.scene.name==REC['scene']; assert col.library is None
meshes=[o for o in col.all_objects if o.type=='MESH']; assert len(meshes)==99,len(meshes)
pts=[]
for ob in meshes:
 for c in ob.bound_box: pts.append(ob.matrix_world @ Vector(c))
local_bounds=bounds(pts)
material_count=sum(bool(o.data.materials) for o in meshes)
assert material_count==99,material_count
external_images=[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
assert not external_images,external_images
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
marker=bpy.data.objects.get(MARKER_NAME); assert marker and marker.instance_type=='COLLECTION' and marker.instance_collection
assert marker.instance_collection.name==REC['collection']
lib=Path(bpy.path.abspath(marker.instance_collection.library.filepath)).resolve(); assert lib==ASSET.resolve(),str(lib)
loc=list(marker.location); xy=REC['placement_origin_xy_m']; assert max(abs(loc[i]-xy[i]) for i in range(2))<.001,(loc,xy)
rot=list(marker.rotation_euler); scale=list(marker.scale)
assert max(abs(v) for v in rot)<1e-7; assert max(abs(v-1) for v in scale)<1e-7
# Reconstruct linked instance bounds from fresh local geometry bounds and master marker transform.
world_bounds=[[local_bounds[i][j]+(loc[i] if i<2 else 0.0) for j in range(2)] for i in range(3)]
expected=REC['bounds_world_m']; bounds_error=max(abs(world_bounds[i][j]-expected[i][j]) for i in range(3) for j in range(2))
assert bounds_error<0.001,(world_bounds,expected,bounds_error)
root_children=list(bpy.context.scene.collection.children)
old_col=bpy.data.collections.get('Asset_'+ASSET_ID)
old_direct=bool(old_col is not None and old_col in root_children); assert not old_direct
report={'asset_id':ASSET_ID,'asset_sha256':asset_sha,'asset_fresh_open':True,'asset_scene':REC['scene'],'asset_collection':col.name,'mesh_object_count':len(meshes),'local_bounds_m':local_bounds,'manifest_local_bounds_m':REC['local_bounds_m'],'material_assigned_mesh_count':material_count,'external_file_images':external_images,'master_sha256':sha(MASTER),'master_fresh_open':True,'marker_name':MARKER_NAME,'marker_location':loc,'manifest_placement_origin_xy_m':xy,'marker_rotation_euler':rot,'marker_scale':scale,'linked_library_path':str(lib),'expected_asset_path':str(ASSET.resolve()),'master_bounds_world_reconstructed_m':world_bounds,'manifest_bounds_world_m':expected,'max_world_bounds_error_m':bounds_error,'old_massing_directly_linked':old_direct,'status':'PASS'}
out=Path(__file__).with_name('fresh_reopen_probe.json');out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
