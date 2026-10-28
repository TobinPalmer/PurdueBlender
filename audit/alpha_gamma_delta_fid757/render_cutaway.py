import bpy, os, bmesh
from mathutils import Vector
here=os.path.dirname(__file__);bpy.ops.wm.open_mainfile(filepath=os.path.join(here,'candidate_alpha_gamma_delta.blend'))
obj=bpy.data.objects.get('House_301841608');assert obj
pts=[obj.matrix_world@Vector(c) for c in obj.bound_box];lo=Vector(tuple(min(v[i] for v in pts) for i in range(3)));hi=Vector(tuple(max(v[i] for v in pts) for i in range(3)));center=(lo+hi)*.5;size=max(hi-lo)
cut=obj.copy();cut.data=obj.data.copy();bpy.context.scene.collection.objects.link(cut);cut.name='AGD_Cutaway_preview_only';me=cut.data
remove=set(); floor_slots={i for i,m in enumerate(me.materials) if m and m.name=='AGD_floor'}
for p in me.polygons:
 c=p.center;n=p.normal
 roof=c.z>7.05 or (p.material_index in floor_slots and c.z>3.4 and n.z>.55)
 west=n.x<-.65 and c.x<lo.x+1.0 and 0<c.z<7.05
 south=n.y<-.65 and c.y<lo.y+1.0 and 0<c.z<7.05
 if roof or west or south: remove.add(p.index)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index in remove],context='FACES_ONLY');bm.to_mesh(me);bm.free();me.update();obj.hide_render=True
scene=bpy.context.scene;camd=bpy.data.cameras.new('AGD_CutawayCamera');cam=bpy.data.objects.new('AGD_CutawayCamera',camd);scene.collection.objects.link(cam);cam.location=center+Vector((-size*1.35,-size*1.25,size*1.1));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=size*1.25;scene.camera=cam
for name,loc,power,area in [('CutawayKey',center+Vector((-size*.5,-size*.3,size*1.8)),size*size*.12,size*1.2),('CutawayFill',center+Vector((size*.4,size*.5,size)),size*size*.08,size*1.5)]:
 ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=area;o=bpy.data.objects.new(name,ld);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
gmat=bpy.data.materials.new('AGD_CutawayGround');gmat.diffuse_color=(.15,.16,.14,1);gmat.use_nodes=True;gmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.15,.16,.14,1);bpy.ops.mesh.primitive_plane_add(size=220,location=(center.x,center.y,-.04));bpy.context.object.data.materials.append(gmat)
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=64;scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(here,'preview_cutaway_interior.png');scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.65;scene.world.color=(.035,.035,.035);bpy.ops.render.render(write_still=True);print('CUTAWAY='+scene.render.filepath+' removed='+str(len(remove)))

