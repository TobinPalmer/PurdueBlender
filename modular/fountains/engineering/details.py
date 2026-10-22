import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(D/'engineering.blend'));s=bpy.context.scene;c=bpy.data.collections['Fountain_Engineering'];xy=json.loads((D/'position_measurement.json').read_text())['centroid_local_m'];x,y=xy
stone=bpy.data.materials['EF_Architectural_concrete'];steel=bpy.data.materials['EF_Stainless']
relief=stone.copy();relief.name='EF_Concrete_relief';relief.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.42,.40,.35,1)
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);c.objects.link(o);me.materials.append(m);return o
# Apply shallow sculptural relief only; original fluid-collision bodies unchanged.
v=[];faces=[]
def box(center,u,w,normal,L,W,T):
 k=len(v)
 for zz in [-1,1]:
  for aa,bb in [(-1,-1),(1,-1),(1,1),(-1,1)]:v.append(tuple(center+u*(aa*L/2)+w*(bb*W/2)+normal*(zz*T/2)))
 faces.extend(tuple(k+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
for a in [45,135,225,315]:
 rad=math.radians(a);r=Vector((math.cos(rad),math.sin(rad),0));q=Vector((-math.sin(rad),math.cos(rad),0));up=Vector((0,0,1))
 # Stepped diagonal networks, estimated from photo; no exact relief drawing available.
 for side in [-1,1]:
  for j in range(7):
   rr=1.5+j*.42;z=.62+j*.12;length=.7+.12*j;u=(r+up).normalized();w=(up-r).normalized();th=.64-.28*(z/11.5824)
   ctr=Vector((x,y,.12))+r*rr+up*z+q*(side*(th/2+.012))
   box(ctr,u,w,q,length,.045,.024)
   box(ctr+u*(length/2)+w*.11,w,u,q,.26,.045,.024)
mesh('EF_Photo_inferred_diagonal_concrete_relief',v,faces,relief)
# Perimeter square inset pattern: backed recesses are modeled geometry/contrast, not verified hydraulic drains.
v=[];faces=[]
for a in [0,90,180,270]:
 for i in range(9):
  t=math.radians(a-27+i*6.75);r=Vector((math.cos(t),math.sin(t),0));q=Vector((-math.sin(t),math.cos(t),0));ctr=Vector((x,y,.53))+r*8.002;box(ctr,q,Vector((0,0,1)),r,.13,.17,.012)
mesh('EF_Perimeter_square_recess_inlays',v,faces,relief)
# Discrete paving units; measured module unavailable, nominal .4x.2m with6mm joints.
v=[];faces=[];rng=random.Random(39)
for j in range(-45,46):
 yy=j*.2
 for i in range(-23,24):
  xx=i*.4+(.2 if j%2 else 0)
  if xx*xx+yy*yy>8.9**2:continue
  k=len(v);v.extend([(x+xx-.197,y+yy-.097,.085),(x+xx+.197,y+yy-.097,.085),(x+xx+.197,y+yy+.097,.085),(x+xx-.197,y+yy+.097,.085)]);faces.append((k,k+1,k+2,k+3))
pave=mesh('EF_Individual_paving_units',v,faces,stone)
for i in range(4):
 m=stone.copy();m.name='EF_Paver_'+str(i);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.42+i*.025,.38+i*.022,.29+i*.018,1);pave.data.materials.append(m)
for p in pave.data.polygons:p.material_index=rng.randrange(1,5)
# Stainless concentric deck grille, a contemporary visual feature, not a resolved drainage hydraulic network.
for rr in [.55,.7,.85,1.0,1.15,1.3]:
 bpy.ops.mesh.primitive_torus_add(major_radius=rr,minor_radius=.012,major_segments=96,minor_segments=6,location=(x,y,.105));o=bpy.context.object;o.name='EF_Grille_ring_'+str(rr)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(steel)
s['detail_uncertainty']='Relief pattern, inset recesses, paving module, grille inferred from photographs; exact shop drawings unavailable. Original liquid collision bodies unchanged.'
bpy.ops.wm.save_as_mainfile(filepath=str(D/'engineering.blend'));s.render.filepath=str(D/'attempt3_detail.png');s.cycles.samples=16;bpy.ops.render.render(write_still=True)
(D/'attempt3_changes.json').write_text(json.dumps({'attempt':3,'changes':['diagonal stepped relief','perimeter square recess inlays','separate paver units','concentric stainless grille'],'not_verified':['relief exact shapes/depth','paver module','recess dimensions','grille detail'],'collision_bodies_changed':False},indent=2))
