import bpy, json, os, hashlib
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..'))
asset=os.path.join(root,'modular','buildings','massing_windsor_halls_80aeb51.blend')
col=bpy.data.collections.get('Asset_massing_windsor_halls_80aeb51')
if col is None: raise RuntimeError('missing asset collection after fresh open')
objs=list(col.objects); meshes=[o for o in objs if o.type=='MESH']
pts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
matdata=[]
for m in sorted({m for o in meshes for m in o.data.materials if m},key=lambda x:x.name):
    p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes and m.node_tree else None
    matdata.append({'name':m.name,'use_nodes':m.use_nodes,'base_color':list(p.inputs['Base Color'].default_value) if p else None,'roughness':p.inputs['Roughness'].default_value if p else None,'metallic':p.inputs['Metallic'].default_value if p else None,'image_textures':[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes and m.node_tree else []})
objects=[{'name':o.name,'type':o.type,'verts':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []} for o in objs]
images=[{'name':im.name,'filepath':im.filepath,'packed':im.packed_file is not None} for im in bpy.data.images]
report={'fresh_open':True,'asset':os.path.relpath(asset,root).replace('\\','/'),'scene':bpy.context.scene.name,'collection':col.name,'objects':len(objs),'meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'faces':sum(len(o.data.polygons) for o in meshes),'bounds':{'xmin':min(p.x for p in pts),'xmax':max(p.x for p in pts),'ymin':min(p.y for p in pts),'ymax':max(p.y for p in pts),'zmin':min(p.z for p in pts),'zmax':max(p.z for p in pts)},'materials':matdata,'external_images':images,'object_inventory':objects}
with open(os.path.join(os.path.dirname(__file__),'fresh_open_probe.json'),'w',encoding='utf8') as f:json.dump(report,f,indent=2)
print('FRESH_OPEN_OK',len(objs),len(meshes),sum(len(o.data.vertices) for o in meshes),sum(len(o.data.polygons) for o in meshes))

