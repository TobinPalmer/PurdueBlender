import bpy,os,math,json
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))
AUDIT=os.path.join(ROOT,'audit','massing_johnson_hall_of_nursing_jnsn_823fca7')
ID='massing_johnson_hall_of_nursing_jnsn_823fca7'; scene=bpy.data.scenes['Building_'+ID]; coll=bpy.data.collections['Asset_'+ID]
ob=next(o for o in coll.objects if o.type=='MESH')
deps=bpy.context.evaluated_depsgraph_get(); ev=ob.evaluated_get(deps); me=ev.to_mesh(); pts=[ev.matrix_world@v.co for v in me.vertices]; ev.to_mesh_clear()
center=Vector((sum(p.x for p in pts)/len(pts),sum(p.y for p in pts)/len(pts),sum(p.z for p in pts)/len(pts)))
for o in list(bpy.data.objects):
 if o.name.startswith('JNSN preview'): bpy.data.objects.remove(o,do_unlink=True)
camd=bpy.data.cameras.new('JNSN preview camera'); cam=bpy.data.objects.new('JNSN preview camera',camd); scene.collection.objects.link(cam); cam.location=center+Vector((-75,-95,55)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=95; scene.camera=cam
ld=bpy.data.lights.new('JNSN preview light','AREA'); lo=bpy.data.objects.new('JNSN preview light',ld);scene.collection.objects.link(lo);lo.location=center+Vector((-50,-60,80)); lo.rotation_euler=(center-lo.location).to_track_quat('-Z','Y').to_euler();ld.energy=5500;ld.size=55
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD';scene.display.shading.background_color=(.64,.67,.70)
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(AUDIT,'renders','jnsn_before_exterior.png');bpy.ops.render.render(write_still=True)
cam.location=Vector((center.x,center.y,center.z+145));cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=80;scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.filepath=os.path.join(AUDIT,'renders','jnsn_before_plan.png');bpy.ops.render.render(write_still=True)
print('JNSN_BEFORE_RENDER',json.dumps({'center':list(center),'render_paths':[scene.render.filepath]}))
