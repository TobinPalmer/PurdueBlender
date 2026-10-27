import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/frieda_parker_hall.blend'
OUT=Path(__file__).with_name('fresh_open_probe.json')
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
scene=bpy.context.scene
col=bpy.data.collections.get('Asset_frieda_parker_hall')
root=bpy.data.objects.get('AssetRoot_frieda_parker_hall')
if col is None: raise RuntimeError('Expected collection not found')
objs=list(col.all_objects)
meshes=[o for o in objs if o.type=='MESH']
def bounds_obj(o):
 pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
allpts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
allbounds=[[min(p[i] for p in allpts),max(p[i] for p in allpts)] for i in range(3)] if allpts else None
interesting=[]
for o in meshes:
 b=bounds_obj(o)
 area=(b[0][1]-b[0][0])*(b[1][1]-b[1][0])
 if area>80 or any(t in o.name.lower() for t in ('upper','roof','bridge','northwing')):
  interesting.append({'name':o.name,'bounds_xyz':b,'xy_bbox_area_m2':area,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)})
images=[]
for im in bpy.data.images:
 if im.source=='FILE':
  p=Path(bpy.path.abspath(im.filepath)) if im.filepath else None
  images.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file),'exists':bool(p and p.exists())})
linked=[{'name':lib.name,'filepath':lib.filepath} for lib in bpy.data.libraries if lib]
matinfo=[]
for mat in bpy.data.materials:
 if mat.users>0:
  matinfo.append({'name':mat.name,'users':mat.users,'nodes':bool(mat.use_nodes)})
probe={'fresh_open':True,'blender_version':bpy.app.version_string,'asset_path':str(ASSET),'sha256':sha,'scene':scene.name,'all_scenes':[s.name for s in bpy.data.scenes],'collection':col.name,'collection_is_scene_linked':any(c==col for c in scene.collection.children) or col in scene.collection.children_recursive,'object_count':len(objs),'mesh_count':len(meshes),'mesh_vertex_count':sum(len(o.data.vertices) for o in meshes),'mesh_polygon_count':sum(len(o.data.polygons) for o in meshes),'root':{'name':root.name if root else None,'location':list(root.location) if root else None,'rotation':list(root.rotation_euler) if root else None,'scale':list(root.scale) if root else None,'matrix_world':[[float(v) for v in row] for row in root.matrix_world] if root else None},'full_mesh_bounds_local_xyz':allbounds,'selected_structural_objects':interesting,'linked_libraries':linked,'file_images':images,'materials':matinfo,'missing_images':[x for x in images if not x['exists'] and not x['packed']]}
OUT.write_text(json.dumps(probe,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:probe[k] for k in ('fresh_open','blender_version','sha256','scene','collection','object_count','mesh_count','full_mesh_bounds_local_xyz','linked_libraries','missing_images')},indent=2))
