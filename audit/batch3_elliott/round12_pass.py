import bpy, math, json, pathlib
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); A=P/'audit/batch3_elliott'; src=P/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(src)); c=bpy.data.collections['Asset_elliott_hall_of_music']; s=bpy.context.scene
rot=math.radians(-129.36); co=math.cos(rot); si=math.sin(rot)
# Shift the two center seat banks outward from their shared centerline, opening
# the longitudinal aisle. Width is inferred from photo description, not measured.
def ly(v): return -si*v.x + co*v.y
def shift_bank(obj):
 moved=0
 for v in obj.data.vertices:
  y=ly(v.co)
  if -5.76 <= y <= -0.29: delta=-0.40
  elif 0.29 <= y <= 5.76: delta=0.40
  else: continue
  v.co.x += (-si)*delta; v.co.y += co*delta; moved+=1
 obj.data.update(); obj['R12_center_aisle']='Central aisle widened by shifting the two center seat banks outward 0.40 m per side. Width remains estimated from Purdue photo description; not measured from R101.'
 return moved
shift_counts={n:shift_bank(bpy.data.objects[n]) for n in ('ELLT_B3_seat','ELLT_B3_frame','ELLT_B3_carpet')}
# Widen only the stair treads in the central aisle; all seven aisle locations remain.
stairs=bpy.data.objects['ELLT_B3_stair']; widen_count=0
for v in stairs.data.vertices:
 y=ly(v.co)
 if abs(y)<0.38:
  newy=y*(1.5/.7); d=newy-y; v.co.x+=(-si)*d; v.co.y+=co*d; widen_count+=1
stairs.data.update(); stairs['R12_center_aisle']='Central tread flight widened to an estimated 1.5 m to align with central aisle; exact dimensions not recoverable from indexed-only R101.'
# Model the documented pit lift as a clearly schematic lowered platform at the
# audience-facing stage edge. No size/elevation claims; source labels its presence.
def cube(name,loc,dims,matname):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.rotation_euler.z=rot
 for coll in list(o.users_collection): coll.objects.unlink(o)
 c.objects.link(o); o.data.materials.append(bpy.data.materials[matname]); return o
# Local stage front at x ~= -16.2, stage extends towards negative local X.
lx=-14.9; wx=lx*co; wy=lx*si
frame=cube('ELLT_R12_Pit_Lift_Perimeter_Schematic',(wx,wy,.31),(2.55,18.6,.10),'ELLT_B3_Seat_Frame_Dark_Bronze')
frame['evidence']='R101 main-floor drawing callout identifies a pit lift; current location and dimensions are inferred from the modeled stage-front geometry and are schematic.'
panel=cube('ELLT_R12_Pit_Lift_Platform_Schematic',(wx,wy,.38),(2.35,18.25,.08),'ELLT_B3_Stage_Oak_Grain')
panel['evidence']='Schematic stage pit-lift platform, added from R101 pit-lift callout; no dimension or operating position verified.'
# Save only this linked building asset. Preserve source/master placement data.
bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Evidence views: stage-to-audience and straight plan with only auditorium objects.
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=64; s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'; s.view_settings.exposure=.25
s.render.resolution_x=1600; s.render.resolution_y=1050; s.render.resolution_percentage=100
allowed={o.name for o in c.objects if o.name.startswith('ELLT_B3_') or o.name.startswith('ELLT_R12_')}
def render(name,loc,target,scale,roll=0):
 hidden=[]
 for o in s.objects:
  if o.name not in allowed and not o.name.startswith('TEMP_R12_'):
   hidden.append((o,o.hide_render));o.hide_render=True
 cd=bpy.data.cameras.new('TEMP_R12_CAM_'+name);cd.type='ORTHO';cd.ortho_scale=scale;cam=bpy.data.objects.new('TEMP_R12_CAM_'+name,cd);s.collection.objects.link(cam);cam.location=loc
 q=(Vector(target)-cam.location).to_track_quat('-Z','Y')
 if roll: q=q@__import__('mathutils').Euler((0,0,roll),'XYZ').to_quaternion()
 cam.rotation_euler=q.to_euler();s.camera=cam;s.render.filepath=str(A/(name+'.png'));bpy.ops.render.render(write_still=True)
 for o,v in hidden:o.hide_render=v
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)
ld=bpy.data.lights.new('TEMP_R12_Interior_Fill','AREA');ld.energy=38000;ld.shape='DISK';ld.size=38;li=bpy.data.objects.new('TEMP_R12_Interior_Fill',ld);s.collection.objects.link(li);li.location=(0,0,28);li.rotation_euler=(Vector((0,0,6))-li.location).to_track_quat('-Z','Y').to_euler();allowed.add(li.name)
render('interior_central_aisle_round12',(22,29,13),(-8,-8,6.5),66)
render('interior_plan_round12',(0,0,100),(0,0,6),82,math.radians(50.64))
for o in list(s.objects):
 if o.name.startswith('TEMP_R12_'):
  d=o.data; bpy.data.objects.remove(o,do_unlink=True)
  if d and d.users==0:
   (bpy.data.cameras if d.type=='CAMERA' else bpy.data.lights).remove(d)
print(json.dumps({'saved':str(src),'mesh_count':sum(o.type=='MESH' for o in c.objects),'shifted_vertices':shift_counts,'central_tread_vertices_widened':widen_count,'new_objects':[frame.name,panel.name],'renders':['interior_central_aisle_round12.png','interior_plan_round12.png']}))
