import bpy, os, bmesh
from mathutils import Vector
here=os.path.dirname(__file__);bpy.ops.wm.open_mainfile(filepath=os.path.join(here,'candidate_alpha_gamma_delta.blend'))
obj=bpy.data.objects.get('House_301841608');assert obj
verts=[obj.matrix_world@Vector(c) for c in obj.bound_box];lo=Vector(tuple(min(v[i] for v in verts) for i in range(3)));hi=Vector(tuple(max(v[i] for v in verts) for i in range(3)));center=(lo+hi)*.5;size=max(hi-lo)
cut=obj.copy();cut.data=obj.data.copy();bpy.context.scene.collection.objects.link(cut);cut.name='AGD_InteriorPlan_preview_only';me=cut.data
keep={'AGD_floor','AGD_interior','AGD_wood','AGD_rug','AGD_upholstery','AGD_red','AGD_gold','AGD_dark'}
remove=set()
for p in me.polygons:
    m=me.materials[p.material_index].name if p.material_index<len(me.materials) and me.materials[p.material_index] else ''
    if p.center.z>3.45 or m not in keep: remove.add(p.index)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index in remove],context='FACES_ONLY');bm.to_mesh(me);bm.free();me.update();obj.hide_render=True
scene=bpy.context.scene;camd=bpy.data.cameras.new('AGD_InteriorPlanCamera');cam=bpy.data.objects.new('AGD_InteriorPlanCamera',camd);scene.collection.objects.link(cam);cam.location=(center.x,center.y,42);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=max(40,size*.82);scene.camera=cam
for name,loc,power,area in [('InteriorPlanKey',(center.x-10,center.y-8,28),12000,36),('InteriorPlanFill',(center.x+10,center.y+8,24),7000,40)]:
 ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=area;o=bpy.data.objects.new(name,ld);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((center.x,center.y,0))-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.eevee.taa_render_samples=64;scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(here,'preview_interior_schematic.png');scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.85;scene.world.color=(.06,.06,.06);bpy.ops.render.render(write_still=True);print('INTERIOR_PREVIEW='+scene.render.filepath)
