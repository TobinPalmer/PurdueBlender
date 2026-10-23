import bpy, math, os, json
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
port=bpy.data.collections['SC_Portico_and_Entrances']
interior=bpy.data.collections['SC_Interior_Shell']
# Utility: operate in world space, then convert through the preserved object matrix.
def wb(o):
 ps=[o.matrix_world@Vector(c) for c in o.bound_box]
 return Vector([min(v[i] for v in ps) for i in range(3)]), Vector([max(v[i] for v in ps) for i in range(3)])
def set_mesh(o, verts_world, faces, material=None):
 inv=o.matrix_world.inverted(); me=bpy.data.meshes.new(o.name+'_Review2Mesh'); me.from_pydata([inv@Vector(v) for v in verts_world],[],faces); 
 if material: me.materials.append(material)
 else:
  for m in o.data.materials:
   if m: me.materials.append(m)
 me.update(); old=o.data; o.data=me
 if old.users==0:bpy.data.meshes.remove(old)
def mesh_boxes(o, boxes, material):
 verts=[];faces=[]
 for (a,b) in boxes:
  x0,y0,z0=a;x1,y1,z1=b;k=len(verts)
  verts += [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
  faces += [tuple(k+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
 set_mesh(o,verts,faces,material)
def box_mesh(o,c,d,mat):
 x,y,z=c;dx,dy,dz=[v*.5 for v in d]
 verts=[(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)]
 set_mesh(o,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def move_scale_world(o, scale=(1,1,1), pivot=None, offset=(0,0,0)):
 lo,hi=wb(o);ctr=Vector(pivot) if pivot else (lo+hi)*.5;inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  q=o.matrix_world@v.co;q=Vector([ctr[i]+(q[i]-ctr[i])*scale[i]+offset[i] for i in range(3)]);v.co=inv@q
 o.data.update()
# Calm exposed Indiana limestone while retaining its existing procedural grain.
stone=bpy.data.materials['Bedford_Indiana_Limestone']
stone.diffuse_color=(0.43,0.35,0.26,1)
if stone.use_nodes:
 bs=stone.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(0.43,0.35,0.26,1);bs.inputs['Roughness'].default_value=0.76
# Correct the giant triangular caps: reconstruct each trim mesh as restrained, rectangular limestone sides, head and sill around its pane.
trim_fixed=0
for o in list(bpy.data.objects):
 if not (o.name.startswith('SC_Win_') and o.name.endswith('_LimestoneTrim')):continue
 pane=bpy.data.objects.get(o.name.replace('_LimestoneTrim','_GlassPane'))
 if not pane: continue
 lo,hi=wb(pane);size=hi-lo;normal=0 if size.x<size.y else 1
 width_axis=1-normal;w=size[width_axis];z0,z1=lo.z,hi.z
 # Step the simple trim slightly forward of the pane so it reads clearly over the masonry reveal.
 direction=1 if ('_East_' in o.name or '_North_' in o.name) else -1
 ncenter=(lo[normal]+hi[normal])*0.5+direction*0.12;nd=0.24
 w0=(lo[width_axis]+hi[width_axis])*0.5-(w*0.5+0.12);w1=(lo[width_axis]+hi[width_axis])*0.5+(w*0.5+0.12)
 sidew=0.09;zlow=z0-0.11;zhigh=z1+0.10
 # Create world-coordinate boxes with orientation appropriate for the facade normal.
 boxes=[]
 if normal==0:
  boxes=[((ncenter-nd/2,w0,zlow),(ncenter+nd/2,w0+sidew,zhigh)),((ncenter-nd/2,w1-sidew,zlow),(ncenter+nd/2,w1,zhigh)),((ncenter-nd/2,w0,zhigh-.10),(ncenter+nd/2,w1,zhigh)),((ncenter-nd/2,w0,zlow),(ncenter+nd/2,w1,z0-.015))]
 else:
  boxes=[((w0,ncenter-nd/2,zlow),(w0+sidew,ncenter+nd/2,zhigh)),((w1-sidew,ncenter-nd/2,zlow),(w1,ncenter+nd/2,zhigh)),((w0,ncenter-nd/2,zhigh-.10),(w1,ncenter+nd/2,zhigh)),((w0,ncenter-nd/2,zlow),(w1,ncenter+nd/2,z0-.015))]
 mesh_boxes(o,boxes,stone);trim_fixed+=1
# Rebalance glazing: tinted architectural glass with visible reflected color and moderated transmission.
glass=bpy.data.materials['Architectural_Glazing'];glass.diffuse_color=(0.17,0.25,0.29,1)
if glass.use_nodes:
 bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(0.17,0.25,0.29,1);bs.inputs['Metallic'].default_value=0.18;bs.inputs['Roughness'].default_value=0.19;bs.inputs['Transmission Weight'].default_value=0.30;bs.inputs['Alpha'].default_value=0.82
# Lower roof pitch to match the relatively low historic hipped silhouette; dormers remain excluded as undocumented.
roof=bpy.data.objects['SC_Historic_Slate_Roof']
move_scale_world(roof,scale=(1,1,0.66),pivot=(0.06,2.24,14.2))
for o in bpy.data.collections['SC_Roof_and_Dormers'].objects:
 if o.name.startswith('SC_Copper_Ridge_'):
  move_scale_world(o,scale=(1,1,0.66),pivot=(0.0,2.0,14.2))
# Shorten the broad cornice band and use the quieter limestone tone.
cornice=bpy.data.objects.get('SC_Classical_Entablature_Cornice')
if cornice: move_scale_world(cornice,scale=(1,1,0.72),pivot=(0.06,2.24,13.75))
# Entry reconstruction: glazed double doors remain inset; add a semicircular glazed fanlight with a bronze curved frame.
for n in ['SC_Main_Fanlight_Glass','SC_Main_Fanlight_Bronze_Frame']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
# Create a mesh object in its own existing portico collection.
def mesh_obj(name, verts, faces, mat):
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();ob=bpy.data.objects.new(name,me);port.objects.link(ob);ob.parent=root;return ob
# Fanlight fill is an arched-top plane facing east (+X); radius/position are estimates guided by the visible entrance photo.
x=27.86; yc=-4.0; base=4.56;R=1.20
outline=[(yc-R,base),(yc+R,base)]
for j in range(25):
 t=math.pi*j/24;outline.append((yc+R*math.cos(t),base+R*math.sin(t)))
verts=[(x,y,z) for y,z in outline];center=(x,yc,base+0.25);verts.append(center);ci=len(verts)-1
faces=[(ci,i,(i+1)%len(outline)) for i in range(len(outline))]
mesh_obj('SC_Arched_Transom_Glass_Review2',verts,faces,glass)
# Curved stone/bronze arch ring as a faceted but smooth-enough ribbon with a slender frame.
arch_verts=[];arch_faces=[]
for r in (R+0.10,R):
 for j in range(25):
  t=math.pi*j/24;arch_verts.append((x+0.10,yc+r*math.cos(t),base+r*math.sin(t)))
for j in range(24):arch_faces.append((j,j+1,25+j+1,25+j))
frame=mesh_obj('SC_Arched_Transom_Bronze_Arch',arch_verts,arch_faces,bpy.data.materials['Dark_Bronze_Framing'])
# Inner shallow double molding around the main rectangular portal, with an open center for doors and transom.
portal_obj=bpy.data.objects['SC_Portico_Rectangular_Stone_Portal_Surround']
mesh_boxes(portal_obj,[((28.00,-5.60,1.95),(28.34,-5.30,6.55)),((28.00,-2.70,1.95),(28.34,-2.40,6.55)),((28.00,-5.60,6.15),(28.34,-2.40,6.55)),((28.34,-5.72,2.0),(28.46,-5.18,6.62)),((28.34,-2.82,2.0),(28.46,-2.28,6.62)),((28.34,-5.72,6.48),(28.46,-2.28,6.72))],stone)
# Reduce projection of the former heavy entablature/canopy while retaining a layered stone header.
ent=bpy.data.objects['SC_Portico_Entablature'];mesh_boxes(ent,[((28.10,-5.75,6.63),(29.35,-2.25,7.12))],stone)
can=bpy.data.objects.get('SC_Portico_Flat_Stone_Canopy')
if can:mesh_boxes(can,[((28.05,-5.85,7.12),(29.42,-2.15,7.34))],stone)
# Replace chunky square columns with slender round supports, shifted back toward the doorway.
def cylinder_mesh(o,cx,cy,z0,z1,r,mat):
 verts=[];faces=[];N=32
 for z in (z0,z1):
  for i in range(N):
   t=2*math.pi*i/N;verts.append((cx+r*math.cos(t),cy+r*math.sin(t),z))
 faces.append(tuple(range(N-1,-1,-1)));faces.append(tuple(range(N,2*N)))
 for i in range(N):j=(i+1)%N;faces.append((i,j,N+j,N+i))
 set_mesh(o,verts,faces,mat)
cols=[('SC_Portico_Column_Plinth_0',29.15,-5.40,1.88,2.34,.27),('SC_Portico_Column_Shaft_0',29.15,-5.40,2.28,6.76,.18),('SC_Portico_Column_Capital_0',29.15,-5.40,6.68,7.15,.27),('SC_Portico_Column_Plinth_3',29.15,-2.60,1.88,2.34,.27),('SC_Portico_Column_Shaft_3',29.15,-2.60,2.28,6.76,.18),('SC_Portico_Column_Capital_3',29.15,-2.60,6.68,7.15,.27)]
for n,cx,cy,z0,z1,r in cols:cylinder_mesh(bpy.data.objects[n],cx,cy,z0,z1,r,stone)
# Shift the sign to the revised header plane; its text orientation remains unchanged.
t=bpy.data.objects.get('SC_Portico_3D_Text')
if t:t.matrix_world.translation += Vector((-1.20,0,-0.45))
# Modest stair refinements to match the narrower entrance opening.
for o in port.objects:
 if o.name.startswith('SC_Portico_Step_'):
  move_scale_world(o,scale=(0.86,0.84,1),pivot=(30.45,-3.95,0.9))
# Improve the interior beyond a diagram: historic-plan-informed partitions, hub signage, desk work, books, and room finishes.
def mat_simple(name,color,rough=.7,metallic=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metallic;return m
wood=mat_simple('SC_Interior_Maple_Wood',(0.34,0.20,0.10,1));red=mat_simple('SC_Interior_Deep_Red_Upholstery',(0.30,0.055,0.038,1));metal=mat_simple('SC_Interior_Dark_Metal',(0.10,0.12,0.13,1));wall=mat_simple('SC_Interior_Paint_Warm_Offwhite',(0.70,0.66,0.57,1));bookmats=[mat_simple('SC_Book_Carmine',(0.42,0.06,0.04,1)),mat_simple('SC_Book_Indigo',(0.06,0.12,0.24,1)),mat_simple('SC_Book_Ochre',(0.62,0.36,0.07,1)),mat_simple('SC_Book_Green',(0.08,0.26,0.18,1))]
def cube(name,center,dims,mat,bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 interior.objects.link(o);o.parent=root;o.data.materials.clear();o.data.materials.append(mat)
 if bevel:
  be=o.modifiers.new('Soft interior edge','BEVEL');be.width=bevel;be.segments=2;o.modifiers.new('Interior weighted normals','WEIGHTED_NORMAL')
 return o
# Enclose the shared study hub with interrupted partitions that create circulation; layout is interpretive, not an as-built plan.
cube('SC_GradHub_Partition_East_South',(25.1,-10.8,3.45),(.18,2.1,3.1),wall,.02)
cube('SC_GradHub_Partition_East_North',(25.1,-4.5,3.45),(.18,2.7,3.1),wall,.02)
cube('SC_GradHub_Partition_South_West',(19.5,-12.1,3.45),(2.9,.18,3.1),wall,.02)
cube('SC_GradHub_Partition_South_East',(24.2,-12.1,3.45),(1.7,.18,3.1),wall,.02)
# Reception desk, wall-mounted wayfinding plaque, and a small lounge pair.
cube('SC_GradHub_Reception_Desk',(19.2,-3.7,2.4),(1.9,.72,.9),wood,.06)
cube('SC_GradHub_Reception_Counter',(19.2,-3.7,2.88),(2.0,.78,.10),wall,.03)
cube('SC_GradHub_Reception_Monitor',(19.2,-3.42,3.12),(.56,.09,.40),metal,.02)
# add books on the existing bookcase shelf runs
for shelf_i,y in enumerate([-10.7,-8.6,-6.5]):
 for shelf_j,z in enumerate([2.35,2.75,3.15]):
  for k in range(6):
   x=18.35+0.14*k;h=.24+0.06*((k+shelf_j)%3);w=.12;d=.16
   cube(f'SC_GradHub_Book_{shelf_i}_{shelf_j}_{k}',(x,y,z+h*.5),(w,d,h),bookmats[(k+shelf_j)%4],.007)
# table equipment/books and task lamps; deliberately generic as room inventory is not documented.
for ti,cy in enumerate([-9.3,-4.9]):
 cube(f'SC_GradHub_Laptop_Base_{ti}',(23.0,cy,2.69),(.58,.42,.045),metal,.015)
 cube(f'SC_GradHub_Laptop_Screen_{ti}',(23.0,cy+.16,2.90),(.58,.045,.40),metal,.015)
 for j in range(2):cube(f'SC_GradHub_BookStack_{ti}_{j}',(21.7+j*.45,cy-.18,2.77),(.38,.27,.12),bookmats[(ti+j)%4],.02)
 for j,x in enumerate([21.9,23.8]):
  cube(f'SC_GradHub_TaskLamp_Base_{ti}_{j}',(x,cy,2.71),(.16,.16,.04),metal,.01)
  cube(f'SC_GradHub_TaskLamp_Stem_{ti}_{j}',(x,cy,2.94),(.035,.035,.42),metal,.01)
  cube(f'SC_GradHub_TaskLamp_Shade_{ti}_{j}',(x,cy,3.15),(.25,.22,.10),wall,.02)
# Furnish research benches with monitors and book trays.
for ti,cx in enumerate([-7.0,-1.5]):
 for j in range(2):
  cube(f'SC_ResearchMonitor_{ti}_{j}',(cx-.7+j*1.4,5.22,6.78),(.70,.08,.46),metal,.02)
  cube(f'SC_ResearchBookTray_{ti}_{j}',(cx+.6-j*.2,4.75,6.34),(.50,.34,.12),wood,.02)
# Re-aim and save a purpose-built ground-floor interior review camera; normal building geometry stays enabled.
cam=bpy.data.objects['Cam_SC_06_Interior_Schematic'];cam.location=(35,-18,12);target=Vector((21.8,-7.1,2.9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=34
scene=bpy.context.scene
scene['SC interior note']='Interpretive furnished ground-floor graduate hub and research work area. The 2022 Trustees plans are historical project plans; current layout and room-by-room furnishings are unverified. Purdue 2025 report supports the hub, English office, office/research-lab functions only.'
scene['SC entry note']='Rebuilt from Purdue CLA exterior photograph and Google Maps place photo: inset glazed double doors, arched transom, layered limestone surround, slender round supports. Detail dimensions remain estimates.'
scene['SC roof note']='Historic roof silhouette retained but pitch lowered as an estimate; dormers remain hidden in presentation pending current-elevation evidence.'
bpy.ops.wm.save_as_mainfile(filepath=p)
print('SAVED',p,'trim meshes simplified',trim_fixed,'asset objects',len(bpy.data.collections['Asset_stanley_coulter_hall'].all_objects),'root',list(root.location),list(root.scale))
