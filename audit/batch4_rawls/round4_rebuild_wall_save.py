import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];glass=bpy.data.objects['RAWL_North_Windows_Glass'];inv=wall.matrix_world.inverted();mesh=wall.data
# Window apertures are defined by the existing 60 pane quads.
holes=[]
for p in glass.data.polygons:
 pts=[glass.matrix_world@glass.data.vertices[i].co for i in p.vertices]
 holes.append((min(v.x for v in pts)-.055,max(v.x for v in pts)+.055,min(v.z for v in pts)-.035,max(v.z for v in pts)+.035))
# The outer/inner north wall faces are the measured quads 24 and 25.
outer=(-21.394,20.193,33.333,20.790,1.5,24.08)
inner=(-21.040,19.847,32.983,20.437,1.5,24.08)
print('hole bounds', holes[:3], holes[-3:])
verts=[v.co.copy() for v in mesh.vertices];faces=[];mats=[]
for p in mesh.polygons:
 if p.index in {24,25}:continue
 faces.append(tuple(p.vertices));mats.append(p.material_index)
def add_world_face(points,matidx=0):
 ids=[]
 for p in points:
  ids.append(len(verts));verts.append(inv@Vector(p))
 faces.append(tuple(ids));mats.append(matidx)
def yline(x,a,b):return a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0])
def grid(a,b,is_outer):
 xa,ya,xb,yb,z0,z1=a
 # Back face holes follow the measured 0.35 m x shift of the inner wall skin.
 dx=0 if is_outer else (inner[0]-outer[0])
 hs=[(h[0]+dx,h[1]+dx,h[2],h[3]) for h in holes]
 xs=sorted(set([round(xa,5),round(xb,5)]+[round(v,5) for h in hs for v in h[:2] if xa-1e-5<=v<=xb+1e-5]))
 zs=sorted(set([z0,z1]+[round(v,5) for h in hs for v in h[2:] if z0-1e-5<=v<=z1+1e-5]))
 skips=0;keeps=0
 for x0,x1 in zip(xs,xs[1:]):
  for zlo,zhi in zip(zs,zs[1:]):
   cx=(x0+x1)/2;cz=(zlo+zhi)/2
   if any(h[0]-1e-4<cx<h[1]+1e-4 and h[2]-1e-4<cz<h[3]+1e-4 for h in hs):skips+=1;continue
   keeps+=1
   y0=yline(x0,(xa,ya),(xb,yb));y1=yline(x1,(xa,ya),(xb,yb))
   if is_outer:ps=[(x0,y0,zlo),(x1,y1,zlo),(x1,y1,zhi),(x0,y0,zhi)]
   else:ps=[(x1,y1,zlo),(x0,y0,zlo),(x0,y0,zhi),(x1,y1,zhi)]
   add_world_face(ps)
grid(outer,(outer[0],outer[1],outer[2],outer[3],outer[4],outer[5]),True)
grid(inner,(inner[0],inner[1],inner[2],inner[3],inner[4],inner[5]),False)
# Close the 60 reveal returns between skins with the existing brick material.
for h in holes:
 x0,x1,z0,z1=h;dx=inner[0]-outer[0];xi0=x0+dx;xi1=x1+dx
 yo0=yline(x0,(outer[0],outer[1]),(outer[2],outer[3]));yo1=yline(x1,(outer[0],outer[1]),(outer[2],outer[3]));yi0=yline(xi0,(inner[0],inner[1]),(inner[2],inner[3]));yi1=yline(xi1,(inner[0],inner[1]),(inner[2],inner[3]))
 add_world_face([(x0,yo0,z0),(xi0,yi0,z0),(xi0,yi0,z1),(x0,yo0,z1)])
 add_world_face([(x1,yo1,z0),(x1,yo1,z1),(xi1,yi1,z1),(xi1,yi1,z0)])
 add_world_face([(x0,yo0,z0),(x1,yo1,z0),(xi1,yi1,z0),(xi0,yi0,z0)])
 add_world_face([(x0,yo0,z1),(xi0,yi0,z1),(xi1,yi1,z1),(x1,yo1,z1)])
new=bpy.data.meshes.new('RAWL_Masonry_Exterior_Walls_Apertures_R4');new.from_pydata(verts,[],faces);new.update()
for m in mesh.materials:new.materials.append(m)
for p,mi in zip(new.polygons,mats):p.material_index=mi
wall.data=new
wall.hide_render=False
wall.hide_viewport=False
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(.08,.24,.38,1);bs.inputs['Roughness'].default_value=.14;bs.inputs['Metallic'].default_value=.20;bs.inputs['Transmission Weight'].default_value=.03;bs.inputs['Alpha'].default_value=1;bs.inputs['IOR'].default_value=1.45
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.45;bs.inputs['Coat Roughness'].default_value=.08
if 'Emission Strength' in bs.inputs:bs.inputs['Emission Strength'].default_value=0
m.diffuse_color=(.08,.24,.38,1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'))
print('saved segmented north wall with 60 measured apertures; faces',len(mesh.polygons),'->',len(new.polygons))
