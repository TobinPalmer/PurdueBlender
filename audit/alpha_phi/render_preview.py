import bpy,json,math,os
from pathlib import Path
from mathutils import Vector
audit=Path(__file__).resolve().parent
feature=json.loads((audit/'sources'/'purdue_gis_fid764_raw.json').read_text(encoding='utf-8-sig'))['features'][0]
ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
lat0,lon0=40.4274,-86.9137
pts=[Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.,0)) for lon,lat in ring]
area2=sum(pts[i].x*pts[(i+1)%len(pts)].y-pts[(i+1)%len(pts)].x*pts[i].y for i in range(len(pts)))
sign=1 if area2>0 else -1
edges=[]
for i,a in enumerate(pts):
 b=pts[(i+1)%len(pts)]; d=b-a;t=Vector((d.x,d.y,0)).normalized();n=Vector((t.y,-t.x,0))*sign;edges.append((d.length,t,n))
_,t,n=max(edges,key=lambda e:e[0])
obj=bpy.data.objects['House_301841331']; cloud=[obj.matrix_world@v.co for v in obj.data.vertices]
low=Vector(tuple(min(p[i] for p in cloud) for i in range(3))); high=Vector(tuple(max(p[i] for p in cloud) for i in range(3))); center=(low+high)*0.5; span=max(high.x-low.x,high.y-low.y,high.z-low.z)
scene=bpy.context.scene
camd=bpy.data.cameras.new('AlphaPhi_Preview_Camera'); cam=bpy.data.objects.new('AlphaPhi_Preview_Camera',camd); scene.collection.objects.link(cam)
cam.location=center+n*span*1.35-t*span*0.22+Vector((0,0,span*0.38)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=span*1.42; scene.camera=cam
ld=bpy.data.lights.new('AlphaPhi_Preview_Area','AREA'); light=bpy.data.objects.new('AlphaPhi_Preview_Area',ld); scene.collection.objects.link(light); light.location=center+n*span*0.7-t*span*0.9+Vector((0,0,span*1.5)); light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler(); ld.energy=span*span*0.02; ld.size=span*0.85
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(audit/'preview.png'); scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.12,0.12,0.12,1); bg.inputs['Strength'].default_value=0.45; scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=-0.10
bpy.ops.render.render(write_still=True); print('RENDERED='+scene.render.filepath)
