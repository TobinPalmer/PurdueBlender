import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch4_knoy\knoy_updated_exterior_check.png'
bpy.ops.render.render(write_still=True)
