import bpy, json, os
from mathutils import Vector
here=os.path.dirname(__file__)
cfg=json.load(open(os.path.join(here,'build_config.json'),encoding='utf8'))
obj=bpy.data.objects.get(cfg['object_name'])
if obj is None: raise RuntimeError('Target asset missing')
verts=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
lo=Vector(tuple(min(v[i] for v in verts) for i in range(3))); hi=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
center=(lo+hi)*0.5; size=max(hi-lo); cam_data=bpy.data.cameras.new('PreviewCamera'); cam=bpy.data.objects.new('PreviewCamera',cam_data); bpy.context.scene.collection.objects.link(cam)
cam.location=center+Vector((-size*1.45,-size*1.65,size*1.05)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.type='ORTHO'; cam_data.ortho_scale=size*1.52; bpy.context.scene.camera=cam
for name,loc,power,area in [('Key',center+Vector((-size,-size,size*2)),size*size*0.45,size*1.2),('Fill',center+Vector((size,size*0.6,size)),size*size*0.18,size*1.5)]:
 ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=area; lo_obj=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(lo_obj); lo_obj.location=loc; lo_obj.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=32; scene.render.resolution_x=1120; scene.render.resolution_y=840; scene.render.resolution_percentage=100
scene.world.color=(0.035,0.035,0.035); scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(here,'preview_detail.png'); scene.camera.data.lens=50
bpy.ops.render.render(write_still=True)
# A separate close view makes the small entrance portal and archive-described relief inspectable.
feature=json.load(open(os.path.join(here,cfg['source_feature_file']),encoding='utf8'))
ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
pts=[Vector(((lon-(-86.9137))*111412.84*__import__('math').cos(__import__('math').radians(40.4274)),(lat-40.4274)*111040.0)) for lon,lat in ring]
area2=sum(pts[i].x*pts[(i+1)%len(pts)].y-pts[(i+1)%len(pts)].x*pts[i].y for i in range(len(pts))); sign=1.0 if area2>0 else -1.0
edges=[]
for i,a in enumerate(pts):
 b=pts[(i+1)%len(pts)]; delta=b-a; length=delta.length
 if length>5:
  tangent=Vector((delta.x/length,delta.y/length,0)); normal=Vector((tangent.y,-tangent.x,0))*sign
  if normal.x < -0.7: edges.append((length,a,b,tangent,normal))
if edges:
 length,a,b,tangent,normal=max(edges,key=lambda e:e[0]); midpoint=(a+b)*0.5
 target=Vector((midpoint.x,midpoint.y,3.5))+normal*0.25
 cam.location=target+normal*8+Vector((0,0,2.0)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.ortho_scale=6.8
 scene.render.filepath=os.path.join(here,'preview_entrance.png'); bpy.ops.render.render(write_still=True)
print('PREVIEW_RENDER='+os.path.join(here,'preview_detail.png'))

