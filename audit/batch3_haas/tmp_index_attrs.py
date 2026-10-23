import bpy
from mathutils import Vector
S=bpy.context.scene;C=bpy.data.collections['Asset_felix_haas_hall'];S.render.engine='CYCLES';S.cycles.samples=1;S.render.resolution_x=100;S.render.resolution_y=80;S.view_layers[0].use_pass_object_index=True
S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/index_tmp.png';bpy.ops.render.render(write_still=True)
r=bpy.data.images['Render Result'];print('attrs', [x for x in dir(r) if 'layer' in x.lower() or 'pass' in x.lower()]);print('layers',r.layers[:])
for l in r.layers:print('layer',l.name,'passes',[p.name for p in l.passes])
