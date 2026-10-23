import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'; bpy.ops.wm.open_mainfile(filepath=p)
for c in bpy.data.collections: print('C',c.name,'hide',c.hide_render,c.hide_viewport)
for nm in ['SC_Lobby_Terrazzo_Floor','SC_Lobby_Limestone_Wall_N','SC_GradHub_CommunalTable_0','SC_GradHub_Chair_0_N_-0.9_Seat','Asset_stanley_coulter_hall']:
 o=bpy.data.objects.get(nm); print('O',nm, o and o.hide_render,o and o.hide_get(),o and tuple(o.location), o and tuple(o.dimensions))
cam=bpy.data.objects['Cam_SC_06_Interior_Schematic'];print('cam',cam.data.type,cam.data.ortho_scale,cam.location,cam.rotation_euler, 'clip',cam.data.clip_start,cam.data.clip_end)
