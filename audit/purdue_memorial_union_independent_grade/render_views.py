import bpy, math
from mathutils import Vector
from pathlib import Path
asset=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
outdir=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\purdue_memorial_union_independent_grade')
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
col=bpy.data.collections['Asset_purdue_memorial_union']
# Only show asset collection during the evidence render.
for c in bpy.data.collections:
    c.hide_render=(c!=col and c.name!='Collection')
# Hide pre-existing debug lights and create controlled studio lighting.
for o in list(scene.objects):
    if o.type in {'LIGHT','CAMERA'}: o.hide_render=True
light_data=bpy.data.lights.new('Grade_Sun','SUN'); light_data.energy=2.0
light=bpy.data.objects.new('Grade_Sun',light_data); scene.collection.objects.link(light)
light.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-25))
fill_data=bpy.data.lights.new('Grade_Fill','AREA'); fill_data.energy=1800; fill_data.shape='DISK'; fill_data.size=45
fill=bpy.data.objects.new('Grade_Fill',fill_data); scene.collection.objects.link(fill); fill.location=(70,-40,85)
fill.rotation_euler=(Vector((0,0,12))-fill.location).to_track_quat('-Z','Y').to_euler()
# World and render.
world=bpy.data.worlds.new('Grade_World') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.22,0.25,0.30,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.7
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=32
scene.render.resolution_x=1000; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
target=Vector((0,0,12))
views=[('oblique',(145,-170,105),165),('south',(0,-205,48),155),('west',(-205,0,48),155),('top',(0,-10,260),180)]
for name,pos,scale in views:
    camd=bpy.data.cameras.new('GradeCamera_'+name); camd.type='ORTHO'; camd.ortho_scale=scale
    cam=bpy.data.objects.new('GradeCamera_'+name,camd); scene.collection.objects.link(cam); cam.location=pos
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); scene.camera=cam
    scene.render.filepath=str(outdir/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True)
print('Rendered:',[str(outdir/(n+'.png')) for n,_,_ in views])

