import bpy
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
def rebuild(name,doors):
 o=bpy.data.objects[name]; old=o.data; mat=old.materials[0] if old.materials else None
 x0,x1=-.35,.35; ymin,ymax=-35.5,35.5; zmin,zmax=-8.25,8.25
 holes=[]
 for y in range(-30,31,5):
  for z in (2.6,6.4,10.5,14.6): holes.append((y-0.97,y+0.97,z-1.08-8.25,z+1.08-8.25))
 if doors:
  # Three existing entry leaves and transoms on the east elevation; opening sized to visible limestone door frames.
  for y in (-2.75,-0.25,2.24): holes.append((y-0.94,y+0.94,-8.25,4.0-8.25))
 edges=sorted({ymin,ymax,*[max(ymin,min(ymax,v)) for h in holes for v in h[:2]]})
 boxes=[]
 for ya,yb in zip(edges[:-1],edges[1:]):
  if yb-ya<1e-4: continue
  active=sorted((max(zmin,h[2]),min(zmax,h[3])) for h in holes if h[0]<yb-1e-5 and h[1]>ya+1e-5 and h[3]>zmin and h[2]<zmax)
  merged=[]
  for a,b in active:
   if merged and a<=merged[-1][1]+1e-5: merged[-1]=(merged[-1][0],max(merged[-1][1],b))
   else: merged.append((a,b))
  cur=zmin
  for a,b in merged:
   if a>cur: boxes.append((ya,yb,cur,a))
   cur=max(cur,b)
  if cur<zmax: boxes.append((ya,yb,cur,zmax))
 verts=[]; faces=[]
 for ya,yb,za,zb in boxes:
  b=len(verts); verts.extend([(x0,ya,za),(x1,ya,za),(x1,yb,za),(x0,yb,za),(x0,ya,zb),(x1,ya,zb),(x1,yb,zb),(x0,yb,zb)])
  faces.extend([(b,b+3,b+2,b+1),(b+4,b+5,b+6,b+7),(b,b+1,b+5,b+4),(b+1,b+2,b+6,b+5),(b+2,b+3,b+7,b+6),(b+3,b,b+4,b+7)])
 mesh=bpy.data.meshes.new(name+'_OpeningsMesh'); mesh.from_pydata(verts,[],faces); mesh.update()
 if mat: mesh.materials.append(mat)
 o.data=mesh; o.location=(10.45 if name.endswith('East') else -10.45,0,8.25)
 if old.users==0: bpy.data.meshes.remove(old)
 print(name,'wall segments',len(boxes),'cutout rectangles',len(holes))
rebuild('HOVD_Wall_East',True); rebuild('HOVD_Wall_West',False)
bpy.ops.wm.save_as_mainfile(filepath=p)
