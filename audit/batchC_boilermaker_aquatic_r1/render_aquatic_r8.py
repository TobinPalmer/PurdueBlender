import bpy
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend';AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'
bpy.ops.wm.open_mainfile(filepath=str(ASSET));scene=bpy.context.scene
ctx=bpy.data.collections['AQUA_R5_Context | approximate site dressing'];roof=bpy.data.collections['AQUA_Roof'];old=(ctx.hide_render,roof.hide_render);ctx.hide_render=True;roof.hide_render=True
world=scene.world;background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg_color=tuple(background.inputs['Color'].default_value);bg_strength=background.inputs['Strength'].default_value
sky_links=[(l.from_socket,l.to_socket) for l in list(world.node_tree.links) if l.to_socket==background.inputs['Color']]
for l in list(world.node_tree.links):
    if l.to_socket==background.inputs['Color']:world.node_tree.links.remove(l)
background.inputs['Color'].default_value=(.28,.30,.31,1);background.inputs['Strength'].default_value=.58
scene.render.engine='BLENDER_EEVEE';scene.render.image_settings.file_format='PNG';scene.render.resolution_x=1700;scene.render.resolution_y=1100;scene.render.resolution_percentage=85
scene.camera=bpy.data.objects['AQUA R8 | pool hall bleacher and lighting camera'];scene.render.filepath=str(AUD/'aquatic_r8_interior_lighting_banners.png');bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['AQUA R8 | bleacher side detail camera'];scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=90;scene.render.filepath=str(AUD/'aquatic_r8_bleacher_aisle_detail.png');bpy.ops.render.render(write_still=True)
background.inputs['Color'].default_value=bg_color;background.inputs['Strength'].default_value=bg_strength
for fr,to in sky_links:world.node_tree.links.new(fr,to)
ctx.hide_render,roof.hide_render=old
scene.camera=bpy.data.objects['AQUA R8 | north entry approach camera'];scene.render.resolution_x=1700;scene.render.resolution_y=1100;scene.render.resolution_percentage=85;scene.render.filepath=str(AUD/'aquatic_r8_north_entry_approach.png');bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['AQUA R8 | north facade close camera'];scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=90;scene.render.filepath=str(AUD/'aquatic_r8_north_facade_reveals.png');bpy.ops.render.render(write_still=True)
print('R8 render set complete; interior roof/context visibility and neutral world restored after cutaway previews')
