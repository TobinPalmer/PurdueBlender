import bpy, math, os
from mathutils import Vector
here=os.path.dirname(__file__)
obj=bpy.data.objects.get('Schleman Hall (SCHM)')
if obj is None: raise RuntimeError('Schleman asset object missing')
# Build a temporary view-only shell with the two near facades and roof opened.
cut=obj.copy(); cut.data=obj.data.copy(); bpy.context.scene.collection.objects.link(cut); cut.name='Cutaway validation duplicate (temporary)'
me=cut.data
coords=[obj.matrix_world @ v.co for v in me.vertices]
lo=Vector(tuple(min(v[i] for v in coords) for i in range(3))); hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
# The west and south perimeter walls are opened for the interior view. Roof slopes are removed.
remove=[]
for p in me.polygons:
    c=p.center; n=p.normal
    near_west=(n.x < -0.65 and c.x < lo.x+1.0 and 0.0 < c.z < 11.5)
    near_south=(n.y < -0.65 and c.y < lo.y+1.0 and 0.0 < c.z < 11.5)
    roof=(c.z > 11.05)
    if near_west or near_south or roof: remove.append(p.index)
import bmesh
bm=bmesh.new(); bm.from_mesh(me)
fs=[f for f in bm.faces if f.index in set(remove)]
bmesh.ops.delete(bm,geom=fs,context='FACES_ONLY'); bm.to_mesh(me); bm.free(); me.update()
obj.hide_render=True
center=(lo+hi)*.5; size=max(hi-lo)
# Camera from southwest elevated angle peers through the two opened sides.
cd=bpy.data.cameras.new('SchlemanCutawayCamera'); cam=bpy.data.objects.new('SchlemanCutawayCamera',cd); bpy.context.scene.collection.objects.link(cam)
cam.location=center+Vector((-size*1.05,-size*0.95,size*.76)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cd.type='ORTHO'; cd.ortho_scale=size*1.25
scene=bpy.context.scene; scene.camera=cam
# Neutral ground and soft interior-friendly light.
gmat=bpy.data.materials.new('CutawayPreviewGround');gmat.diffuse_color=(.16,.18,.17,1);gmat.use_nodes=True;gmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.16,.18,.17,1)
bpy.ops.mesh.primitive_plane_add(size=180,location=(center.x,center.y,-.04));ground=bpy.context.object;ground.name='CutawayPreviewGround';ground.data.materials.append(gmat)
for name,loc,power,area in [('CutawayKey',center+Vector((-size*.8,-size*.5,size*1.5)),size*size*.12,size*1.0),('CutawayFill',center+Vector((size*.65,size*.4,size*.8)),size*size*.08,size*1.0),('CutawayInterior',center+Vector((0,0,size*.7)),size*size*.075,size*.35)]:
    ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=area;lo_obj=bpy.data.objects.new(name,ld);scene.collection.objects.link(lo_obj);lo_obj.location=loc;lo_obj.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=64
scene.world.color=(.035,.035,.035);scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.35;scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(here,'preview_cutaway_interior.png');scene.camera.data.lens=50
bpy.ops.render.render(write_still=True)
print('CUTAWAY_PREVIEW='+scene.render.filepath+' removed_faces='+str(len(remove))+' duplicate_faces='+str(len(cut.data.polygons)))


