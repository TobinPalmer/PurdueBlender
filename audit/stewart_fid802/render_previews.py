import bpy, math, os
from mathutils import Vector

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT=os.path.join(ROOT,"audit","stewart_fid802")
ASSET=os.path.join(ROOT,"modular","buildings","massing_house_1089875810_8c9b95d.blend")
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
scene.view_settings.exposure=0; scene.view_settings.gamma=1
scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Color'].default_value=(.30,.27,.22,1); bg.inputs['Strength'].default_value=.16
for o in list(bpy.data.objects):
    if o.type in {'CAMERA','LIGHT'} or o.name.startswith('Stewart_Temp'):
        bpy.data.objects.remove(o,do_unlink=True)
cx=-99.597; cy=688.313
center=Vector((cx,cy,5.6))
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('StewartPreviewCamera'); cam=bpy.data.objects.new('StewartPreviewCamera',camd); scene.collection.objects.link(cam)
scene.camera=cam; cam.data.type='ORTHO'; cam.data.ortho_scale=36
lightd=bpy.data.lights.new('StewartSoftbox','AREA'); light=bpy.data.objects.new('StewartSoftbox',lightd); scene.collection.objects.link(light)
light.location=center+Vector((-28,-30,40)); light.data.energy=2200; light.data.shape='DISK'; light.data.size=24; light.data.color=(1.0,.88,.72); aim(light,center)
sund=bpy.data.lights.new('StewartDirectional','SUN'); sun=bpy.data.objects.new('StewartDirectional',sund); scene.collection.objects.link(sun)
sun.location=center+Vector((-50,-60,80)); sun.data.energy=.28; sun.data.angle=math.radians(18); aim(sun,center)
# Temporary neutral studio ground, excluded from saved asset.
bpy.ops.mesh.primitive_plane_add(size=300,location=(cx,cy,-2.50))
ground=bpy.context.object; ground.name='Stewart_Temp_Ground'
gm=bpy.data.materials.new('Stewart_Temp_Ground_Material'); gm.diffuse_color=(.14,.16,.18,1); gm.use_nodes=True
gbs=next(n for n in gm.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); gbs.inputs['Base Color'].default_value=(.14,.16,.18,1); gbs.inputs['Roughness'].default_value=.95
ground.data.materials.append(gm)

def render(name,offset,target,ortho=36):
    cam.location=Vector(target)+Vector(offset); aim(cam,target); cam.data.ortho_scale=ortho
    scene.render.filepath=os.path.join(AUDIT,name)
    bpy.ops.render.render(write_still=True)

render('exterior_west_oblique.png',(-37,-18,23),(cx,cy,5.6),36)
render('exterior_south_oblique.png',(0,-42,23),(cx,cy,5.6),36)
render('roof_plan_view.png',(0,0,55),(cx,cy,5.3),35)

roof=bpy.data.objects.get('House_1089875810_roof')
chimney=bpy.data.objects.get('House_1089875810_chimney')
if roof: roof.hide_render=True
if chimney: chimney.hide_render=True
interior_objects=[o for o in bpy.data.objects if o.name.startswith('House_1089875810_schematic_interior_')]
shell=bpy.data.objects.get('House_1089875810')
if shell: shell.hide_render=True
for o in interior_objects: o.hide_render=True
ground.hide_render=True
# Workbench shading is used for the schematic interior plans so their
# partitions and use cues remain legible without EEVEE lighting variation.
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.background_type='WORLD'
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='WORLD'
scene.display.shading.curvature_ridge_factor=1.2
scene.display.shading.curvature_valley_factor=1.0
scene.world.color=(.17,.17,.16)
# Temporarily display only the chosen level as an exact-footprint plan.
for story,z in [('basement',-2.45),('ground',.12),('second',3.02),('third',5.92)]:
    for o in interior_objects: o.hide_render=(not o.name.endswith(story))
    for floor in [o for o in bpy.data.objects if 'schematic_floor_' in o.name]: floor.hide_render=(not floor.name.endswith(story))
    render('interior_'+story+'_plan.png',(0,0,50),(cx,cy,z+.1),32)

print('Rendered Stewart exterior, roof plan, and level-specific schematic interior views.')
