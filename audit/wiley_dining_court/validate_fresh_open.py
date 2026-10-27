import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
asset=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_wiley_dining_court_wdct_8a6c669.blend')
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\wiley_dining_court\fresh_open_validation.json')
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.data.scenes.get('Building_massing_wiley_dining_court_wdct_8a6c669');col=bpy.data.collections.get('Asset_massing_wiley_dining_court_wdct_8a6c669');root=bpy.data.objects.get('Wiley Dining Court (WDCT)')
assert scene and col and root and root.name in col.objects
assert not root.hide_render and not root.hide_viewport
meshes=[];coords=[]
for ob in col.objects:
 if ob.type=='MESH':
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
  coords.extend(ob.matrix_world@v.co for v in me.vertices);meats=list(me.materials)
  meshes.append({'name':ob.name,'vertices':len(me.vertices),'polygons':len(me.polygons),'materials':[m.name for m in meats if m]});ev.to_mesh_clear()
external=[]
for image in bpy.data.images:
 if image.source=='FILE' and image.filepath and not image.packed_file:
  p=Path(bpy.path.abspath(image.filepath));external.append({'path':image.filepath,'exists':p.exists()})
rootcoords=[root.matrix_world@v.co for v in root.data.vertices]
allmats=sorted({m.name for ob in col.objects if hasattr(ob.data,'materials') for m in ob.data.materials if m})
result={'fresh_open':True,'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),'scene':scene.name,'collection':col.name,'asset_object_count':len(col.objects),'mesh_object_count':len(meshes),'root_object':root.name,'root_hidden_render':root.hide_render,'root_hidden_viewport':root.hide_viewport,'root_location':list(root.location),'root_rotation_radians':list(root.rotation_euler),'root_scale':list(root.scale),'root_mesh_vertices':len(root.data.vertices),'root_mesh_polygons':len(root.data.polygons),'root_bounds_local_xyz_m':[[min(p[i] for p in rootcoords),max(p[i] for p in rootcoords)] for i in range(3)],'whole_collection_bounds_local_xyz_m':[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)],'material_names':allmats,'image_dependencies':external,'missing_external_images':[x['path'] for x in external if not x['exists']],'mesh_objects_without_materials':[m['name'] for m in meshes if not m['materials']],'all_materials_use_nodes':all(m.use_nodes for m in bpy.data.materials if m.name.startswith('WDCT |')),'root_uv_layers':[uv.name for uv in root.data.uv_layers]}
assert result['root_location']==[0,0,0] and result['root_scale']==[1,1,1]
assert not result['missing_external_images'] and not result['mesh_objects_without_materials']
out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
