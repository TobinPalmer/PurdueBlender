import bpy, math, pathlib, json
from mathutils import Vector, Euler
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); A=P/'audit/batch3_elliott'; src=P/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(src)); s=bpy.context.scene; c=bpy.data.collections['Asset_elliott_hall_of_music']
# Keep the pending interface status in evidence notes; remove the overlapping in-scene review label.
status=bpy.data.objects.get('ELLT_R8_Interface_Status_ReviewOnly')
if status: bpy.data.objects.remove(status,do_unlink=True)
# Estimated limestone shelf brackets visually support the isolated Elliott-side landing.
# Geometry remains explicitly an estimate and does not claim route continuity to Hovde.
mat=bpy.data.materials.get('ELLT_R8_Limestone')
if not mat:
 mat=bpy.data.materials.new('ELLT_R9_Estimated_Limestone_Corbel'); mat.diffuse_color=(0.62,0.58,0.49,1)
# Align two simple triangular corbels under the existing landing, on outward facade side.
t=Vector((0.63281,-0.77431,0)); n=Vector((0.77431,0.63281,0)); origin=Vector((44.075,9.162,0))
for i,off in enumerate((-1.2,1.2),1):
 center=origin+t*off
 # wedge runs from wall plane to landing outer edge; triangular side profile, 0.48m width
 v=[(0,-.24,0),(0,.24,0),(0,.24,.44),(1.46,.24,0),(1.46,-.24,0),(1.46,-.24,.44)]
 # local axes: X outward, Y along facade tangent, Z vertical. top face projects to landing underside.
 mesh=bpy.data.meshes.new(f'ELLT_R9_Estimated_Landing_Corbel_{i:02d}_Mesh'); mesh.from_pydata(v,[],[(0,1,2,3,4,5),(0,4,3),(0,3,2),(2,3,5),(0,2,5,1),(4,5,3)]); mesh.update()
 ob=bpy.data.objects.new(f'ELLT_R9_Estimated_Landing_Corbel_{i:02d}',mesh); c.objects.link(ob)
 # local x outward, local y tangent. Build 3D orientation basis.
 from mathutils import Matrix
 x=Vector((n.x,n.y,0)); y=Vector((t.x,t.y,0)); z=Vector((0,0,1))
 ob.matrix_world=Matrix(((x.x,y.x,z.x,center.x),(x.y,y.y,z.y,center.y),(x.z,y.z,z.z,3.53),(0,0,0,1)))
 ob.data.materials.append(mat)
 ob['evidence_status']='estimated support under Elliott-only interface landing; dimensions not sourced; Hovde portal and route continuity deferred'
# Save asset changes.
bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Render configuration
s.render.engine='BLENDER_EEVEE'; s.render.resolution_x=1600; s.render.resolution_y=1050; s.render.resolution_percentage=100; s.eevee.taa_render_samples=48
s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'; s.view_settings.exposure=1.0
# render tools only, restore hide_render after each render

def do_render(name,loc,target,scale,allow=None, prefixes=(), res=(1600,1050), camera_rot=None):
 old=[]
 for o in s.objects:
  hide=(allow is not None and o.name not in allow) or any(o.name.startswith(p) for p in prefixes)
  if hide: old.append((o,o.hide_render)); o.hide_render=True
 d=bpy.data.cameras.new('TEMP_R9_'+name); d.type='ORTHO'; d.ortho_scale=scale
 cam=bpy.data.objects.new('TEMP_R9_'+name,d); s.collection.objects.link(cam); cam.location=loc
 q=(Vector(target)-cam.location).to_track_quat('-Z','Y')
 if camera_rot is not None: q=q @ Euler((0,0,camera_rot),'XYZ').to_quaternion()
 cam.rotation_euler=q.to_euler(); s.camera=cam
 s.render.resolution_x,s.render.resolution_y=res; s.render.filepath=str(A/(name+'.png')); bpy.ops.render.render(write_still=True)
 for o,v in old:o.hide_render=v
 bpy.data.objects.remove(cam,do_unlink=True); bpy.data.cameras.remove(d)
# Entry detail from the exterior approach; clean wall/door read, no embedded deferred label.
ring=json.load(open(A/'polygon.json')); area=.5*sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring))); best=(1e9,None)
for i,a in enumerate(ring):
 b=ring[(i+1)%len(ring)]; dx=b[0]-a[0]; dy=b[1]-a[1]; den=dx*dx+dy*dy; u=max(0,min(1,((44.075-a[0])*dx+(9.162-a[1])*dy)/den)); pp=(a[0]+u*dx,a[1]+u*dy); dist=math.dist(pp,(44.075,9.162))
 if dist<best[0]:
  L=math.hypot(dx,dy); tangent=(dx/L,dy/L); normal=(tangent[1],-tangent[0]) if area>0 else (-tangent[1],tangent[0]); best=(dist,(pp,tangent,normal))
p,t,n=best[1]
ld=bpy.data.lights.new('TEMP_R9_Entry_Fill','AREA'); ld.energy=6500; ld.shape='DISK'; ld.size=16
light=bpy.data.objects.new('TEMP_R9_Entry_Fill',ld); s.collection.objects.link(light); light.location=(p[0]+n[0]*11,p[1]+n[1]*11,11); light.rotation_euler=(Vector((p[0],p[1],5.5))-light.location).to_track_quat('-Z','Y').to_euler()
# Area light excluded by scene object visibility? hide during auditorium, but entry too. keep enabled.
render_allow={o.name for o in s.objects if o.name not in {'ELLT_R4_Hovde_Walkway_Connector_Estimated','ELLT_R8_Interface_Status_ReviewOnly'}}
# Entry all architecture, tighter orthographic detail.
do_render('entry_portal_round9',(p[0]+n[0]*17,p[1]+n[1]*17,10.5),(p[0]+n[0]*.3,p[1]+n[1]*.3,5.8),13.5,allow=render_allow,prefixes=('TEMP_R9_'))
# Interior objects only for legible seating/stage evidence.
interior={o.name for o in s.objects if o.name.startswith('ELLT_B3_') and any(k in o.name.lower() for k in ('seat','stage','curtain','balcony','rail','stair','carpet','plaster','frame','aisle','wall','ceiling'))}
# Remove the ceiling from these cutaway renders.
interior={x for x in interior if 'ceiling' not in x.lower()}
# Hidden structural-shell remnants from the old model are omitted.
ld2=bpy.data.lights.new('TEMP_R9_Auditorium_Fill','AREA'); ld2.energy=32000; ld2.shape='DISK'; ld2.size=35
li=bpy.data.objects.new('TEMP_R9_Auditorium_Fill',ld2); s.collection.objects.link(li); li.location=(0,0,27)
for obj in s.objects:
 if obj.type=='LIGHT' and obj.name.startswith('TEMP_R9_'): obj.hide_render=True
li.hide_render=False
s.world.color=(0.22,0.22,0.22)
if s.world.use_nodes:
 bg=s.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.32,0.34,0.38,1); bg.inputs['Strength'].default_value=0.8
# Render audience looking from the rear, elevated and centered on central aisle.
do_render('interior_audience_round9',(-20,-28,17),(4,10,6.5),58,allow=interior,res=(1600,1050),prefixes=('TEMP_R9_'))
# Top-down full plan, north-up local axes corrected for the asset's ~-129 degree orientation.
do_render('interior_plan_round9',(0,0,100),(0,0,6),88,allow=interior,res=(1600,1250),camera_rot=math.radians(50.64),prefixes=('TEMP_R9_'))
# Remove render-only objects and restore global render settings to avoid saving cameras/lights.
for ob in list(s.objects):
 if ob.name.startswith('TEMP_R9_'):
  data=ob.data; bpy.data.objects.remove(ob,do_unlink=True)
  if data and data.users==0:
   (bpy.data.cameras if data.type=='CAMERA' else bpy.data.lights).remove(data)
# reopen is performed in separate process after save.
print(json.dumps({'saved':str(src),'mesh_objects':sum(o.type=='MESH' for o in c.objects),'round9_additions':[o.name for o in c.objects if o.name.startswith('ELLT_R9_')],'interior_allowlist':sorted(interior),'renders':['entry_portal_round9.png','interior_audience_round9.png','interior_plan_round9.png']}))
