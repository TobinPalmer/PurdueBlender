"""ME r02: discrete low-wing roof datum and r01 artifact corrections.

Run only after coordinator unlocks the tracked asset. Uses the reviewed r01
input snapshot, preserves all r01 files, saves/reopens modular ME library.
"""
import bpy,math,json,shutil,hashlib
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'audit/mechanical_engineering/second_pass/revision_r02_2026-11-03'
ASSET=ROOT/'modular/buildings/mechanical_engineering.blend'
BASE=OUT/'input_r01.blend'
OUT.mkdir(parents=True,exist_ok=True)
if not BASE.exists():
 expected='5249198727edf3220ffc791233a2bfd2c58a40f78853feacc3513260e3277272'
 if hashlib.sha256(ASSET.read_bytes()).hexdigest()!=expected:raise RuntimeError('Expected independently reviewed r01 input')
 shutil.copy2(ASSET,BASE)
bpy.ops.wm.open_mainfile(filepath=str(BASE))
asset=bpy.data.collections['Asset_mechanical_engineering']

def split(poly,origin,axis,threshold,positive):
 """Half-plane split of a3D polygon, retaining exact interpolated vertices."""
 inside=[];outside=[]
 def d(v):return (((v.x-origin.x)*axis.x+(v.y-origin.y)*axis.y)-threshold)*(1 if positive else -1)
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da,db=d(a),d(b)
  (inside if da>=0 else outside).append(a.copy())
  if (da>=0)!=(db>=0):
   q=a+(b-a)*(da/(da-db));inside.append(q);outside.append(q.copy())
 return inside,outside

def region(poly,origin,t,n,L,W):
 carry=poly;outside=[]
 for axis,threshold,positive in [(t,0,True),(t,L,False),(n,0,True),(n,W,False)]:
  if len(carry)<3:break
  carry,other=split(carry,origin,axis,threshold,positive)
  if len(other)>2:outside.append(other)
 return carry,outside

def rebuild(ob,polys):
 old=ob.data;new=bpy.data.meshes.new(old.name+'_r02');vs=[];fs=[];mi=[]
 for poly,material in polys:
  if len(poly)<3:continue
  normal=Vector((0,0,0))
  for a,b in zip(poly,poly[1:]+poly[:1]):normal+=a.cross(b)
  if normal.length<1e-7:continue
  start=len(vs);vs.extend([tuple(p) for p in poly]);fs.append(tuple(range(start,len(vs))));mi.append(material)
 new.from_pydata(vs,[],fs);new.update()
 for m in old.materials:new.materials.append(m)
 for p,i in zip(new.polygons,mi):p.material_index=i
 ob.data=new

# Official east low bar edges2/3/4, approximately47.8 by15.25m. The2018
# class1 candidate surface median7.72m/p757.85m supports estimated7.8m cap.
ea=Vector((32.46,42.62));eb=Vector((62.699,5.62));et=(eb-ea).normalized();en=Vector((et.y,-et.x));EL=(eb-ea).length;EW=15.25
oa=Vector((-33.66,13.69));ob=Vector((20.27,57.9013));ot=(ob-oa).normalized();on=Vector((ot.y,-ot.x));OL=(ob-oa).length;OW=19.55

# Replace the deformed whole-footprint cap with independently clipped flat
# patches. Main1932 roof retains its r01 physical hip/raised flat centre.
roof=bpy.data.objects['ME_Official_857_Roof'];patches=[]
for face in roof.data.polygons:
 if face.normal.z<.1:continue
 poly=[roof.data.vertices[i].co.copy() for i in face.vertices]
 _,rem=region(poly,oa,ot,on,OL,OW)
 for part in rem:
  low,rest=region(part,ea,et,en,EL,EW)
  if len(low)>2:patches.append(([Vector((p.x,p.y,7.85)) for p in low],0))
  patches.extend([([Vector((p.x,p.y,18.75)) for p in q],1) for q in rest])
rebuild(roof,patches)
membrane=bpy.data.materials['ME_SP_Charcoal_Membrane'];roof.data.materials.clear();roof.data.materials.append(membrane)
roof.data.materials.append(bpy.data.materials['ME_R3_FID857_2023_Orthophoto_Roof'])
# Preserve the existing registered image only on untouched provisional zones.
# This source is appearance evidence; it is not substituted for roof geometry.
reg=json.loads((ROOT/'audit/complete_me/mechanical_engineering_ortho_registration_r2.json').read_text())
xmin,ymin,xmax,ymax=reg['request_bbox_3857'];uv=roof.data.uv_layers.new(name='ME_R3_Ortho_UV')
for loop in roof.data.loops:
 v=roof.data.vertices[loop.vertex_index].co
 lon=-86.9137+(v.x+66.30000114440918)/(111412.84*math.cos(math.radians(40.4274)))
 lat=40.4274+(v.y+86.5)/111040
 mx=6378137*math.radians(lon);my=6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2))
 uv.data[loop.index].uv=((mx-xmin)/(xmax-xmin),(my-ymin)/(ymax-ymin))
roof['r02_status']='Separated constant-datum roof patches.1942 receives plain membrane; existing baked image retained only on untouched provisional zones. Main1932 physical hip retained; modern/1929 geometry still unresolved.'

# Split actual wall faces at wing boundary before clamping the low roof. This
# avoids the r01 mistake of deforming an unsplit long polygon across datums.
changed={}
names=['ME_Official_857_Structural_Envelope','ME_R1_Facade_Window_Glazing','ME_R1_Facade_Window_Frames','ME_R1_Limestone_Window_Sills_And_Stringcourses','ME_Official_857_Estimated_Floor_9','ME_Official_857_Estimated_Floor_13.5']
for name in names:
 obj=bpy.data.objects[name];polys=[];n=0
 margin=.65 if name.startswith('ME_R1_') else 0
 clip_origin=ea-et*margin-en*margin
 for face in obj.data.polygons:
  poly=[obj.data.vertices[i].co.copy() for i in face.vertices]
  low,rest=region(poly,clip_origin,et,en,EL+2*margin,EW+2*margin)
  polys.extend([(q,face.material_index) for q in rest])
  if len(low)>2:
   n+=1
   if name=='ME_Official_857_Structural_Envelope':
    low=[Vector((v.x,v.y,min(v.z,7.8))) for v in low];polys.append((low,face.material_index))
   elif max(v.z for v in low)<=7.8:polys.append((low,face.material_index))
 rebuild(obj,polys);changed[name]=n

# Recut the historic doorway AFTER datum correction: r01 compressed its old
# Boolean aperture but left its photographed full-height fanlight unchanged.
portal=(oa+ob)/2;out=-on
shape=[(-1.55,.08),(1.55,.08),(1.55,3.25)]
for i in range(1,49):
 a=math.pi*i/48;shape.append((1.55*math.cos(a),3.25+1.55*math.sin(a)))
vs=[]
for depth in [-.8,.8]:
 for u,z in shape:
  p=portal+ot*u+out*depth;vs.append((p.x,p.y,z))
s=len(shape);fs=[tuple(reversed(range(s))),tuple(range(s,2*s))]+[(i,(i+1)%s,(i+1)%s+s,i+s) for i in range(s)]
me=bpy.data.meshes.new('ME_SP_r02_Arch_Cutter');me.from_pydata(vs,[],fs);me.update()
cut=bpy.data.objects.new('ME_SP_r02_Arch_Cutter',me);bpy.context.scene.collection.objects.link(cut)
shell=bpy.data.objects['ME_Official_857_Structural_Envelope'];bpy.context.view_layer.objects.active=shell
mod=shell.modifiers.new('Restore_Full_Height_Historic_Aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
asset['second_pass_r02']='Fix roof cap deformation and clipped historic fanlight; lower distinct1942wing to estimated7.8m. Remaining wings/schedules unaccepted.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET));bpy.ops.wm.open_mainfile(filepath=str(ASSET))
record={'revision':'r02','input_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'saved_reopened':True,'collection':'Asset_mechanical_engineering','root_location':list(bpy.data.objects['AssetRoot_mechanical_engineering'].location),'root_scale':list(bpy.data.objects['AssetRoot_mechanical_engineering'].scale),'split_face_counts':changed,'roof_patch_count':len(bpy.data.objects['ME_Official_857_Roof'].data.polygons),'low_wing_roof_estimate_m':7.85,'sources':['research/second_pass/buildings/mechanical_engineering/sources/purdue_five_wings_diagram.jpg','audit/mechanical_engineering/second_pass/source_analysis/zone_statistics.json','research/second_pass/buildings/mechanical_engineering/sources/purdue_2025_current.jpg'],'uncertainties':['Low-wing current all-face schedule unresolved; retained lower existing rows are provisional','1929andGatewoodroofgeometry still unresolved','Exact carvedrelief/materials not established'],'accepted':False}
(OUT/'validation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
