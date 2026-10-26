import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
outdir=root/'audit'/'university_hall_refine'
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=24
scene.render.resolution_x=960;scene.render.resolution_y=760;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new('R2_ReviewWorld')
scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.40,0.49,0.59,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.5
mat=bpy.data.materials.new('R2_TemporaryGround');mat.diffuse_color=(0.28,0.31,0.28,1);mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.28,0.31,0.28,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.9
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-0.14));ground=bpy.context.object;ground.name='R2_TemporaryGround';ground.data.materials.append(mat)
bpy.ops.object.light_add(type='SUN',location=(35,-50,70));sun=bpy.context.object;sun.data.energy=3.2;sun.rotation_euler=(math.radians(25),math.radians(-25),math.radians(-30))
bpy.ops.object.light_add(type='AREA',location=(-30,-20,50));fill=bpy.context.object;fill.data.energy=1200;fill.data.shape='DISK';fill.data.size=42;fill.rotation_euler=(Vector((0,0,12))-fill.location).to_track_quat('-Z','Y').to_euler()
def render(name,loc,target,scale,cutaway=False):
 hidden=[]
 if cutaway:
  for o in bpy.data.objects:
   n=o.name.lower()
   if n.startswith(('univ_wall_','univ_win_','univ_winsill','univ_winhoo','univ_winkeystone','univ_mansard_roof','univ_r2_mansard','univ_r2_dormer','univ_r2_ridgedeck','univ_belfry_roof','univ_tower_brick','univ_tower_stone','univ_r3_','univ_water','univ_beltcourse','univ_quoin','univ_portico','univ_east_step')) or n=='univ_interior_ceiling_second':
    hidden.append((o,o.hide_render));o.hide_render=True
 data=bpy.data.cameras.new('R2CameraData');cam=bpy.data.objects.new('R2Camera',data);scene.collection.objects.link(cam)
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;scene.camera=cam
 scene.render.filepath=str(outdir/(name+'.png'));bpy.ops.render.render(write_still=True)
 for o,value in hidden:o.hide_render=value
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(data)
render('oblique_southwest_r2',(-60,-75,58),(0,0,13),75)
render('east_elevation_r2',(85,0,28),(0,0,13),64)
render('interior_cutaway_r2',(30,-45,22),(-7.5,0,5.5),60,True)
for o in (ground,sun,fill):
 data=o.data;bpy.data.objects.remove(o,do_unlink=True)
 if data.users==0:(bpy.data.meshes if isinstance(data,bpy.types.Mesh) else bpy.data.lights).remove(data)
print('R2 rendered three views into',outdir)
