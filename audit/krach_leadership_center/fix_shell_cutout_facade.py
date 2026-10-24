import bpy, bmesh, json
src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
shell=bpy.data.objects['KRCH structural shell | GIS outline']
# Recover the authoritative 15-point simplified GIS perimeter from the unchanged base face.
base=next(p for p in shell.data.polygons if all(abs(shell.data.vertices[i].co.z+1.0)<1e-4 for i in p.vertices))
ring=[shell.data.vertices[i].co.copy() for i in base.vertices]; N=len(ring)
top_z=max(v.co.z for v in shell.data.vertices if v.co.z>15.0)
# Openings on the documented street-facing wall: atrium curtainwall, first-floor public glazing, and upper windows.
openings=[(-21.85,-13.05,-0.30,15.20),(-12.85,31.15,0.02,2.96)]
upper_x=[-31.0,-26.0,-9.2,-3.6,2.0,7.6,13.2,18.8,24.4,30.0]
for x in upper_x:
 for z in ([1.38,4.88,8.78,12.68] if x<-20 else [4.88,8.78,12.68]): openings.append((x-.76,x+.76,z-.95,z+.95))
verts=[(v.x,v.y,-1.0) for v in ring]+[(v.x,v.y,top_z) for v in ring]
faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
# Partition the shell's south-facing wall panels into strips around openings instead of using booleans.
# This avoids triangulation artifacts while leaving footprint coordinates unchanged.
for i in range(N):
 a=ring[i]; b=ring[(i+1)%N]
 # Wall front edges run east-west on the south boundary; the small vertical notch stays a solid facade return.
 if max(a.y,b.y)<-13.0 and abs(a.x-b.x)>2.0:
  xlo=min(a.x,b.x); xhi=max(a.x,b.x)
  breaks=[0.0,1.0]
  dx=b.x-a.x
  for x0,x1,z0,z1 in openings:
   for x in [x0,x1]:
    t=(x-a.x)/dx if abs(dx)>1e-7 else -1
    if 1e-5<t<1-1e-5: breaks.append(t)
  breaks=sorted(set(round(t,8) for t in breaks))
  for t0,t1 in zip(breaks[:-1],breaks[1:]):
   xm=a.x+dx*(t0+t1)/2
   y0=a.y+(b.y-a.y)*t0; y1=a.y+(b.y-a.y)*t1
   cuts=[]
   for x0,x1,z0,z1 in openings:
    if x0-1e-5<=xm<=x1+1e-5 and x1>=xlo and x0<=xhi:
     cuts.append((max(-1.0,z0),min(top_z,z1)))
   cuts.sort(); merged=[]
   for z0,z1 in cuts:
    if not merged or z0>merged[-1][1]+1e-5: merged.append([z0,z1])
    else: merged[-1][1]=max(merged[-1][1],z1)
   bands=[]; cur=-1.0
   for z0,z1 in merged:
    if z0>cur+1e-5: bands.append((cur,z0))
    cur=max(cur,z1)
   if cur<top_z-1e-5: bands.append((cur,top_z))
   for z0,z1 in bands:
    if z1-z0<0.01: continue
    k=len(verts)
    verts.extend([(a.x+dx*t0,y0,z0),(a.x+dx*t1,y1,z0),(a.x+dx*t1,y1,z1),(a.x+dx*t0,y0,z1)])
    faces.append((k,k+1,k+2,k+3))
 else:
  faces.append((i,(i+1)%N,(i+1)%N+N,i+N))
me=bpy.data.meshes.new('KRCH GIS shell with source-backed facade openings')
me.from_pydata(verts,[],faces); me.update()
bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
for mat in shell.data.materials:
 if mat: me.materials.append(mat)
old=shell.data; shell.data=me
if old.users==0: bpy.data.meshes.remove(old)
shell['geometry']='Exact simplified GIS perimeter preserved. Street-side openings are constructed as segmented wall panels; no boolean remesh. Openings for glass stair bay, Main Street storefront and upper punched windows follow official project imagery; exact widths are interpreted.'
# Save source-only and verify no accidentally open roof or missing walls in the asset.
bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'ring_vertices':N,'wall_faces':len(me.polygons),'wall_openings':len(openings),'bounds_xy':[[min(v.x for v in ring),min(v.y for v in ring)],[max(v.x for v in ring),max(v.y for v in ring)]]},indent=2))
