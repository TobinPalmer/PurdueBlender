import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
blend=root/'modular/buildings/alpha_chi_omega_fid765.blend'
# This script is intended to be run in a separate Blender process with the saved blend already opened.
scene=bpy.context.scene
asset=bpy.data.collections.get('Asset_alpha_chi_omega_fid765')
assert scene.name=='Building_alpha_chi_omega_fid765'
assert asset is not None
objs=list(asset.all_objects)
meshes=[o for o in objs if o.type=='MESH']
rootob=bpy.data.objects.get('AssetRoot_alpha_chi_omega_fid765')
assert rootob is not None
assert rootob.get('source_feature_id')==765 and rootob.get('source_building_code')=='SOACO'
assert abs(rootob['local_origin_xy_m'][0]-(-1081.086543521541))<0.01
assert abs(rootob['local_origin_xy_m'][1]-817.2396545775244)<0.01
verts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
bounds=[[min(v[i] for v in verts) for i in range(3)],[max(v[i] for v in verts) for i in range(3)]]
external_images=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath]
external_nodes=[]
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE':external_nodes.append((m.name,n.image.filepath))
linked_libraries=[lib.filepath for lib in bpy.data.libraries]
report={'fresh_open':True,'scene':scene.name,'export_collection':asset.name,'object_count':len(objs),'mesh_count':len(meshes),'text_count':sum(o.type=='FONT' for o in objs),'bounds_local_m':bounds,'local_origin_xy_m':list(rootob['local_origin_xy_m']),'local_origin_lonlat':list(rootob['local_origin_lonlat']),'external_file_images':external_images,'external_image_texture_nodes':external_nodes,'linked_blend_libraries':linked_libraries,'asset_sha256':hashlib.sha256(blend.read_bytes()).hexdigest()}
assert not external_images and not external_nodes and not linked_libraries
out=root/'audit/alpha_chi_omega_fid765/fresh_open_validation.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
