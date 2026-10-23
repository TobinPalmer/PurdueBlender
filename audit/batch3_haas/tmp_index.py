import bpy
from mathutils import Vector
S=bpy.context.scene;C=bpy.data.collections['Asset_felix_haas_hall']
for i,o in enumerate(bpy.data.objects,1):o.pass_index=i
vl=bpy.context.view_layer;vl.use_pass_object_index=True
S.render.engine='CYCLES';S.cycles.samples=1;S.render.resolution_x=600;S.render.resolution_y=420;S.render.resolution_percentage=100
camd=bpy.data.cameras.new('idxcam');cam=bpy.data.objects.new('idxcam',camd);S.collection.objects.link(cam);S.camera=cam;camd.type='ORTHO';camd.ortho_scale=68;cam.location=(-6,72,19);cam.rotation_euler=(Vector((-6,0,5))-cam.location).to_track_quat('-Z','Y').to_euler()
S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/north_index.png';bpy.ops.render.render(write_still=True)
rr=bpy.data.images['Render Result'];ps=rr.view_layers[0].passes.get('IndexOB')
print('pass',ps, len(ps.rect) if ps else None)
if ps:
 data=list(ps.rect);w=600;h=420
 for xy in [(130,155),(140,160),(165,155),(180,150),(200,150)]:
  x,y=xy;idx=int(data[(h-1-y)*w+x][0]);obj=next((o for o in bpy.data.objects if o.pass_index==idx),None);print(xy,idx,obj.name if obj else 'none')
