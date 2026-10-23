import bpy
from mathutils import Vector
from pathlib import Path
src=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
out=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_elliott')
bpy.ops.wm.open_mainfile(filepath=str(src));scene=bpy.context.scene
for o in scene.objects: o.hide_render=False
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
w=bpy.data.worlds.new('IndependentReview');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.35,.35,.35,1);scene.world=w
ld=bpy.data.lights.new('review_sun','SUN');ld.energy=2.5;lo=bpy.data.objects.new('review_sun',ld);scene.collection.objects.link(lo);lo.rotation_euler=(.5,.25,.6)
# Three exterior elevations in local source frame.
for name,loc,target in [('north',(0,150,62),(0,0,7)),('east',(155,0,62),(0,0,7)),('south',(0,-150,62),(0,0,7))]:
 cd=bpy.data.cameras.new('review_'+name);cam=bpy.data.objects.new('review_'+name,cd);scene.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=130;scene.camera=cam;scene.render.filepath=str(out/f'independent_exterior_{name}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)
