import bpy,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3]
asset=root/'modular/buildings/massing_wiley_dining_court_wdct_8a6c669.blend'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.data.scenes.get('Building_massing_wiley_dining_court_wdct_8a6c669')
coll=bpy.data.collections.get('Asset_massing_wiley_dining_court_wdct_8a6c669')
root_obj=bpy.data.objects.get('Wiley Dining Court (WDCT)')
assert scene and coll and root_obj and root_obj.name in coll.objects
mesh_objs=[o for o in coll.all_objects if o.type=='MESH']
images=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  p=Path(bpy.path.abspath(im.filepath)); images.append({'name':im.name,'path':im.filepath,'exists':p.is_file(),'packed':bool(im.packed_file)})
material_counts={}
for o in mesh_objs:
 for m in o.data.materials:
  if m: material_counts[m.name]=material_counts.get(m.name,0)+1
coords=[tuple(o.matrix_world @ v.co) for o in mesh_objs for v in o.data.vertices]
report={'fresh_open':True,'blender':bpy.app.version_string,'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),'scene':scene.name,'collection':coll.name,'collection_object_count':len(coll.all_objects),'mesh_object_count':len(mesh_objs),'root':root_obj.name,'root_transform':{'location':list(root_obj.location),'rotation':list(root_obj.rotation_euler),'scale':list(root_obj.scale)},'root_local_bbox':[[min(v.co[i] for v in root_obj.data.vertices),max(v.co[i] for v in root_obj.data.vertices)] for i in range(3)],'collection_local_bbox':[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)],'materials':sorted(material_counts),'material_mesh_assignments':material_counts,'unmaterialed_meshes':[o.name for o in mesh_objs if not any(o.data.materials)],'external_images':images,'mesh_vertices':sum(len(o.data.vertices) for o in mesh_objs),'mesh_polygons':sum(len(o.data.polygons) for o in mesh_objs)}
out=Path(__file__).resolve().parent/'fresh_open.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
