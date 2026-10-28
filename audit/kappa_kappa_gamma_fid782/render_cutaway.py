import bpy, bmesh, math, os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
blend=os.path.join(root,'modular','buildings','massing_house_301840871_5d1bc06.blend')
out=os.path.join(os.path.dirname(__file__),'interior_cutaway.png')
bpy.ops.wm.open_mainfile(filepath=blend)
scene=bpy.context.scene; original=bpy.data.objects['House_301840871']
original.hide_render=True
cut=original.copy();cut.data=original.data.copy();cut.name='KKG review-only interior cutaway';scene.collection.objects.link(cut);cut.hide_render=False
# Review-only cut removes the roof/upper sleeping level and the two horizontal
# faces of the first-floor slab. Keeping the room walls and furniture while
# opening this floor makes the common-room layout legible from the camera.
bm=bmesh.new();bm.from_mesh(cut.data);bm.faces.ensure_lookup_table()
remove=[]
for face in bm.faces:
 z=face.calc_center_median().z
 horizontal=all(abs(v.co.z-face.verts[0].co.z)<0.001 for v in face.verts)
 if z>6.90 or (horizontal and (abs(z-3.58)<0.03 or abs(z-3.72)<0.03)):
  remove.append(face)
bmesh.ops.delete(bm,geom=remove,context='FACES')
bm.to_mesh(cut.data);bm.free();cut.data.update()
center=Vector((-391.8,63.3,3.1))
camdata=bpy.data.cameras.new('KKG interior cutaway camera');cam=bpy.data.objects.new('KKG interior cutaway camera',camdata);scene.collection.objects.link(cam)
cam.location=center+Vector((37,-35,37));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=58;scene.camera=cam
for name,loc,energy,size in [('Cutaway key',(-350,35,50),2200,24),('Cutaway fill',(-420,90,45),1500,20)]:
 ld=bpy.data.lights.new(name,'AREA');lo=bpy.data.objects.new(name,ld);scene.collection.objects.link(lo);lo.location=loc;ld.energy=energy;ld.shape='DISK';ld.size=size;lo.rotation_euler=(center-lo.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
shade=scene.display.shading;shade.light='STUDIO';shade.color_type='MATERIAL';shade.show_cavity=True;shade.cavity_type='BOTH';shade.cavity_ridge_factor=1.2;shade.cavity_valley_factor=1.0;shade.show_shadows=False;shade.background_type='WORLD'
scene.render.image_settings.file_format='PNG';scene.render.filepath=out
bpy.ops.render.render(write_still=True)
print('RENDERED',out)
