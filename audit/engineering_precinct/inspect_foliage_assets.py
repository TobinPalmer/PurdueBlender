import bpy, json
from mathutils import Vector

for col in bpy.data.collections:
    objects=list(col.all_objects)
    if not objects:
        continue
    mesh_count=sum(o.type=='MESH' for o in objects)
    verts=sum(len(o.data.vertices) for o in objects if o.type=='MESH')
    print('COLLECTION',col.name,'objects',len(objects),'meshes',mesh_count,'verts',verts)
    for ob in objects:
        if ob.type!='MESH':
            print('  OBJECT',ob.name,ob.type,'mods',len(ob.modifiers))
            continue
        bpy.context.view_layer.update()
        coords=[ob.matrix_world @ Vector(corner) for corner in ob.bound_box]
        lo=[min(v[i] for v in coords) for i in range(3)]
        hi=[max(v[i] for v in coords) for i in range(3)]
        mats=[]
        for m in ob.data.materials:
            if m:
                images=[]
                if m.use_nodes:
                    images=[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
                mats.append({'name':m.name,'images':images})
        print('  OBJECT',ob.name,'vertices',len(ob.data.vertices),'faces',len(ob.data.polygons),'bounds',[round(hi[i]-lo[i],3) for i in range(3)],'mods',[(m.name,m.type) for m in ob.modifiers],'materials',json.dumps(mats))
for im in bpy.data.images:
    print('IMAGE',im.name,'path',im.filepath,'packed',bool(im.packed_file),'size',list(im.size))
