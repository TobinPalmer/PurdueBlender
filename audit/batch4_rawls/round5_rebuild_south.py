import bpy, os, json, math
from mathutils import Vector
blend=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=blend)
wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls']; mesh=wall.data; inv=wall.matrix_world.inverted()
glass=bpy.data.objects['RAWL_South_Windows_South_Glass']
outer={'x0':-12.708,'x1':-3.088,'y0':-24.407,'y1':-24.302,'z0':1.5,'z1':24.08}
inner={'x0':-12.362,'x1':-3.442,'y0':-24.053,'y1':-23.955,'z0':1.5,'z1':24.08}
holes=[]
for poly in glass.data.polygons:
 pts=[glass.matrix_world@glass.data.vertices[i].co for i in poly.vertices]
 holes.append((min(v.x for v in pts)-.055,max(v.x for v in pts)+.055,min(v.z for v in pts)-.035,max(v.z for v in pts)+.035))
verts=[v.co.copy() for v in mesh.vertices]; faces=[]; mats=[]
def add_world_face(points, matidx=0):
 ids=[]
 for p in points:
  ids.append(len(verts)); verts.append(inv@Vector(p))
 faces.append(tuple(ids));mats.append(matidx)
def y_outer(x):return outer['y0']+(x-outer['x0'])*(outer['y1']-outer['y0'])/(outer['x1']-outer['x0'])
def x_inner(x):return inner['x0']+(x-outer['x0'])*(inner['x1']-inner['x0'])/(outer['x1']-outer['x0'])
def y_inner(x):
 t=(x-inner['x0'])/(inner['x1']-inner['x0']);return inner['y0']+t*(inner['y1']-inner['y0'])
for p in mesh.polygons:
 if p.index in {90,91}: continue
 faces.append(tuple(p.vertices));mats.append(p.material_index)
def grid(inner_skin=False):
 a=inner if inner_skin else outer
 xa,xb,z0,z1=a['x0'],a['x1'],a['z0'],a['z1']
 if inner_skin: hs=[(x_inner(h[0]),x_inner(h[1]),h[2],h[3]) for h in holes]
 else: hs=holes
 xs=sorted(set([xa,xb]+[v for h in hs for v in h[:2] if xa-1e-5<=v<=xb+1e-5]))
 zs=sorted(set([z0,z1]+[v for h in hs for v in h[2:] if z0-1e-5<=v<=z1+1e-5]))
 for x0,x1 in zip(xs,xs[1:]):
  for zlo,zhi in zip(zs,zs[1:]):
   cx=(x0+x1)/2;cz=(zlo+zhi)/2
   if any(h[0]-1e-5<cx<h[1]+1e-5 and h[2]-1e-5<cz<h[3]+1e-5 for h in hs):continue
   if inner_skin: y0,y1=y_inner(x0),y_inner(x1)
   else: y0,y1=y_outer(x0),y_outer(x1)
   if not inner_skin: pts=[(x0,y0,zlo),(x1,y1,zlo),(x1,y1,zhi),(x0,y0,zhi)]
   else: pts=[(x1,y1,zlo),(x0,y0,zlo),(x0,y0,zhi),(x1,y1,zhi)]
   add_world_face(pts)
grid(False);grid(True)
for h in holes:
 x0,x1,z0,z1=h; ix0,ix1=x_inner(x0),x_inner(x1)
 yo0,yo1=y_outer(x0),y_outer(x1); yi0,yi1=y_inner(ix0),y_inner(ix1)
 add_world_face([(x0,yo0,z0),(ix0,yi0,z0),(ix0,yi0,z1),(x0,yo0,z1)])
 add_world_face([(x1,yo1,z0),(x1,yo1,z1),(ix1,yi1,z1),(ix1,yi1,z0)])
 add_world_face([(x0,yo0,z0),(x1,yo1,z0),(ix1,yi1,z0),(ix0,yi0,z0)])
 add_world_face([(x0,yo0,z1),(ix0,yi0,z1),(ix1,yi1,z1),(x1,yo1,z1)])
new=bpy.data.meshes.new('RAWL_Masonry_Exterior_Walls_South_Apertures_R5');new.from_pydata(verts,[],faces);new.update()
for m in mesh.materials:new.materials.append(m)
for poly,mi in zip(new.polygons,mats):poly.material_index=mi
wall.data=new
# Replace only the eight pane-sized solid boxes on the south elevation with four slim perimeter bars per pane.
frm=bpy.data.objects['RAWL_South_Windows_South_BronzeMullions']; fmat=frm.data.materials[0]
fv=[];ff=[]
def bar(center,haxis,vaxis,naxis,dx,dy,dz):
 base=len(fv); c=Vector(center)
 for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
  q=c+haxis*(sx*dx/2)+vaxis*(sy*dy/2)+naxis*(sz*dz/2);fv.append(tuple(q))
 for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:ff.append(tuple(base+i for i in face))
for poly in glass.data.polygons:
 pts=[glass.matrix_world@glass.data.vertices[i].co for i in poly.vertices]
 # The quad is planar and almost vertical. Sort its two lower and two upper vertices by X.
 lo=sorted([v for v in pts if v.z<sum(q.z for q in pts)/4],key=lambda v:v.x)
 hi=sorted([v for v in pts if v.z>sum(q.z for q in pts)/4],key=lambda v:v.x)
 if len(lo)!=2 or len(hi)!=2:continue
 pbl,pbr=lo;ptl,ptr=hi;hax=((pbr-pbl)+(ptr-ptl)).normalized();vax=Vector((0,0,1));nax=hax.cross(vax).normalized()
 center=sum((v for v in pts),Vector())/4; w=(pbr-pbl).length;ht=(ptl-pbl).length
 for zsign in [-1,1]:bar(center+vax*(zsign*(ht/2-.0275)),hax,vax,nax,w+.055,.055,.065)
 for xsign in [-1,1]:bar(center+hax*(xsign*(w/2-.0275)),hax,vax,nax,.055,ht,.065)
fm=bpy.data.meshes.new('RAWL_South_Windows_Slim_Perimeter_Frames_R5');fm.from_pydata(fv,[],ff);fm.materials.append(fmat);fm.update();frm.data=fm
# Shared architectural glass is given moderate transmission so genuine rooms behind the north panes read through.
mat=bpy.data.materials['RAWL_CurtainWall_Glass'];mat.use_nodes=True;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Transmission Weight'].default_value=.18;bs.inputs['Roughness'].default_value=.16;bs.inputs['Metallic'].default_value=.08
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.25
bpy.ops.wm.save_as_mainfile(filepath=blend)
report={'asset':blend,'wall_face_indices_rebuilt':[90,91],'south_pane_count':len(holes),'south_frame_faces':len(ff),'wall_faces_before':len(mesh.polygons),'wall_faces_after':len(new.polygons),'changed_shared_glass_transmission':.18,'geometry_basis':'Measured south wall skins 90/91 and existing eight south-facing pane quads. The adjacent east-facing glazed wall was not modified.'}
with open('audit/batch4_rawls/round5_model_changes.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
