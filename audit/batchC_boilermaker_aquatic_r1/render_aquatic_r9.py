import bpy
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend';AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'
bpy.ops.wm.open_mainfile(filepath=str(ASSET));scene=bpy.context.scene
ctx=bpy.data.collections['AQUA_R5_Context | approximate site dressing'];ctx_old=ctx.hide_render;ctx.hide_render=True
ground=bpy.data.objects.get('AQUA R2 | preview ground plane');g_old=ground.hide_render if ground else None
if ground:ground.hide_render=True
roof_objects=[o for o in bpy.data.objects if o.name.startswith(('AQUA | clear-span natatorium | pitched roof planes','AQUA R4 | raised standing seams across estimated roof planes','AQUA R2 | continuous roof ridge cap','AQUA R2 | north roof eave fascia'))]
roof_old=[o.hide_render for o in roof_objects]
for o in roof_objects:o.hide_render=True
old_engine=scene.render.engine;old_x=scene.render.resolution_x;old_y=scene.render.resolution_y;old_pct=scene.render.resolution_percentage
old_format=scene.render.image_settings.file_format;old_filepath=scene.render.filepath;old_camera=scene.camera
scene.render.engine='BLENDER_EEVEE';scene.render.image_settings.file_format='PNG';scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=85
scene.camera=bpy.data.objects['AQUA R9 | truss pool and bleacher cutaway camera'];scene.render.filepath=str(AUD/'aquatic_r9_interior_truss_cutaway.png');bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['AQUA R8 | bleacher side detail camera'];scene.render.resolution_x=1400;scene.render.resolution_y=950;scene.render.resolution_percentage=85;scene.render.filepath=str(AUD/'aquatic_r9_bleacher_aisle_detail.png');bpy.ops.render.render(write_still=True)
ctx.hide_render=ctx_old
if ground:ground.hide_render=g_old
for o,v in zip(roof_objects,roof_old):o.hide_render=v
scene.render.engine=old_engine;scene.render.resolution_x=old_x;scene.render.resolution_y=old_y;scene.render.resolution_percentage=old_pct;scene.render.image_settings.file_format=old_format;scene.render.filepath=old_filepath;scene.camera=old_camera
print('Rendered two R9 review views; all visibility and render settings were restored without saving preview-only changes.')
