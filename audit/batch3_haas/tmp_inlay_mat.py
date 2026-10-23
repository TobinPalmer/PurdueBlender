import bpy
for n in ['HAAS_R7_EastFacade_Inlaid_Brickwork','HAAS_R8_EastWing_Brick_Inlays_EST']:
 o=bpy.data.objects[n];print(n,[(m.name if m else None) for m in o.data.materials],[(p.material_index) for p in o.data.polygons][:10], 'dims',tuple(o.dimensions))
for m in bpy.data.materials:
 if 'Brick' in m.name or 'brick' in m.name or 'Red' in m.name:print('MAT',m.name,tuple(m.diffuse_color),m.use_nodes)
