import bpy, math
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
root=bpy.data.objects['AssetRoot_stanley_coulter_hall'];port=bpy.data.collections['SC_Portico_and_Entrances'];inter=bpy.data.collections['SC_Interior_Shell']
def wb(o):
 ps=[o.matrix_world@Vector(c) for c in o.bound_box];return Vector([min(q[i] for q in ps) for i in range(3)]),Vector([max(q[i] for q in ps) for i in range(3)])
def set_mesh(o,verts,faces,mat):
 inv=o.matrix_world.inverted();me=bpy.data.meshes.new(o.name+'_Round2FinalMesh');me.from_pydata([inv@Vector(v) for v in verts],[],faces);me.materials.append(mat);me.update();old=o.data;o.data=me
 if old.users==0:bpy.data.meshes.remove(old)
def boxes(o,boxlist,mat):
 vs=[];fs=[]
 for a,b in boxlist:
  x0,y0,z0=a;x1,y1,z1=b;k=len(vs);vs += [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)];fs += [tuple(k+j for j in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
 set_mesh(o,vs,fs,mat)
def move_scale(o,sz,pivot):
 inv=o.matrix_world.inverted();c=Vector(pivot)
 for v in o.data.vertices:
  q=o.matrix_world@v.co;q.z=c.z+(q.z-c.z)*sz;v.co=inv@q
 o.data.update()
stone=bpy.data.materials['Bedford_Indiana_Limestone'];mix=stone.node_tree.nodes.get('Mix')
# Existing procedural color mix overrode the earlier base color assignment. Set the actual A/B colors.
mix.inputs[6].default_value=(0.48,0.39,0.29,1);mix.inputs[7].default_value=(0.34,0.265,0.195,1);mix.inputs[0].default_value=0.8
stone.diffuse_color=(0.40,0.31,0.22,1);stone.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.78
# Historic image suggests low hipped roof; lower the current pitched roof and copper ridges further.
move_scale(bpy.data.objects['SC_Historic_Slate_Roof'],.55,(.06,2.24,14.2))
for o in bpy.data.collections['SC_Roof_and_Dormers'].objects:
 if o.name.startswith('SC_Copper_Ridge_'):move_scale(o,.55,(0,2,14.2))
rm=bpy.data.materials['Historic_Slate_Roof_Procedural'];mixr=rm.node_tree.nodes.get('Mix');mixr.inputs[6].default_value=(.10,.13,.17,1);mixr.inputs[7].default_value=(.055,.075,.105,1);mixr.inputs[0].default_value=.5
# Keep existing procedural slate waves but increase the mineral variation, not the highlight brightness.
for n in rm.node_tree.nodes:
 if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=3.5;n.inputs['Detail'].default_value=3
 if n.type=='BUMP':n.inputs['Strength'].default_value=.12;n.inputs['Distance'].default_value=.018
# Lower header/sign assembly clear of the centered upper-story window; retain the measured facade rhythm.
for n in ['SC_Portico_Entablature','SC_Portico_Flat_Stone_Canopy']:
 o=bpy.data.objects.get(n)
 if o:
  for v in o.data.vertices:
   q=o.matrix_world@v.co;q.z-=.48;v.co=o.matrix_world.inverted()@q
  o.data.update()
t=bpy.data.objects.get('SC_Portico_3D_Text')
if t:t.matrix_world.translation.z-=.34
# Rebuild round support pieces at the lower lintel elevation.
def cylinder(o,cx,cy,z0,z1,r):
 N=32;vs=[];fs=[]
 for z in [z0,z1]:
  for i in range(N):a=2*math.pi*i/N;vs.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
 fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 for i in range(N):j=(i+1)%N;fs.append((i,j,N+j,N+i))
 set_mesh(o,vs,fs,stone)
for n,cx,cy,z0,z1,r in [('SC_Portico_Column_Plinth_0',29.15,-5.4,1.88,2.34,.25),('SC_Portico_Column_Shaft_0',29.15,-5.4,2.28,6.18,.17),('SC_Portico_Column_Capital_0',29.15,-5.4,6.14,6.62,.25),('SC_Portico_Column_Plinth_3',29.15,-2.6,1.88,2.34,.25),('SC_Portico_Column_Shaft_3',29.15,-2.6,2.28,6.18,.17),('SC_Portico_Column_Capital_3',29.15,-2.6,6.14,6.62,.25)]:cylinder(bpy.data.objects[n],cx,cy,z0,z1,r)
# Layered header and cap now remain below second-level glazing.
boxes(bpy.data.objects['SC_Portico_Entablature'],[((28.10,-5.75,6.15),(29.35,-2.25,6.62))],stone)
boxes(bpy.data.objects['SC_Portico_Flat_Stone_Canopy'],[((28.05,-5.85,6.62),(29.42,-2.15,6.84))],stone)
# Add a real bounded floor finish to the new interpretive hub cutaway; the full building floor remains untouched.
terrazzo=bpy.data.materials.get('Polished_Terrazzo') or bpy.data.materials.new('SC_GradHub_Terrazzo_Interpretive')
terrazzo.use_nodes=True;bs=terrazzo.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.31,.29,.25,1);bs.inputs['Roughness'].default_value=.42
floor=bpy.data.objects.get('SC_GradHub_Cutaway_Floor')
if not floor:
 me=bpy.data.meshes.new('SC_GradHub_Cutaway_FloorMesh');me.from_pydata([(17.8,-13.0,1.84),(26.1,-13.0,1.84),(26.1,-2.4,1.84),(17.8,-2.4,1.84)],[],[(0,1,2,3)]);me.materials.append(terrazzo);me.update();floor=bpy.data.objects.new('SC_GradHub_Cutaway_Floor',me);inter.objects.link(floor);floor.parent=root
# Correct scene-facing evidence notes with chronology and uncertainty.
s=bpy.context.scene;s['SC entry note']='Entry uses inset glazed double doors and an arched transom beneath a layered, restrained limestone frame, plus slender round supports, guided by Purdue CLA exterior imagery and Google Maps place photo; dimensions are estimated.'
s['SC roof note']='Low hipped roof plane is a visual estimate informed by the undated Purdue Archives photograph; height/profile remain unverified.'
s['SC interior note']='Interpretive furnished hub and work spaces use the historical 2022 Trustees plan for partitions and stated 2025 functions for program; not an as-built current floor plan.'
bpy.ops.wm.save_as_mainfile(filepath=p);print('final refinement saved',len(bpy.data.collections['Asset_stanley_coulter_hall'].all_objects),list(root.location),list(root.scale))
