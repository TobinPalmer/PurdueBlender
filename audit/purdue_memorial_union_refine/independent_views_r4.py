import bpy,os,json,hashlib
from mathutils import Vector
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap";ASSET=os.path.join(ROOT,'modular','buildings','purdue_memorial_union.blend');OUT=os.path.join(ROOT,'audit','purdue_memorial_union_refine')
bpy.ops.wm.open_mainfile(filepath=ASSET);scene=bpy.context.scene
def point(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('PMU_R4_Grader_Camera');cam=bpy.data.objects.new('PMU_R4_Grader_Camera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.ortho_scale=145
world=scene.world or bpy.data.worlds.new('PMU_R4_Grader_World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.07,.075,.085,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
for n,loc,power,size,color in [('key',(-60,-100,90),900,55,(1,.88,.75)),('fill',(80,-60,50),550,55,(.72,.82,1)),('rim',(10,70,85),900,50,(1,.9,.78))]:
 d=bpy.data.lights.new('PMU_R4_Grader_'+n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new('PMU_R4_Grader_'+n,d);scene.collection.objects.link(o);o.location=loc;point(o,(0,-5,10))
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=32;scene.render.resolution_x=1300;scene.render.resolution_y=950;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.render.film_transparent=False
for n,loc,target,scale in [('grader_south_oblique_r4',(75,-150,60),(0,-2,12),145),('grader_west_oblique_r4',(-150,-30,60),(0,-2,12),145),('grader_roof_r4',(0,-20,220),(0,0,10),145),('grader_courtyard_r4',(80,-125,65),(2,5,12),120)]:
 cam.location=loc;point(cam,target);cd.ortho_scale=scale;scene.render.filepath=os.path.join(OUT,n+'.png');bpy.ops.render.render(write_still=True)
print('Fresh R4 evaluator views rendered from saved asset.')
