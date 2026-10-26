import bpy, math
from mathutils import Vector
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=96
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
w=s.world;w.use_nodes=True;bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(0.22,.27,.34,1);bg.inputs['Strength'].default_value=.48
for o in bpy.data.objects:
 n=o.name
 o.hide_render=not (o.type=='MESH' and n.startswith('Tark_Dorm_') and '_Representative_' not in n and '_Wall_' not in n and 'Door' not in n)
# Flat plan-view lighting emphasizes the documented room program and furnishings.
ld=bpy.data.lights.new('Room118_PlanSoftbox','AREA');ld.energy=5000;ld.shape='DISK';ld.size=8
l=bpy.data.objects.new('Room118_PlanSoftbox',ld);s.collection.objects.link(l);l.location=(-38,-31,16);l.rotation_euler=(0,0,0)
cd=bpy.data.cameras.new('Room118_PlanCamera');cd.type='ORTHO';cd.ortho_scale=8.1
cam=bpy.data.objects.new('Room118_PlanCamera',cd);s.collection.objects.link(cam);t=Vector((-37.4,-31,0));c=Vector((-37.4,-31,21));cam.location=c;cam.rotation_euler=(t-c).to_track_quat('-Z','Y').to_euler();s.camera=cam
s.render.filepath='//room118_plan_evidence_r4.png';bpy.ops.render.render(write_still=True)
