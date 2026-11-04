"""ME second-pass revision 2026-11-03. Source-backed, bounded corrections.

Run Blender -b --python this_file. Opens the preserved exact input snapshot.
Scope: historic 1932 mall bar roof and entrance. Dimensions are estimates;
remaining wings and facade schedules require independent review and iteration.
"""
import bpy, math, json, shutil, hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'audit/mechanical_engineering/second_pass/revision_2026-11-03'
OUT.mkdir(parents=True,exist_ok=True)
ASSET=ROOT/'modular/buildings/mechanical_engineering.blend'
BASE=OUT/'baseline.blend'
if not BASE.exists(): shutil.copy2(ASSET,BASE)
bpy.ops.wm.open_mainfile(filepath=str(BASE))
asset=bpy.data.collections['Asset_mechanical_engineering']
scene=bpy.context.scene

def mat(name,c,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1)
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough
 return m
tile=mat('ME_SP_RedBrown_Clay_Roof',(0.25,.075,.04))
membrane=mat('ME_SP_Charcoal_Membrane',(.065,.072,.075),.85)
stone=bpy.data.materials['ME_R1_Limestone_Portal_Qualitative']
metal=bpy.data.materials['ME_R1_Window_Frame_DarkBronze']
glass=bpy.data.materials['ME_R1_Entry_Glazing_Dark']

def mesh(name,vs,fs,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
 ob=bpy.data.objects.new(name,me);asset.objects.link(ob);me.materials.append(ma)
 ob['second_pass_source']='M01/M11 historic portal; M10/M13 roof; dimensions estimated'
 return ob

def box(name,c,axes,dims,ma):
 vs=[]
 for z in [-1,1]:
  for y in [-1,1]:
   for x in [-1,1]: vs.append(tuple(Vector(c)+axes[0]*x*dims[0]/2+axes[1]*y*dims[1]/2+axes[2]*z*dims[2]/2))
 return mesh(name,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],ma)

# Register the long 1932 bar to official wall edges 103/0, not image roof lean.
a=Vector((-33.660,13.690));b=Vector((20.270,57.9013));t=(b-a).normalized();n=Vector((-t.y,t.x));L=(b-a).length
width=19.55
datum_scale=15.8/18.5
changed={}
for name in ['ME_Official_857_Structural_Envelope','ME_Official_857_Roof','ME_R1_Facade_Window_Glazing','ME_R1_Facade_Window_Frames','ME_R1_Limestone_Window_Sills_And_Stringcourses']:
 ob=bpy.data.objects[name];count=0
 for v in ob.data.vertices:
  d=Vector((v.co.x,v.co.y))-a;u=d.dot(t);iv=-d.dot(n)
  if -.4<=u<=L+.4 and -.4<=iv<=width+.4:
   v.co.z*=datum_scale;count+=1
 ob.data.update();changed[name]=count
outer=[a,b,b-n*width,a-n*width]
inset=7.0
inner=[a+t*inset-n*inset,b-t*inset-n*inset,b-t*inset-n*(width-inset),a+t*inset-n*(width-inset)]
# Retained2018 unclassified returns in the1932 bar show v2..4m median16.84m,
# v4..6 median17.76, v6..8 median18.68, v8..14 median18.88m. This supports
# an estimated15.8m eave and18.9m high seam; vegetation/equipment remain risks.
eave=15.8;high=18.9
vs=[(p.x,p.y,eave) for p in outer]+[(p.x,p.y,high) for p in inner]
roof=mesh('ME_SP_1932_Hipped_Red_Perimeter',vs,[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],tile)
mesh('ME_SP_1932_Raised_Flat_Centre',[(p.x,p.y,high+.015) for p in inner],[(0,1,2,3)],membrane)
roof['height_status']='Photo/2018 unclassified LiDAR fit: eave15.8m, high seam18.9m estimated, not certified measurement'
# Fine parallel seams follow the roof slope rather than a flat aerial image.
# Material variation is qualitative; no product or calibrated color assertion.

# Historic portal identity: this is the1932 bar, not the separate Gatewood entry.
portal=(a+b)/2
tz=Vector((t.x,t.y,0));nz=Vector((n.x,n.y,0));up=Vector((0,0,1));axes=(tz,nz,up)
def p(u,v,z):return (portal.x+t.x*u+n.x*v,portal.y+t.y*u+n.y*v,z)
old=bpy.data.objects.get('ME_R1_Gatewood_Fountain_Facing_Stone_Arch')
old['identity_correction']='Historic1932 portal, source M01/M11, incorrectly named Gatewood in R1'
old.name='ME_SP_Historic_1932_Stone_Arch_Base'
# Thin secondary archivolts make the layered reveal visible at oblique views.
def ring(name,ri,ro,depth,offset):
 vs=[];steps=48
 for v in [offset-depth/2,offset+depth/2]:
  for r in [ri,ro]:
   for i in range(steps+1):vs.append(p(r*math.cos(math.pi*i/steps),v,3.25+r*math.sin(math.pi*i/steps)))
 fs=[];s=steps+1
 for i in range(steps):
  fs.extend([(i,i+1,s+i+1,s+i),(2*s+i,3*s+i,3*s+i+1,2*s+i+1),(s+i,s+i+1,3*s+i+1,3*s+i),(i,2*s+i,2*s+i+1,i+1)])
 return mesh(name,vs,fs,stone)
ring('ME_SP_Historic_Inner_Archivolt',1.39,1.58,.18,.26)
ring('ME_SP_Historic_Outer_Archivolt_Moulding',2.10,2.22,.16,.47)
# Fanlight's orthogonal metal grid clipped analytically to the semicircle.
r=1.36
for i in range(-9,10):
 u=i*.14;h=math.sqrt(max(0,r*r-u*u))
 if h>0:box('ME_SP_Fanlight_Vertical_%02d'%(i+9),p(u,-.01,3.25+h/2),axes,(.025,.05,h),metal)
for i in range(1,10):
 z=i*.14;w=2*math.sqrt(max(0,r*r-z*z))
 if w>0:box('ME_SP_Fanlight_Horizontal_%02d'%i,p(0,-.01,3.25+z),axes,(w,.05,.025),metal)
# Real name is incised in a two-line stone field below the fanlight.
bpy.data.objects.remove(bpy.data.objects['ME_R1_Entrance_Lettering'],do_unlink=True)
box('ME_SP_Historic_Name_Field',p(0,.22,3.18),axes,(2.81,.23,.50),stone)
font=bpy.data.curves.new('ME_SP_Stone_Name_Curve','FONT');font.body='MECHANICAL\nENGINEERING';font.size=.19;font.space_line=.82;font.align_x='CENTER';font.align_y='CENTER';font.extrude=.0005
ob=bpy.data.objects.new('ME_SP_Historic_Incised_Name_Approximation',font);asset.objects.link(ob)
rot=Matrix.Identity(3);rot.col[0]=-tz;rot.col[1]=up;rot.col[2]=nz;ob.rotation_euler=rot.to_euler();ob.location=p(0,.341,3.18);font.materials.append(bpy.data.materials['ME_R1_Entrance_Lettering'])
for u in [-1.88,1.88]:
 for z,w,d,h in [(.18,.97,.59,.16),(.39,.90,.54,.13),(.52,.79,.50,.10),(3.28,.94,.57,.10),(3.43,.90,.55,.10)]:
  box('ME_SP_Historic_Base_And_Spring_Moulding',p(u,.24,z),axes,(w,d,h),stone)
# Segment joints in the outer ring, visibly present in the source's cut stone.
joint=mat('ME_SP_Stone_Joint',(.27,.24,.20))
for i in range(1,9):
 ang=math.pi*i/9;u=1.90*math.cos(ang);z=3.25+1.90*math.sin(ang)
 radial=tz*math.cos(ang)+up*math.sin(ang);circ=-tz*math.sin(ang)+up*math.cos(ang)
 box('ME_SP_Historic_Stone_Radial_Joint',p(u,.432,z),(radial,nz,circ),(.52,.008,.015),joint)
asset['second_pass_2026_11_03']='1932 roof slopes/flat centre and corrected historic portal profiles/grid/name; provisional, unaccepted'
asset['second_pass_remaining']='Other wings still flat/incorrectly repeated facade; roof seam/eave heights estimated; current all-face opening counts and carved relief unresolved'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_mechanical_engineering']
checks={'saved_reopened':True,'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'export_collection':asset.name,'root_location':list(bpy.data.objects['AssetRoot_mechanical_engineering'].location),'root_scale':list(bpy.data.objects['AssetRoot_mechanical_engineering'].scale),'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'limitations':['Provisional1932 roof height/plan profile','Remaining wings unchanged','Opening schedule incomplete','Historic carved relief not yet replicated','Gatewood portal unresolved'],'accepted':False}
(OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
(OUT/'datum_correction.json').write_text(json.dumps({'region':'1932 long mall bar','method':'Spatially selected original mesh vertices within GIS-registered bar; z scaled15.8/18.5. New hipped perimeter estimated from roof photographs and unclassified2018 return profile.','changed_vertex_counts':changed,'eave_estimate_m':15.8,'high_seam_estimate_m':18.9,'slope_inset_m':inset,'point_data':'audit/mechanical_engineering/second_pass/source_analysis/class1_asset_local_xyz.npy','uncertainty':'Unclassified returns can contain vegetation and equipment; ground datum is pooled local median; polygon and roof slope are model fits, not survey.'},indent=2))
print(json.dumps(checks,indent=2))
