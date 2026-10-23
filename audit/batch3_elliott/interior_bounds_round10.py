import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');c=bpy.data.collections['Asset_elliott_hall_of_music']
for name in ['ELLT_B3_stage','ELLT_B3_curtain','ELLT_B3_seat','ELLT_B3_rail','ELLT_B3_stair','ELLT_B3_balcony','ELLT_B3_carpet']:
 o=bpy.data.objects.get(name);pts=[o.matrix_world@v.co for v in o.data.vertices];print(name,'bounds',[[round(min(p[i] for p in pts),2) for i in range(3)],[round(max(p[i] for p in pts),2) for i in range(3)]],'mats',[(m.name,tuple(round(x,2) for x in m.diffuse_color)) for m in o.data.materials])
