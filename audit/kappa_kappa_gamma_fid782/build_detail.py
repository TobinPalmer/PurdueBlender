import bpy, json, math, os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
BLEND=os.path.join(ROOT,'modular','buildings','massing_house_301840871_5d1bc06.blend')
with open(os.path.join(os.path.dirname(__file__),'source_fid_782_raw.json'),encoding='utf-8') as f: feature=json.load(f)['features'][0]
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene=bpy.context.scene
target=bpy.data.objects.get('House_301840871')
collection=next((c for c in target.users_collection if c.name=='Asset_massing_house_301840871_5d1bc06'),None)
if not target or not collection: raise RuntimeError('Expected manifest object and asset collection')
world=target.matrix_world.copy()
for ob in list(bpy.data.objects):
    if ob!=target: bpy.data.objects.remove(ob,do_unlink=True)
target.data.clear_geometry(); target.data.materials.clear()
for m in list(bpy.data.materials):
 if m.users==0: bpy.data.materials.remove(m)
raw=feature['geometry']['rings'][0][:-1]
lat0,lon0=40.4274,-86.9137
ring=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in raw]
xs,ys=zip(*ring); cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
ring=[(x-cx,y-cy) for x,y in ring]

def mat(name,color,rough=.7,scale=16,bump=.08,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 n=m.node_tree.nodes; l=m.node_tree.links; p=next(x for x in n if x.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 t=n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value=scale; t.inputs['Detail'].default_value=3
 b=n.new('ShaderNodeBump'); b.inputs['Strength'].default_value=bump; b.inputs['Distance'].default_value=.035
 ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(*(v*.80 for v in color),1); ramp.color_ramp.elements[1].color=(*(min(v*1.12,1) for v in color),1)
 l.new(t.outputs['Fac'],ramp.inputs['Fac']); l.new(ramp.outputs['Color'],p.inputs['Base Color'])
 l.new(t.outputs['Fac'],b.inputs['Height']); l.new(b.outputs['Normal'],p.inputs['Normal']); return m
stone=mat('KKG warm pale Rostone ashlar',(.76,.72,.63),.82,11,.12)
limestone=mat('KKG pale limestone trim',(.84,.80,.70),.72,15,.05)
slate=mat('KKG blue green slate',(.075,.13,.15),.76,24,.12)
slate2=mat('KKG slate variation',(.12,.19,.20),.78,25,.10)
slate_cap=mat('KKG dark slate roof cap',(.035,.06,.07),.78,24,.12)
blue=mat('KKG blue painted shutters',(.055,.15,.25),.66,10,.06)
glass=mat('KKG reflective window glass',(.035,.085,.12),.23,5,.01,.25)
wood=mat('KKG stained oak',(.25,.145,.075),.5,8,.08)
bronze=mat('KKG dark bronze',(.12,.13,.11),.34,6,.02,.7)
plaster=mat('KKG interior plaster',(.75,.70,.60),.86,12,.03)
floor=mat('KKG oak floor',(.32,.205,.11),.66,8,.08)
tile=mat('KKG green slate entry floor',(.16,.23,.20),.78,16,.06)
chapter=mat('KKG blue chapter room tile',(.12,.29,.37),.48,18,.03)
upholstery=mat('KKG warm lounge upholstery',(.58,.47,.31),.9,11,.03)
parts=[]
def mesh(name,v,f,mats,inds=None):
 me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(v,[],f); me.update()
 ob=bpy.data.objects.new(name,me); collection.objects.link(ob)
 for m in mats: me.materials.append(m)
 if inds:
  for p,i in zip(me.polygons,inds): p.material_index=i
 parts.append(ob); return ob
def box(name,c,d,m,ang=0):
 x,y,z=c; a,b,h=[q/2 for q in d]; co=math.cos(ang); si=math.sin(ang)
 v=[(x+xx*co-yy*si,y+xx*si+yy*co,z+zz) for zz in (-h,h) for yy in (-b,b) for xx in (-a,a)]
 return mesh(name,v,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],[m])
def prism(name,poly,z0,z1,m):
 n=len(poly); v=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,[m])

def perimeter_walls(name,poly,z0,z1,m):
 # Keep the outline's roof surface open: a capped footprint extrusion reads as
 # a flat cream roof wherever the separate mansard wings do not cover it.
 n=len(poly); v=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
 f=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,[m])

# Exact official-building wall outline from the 12-vertex FID 782 GIS ring.
perimeter_walls('continuous two story Rostone shell',ring,.20,7.25,stone)
for z,h in [(.4,.35),(3.72,.15),(7.10,.20)]:
 for i,p in enumerate(ring):
  q=ring[(i+1)%len(ring)]; dx=q[0]-p[0];dy=q[1]-p[1];L=math.hypot(dx,dy)
  if L>1: box('continuous limestone belt',((p[0]+q[0])/2,(p[1]+q[1])/2,z),(L,.15,h),limestone,math.atan2(dy,dx))

# Masonry-framed sash windows and paired blue shutters, repeated around the GIS perimeter.
for i,p in enumerate(ring):
 q=ring[(i+1)%len(ring)]; dx=q[0]-p[0];dy=q[1]-p[1];L=math.hypot(dx,dy)
 if L<4: continue
 ux,uy=dx/L,dy/L; angle=math.atan2(dy,dx); n=max(1,int(L//4.4))
 # outward normal derived from the footprint centroid
 nx,ny=uy,-ux
 if nx*(-(p[0]+q[0])/2)+ny*(-(p[1]+q[1])/2)>0: nx,ny=-nx,-ny
 for level,z in enumerate((2.12,5.47)):
  for j in range(n):
   t=(j+.5)*L/n-L/2; x=(p[0]+q[0])/2+ux*t; y=(p[1]+q[1])/2+uy*t
   def put(name,u,v,zz,d,m): box(name,(x+ux*u+nx*v,y+uy*u+ny*v,zz),d,m,angle)
   w=1.35; h=1.52 if level==0 else 1.44
   put('stone window surround',0,.14,z,(w+.24,.12,h+.24),limestone)
   put('dark glazed sash',0,.22,z,(w,.055,h),glass)
   put('sash mullion',0,.26,z,(.055,.035,h-.08),limestone)
   put('sash cross rail',0,.26,z,(w-.06,.035,.05),limestone)
   for s in (-1,1):
    put('blue louvered shutter',s*(w/2+.18),.17,z,(.27,.16,h*.98),blue)
    for k in range(5): put('shutter louver',s*(w/2+.18),.26,z-h*.4+k*h*.19,(.22,.04,.035),bronze)
   put('projecting stone sill',0,.24,z-h/2-.10,(w+.5,.30,.11),limestone)

# Entry lies on the courtyard-facing inner western wall, inferred from the GIS notch and 2017 photo.
entry=None
for i,p in enumerate(ring):
 q=ring[(i+1)%len(ring)]; dx=q[0]-p[0];dy=q[1]-p[1]; L=math.hypot(dx,dy)
 mx=(p[0]+q[0])/2+cx; my=(p[1]+q[1])/2+cy
 if abs(mx+392.4)<1.5 and 54<my<76 and abs(dx)<1.2:
  entry=(p,q,dx,dy,L);break
if entry:
 p,q,dx,dy,L=entry; ux,uy=dx/L,dy/L; angle=math.atan2(dy,dx); nx,ny=uy,-ux
 if nx*(-(p[0]+q[0])/2)+ny*(-(p[1]+q[1])/2)>0:nx,ny=-nx,-ny
 x=(p[0]+q[0])/2; y=(p[1]+q[1])/2
 def ebox(name,u,v,z,d,m):box(name,(x+ux*u+nx*v,y+uy*u+ny*v,z),d,m,angle)
 ebox('arched limestone entry surround',0,.26,1.94,(2.55,.42,3.45),limestone)
 ebox('recessed oak double doors',0,.52,1.68,(1.35,.08,2.55),wood)
 ebox('entry transom glass',0,.53,3.08,(1.40,.06,.42),glass)
 ebox('threshold',0,.78,.27,(2.7,.90,.18),limestone)
 for j in range(3): ebox('limestone entrance step',0,1.05+j*.40,.16-j*.05,(3.3,.76,.18),limestone)
 for s in (-1,1): ebox('bronze door pull',s*.38,.59,1.42,(.06,.04,.22),bronze)
 ebox('KKG chapter letter plaque',0,.39,3.98,(1.8,.15,.52),limestone)
 # The 2017 courtyard photo shows centered KKG lettering above the entry.
 # Make readable raised KKG strokes on the plaque instead of placeholder bars.
 def sign_stroke(u0,z0,u1,z1,width=.052):
  du=u1-u0; dz=z1-z0; length=math.hypot(du,dz); pu=-dz/length*width/2; pz=du/length*width/2
  outline=[(u0+pu,z0+pz),(u1+pu,z1+pz),(u1-pu,z1-pz),(u0-pu,z0-pz)]
  verts0=[]
  for depth in (.50,.57):
   for u,z in outline: verts0.append((x+ux*u+nx*depth,y+uy*u+ny*depth,3.98+z))
  faces0=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
  mesh('raised KKG plaque lettering',verts0,faces0,[bronze])
 # Two K strokes, followed by a compact G; geometry remains in the single joined asset mesh.
 for shift in (-.34,.02):
  sign_stroke(shift-.09,-.16,shift-.09,.16)
  sign_stroke(shift-.09,0,shift+.10,.16)
  sign_stroke(shift-.09,0,shift+.10,-.16)
 sign_stroke(.25,.16,.48,.16);sign_stroke(.25,.16,.25,-.16)
 sign_stroke(.25,-.16,.48,-.16);sign_stroke(.48,-.02,.48,-.16)
 sign_stroke(.35,-.02,.48,-.02)

# Schematic floorplates/rooms follow period account: chapter room below; slate hall,
# dining/lounge and services at grade; bedrooms above. Layout is not a verified current plan.
prism('basement chapter room floor',ring,-2.8,-2.64,chapter)
prism('first floor interior slab',ring,3.58,3.72,tile)
prism('second floor interior slab',ring,6.96,7.10,floor)
def wall(a,b,z0,z1):
 dx=b[0]-a[0];dy=b[1]-a[1]; L=math.hypot(dx,dy)
 if L>.6: box('schematic room partition',((a[0]+b[0])/2,(a[1]+b[1])/2,(z0+z1)/2),(L,.12,z1-z0),plaster,math.atan2(dy,dx))
for z0,z1 in [(.0,3.55),(3.8,6.9)]:
 wall((-5,-14),(-5,14),z0,z1);wall((-8,-1),(-1,-1),z0,z1);wall((-8,7),(-1,7),z0,z1)
wall((-1,12),(10,12),3.8,6.9);wall((-1,-10),(10,-10),3.8,6.9)
# Keep the schematic partition inside the massing footprint; x=+2 falls into
# the source-plan courtyard notch and blocks the photo-visible entry sign.
wall((-1.8,-9),(-1.8,11),3.8,6.9)
def furniture_table(x,y,z):
 box('dining table',(x,y,z+.78),(2.4,1,.12),wood)
 for dx in (-.9,.9):
  for dy in (-.35,.35):box('table leg',(x+dx,y+dy,z+.38),(.10,.10,.72),wood)
for x,y in [(-8,-6),(-4,-6),(-8,-2),(-4,-2)]:
 furniture_table(x,y,3.72)
 for xx in (-1.1,1.1):
  for yy in (-1,1):box('dining chair',(x+xx,y+yy,4.25),(.48,.48,.92),upholstery)
# Upstairs dormitory furnishings, presented as schematic beds/wardrobes.
for x,y in [(-8,14),(-3,14),(4,14),(-9,-14),(-4,-14),(2,-14)]:
 box('bed frame',(x,y,7.43),(2.1,2.8,.30),wood);box('bed linen',(x,y,7.63),(1.9,2.55,.14),upholstery)
 box('wardrobe',(x+1.9,y,8.0),(.6,1.4,1.65),limestone)
box('chapter room platform',(-1,0,-2.25),(7.8,3.2,.3),wood)
for y in (-5,-2,1,4):
 for x in (-5,-2,1,4):box('chapter room bench',(x,y,-2.02),(2,.42,.42),wood)

# Mansard slate roof: block zoning follows the exact U/notched foot shape;
# profile and story heights are estimates informed by official 2017 exterior.
def mansard(x0,x1,y0,y1,name):
 # Broad inset keeps the visible blue-green slate on the sloped roof field,
 # rather than allowing a large flat cap to dominate the courtyard elevation.
 z0,z1,z2,z3=7.25,7.4,9.35,9.58; a,b=.38,3.2
 v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
 (x0+a,y0+a,z1),(x1-a,y0+a,z1),(x1-a,y1-a,z1),(x0+a,y1-a,z1),
 (x0+b,y0+b,z2),(x1-b,y0+b,z2),(x1-b,y1-b,z2),(x0+b,y1-b,z2),
 (x0+b,y0+b,z3),(x1-b,y0+b,z3),(x1-b,y1-b,z3),(x0+b,y1-b,z3)]
 f=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,9,8),(5,6,10,9),(6,7,11,10),(7,4,8,11),(8,9,13,12),(9,10,14,13),(10,11,15,14),(11,8,12,15),(12,13,14,15)]
 mesh(name,v,f,[slate,slate2,slate_cap],[0,1,0,1,0,1,0,1,0,1,0,1,2])
xmin,xmax=min(xs)-cx,max(xs)-cx; ymin,ymax=min(ys)-cy,max(ys)-cy
mansard(xmin-.3,.9,-8.5,11.9,'mansard roof west connector')
mansard(xmin-.2,xmax+.2,8.4,ymax+.2,'mansard roof north wing')
mansard(xmin-.2,7.6,ymin-.2,-8.3,'mansard roof south wing')

# Dormers replicate the visible slate roof rhythm; trim and blue glazing echo the photo.
def dormer(x,y,angle=0):
 box('pale stone dormer',(x,y,9.25),(1.5,.78,1.62),stone,angle)
 box('dormer window frame',(x,y-.43,9.30),(1.05,.10,1.18),limestone,angle)
 box('dormer window glass',(x,y-.50,9.30),(.76,.04,.90),glass,angle)
 box('dormer mullion',(x,y-.53,9.30),(.05,.035,.86),limestone,angle)
 c=math.cos(angle);s=math.sin(angle)
 def pt(a,b,z):return (x+a*c-b*s,y+a*s+b*c,z)
 mesh('triangular slate dormer roof',[pt(-.85,-.48,10.02),pt(.85,-.48,10.02),pt(0,-.48,10.74),pt(-.85,.48,10.02),pt(.85,.48,10.02),pt(0,.48,10.74)],[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],[slate])
for x in (-8,-3,2,7):dormer(x,10.25)
# The single four-dormer row is the row visible in the official 2017 courtyard photo;
# unseen roof elevations are not populated with an unverified second row.
for x,y in [(xmin+.4,ymin+.7),(xmin+.4,ymax-.7),(xmax-.4,ymin+.7),(xmax-.4,ymax-.7)]:box('bronze rainwater downpipe',(x,y,3.8),(.08,.08,6.9),bronze)

# Build one joined mesh with explicit material-index remapping. Blender's
# generic object-join left several source faces mapped to unrelated slots.
verts=[];faces=[];face_materials=[];all_mats=[];mat_indices={}
for ob in parts:
 base=len(verts)
 for v in ob.data.vertices:verts.append((v.co.x+cx,v.co.y+cy,v.co.z))
 slot_map=[]
 for m in ob.data.materials:
  if m is None:slot_map.append(0);continue
  key=m.as_pointer()
  if key not in mat_indices:mat_indices[key]=len(all_mats);all_mats.append(m)
  slot_map.append(mat_indices[key])
 for poly in ob.data.polygons:
  faces.append(tuple(base+i for i in poly.vertices))
  face_materials.append(slot_map[poly.material_index] if poly.material_index<len(slot_map) else 0)
newmesh=bpy.data.meshes.new('House_301840871_DetailedMesh')
newmesh.from_pydata(verts,[],faces);newmesh.update()
for m in all_mats:newmesh.materials.append(m)
for poly,index in zip(newmesh.polygons,face_materials):poly.material_index=index
oldmesh=target.data;target.data=newmesh
for ob in list(bpy.data.objects):
 if ob!=target:bpy.data.objects.remove(ob,do_unlink=True)
if oldmesh.users==0:bpy.data.meshes.remove(oldmesh)
target.name='House_301840871';target.matrix_world=world;target.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bb=[target.matrix_world @ __import__('mathutils').Vector(v) for v in target.bound_box]
metrics={'asset_id':'massing_house_301840871_5d1bc06','object':target.name,'collection':collection.name,'scene':scene.name,'object_count':len(bpy.data.objects),'vertices':len(target.data.vertices),'polygons':len(target.data.polygons),'materials':[m.name if m else None for m in target.data.materials],'world_bounds':{'min':[min(v[i] for v in bb) for i in range(3)],'max':[max(v[i] for v in bb) for i in range(3)]},'source_fid':782,'gis_vertices':len(ring),'dependencies':'procedural materials only'}
with open(os.path.join(os.path.dirname(__file__),'build_metrics.json'),'w',encoding='utf-8') as f:json.dump(metrics,f,indent=2)
print(json.dumps(metrics,indent=2))
