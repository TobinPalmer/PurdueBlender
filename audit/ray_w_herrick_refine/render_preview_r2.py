import bpy
s=bpy.context.scene
s.render.resolution_x=1280;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\ray_w_herrick_refine\preview_r2.png'
bpy.ops.render.render(write_still=True)
