"""Fresh R3 candidate views; all stage objects are temporary, never saved."""
import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
out=root/'audit'/'university_hall_refine'
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=8
scene.render.resolution_x=820;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new('UH_R3_ReviewWorld')
scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.37,0.45,0.55,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.28
hidden_lights=[]
for obj in bpy.data.objects:
    if obj.type=='LIGHT':hidden_lights.append((obj,obj.hide_render));obj.hide_render=True

mat=bpy.data.materials.new('UH_R3_TemporaryGround');mat.diffuse_color=(0.20,0.23,0.21,1);mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.20,0.23,0.21,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.92
bpy.ops.mesh.primitive_plane_add(size=180,location=(0,0,-0.12));ground=bpy.context.object;ground.name='UH_R3_TemporaryGround';ground.data.materials.append(mat)
bpy.ops.object.light_add(type='SUN',location=(32,-44,55));sun=bpy.context.object;sun.name='UH_R3_TemporarySun';sun.data.energy=2.2
sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-38))
bpy.ops.object.light_add(type='AREA',location=(-32,-18,38));fill=bpy.context.object;fill.name='UH_R3_TemporaryFill';fill.data.energy=520;fill.data.shape='DISK';fill.data.size=32
fill.rotation_euler=(Vector((-7.5,0,10))-fill.location).to_track_quat('-Z','Y').to_euler()

def render(name,location,target,scale,cutaway=False):
    changed=[]
    if cutaway:
        hide_prefixes=('UNIV_Wall_East_','UNIV_Wall_South','UNIV_Win_','UNIV_WinSill','UNIV_WinHood','UNIV_WinKeystone',
            'UNIV_R2_Mansard','UNIV_R2_Dormer','UNIV_R2_RidgeDeck','UNIV_R2_SlateStandingSeam',
            'UNIV_R5_Mansard','UNIV_R5_Dormer','UNIV_R5_Belfry','UNIV_R5_Lantern','UNIV_R5_Weathervane','UNIV_R5_Finial','UNIV_R5_Portico',
            'UNIV_Tower_','UNIV_Belfry_','UNIV_Cupola_','UNIV_Clock_','UNIV_Historic_Bronze','UNIV_Bell_Yoke_',
            'UNIV_R3_Belfry_','UNIV_R3_East_Clock','UNIV_R3_West_Clock','UNIV_R3_North_Clock','UNIV_R3_South_Clock',
            'UNIV_R3_ArchedWindowMoulds','UNIV_R3_North_Window','UNIV_R3_South_Window','UNIV_R3_East_Window','UNIV_R3_West_Window',
            'UNIV_WaterTable_East','UNIV_WaterTable_South','UNIV_Beltcourse_E','UNIV_Beltcourse_S','UNIV_Quoin','UNIV_Portico','UNIV_East_Step')
        for o in bpy.data.objects:
            old=o.hide_render
            if old:continue
            if o.name.startswith(hide_prefixes) or o.name=='UNIV_Interior_Ceiling_Second':
                changed.append((o,old));o.hide_render=True
    cd=bpy.data.cameras.new('UH_R3_TempCameraData');cam=bpy.data.objects.new('UH_R3_TempCamera',cd);scene.collection.objects.link(cam)
    cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cd.type='ORTHO';cd.ortho_scale=scale;scene.camera=cam
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)
    for o,val in changed:o.hide_render=val

render('ground_oblique_r3',(28,-62,23),(-7.5,0,11),66)
render('east_elevation_r3',(72,0,18),(-7.5,0,12.2),64)
render('entry_ground_r3',(27,-44,9),(2.5,0,4.3),25)
render('interior_cutaway_r3',(35,-48,20),(-7.5,0,6.0),62,True)

for obj in (ground,sun,fill):
    data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
    if data.users==0:(bpy.data.meshes if isinstance(data,bpy.types.Mesh) else bpy.data.lights).remove(data)
for obj,val in hidden_lights:obj.hide_render=val
print('R3 views rendered to',out)
