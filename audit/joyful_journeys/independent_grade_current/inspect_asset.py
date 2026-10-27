import bpy,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3]
asset=root/'modular/buildings/massing_joyful_journeys_abaf5c3.blend'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.data.scenes.get('Building_massing_joyful_journeys_abaf5c3')
coll=bpy.data.collections.get('Asset_massing_joyful_journeys_abaf5c3')
obj=bpy.data.objects.get('Joyful Journeys')
assert scene and coll and obj and obj.name in coll.objects and len(coll.objects)==1 and obj.type=='MESH'
mesh=obj.data
materials=[]
for m in mesh.materials:
 if not m: continue
 mats={'name':m.name,'use_nodes':bool(m.use_nodes),'diffuse_color':list(m.diffuse_color),'principled_base_colors':[],'image_nodes':[]}
 if m.use_nodes and m.node_tree:
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED':
    inp=n.inputs.get('Base Color')
    if inp and inp.is_linked is False: mats['principled_base_colors'].append(list(inp.default_value))
   if n.type=='TEX_IMAGE' and n.image: mats['image_nodes'].append(n.image.name)
 materials.append(mats)
images=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  p=Path(bpy.path.abspath(im.filepath));images.append({'name':im.name,'path':im.filepath,'exists':p.is_file(),'packed':bool(im.packed_file)})
report={'fresh_open':True,'blender_version':bpy.app.version_string,'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),'scene':scene.name,'collection':coll.name,'collection_objects':len(coll.objects),'object':obj.name,'object_type':obj.type,'identity_transform':list(obj.location)==[0,0,0] and list(obj.rotation_euler)==[0,0,0] and list(obj.scale)==[1,1,1],'location':list(obj.location),'rotation':list(obj.rotation_euler),'scale':list(obj.scale),'vertex_count':len(mesh.vertices),'face_count':len(mesh.polygons),'materials':materials,'image_dependencies':images,'bounds_world_m':[[min((obj.matrix_world@v.co)[i] for v in mesh.vertices),max((obj.matrix_world@v.co)[i] for v in mesh.vertices)] for i in range(3)],'modifiers':[m.name for m in obj.modifiers],'linked_libraries':[lib.filepath for lib in bpy.data.libraries if lib.filepath]}
out=Path(__file__).resolve().parent/'fresh_open.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
