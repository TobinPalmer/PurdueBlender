import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\owen_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
s=bpy.context.scene
s.camera=bpy.data.objects.get('Cam_27_Owen_Hall_StadiumAve_StreetView')
s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\owen_hall_independent_grade\owen_hall_facade.png'
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
bpy.ops.render.render(write_still=True)
