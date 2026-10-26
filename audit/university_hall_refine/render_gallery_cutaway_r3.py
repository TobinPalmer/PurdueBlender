"""Architectural section view: remove two viewing façades, retain back shell."""
import bpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'audit'/'university_hall_refine'
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=8
scene.render.resolution_x=820;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new('UH_R3_CutawayWorld')
scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.36,0.44,0.54,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
old_lights=[]
for o in bpy.data.objects:
    if o.type=='LIGHT':old_lights.append((o,o.hide_render));o.hide_render=True
groundmat=bpy.data.materials.new('UH_R3_CutawayGround');groundmat.use_nodes=True;groundmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.20,.23,.21,1)
bpy.ops.mesh.primitive_plane_add(size=180,location=(0,0,-.12));ground=bpy.context.object;ground.name='UH_R3_CutawayGround';ground.data.materials.append(groundmat)
bpy.ops.object.light_add(type='SUN',location=(30,-40,50));sun=bpy.context.object;sun.data.energy=2.2;sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-38))
bpy.ops.object.light_add(type='AREA',location=(-30,-25,32));fill=bpy.context.object;fill.data.energy=650;fill.data.shape='DISK';fill.data.size=35;fill.rotation_euler=(Vector((-7.5,0,6))-fill.location).to_track_quat('-Z','Y').to_euler()
hidden=[]
hide_prefixes=('UNIV_Wall_East_','UNIV_Wall_South','UNIV_Win_','UNIV_WinSill','UNIV_WinHood','UNIV_WinKeystone',
 'UNIV_R2_Mansard','UNIV_R2_Dormer','UNIV_R2_RidgeDeck','UNIV_R2_SlateStandingSeam',
 'UNIV_R5_Mansard','UNIV_R5_Dormer','UNIV_R5_Belfry','UNIV_R5_Lantern','UNIV_R5_Weathervane','UNIV_R5_Finial','UNIV_R5_Portico',
 'UNIV_Tower_','UNIV_Belfry_','UNIV_Cupola_','UNIV_Clock_','UNIV_Historic_Bronze','UNIV_Bell_Yoke_',
 'UNIV_R3_Belfry_','UNIV_R3_East_Clock','UNIV_R3_West_Clock','UNIV_R3_North_Clock','UNIV_R3_South_Clock',
 'UNIV_R3_ArchedWindowMoulds','UNIV_R3_North_Window','UNIV_R3_South_Window','UNIV_R3_East_Window','UNIV_R3_West_Window',
 'UNIV_WaterTable_East','UNIV_WaterTable_South','UNIV_Beltcourse_E','UNIV_Beltcourse_S','UNIV_Quoin','UNIV_Portico','UNIV_East_Step')
for o in bpy.data.objects:
    n=o.name
    if n.startswith(hide_prefixes) or n=='UNIV_Interior_Ceiling_Second':
        hidden.append((o,o.hide_render));o.hide_render=True
cd=bpy.data.cameras.new('UH_R3_CutawayCameraData');cam=bpy.data.objects.new('UH_R3_CutawayCamera',cd);scene.collection.objects.link(cam)
cam.location=(35,-48,20);target=Vector((-7.5,0,6.0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=62;scene.camera=cam
scene.render.filepath=str(out/'interior_cutaway_r3.png');bpy.ops.render.render(write_still=True)
for o,v in hidden:o.hide_render=v
for o,v in old_lights:o.hide_render=v
for o in (cam,ground,sun,fill):
    data=o.data;bpy.data.objects.remove(o,do_unlink=True)
    if isinstance(data,bpy.types.Camera):bpy.data.cameras.remove(data)
    elif data.users==0:(bpy.data.meshes if isinstance(data,bpy.types.Mesh) else bpy.data.lights).remove(data)
print('R3 architectural cutaway saved; no source asset saved.')
