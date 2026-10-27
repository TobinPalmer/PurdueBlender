import bpy
sc=bpy.context.scene
m=bpy.data.materials['PhiGam_Buff_Tan_Brick']
print('ENGINE',sc.render.engine,'VIEW',sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure)
print('MAT',m.diffuse_color[:],[(n.name,n.type) for n in m.node_tree.nodes],[(l.from_node.name,l.to_node.name) for l in m.node_tree.links])
print('BASE',m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:])
print('OVERRIDE',bpy.context.view_layer.material_override)
for o in ('House_301837281','Original_Chapter_House_Upper_Stories'):
 ob=bpy.data.objects[o];print(o,[(x.name if x else None) for x in ob.data.materials])
