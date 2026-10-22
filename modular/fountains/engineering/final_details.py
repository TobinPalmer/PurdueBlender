import bpy,math,json
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(D/'engineering.blend'));s=bpy.context.scene;c=bpy.data.collections['Fountain_Engineering'];x,y=json.loads((D/'position_measurement.json').read_text())['centroid_local_m'];stone=bpy.data.materials['EF_Architectural_concrete'];relief=bpy.data.materials['EF_Concrete_relief']
def mesh(n,v,f,m=None):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);c.objects.link(o)
 if m:me.materials.append(m)
 return o
v=[];faces=[]
def box(center,u,w,normal,L,W,T):
 k=len(v)
 for zz in [-1,1]:
  for aa,bb in [(-1,-1),(1,-1),(1,1),(-1,1)]:v.append(tuple(center+u*(aa*L/2)+w*(bb*W/2)+normal*(zz*T/2)))
 faces.extend(tuple(k+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
# Real blind recess cavities through exterior70mm of the low wall (dimensions estimated, not plans).
for a in [0,90,180,270]:
 for i in range(9):
  t=math.radians(a-27+i*6.75);r=Vector((math.cos(t),math.sin(t),0));q=Vector((-math.sin(t),math.cos(t),0));box(Vector((x,y,.53))+r*7.99,q,Vector((0,0,1)),r,.13,.17,.12)
cut=mesh('EF_Recess_boolean_tool',v,faces)
bpy.ops.object.select_all(action='DESELECT')
for a in [0,90,180,270]:
 ob=bpy.data.objects['EF_Perimeter_wall_'+str(a)];bpy.context.view_layer.objects.active=ob;ob.select_set(True);md=ob.modifiers.new('Actual square recess cavities','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=cut;bpy.ops.object.modifier_apply(modifier=md.name);ob.select_set(False)
bpy.data.objects.remove(cut,do_unlink=True)
old=bpy.data.objects.get('EF_Perimeter_square_recess_inlays')
if old:bpy.data.objects.remove(old,do_unlink=True)
old=bpy.data.objects.get('EF_Photo_inferred_diagonal_concrete_relief')
if old:bpy.data.objects.remove(old,do_unlink=True)
# Photo-inspired layered rectilinear network in lower/mid fin faces. Exact commissionedart geometry still unverified.
v=[];faces=[]
for a in [45,135,225,315]:
 rad=math.radians(a);r=Vector((math.cos(rad),math.sin(rad),0));q=Vector((-math.sin(rad),math.cos(rad),0));up=Vector((0,0,1));u=(r+up).normalized();w=(up-r).normalized()
 for side in [-1,1]:
  for j in range(6):
   for k in range(6):
    rr=1.38+k*.43;z=.6+j*.41;ro=1.5+6*(1-z/11.5824)**2.7
    if rr+.46>ro or (j+k)%3==0:continue
    th=.64-.28*(z/11.5824);ctr=Vector((x,y,.12))+r*rr+up*z+q*(side*(th/2+.017));L=.40;W=.24
    for du,dw,uu,ww,ll in [(-L/2,0,w,u,W),(L/2,0,w,u,W),(0,-W/2,u,w,L)]:box(ctr+u*du+w*dw,uu,ww,q,ll,.033,.03)
mesh('EF_Estimated_rectilinear_relief_network',v,faces,relief)
# Smooth concentric brick band hides cut pavingunit ends, as visible in reference plaza.
v=[];faces=[]
for i in range(257):
 t=2*math.pi*i/256
 for rr in [8.5,9.0]:v.append((x+rr*math.cos(t),y+rr*math.sin(t),.091))
 if i:k=2*i;faces.append((k-2,k,k+1,k-1))
mesh('EF_Concentric_brick_trim',v,faces,bpy.data.materials['EF_Brick'])
s['accuracy_status']='Evidence-limited reconstruction, NOT100% accurate. OSM horizontal alignment approximate; only38ft structuralspan supported. No surveyedhorizontalprofile or calibratedhydraulics.'
s.frame_set(96);bpy.ops.wm.save_as_mainfile(filepath=str(D/'engineering.blend'));s.render.filepath=str(D/'final_front.png');bpy.ops.render.render(write_still=True)
(D/'attempt5_changes.json').write_text(json.dumps({'attempt':5,'changes':['36 real shallow wall recess cavities replacing inlays','photo-inspired layered rectilinear relief replacing sparsechevrons','smoothbrickannulartrim','explicitaccuracyandhydraulicsmetadata'],'hydraulic_collision_bodies_changed':False,'stop_reason':'five implementation/gradingattemptcap regardlessoffinalscore'},indent=2))
