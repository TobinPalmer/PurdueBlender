import bpy, json, hashlib, os, bmesh
from mathutils import Vector
asset = bpy.data.filepath
obj = bpy.data.objects.get('Village Bottle Shoppe')
coll = bpy.data.collections.get('Asset_massing_village_bottle_shoppe_6a17e23')
scene = bpy.data.scenes.get('Building_massing_village_bottle_shoppe_6a17e23')
issues=[]
if obj is None or obj.type!='MESH': issues.append('stable mesh object missing')
if coll is None: issues.append('stable collection missing')
if scene is None: issues.append('stable scene missing')
if obj and coll and coll not in obj.users_collection: issues.append('object not linked to expected collection')
if coll and [o.name for o in coll.objects] != ['Village Bottle Shoppe']: issues.append('unexpected collection objects')
if scene and [o.name for o in scene.objects] != ['Village Bottle Shoppe']: issues.append('unexpected scene objects')
materials=[]
if obj:
 for slot in obj.material_slots:
  m=slot.material
  entry={'name':m.name if m else None,'uses_nodes':bool(m and m.use_nodes),'links':len(m.node_tree.links) if m and m.use_nodes and m.node_tree else 0}
  if m and m.use_nodes and m.node_tree:
   p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   entry['principled']=bool(p)
   if p:
    entry['base_color']=list(p.inputs['Base Color'].default_value)
    entry['roughness']=p.inputs['Roughness'].default_value
  materials.append(entry)
 bm=bmesh.new(); bm.from_mesh(obj.data)
 nonmanifold=sum(not e.is_manifold for e in bm.edges)
 loose=sum(len(e.link_faces)==0 for e in bm.edges)
 bm.free()
 world=[[(obj.matrix_world@Vector(v))[i] for i in range(3)] for v in obj.bound_box]
 bbox=[[min(p[i] for p in world),max(p[i] for p in world)] for i in range(3)]
 data={'asset':asset,'sha256':hashlib.sha256(open(asset,'rb').read()).hexdigest(),'blender_version':bpy.app.version_string,'stable_scene':scene.name if scene else None,'stable_collection':coll.name if coll else None,'collection_objects':[o.name for o in coll.objects] if coll else [],'object_type':obj.type if obj else None,'vertices':len(obj.data.vertices) if obj else None,'faces':len(obj.data.polygons) if obj else None,'materials':materials,'bbox_world_xyz':bbox if obj else None,'nonmanifold_edges':nonmanifold if obj else None,'loose_edges':loose if obj else None,'external_libraries':len(bpy.data.libraries),'file_images':[i.filepath for i in bpy.data.images if i.source=='FILE'],'issues':issues}
out=os.path.join(os.path.dirname(__file__),'fresh_open_probe.json')
with open(out,'w',encoding='utf-8') as f: json.dump(data,f,indent=2)
print('INDEPENDENT_FRESH_OPEN',json.dumps(data))
