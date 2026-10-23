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
# diagnostic duplicate; do not save asset in this script
dup=wall.copy();dup.data=new;dup.name='R4_NorthWall_Aperture_Diagnostic';s.collection.objects.link(dup);wall.hide_render=True
wall.hide_viewport=True
s.view_layers[0].update(); dg=bpy.context.evaluated_depsgraph_get()
for xx,zz in [(23.55,2.4),(23.55,7.89),(23.55,13.38),(20.03,2.4),(20.03,7.89),(20.03,13.38)]:
 hit,loc,n,fi,obj,mat=s.ray_cast(dg,Vector((xx,30,zz)),Vector((0,-1,0)),distance=30);print("NEW RAY",xx,zz,hit,obj.name if obj else None,tuple(round(v,3) for v in loc))
# set pane to diagnostic emission, retaining frames
m=bpy.data.materials.new('R4_EMIT_DIAG');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.02,.4,1,1);e.inputs['Strength'].default_value=1;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);glass.data.materials.clear();glass.data.materials.append(m)
# daytime direct front render
cd=bpy.data.cameras.new('R4_ApertureCam');cam=bpy.data.objects.new('R4_ApertureCam',cd);s.collection.objects.link(cam);cam.location=(25,62,10);cam.rotation_euler=(Vector((25,20,10))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=30;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=750
for ob in s.objects:
 if ob.type=='LIGHT':ob.hide_render=True
ld=bpy.data.lights.new('R4_ApertureSun','SUN');ld.energy=2;l=bpy.data.objects.new('R4_ApertureSun',ld);s.collection.objects.link(l);l.rotation_euler=(.4,-.5,-.8)
s.render.filepath=os.path.abspath('audit/batch4_rawls/northwall_rebuilt_emission_diagnostic.png');bpy.ops.render.render(write_still=True)
print('panels',len(holes),'faces old/new',len(mesh.polygons),len(new.polygons))




