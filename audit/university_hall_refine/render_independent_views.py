import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
outdir=root/'audit/university_hall_refine'
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=32
scene.render.resolution_x=1100
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
# Neutral studio background and ground are temporary scene objects; never save the source .blend.
world=bpy.data.worlds.new('ReviewStudioWorld') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.28,0.36,0.48,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.35
# Ground plane at the foot of the actual asset bounds.
mat=bpy.data.materials.new('ReviewGround');mat.diffuse_color=(0.18,0.22,0.20,1);mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.18,0.22,0.20,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.9
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-0.13)); ground=bpy.context.object;ground.name='ReviewGround_Temporary';ground.data.materials.append(mat)
# Sun and soft fill.
bpy.ops.object.light_add(type='SUN', location=(30,-50,80)); sun=bpy.context.object;sun.name='ReviewSun_Temporary';sun.data.energy=3.0;sun.rotation_euler=(math.radians(25),math.radians(-25),math.radians(-30))
bpy.ops.object.light_add(type='AREA', location=(-35,-20,55));fill=bpy.context.object;fill.name='ReviewFill_Temporary';fill.data.energy=1800;fill.data.shape='DISK';fill.data.size=45;fill.rotation_euler=(Vector((0,0,12))-fill.location).to_track_quat('-Z','Y').to_euler()
# Camera helpers.
def camera(name, location, target, ortho=65, lens=52):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    obj.location=location;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=ortho;data.lens=lens;scene.camera=obj
    return obj
views=[
 ('oblique_southwest',(-60,-75,58),(0,0,13),75),
 ('south_elevation',(0,-85,28),(0,0,13),64),
 ('north_elevation',(0,85,28),(0,0,13),64),
 ('east_elevation',(85,0,28),(0,0,13),64),
 ('roof_plan',(0,0,105),(0,0,10),64),
]
for name,loc,target,scale in views:
    cam=camera('ReviewCamera_'+name,loc,target,scale)
    scene.render.filepath=str(outdir/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    camdata=cam.data;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)
# Interior cutaway: hide only the exterior wall/roof shell and show surviving interior geometry.
hidden=[]
for obj in bpy.data.objects:
    n=obj.name.lower()
    if n.startswith('univ_wall_') or n.startswith('univ_mansard_roof') or n.startswith('univ_belfry_roof') or n.startswith('univ_tower_brick') or n.startswith('univ_tower_stone') or n.startswith('univ_roof_'):
        hidden.append((obj,obj.hide_render));obj.hide_render=True
cam=camera('ReviewCamera_interior_cutaway',(55,-70,38),(0,0,9),70)
scene.render.filepath=str(outdir/'interior_cutaway.png')
bpy.ops.render.render(write_still=True)
for obj,value in hidden: obj.hide_render=value
camdata=cam.data;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)
# Remove only our temporary stage objects, keeping source file in memory unchanged on disk.
for obj in [ground,sun,fill]:
    data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
    if data.users==0:
        (bpy.data.meshes if isinstance(data,bpy.types.Mesh) else bpy.data.lights).remove(data)
print('RENDERED',*[str(outdir/(name+'.png')) for name,_,_,_ in views],str(outdir/'interior_cutaway.png'))
