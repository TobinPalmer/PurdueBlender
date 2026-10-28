import bpy,bmesh,json,math,os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
HERE=os.path.dirname(__file__);ROOT=os.path.abspath(os.path.join(HERE,'..','..'));cfg=json.load(open(os.path.join(HERE,'build_config.json'),encoding='utf-8'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841601_7ae6159.blend');bpy.ops.wm.open_mainfile(filepath=ASSET)
feature=json.load(open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf-8-sig'))['features'][0]
obj=bpy.data.objects[cfg['object_name']];coll=bpy.data.collections[cfg['collection_name']]
if len(coll.objects)!=1 or obj not in coll.objects[:]:raise RuntimeError('Expected stable one-object DZ library')
old=obj.data;obj.data=None;old.materials.clear()
for m in list(bpy.data.materials):
 if m.name.startswith('DELTAZETA_') and m.users==0:bpy.data.materials.remove(m)
ring=feature['geometry']['rings'][0];ring=ring[:-1] if ring[0]==ring[-1] else ring
R=6378137.;lat0=40.4274;lon0=-86.9137;pts=[]
for x,y in ring:
 lon=x/R*180/math.pi;lat=(2*math.atan(math.exp(y/R))-math.pi/2)*180/math.pi
 pts.append(Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.,0)))
area2=sum(pts[i].x*pts[(i+1)%len(pts)].y-pts[(i+1)%len(pts)].x*pts[i].y for i in range(len(pts)));sign=1 if area2>0 else -1
materials=[]
def mat(name,color,rough=.82):
 m=bpy.data.materials.new('DELTAZETA_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
 materials.append(m);return len(materials)-1
brick=mat('Interpretive_Brick',cfg['palette']['brick_interpretive']);stone=mat('Interpretive_Stone',cfg['palette']['stone_interpretive']);roof=mat('Estimated_Roof_Cap',cfg['palette']['roof_interpretive']);glass=mat('Interpretive_Glazing',cfg['palette']['glass_interpretive'],.22);wood=mat('Interpretive_Wood_Door',cfg['palette']['door_interpretive'],.65);trim=mat('Warm_Trim',(.86,.83,.75));floor=mat('Schematic_Interior_Floor',cfg['palette']['floor']);rug=mat('Schematic_Room_Rugs',cfg['palette']['carpet']);furn=mat('Schematic_Furniture',cfg['palette']['furniture']);dark=mat('Dark_Metal',(.08,.07,.06),.45)
vtx=[];faces=[];mi=[]
def poly(ps,m):
 k=len(vtx);vtx.extend(tuple(Vector(p)) for p in ps);faces.append(tuple(range(k,k+len(ps))));mi.append(m)
def box(c,t,n,w,d,h,m):
 c=Vector(c);t=Vector((t.x,t.y,0)).normalized();n=Vector((n.x,n.y,0)).normalized();z=Vector((0,0,1));offset=[(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)];k=len(vtx);vtx.extend(tuple(c+t*a+n*b+z*q) for a,b,q in offset)
 for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):faces.append(tuple(k+j for j in f));mi.append(m)
def rail(a,b,width,depth,n,m):
 a=Vector(a);b=Vector(b);t=(b-a).normalized();n=Vector(n).normalized();side=t.cross(n);c=(a+b)*.5;L=(b-a).length;w=width/2;d=depth/2;k=len(vtx)
 vtx.extend(tuple(c+t*x+n*y+side*z) for x,y,z in ((-L/2,-d,-w),(L/2,-d,-w),(L/2,d,-w),(-L/2,d,-w),(-L/2,-d,w),(L/2,-d,w),(L/2,d,w),(-L/2,d,w)))
 for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):faces.append(tuple(k+j for j in f));mi.append(m)
H=cfg['estimated_wall_eave_height_m'];level=H/2;roof_z=cfg['estimated_roof_height_m'];edges=[]
for z in (.18,level,H):
 for ti in tessellate_polygon([pts]):poly([Vector((pts[int(i)].x,pts[int(i)].y,z)) for i in ti],floor)
for i,a in enumerate(pts):
 b=pts[(i+1)%len(pts)];delta=b-a;L=delta.length
 if L<.2:continue
 t=Vector((delta.x/L,delta.y/L,0));n=Vector((t.y,-t.x,0))*sign;edges.append((i,a,b,L,t,n))
 poly((Vector((a.x,a.y,0)),Vector((b.x,b.y,0)),Vector((b.x,b.y,.42)),Vector((a.x,a.y,.42))),stone)
 poly((Vector((a.x,a.y,.42)),Vector((b.x,b.y,.42)),Vector((b.x,b.y,H)),Vector((a.x,a.y,H))),brick)
# Source provides no roof plan; use an explicitly estimated low ridge over the
# complete concave footprint, triangulated only within the official GIS ring.
cx=sum(p.x for p in pts)/len(pts);cy=sum(p.y for p in pts)/len(pts);xx=sum((p.x-cx)**2 for p in pts);xy=sum((p.x-cx)*(p.y-cy) for p in pts);yy=sum((p.y-cy)**2 for p in pts);ang=.5*math.atan2(2*xy,xx-yy);axis=Vector((math.cos(ang),math.sin(ang),0));normal=Vector((-axis.y,axis.x,0));proj_n=[(p.x-cx)*normal.x+(p.y-cy)*normal.y for p in pts];maxn=max(abs(v) for v in proj_n);ridge_fraction=1-min(abs(v) for v in proj_n)/maxn
for ti in tessellate_polygon([pts]):
 ps=[]
 for i in ti:
  p=pts[int(i)];off=(p.x-cx)*normal.x+(p.y-cy)*normal.y;z=H+(roof_z-H)*(1-abs(off)/maxn)/ridge_fraction;ps.append(Vector((p.x,p.y,z)))
 poly(ps,roof)
for i,a,b,L,t,n in edges:box((a+b)*.5+Vector((0,0,H+.06)),t,n,L+.1,.16,.14,stone)
# Repeated windows are illustrative; source photo gives no measured schedule.
entry=next(e for e in edges if e[0]==cfg['entry_edge_index']);ei,ea,eb,eL,et,en=entry;p=ea.lerp(eb,.5)
for idx,a,b,L,t,n in edges:
 if L<5:continue
 count=max(1,int(L//7));space=L/(count+1);w=min(1.6,space*.54)
 for fl in range(2):
  z=.42+level*(fl+.5)
  for bay in range(count):
   d=space*(bay+1)
   if idx==ei and abs(d-L/2)<4:continue
   q=a.lerp(b,d/L);c=Vector((q.x,q.y,z))+n*.07;box(c,t,n,w,.08,1.55,glass)
   box(c+Vector((0,0,.88)),t,n,w+.2,.13,.12,trim);box(c-Vector((0,0,.88)),t,n,w+.22,.15,.12,trim)
   for s in (-1,1):box(c+t*(s*(w/2+.06)),t,n,.1,.13,1.65,trim)
   box(c,t,n,.045,.11,1.45,trim)
# Double entry doors and tall arched glazed panel above, supported qualitatively
# by the official Purdue chapter-house image. Dimensions/position are estimates.
doorbase=.48;doorh=2.45;doorw=2.6;doorc=Vector((p.x,p.y,doorbase+doorh/2))+en*.20
for s in (-1,1):
 c=doorc+et*(s*.63);box(c,et,en,1.2,.12,doorh,wood)
 for z in (.65,1.25,1.95):box(c+Vector((0,0,z-doorbase-doorh/2)),et,en,1.04,.06,.06,trim)
 box(c+et*(s*.36),et,en,.045,.08,doorh-.18,trim)
archw=2.9;zbot=3.05;spring=5.05;top=5.82;arc=[Vector((p.x,p.y,spring))+et*(math.cos(i*math.pi/8)*archw/2)+Vector((0,0,(top-spring)*math.sin(i*math.pi/8)))+en*.18 for i in range(9)]
arch=[Vector((p.x,p.y,zbot))+et*(-archw/2)+en*.18,Vector((p.x,p.y,zbot))+et*(archw/2)+en*.18]+arc;poly(arch,glass)
path=[Vector((p.x,p.y,zbot))+et*(-archw/2-.13)+en*.22,Vector((p.x,p.y,spring))+et*(-archw/2-.13)+en*.22]
for i in range(9):path.append(Vector((p.x,p.y,spring))+et*(math.cos(math.pi-i*math.pi/8)*(archw/2+.13))+Vector((0,0,(top-spring+.13)*math.sin(math.pi-i*math.pi/8)))+en*.22)
path.append(Vector((p.x,p.y,zbot))+et*(archw/2+.13)+en*.22)
for a,b in zip(path,path[1:]):rail(a,b,.14,.1,en,trim)
box(Vector((p.x,p.y,4.1))+en*.24,et,en,.06,.08,1.6,trim)
# Front landing, wide steps, globe-post proxies, and chapter sign. These site
# elements are illustrative and are excluded from structural footprint checks.
box(Vector((p.x,p.y,.4))+en*1.15,et,en,6.5,2.5,.22,stone)
for k in range(4):box(Vector((p.x,p.y,.10+k*.10))+en*(2.35+k*.44),et,en,7.2+k*.2,.55,.18,stone)
for s in (-1,1):
 q=Vector((p.x,p.y,0))+en*3.1+et*(s*4.5);box(q+Vector((0,0,1.2)),et,en,.16,.16,2.4,trim);box(q+Vector((0,0,2.55)),et,en,.42,.42,.42,trim)
sc=Vector((p.x,p.y,.58))+en*6.3+et*7.2;box(sc,et,en,3.2,.6,1.16,stone)
front=sc+en*.34
for a,b in ((front+et*(-.9)+Vector((0,0,-.2)),front+et*(-.35)+Vector((0,0,-.2))),(front+et*(-.9)+Vector((0,0,-.2)),front+et*(-.62)+Vector((0,0,.2))),(front+et*(-.35)+Vector((0,0,-.2)),front+et*(-.62)+Vector((0,0,.2))),(front+et*.2+Vector((0,0,.2)),front+et*.78+Vector((0,0,.2))),(front+et*.78+Vector((0,0,.2)),front+et*.2+Vector((0,0,-.2))),(front+et*.2+Vector((0,0,-.2)),front+et*.78+Vector((0,0,-.2)))):rail(a,b,.07,.06,en,dark)
# Room-use modules are diagrams only; room categories come from the 2023 chapter feature.
room_centers=[]
def inside(x,y):
 hit=False;j=len(pts)-1
 for i,a in enumerate(pts):
  b=pts[j]
  if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:hit=not hit
  j=i
 return hit
for y in [min(p.y for p in pts)+5+i*7 for i in range(5)]:
 for x in [min(p.x for p in pts)+5+i*7 for i in range(8)]:
  if all(inside(x+axis.x*u+normal.x*v,y+axis.y*u+normal.y*v) for u in (-4,4) for v in (-3.5,3.5)) and all(math.hypot(x-c.x,y-c.y)>11 for c in room_centers):room_centers.append(Vector((x,y,0)))
room_centers.sort(key=lambda q:(q.x-cx)**2+(q.y-cy)**2);room_centers=room_centers[:4]
json.dump({'status':'schematic only; not a measured or current floor plan','rooms':[{'name':name,'center_xy_m':[c.x,c.y],'center_z_m':level+.13,'source_basis':'2023 official chapter feature names this shared room type; its position and size are illustrative'} for name,c in zip(('Foyer','Living room','Dining room','Kitchen'),room_centers)]},open(os.path.join(HERE,'room_layout.json'),'w',encoding='utf-8'),indent=2)
for i,c in enumerate(room_centers):
 z=level+.13;box(Vector((c.x,c.y,z)),axis,normal,8,7,.1,rug)
 if i==0:box(Vector((c.x,c.y,z+.4))+normal*1.4,axis,normal,2.1,.7,.6,furn)
 elif i==1:
  box(Vector((c.x,c.y,z+.72)),axis,normal,3.5,1.4,.16,furn)
  for u in (-2.2,-.7,.7,2.2):
   for s in (-1,1):box(Vector((c.x,c.y,z+.4))+axis*u+normal*s*1.35,axis,normal,.5,.5,.65,furn)
 elif i==2:
  for u in (-2,2):box(Vector((c.x,c.y,z+.4))+axis*u+normal*1.5,axis,normal,2.3,.8,.5,furn)
 else:
  for s in (-1,1):box(Vector((c.x,c.y,z+.75))+normal*s*2.2,axis,normal,5.7,.7,.12,furn)

mesh=bpy.data.meshes.new(old.name+'_delta_zeta_detail');mesh.from_pydata(vtx,[],faces)
for m in materials:mesh.materials.append(m)
mesh.update()
for p,m in zip(mesh.polygons,mi):p.material_index=m
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();obj.data=mesh
obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
if old.users==0:bpy.data.meshes.remove(old)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('DELTA_ZETA_BUILD='+json.dumps({'feature_id':feature['attributes']['FID'],'ring_vertices':len(pts),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'estimated_eave_m':H,'estimated_roof_m':roof_z,'estimated_roof_axis_deg':math.degrees(ang)%180,'schematic_room_centers_xy_m':[[c.x,c.y] for c in room_centers],'collection_object_count':len(coll.objects)}))
