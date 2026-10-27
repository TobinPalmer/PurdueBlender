import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'audit/delta_zeta/sources/purdue_gis_fid752_raw.json';OUT=ROOT/'modular/buildings/massing_house_301841601_7ae6159.blend'
f=json.load(open(RAW,encoding='utf8'))['features'][0];assert f['attributes']['FID']==752 and f['attributes']['BUILDING_N']=='Delta Zeta';ring=f['geometry']['rings'][0][:-1]
lat0=40.4274;lon0=-86.9137;xy=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring];assert len(xy)==11
# Use the first long GIS wall segment as the illustrative facade axis. The footprint stays in campus coordinates.
p0,p1=xy[0],xy[1];dx=p1[0]-p0[0];dy=p1[1]-p0[1];L=math.hypot(dx,dy);u=(dx/L,dy/L);n=(dy/L,-dx/L) # inward right-hand normal for clockwise ring
local=[((x-p0[0])*u[0]+(y-p0[1])*u[1],(x-p0[0])*n[0]+(y-p0[1])*n[1]) for x,y in xy]
smin,smax=min(s for s,t in local),max(s for s,t in local);tmin,tmax=min(t for s,t in local),max(t for s,t in local)
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.users==0:bpy.data.collections.remove(c)
scene=bpy.context.scene;scene.name='Building_massing_house_301841601_7ae6159';asset=bpy.data.collections.new('Asset_massing_house_301841601_7ae6159');scene.collection.children.link(asset)
def mat(name,c,r=.82):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=r;return m
brick=mat('Hilltop brown brick',(.38,.19,.12));brick2=mat('Entry bay brick',(.45,.23,.15));stone=mat('Warm ivory stone',(.84,.80,.70));trim=mat('White gable/window trim',(.91,.90,.84));glass=mat('Deep blue glass',(.025,.10,.15),.28);roof=mat('Dark gray shingles',(.13,.15,.17));door=mat('Deep green-blue doors',(.025,.065,.08));base=mat('Foundation stone',(.43,.39,.33))
materials=[brick,brick2,stone,trim,glass,roof,door,base]
V=[];F=[];MI=[]
def world(s,t,z):return (p0[0]+u[0]*s+n[0]*t,p0[1]+u[1]*s+n[1]*t,z)
def face_local(coords,mi):
 ids=[]
 for s,t,z in coords:ids.append(len(V));V.append(world(s,t,z))
 F.append(ids);MI.append(mi)
def box(s,t,z,ds,dt,dz,mi):
 s0,s1=s-ds/2,s+ds/2;t0,t1=t-dt/2,t+dt/2;z0,z1=z-dz/2,z+dz/2
 q=[(s0,t0,z0),(s1,t0,z0),(s1,t1,z0),(s0,t1,z0),(s0,t0,z1),(s1,t0,z1),(s1,t1,z1),(s0,t1,z1)]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face_local([q[i] for i in ids],mi)
def prism(poly,z0,z1,mi):
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];face_local([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)],mi if i%4 else 1)
 face_local([(s,t,z1) for s,t in poly],mi);face_local([(s,t,z0) for s,t in reversed(poly)],mi)
def beam_front(s1,z1,s2,z2,t,thick,depth,mi):
 ds=s2-s1;dz=z2-z1;ll=math.hypot(ds,dz);ps=-dz/ll*thick/2;pz=ds/ll*thick/2
 q=[(s1+ps,t,z1+pz),(s2+ps,t,z2+pz),(s2-ps,t,z2-pz),(s1-ps,t,z1-pz)];back=[(s,t-depth,z) for s,_,z in q]
 face_local(q,mi);face_local(list(reversed(back)),mi)
 for j in range(4):face_local([q[j],q[(j+1)%4],back[(j+1)%4],back[j]],mi)
def arch_front(s,t,zbase,w,h,thick,depth,mi):
 r=w/2;spring=zbase+h
 box(s-r-thick/2,t,zbase+h/2,thick,depth,h,mi);box(s+r+thick/2,t,zbase+h/2,thick,depth,h,mi)
 for i in range(12):
  a0=math.pi*i/12;a1=math.pi*(i+1)/12
  o0=(s+(r+thick)*math.cos(a0),spring+(r+thick)*math.sin(a0));o1=(s+(r+thick)*math.cos(a1),spring+(r+thick)*math.sin(a1));i0=(s+r*math.cos(a0),spring+r*math.sin(a0));i1=(s+r*math.cos(a1),spring+r*math.sin(a1))
  q=[(o0[0],t,o0[1]),(o1[0],t,o1[1]),(i1[0],t,i1[1]),(i0[0],t,i0[1])];back=[(x,t-depth,z) for x,_,z in q]
  face_local(q,mi);face_local(list(reversed(back)),mi)
  for j in range(4):face_local([q[j],q[(j+1)%4],back[(j+1)%4],back[j]],mi)
def arch_glass(s,t,zbase,w,h,mi=4):
 r=w/2;spring=zbase+h;q=[(s-r,t,spring),(s+r,t,spring)]
 for i in range(13):
  a=math.pi*i/12;q.append((s+r*math.cos(a),t,spring+r*math.sin(a)))
 face_local(q,mi)
def window_front(s,t,z,w=1.8,h=1.75):
 box(s,t-.1,z,w,.12,h,4)
 for ss in (s-w/2-.12,s+w/2+.12):box(ss,t-.22,z,.18,.18,h+.25,3)
 for zz in (z-h/2-.12,z+h/2+.12):box(s,t-.22,zz,w+.42,.18,.18,3)
 box(s,t-.29,z,.09,.10,h,3);box(s,t-.29,z,w,.10,.08,3)
# Exact official GIS shell, two main stories. A dormered attic is suggested by gables.
prism(local,0,.55,7);prism(local,.55,4.05,0);prism(local,4.05,4.32,2);prism(local,4.32,8.15,0)
# Roof plan follows the footprint's stepped wings; gables do not bridge the whole bounding rectangle.
roof_front=-.2;eave=8.15
# Exact GIS outline cap keeps the model roof base registered to the official building envelope.
face_local([(ss,tt,8.20) for ss,tt in local],5)
def gable_roof(s0,s1,tfront,tback,ridge,front_gable=True):
 mid=(s0+s1)/2
 face_local([(s0,tfront,eave),(s0,tback,eave),(mid,tback,ridge),(mid,tfront,ridge)],5)
 face_local([(mid,tfront,ridge),(mid,tback,ridge),(s1,tback,eave),(s1,tfront,eave)],5)
 face_local([(s0,tfront,eave),(s1,tfront,eave),(mid,tfront,ridge)],1 if front_gable else 0)
 face_local([(s0,tback,eave),(mid,tback,ridge),(s1,tback,eave)],0)
 if front_gable:
  for a,b in [((s0,eave),(mid,ridge)),((mid,ridge),(s1,eave))]:beam_front(a[0],a[1],b[0],b[1],tfront-.03,.20,.10,3)
# Main entrance-facing wing: three gables over the actual shallow front wing.
segments=[(5.5,17.0,13.5),(17.0,29.0,12.6),(29.0,smax,13.0)]
for s0,s1,ridge in segments:gable_roof(s0,s1,roof_front,16.6,ridge,True)
# The footprint's northwest/rear wing occupies a deeper, narrower polygon range.
# Give it its own gable roof and keep it within that GIS wing's limits.
gable_roof(-11.35,5.45,16.55,36.35,12.4,False)
# Front bay and entrance positioned along the long source perimeter wall.
entry_s=9.0;front_t=roof_front-.05
# raised entry tower: brick mass and simple front-facing gable cap.
box(entry_s,front_t-.30,9.9,9.0,.70,3.5,1)
face_local([(entry_s-4.6,front_t-.68,11.55),(entry_s+4.6,front_t-.68,11.55),(entry_s,front_t-.68,14.0)],1)
beam_front(entry_s-4.6,11.55,entry_s,14.0,front_t-.74,.28,.14,3);beam_front(entry_s,14.0,entry_s+4.6,11.55,front_t-.74,.28,.14,3)
# tall arched upper glazing in the entry bay
box(entry_s,front_t-.77,9.95,3.8,.08,1.65,4)
arch_glass(entry_s,front_t-.86,10.75,3.8,1.65,4)
arch_front(entry_s,front_t-.98,10.75,3.8,1.65,.35,.18,2)
# double-door entry with pale stone arch surround
box(entry_s,front_t-.70,2.1,2.7,.10,2.9,6)
arch_glass(entry_s,front_t-.84,.65,2.7,2.9,6)
arch_front(entry_s,front_t-1.0,.65,2.7,2.9,.40,.18,2)
# lantern-like sconces and horizontal stone entry belt
for ss in (entry_s-2.2,entry_s+2.2):box(ss,front_t-.90,2.6,.22,.18,.55,3)
box(entry_s,front_t-.76,4.7,8.7,.32,.28,2)
# wing windows in the front facade; central entry bay breaks the otherwise regular rhythm.
front_centers=[2.5,4.8,14.5,19.5,24.0,29.0,34.0,38.0]
for ss in front_centers:
 if abs(ss-entry_s)<5.1:continue
 for zz in (2.35,6.25):window_front(ss,front_t,zz,2.0,1.75)
# Windows on the exposed end walls of the front and rear wings, kept on GIS footprint edges.
for ss,ts in [(smax-.12,(3.5,8.5,13.2)),(5.58,(20.0,27.0,34.0)),(smin+.12,(15.0,22.5,30.0))]:
 for tt in ts:
  for zz in (2.35,6.25):
   box(ss,tt,zz,.12,1.8,1.75,4)
   for t2 in (tt-.98,tt+.98):box(ss-.16,t2,zz,.20,.16,1.98,3)
   for z2 in (zz-.98,zz+.98):box(ss-.16,tt,z2,.20,2.12,.16,3)
# Rear gable wing windows on its actual far wall.
for ss in (-8.0,-3.0,2.0):
 for zz in (2.35,6.25):
  box(ss,36.70,zz,1.8,.12,1.75,4)
  for s2 in (ss-.98,ss+.98):box(s2,36.54,zz,.16,.20,1.98,3)
  for z2 in (zz-.98,zz+.98):box(ss,36.54,z2,2.12,.20,.16,3)
# Small triangular attic windows on the three source-inspired front gables.
for s0,s1,ridge in segments:
 mid=(s0+s1)/2;zwin=9.55
 box(mid,roof_front-.15,zwin,1.25,.12,1.0,4)
 for sgn in (-1,1):box(mid+sgn*.72,roof_front-.24,zwin,.14,.18,1.2,3)
# Build the required single mesh asset object.
mesh=bpy.data.meshes.new('Delta Zeta official GIS and photo based mesh');mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new('House_301841601',mesh);asset.objects.link(obj)
for m in materials:mesh.materials.append(m)
for p,mi in zip(mesh.polygons,MI):p.material_index=mi
obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
obj['building_name']='Delta Zeta, Xi Omega Chapter';obj['source_fid']=752;obj['official_address']='825 Hilltop Dr';obj['footprint_source']='Purdue BuildingShapesZip4 FID 752';obj['floor_status']='Two main levels plus gabled attic estimated from official exterior photo; GIS NUM_LEVELS=1 undefined';obj['height_status']='Estimated; Extrution=36 field unit unknown';obj['front_status']='Illustrative facade along the longest source polygon edge; photo not georeferenced'
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));print('SAVED',OUT,'verts',len(mesh.vertices),'faces',len(mesh.polygons),'local_extent',smin,smax,tmin,tmax,'bounds',min(x for x,y in xy),max(x for x,y in xy),min(y for x,y in xy),max(y for x,y in xy))
