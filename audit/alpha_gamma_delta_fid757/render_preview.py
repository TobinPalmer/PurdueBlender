import bpy, os
from mathutils import Vector
here=os.path.dirname(__file__)
asset=os.path.join(here,'candidate_alpha_gamma_delta.blend')
bpy.ops.wm.open_mainfile(filepath=asset)
obj=bpy.data.objects.get('House_301841608')
if obj is None: raise RuntimeError('AGD object missing')
world=[obj.matrix_world@Vector(c) for c in obj.bound_box];lo=Vector(tuple(min(v[i] for v in world) for i in range(3)));hi=Vector(tuple(max(v[i] for v in world) for i in range(3)));center=(lo+hi)*.5;size=max(hi-lo)
scene=bpy.context.scene
camdata=bpy.data.cameras.new('AGD_PreviewCamera');cam=bpy.data.objects.new('AGD_PreviewCamera',camdata);scene.collection.objects.link(cam);cam.location=center+Vector((-size*.65,-size*1.8,size*.75));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=size*1.18;scene.camera=cam
for name,loc,power,area in [('Key',center+Vector((-size,size,size*1.8)),size*size*.055,size*1.25),('Fill',center+Vector((size*.7,-size*.2,size)),size*size*.025,size*1.5)]:
    ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=area;o=bpy.data.objects.new(name,ld);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
gmat=bpy.data.materials.new('AGD_PreviewGround');gmat.diffuse_color=(.18,.21,.16,1);gmat.use_nodes=True;gmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.18,.21,.16,1);bpy.ops.mesh.primitive_plane_add(size=220,location=(center.x,center.y,-.04));bpy.context.object.name='AGD_PreviewGround';bpy.context.object.data.materials.append(gmat)
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=64;scene.render.film_transparent=False;scene.world.color=(.035,.035,.035);scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.7
if scene.world and scene.world.use_nodes:
    bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.12,.13,.15,1);bg.inputs['Strength'].default_value=.25
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(here,'preview_exterior.png');bpy.ops.render.render(write_still=True);print('PREVIEW='+scene.render.filepath)



