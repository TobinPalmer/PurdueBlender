import bpy
s=bpy.context.scene
s.render.resolution_percentage=70
if s.render.engine=='CYCLES':s.cycles.samples=24
s.render.image_settings.file_format='PNG'
s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\veterinary_medicine_isolation_facility\independent_grade_r2\exterior_material_render.png'
bpy.ops.render.render(write_still=True)
