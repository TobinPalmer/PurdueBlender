import bpy
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'))
sc=bpy.context.scene; root=bpy.data.objects['HOVD_Root']
sc.render.engine='BLENDER_EEVEE'; sc.eevee.taa_render_samples=48
sc.render.resolution_x=1200; sc.render.resolution_y=900; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'; sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'; sc.view_settings.exposure=.85
world=bpy.data.worlds[0]; sc.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.34,.43,.58,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
side=(root.matrix_world.to_3x3()@Vector((1,0,0))).normalized(); along=(root.matrix_world.to_3x3()@Vector((0,1,0))).normalized()
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size,color in [('R12_close_key',(0,0,0),2100,10,(1,.86,.70)),('R12_close_fill',(0,0,0),1250,12,(.7,.82,1))]:
 d=bpy.data.lights.new(name,'AREA'); o=bpy.data.objects.new(name,d); sc.collection.objects.link(o); o.location=loc; d.energy=power; d.shape='DISK'; d.size=size; d.color=color
# Capital 3, seen from street-facing front and a slight lateral angle.
focus=root.matrix_world@Vector((14.685,-1.875,10.40))
for o in [obj for obj in sc.objects if obj.name.startswith('R12_close_')]: aim(o,focus)
sc.objects['R12_close_key'].location=focus+side*5+along*1+Vector((0,0,3.0))
sc.objects['R12_close_fill'].location=focus+side*4-along*4+Vector((0,0,1.0))
d=bpy.data.cameras.new('HOVD_R12_Capital_Close'); cam=bpy.data.objects.new('HOVD_R12_Capital_Close',d); sc.collection.objects.link(cam); cam.location=focus+side*5.6-along*1.8+Vector((0,0,1.8)); d.lens=65; d.sensor_width=36; aim(cam,focus); sc.camera=cam
sc.render.filepath=str(P/'audit/batch3_hovde/portico_capital_close_round12.png'); bpy.ops.render.render(write_still=True)
print('Saved elevated capital close view from reopened Hovde asset.')

