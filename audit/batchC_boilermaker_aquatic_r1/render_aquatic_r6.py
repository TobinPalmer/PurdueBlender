import bpy
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'; AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'; bpy.ops.wm.open_mainfile(filepath=str(ASSET)); scene=bpy.context.scene
ctx=bpy.data.collections['AQUA_R5_Context | approximate site dressing']; roof=bpy.data.collections['AQUA_Roof']
old=(ctx.hide_render,roof.hide_render);ctx.hide_render=True;roof.hide_render=True
world=scene.world; background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND'); bg_color=tuple(background.inputs['Color'].default_value); bg_strength=background.inputs['Strength'].default_value
sky_links=[(l.from_socket,l.to_socket) for l in list(world.node_tree.links) if l.to_socket==background.inputs['Color']]
for l in list(world.node_tree.links):
    if l.to_socket==background.inputs['Color']: world.node_tree.links.remove(l)
background.inputs['Color'].default_value=(.34,.35,.33,1);background.inputs['Strength'].default_value=.75
scene.render.engine='BLENDER_EEVEE';scene.render.image_settings.file_format='PNG';scene.render.resolution_x=1700;scene.render.resolution_y=1100;scene.render.resolution_percentage=85;scene.render.filepath=str(AUD/'aquatic_r6_interior_longitudinal.png');scene.camera=bpy.data.objects['AQUA R6 | pool-hall longitudinal interior camera'];bpy.ops.render.render(write_still=True)
# A closer pool-side view makes spectator seats, aisle, rails, and mezzanine legible.
scene.camera=bpy.data.objects['AQUA R4 | spectator aisle detail camera'];scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=90;scene.render.filepath=str(AUD/'aquatic_r6_interior_seating_gallery.png');bpy.ops.render.render(write_still=True)
background.inputs['Color'].default_value=bg_color;background.inputs['Strength'].default_value=bg_strength
for fr,to in sky_links: world.node_tree.links.new(fr,to)
ctx.hide_render,roof.hide_render=old
print('R6 interior render complete; render-only visibility and world restored')
