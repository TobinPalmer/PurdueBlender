import bpy,os
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
ASSET=os.path.join(ROOT,'modular','buildings','purdue_memorial_union.blend')
OUT=os.path.join(ROOT,'audit','purdue_memorial_union_refine')
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
col=bpy.data.collections['Asset_purdue_memorial_union']
def point(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('PMU_Independent_Grader_Camera'); cam=bpy.data.objects.new('PMU_Independent_Grader_Camera',camdata); scene.collection.objects.link(cam); scene.camera=cam; camdata.type='ORTHO'; camdata.ortho_scale=135
world=scene.world or bpy.data.worlds.new('PMU_Independent_Grader_World'); scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.07,0.075,0.085,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
for name,loc,power,size,color in [('key',(-60,-100,90),900,55,(1,.88,.75)),('fill',(80,-60,50),550,55,(.72,.82,1)),('rim',(10,70,85),900,50,(1,.9,.78))]:
 d=bpy.data.lights.new('PMU_Independent_'+name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.color=color; o=bpy.data.objects.new('PMU_Independent_'+name,d); scene.collection.objects.link(o); o.location=loc; point(o,(0,-5,10))
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=32; scene.render.resolution_x=1300; scene.render.resolution_y=950; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='AgX'; scene.render.film_transparent=False
for name,loc,target,scale in [('grader_south_oblique',(75,-150,60),(0,-2,12),145),('grader_west_oblique',(-150,-30,60),(0,-2,12),145),('grader_roof',(0,-20,220),(0,0,10),145)]:
 cam.location=loc; point(cam,target); camdata.ortho_scale=scale; scene.render.filepath=os.path.join(OUT,name+'.png'); bpy.ops.render.render(write_still=True)
print('Rendered independent views for grading only.')
