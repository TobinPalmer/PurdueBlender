import bpy,json,math
from pathlib import Path
p=bpy.data.filepath;c=bpy.data.collections['Asset_felix_haas_hall'];
# Door threshold and door parts move up to a 1.5 m raised first-floor entry.
for o in bpy.data.objects:
 if not any(col.name=='Asset_felix_haas_hall' for col in o.users_collection):continue
 if o.name.startswith(('HAAS_Photo_Main_Door_','HAAS_Photo_Door_Glazing_','HAAS_Photo_Door_Handle_')):o.location.z+=1.0
 if o.name=='HAAS_Photo_Door_Threshold':o.location.z=1.42
 if o.name=='HAAS_Photo_Main_Entry_Arch':
  for sp in o.data.splines:
   for pt in sp.points:pt.co.z+=.9
# Retire three inherited overly tall step blocks; replace with a clear 10-tread approach flight.
for n in ['HAAS_Step_Upper_4','HAAS_Step_Upper_5','HAAS_Step_Upper_6']:
 o=bpy.data.objects.get(n)
 if o and any(col.name=='Asset_felix_haas_hall' for col in o.users_collection):bpy.data.objects.remove(o,do_unlink=True)
for i in range(10):
 o=bpy.data.objects.get('HAAS_Photo_Entry_Stair_Tread_'+str(i))
 if o:
  h=1.5-.15*i;o.dimensions.z=h;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.location.z=h/2
# Rebuild the limestone elevation skin with window apertures and the raised door opening.
o=bpy.data.objects.get('HAAS_Photo_Entrance_Limestone_Facade')
if o:bpy.data.objects.remove(o,do_unlink=True)
stone=bpy.data.materials['HAAS_Photo_Limestone'];ys=set([-12.0,12.0,-4.9,-4.1,4.1,4.9])
for center in [-7.65,0,7.65]:ys.update([center-1.6,center+1.6])
for center in [-7.65,7.65]:ys.update([center-1.5,center+1.5])
ys.update([-1.1,1.1]);ys=sorted(ys);zs=[.45,1.5,3.14,3.9,4.7,5.4,5.8,6.9,8.5,9.1,10.2]
verts=[];faces=[];skip=0
for a,b in zip(ys,ys[1:]):
 ym=(a+b)/2
 for z0,z1 in zip(zs,zs[1:]):
  zm=(z0+z1)/2;hole=False
  if 6.9<=zm<8.5 and any(abs(ym-center)<1.6 for center in [-7.65,0,7.65]):hole=True
  if 1.5<=zm<4.7 and any(abs(ym-center)<1.5 for center in [-7.65,7.65]):hole=True
  if 1.5<=zm<3.9 and abs(ym)<1.1:hole=True
  if abs(ym-4.5)<.4 or abs(ym+4.5)<.4:hole=True
  if hole:skip+=1;continue
  k=len(verts);verts.extend([(13.005,a,z0),(13.005,b,z0),(13.005,b,z1),(13.005,a,z1)]);faces.append((k,k+1,k+2,k+3))
mesh=bpy.data.meshes.new('HAAS_Photo_Limestone_Elevation_Mesh');mesh.from_pydata(verts,[],faces);mesh.update();skin=bpy.data.objects.new('HAAS_Photo_Entrance_Limestone_Facade',mesh);c.objects.link(skin);mesh.materials.append(stone);skin['evidence']='Purdue Felix Haas Hall exterior photo gallery, qualitative elevation https://events.purdue.edu/felix_haas_hall';skin['openings']='Three upper windows; two lower windows; raised central entrance; placements approximate.'
bpy.ops.wm.save_as_mainfile(filepath=p)
Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/entrance_refinement.json').write_text(json.dumps({'raised_door_vertical_delta_m':1.0,'threshold_center_z_m':1.42,'tread_count':10,'tread_height_range_m':[.15,1.5],'removed_duplicate_old_steps':['HAAS_Step_Upper_4','HAAS_Step_Upper_5','HAAS_Step_Upper_6'],'source':'https://events.purdue.edu/felix_haas_hall','elevation_positions_and_stair_rise':'estimated from qualitative exterior photo; GIS outline preserved'},indent=2))
