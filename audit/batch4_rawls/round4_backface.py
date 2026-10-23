import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_CurtainWall_Glass','RAWL_Dark_Bronze_Metal']:
 m=bpy.data.materials[n];print(n,'backface_culling',m.use_backface_culling,'surface_render_method',m.surface_render_method,'blend_method?',getattr(m,'blend_method',None))
