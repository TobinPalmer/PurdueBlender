import bpy,json
m=bpy.data.materials['DUHME_Red_Oxide_Handmade_Brick'];o=bpy.data.objects['DUHME_Continuous_Red_Brick_Wall_Envelope']
print('backface',m.use_backface_culling,'surface',m.surface_render_method,'polycount',len(o.data.polygons),'materialindexes',set(p.material_index for p in o.data.polygons))
for p in o.data.polygons[:6]: print(p.index,p.normal[:],p.center[:])
