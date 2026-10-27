import bpy, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'audit/alpha_xi_delta/sources/purdue_gis_fid788_raw.json'
OUT=ROOT/'modular/buildings/massing_house_301841248_fe939c7.blend'
data=json.load(open(RAW,encoding='utf8')); feature=data['features'][0]
assert feature['attributes']['FID']==788 and feature['attributes']['BUILDING_N']=='Alpha Xi Delta'
ring=feature['geometry']['rings'][0][:-1]; lat0=40.4274; lon0=-86.9137
pts=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
assert len(pts)==24
xs=[p[0] for p in pts];ys=[p[1] for p in pts]; minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.users==0: bpy.data.collections.remove(c)
scene=bpy.context.scene; scene.name='Building_massing_house_301841248_fe939c7'
asset=bpy.data.collections.new('Asset_massing_house_301841248_fe939c7');scene.collection.children.link(asset)
def mat(name,color,rough=.82):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=rough;return m
brick=mat('Alpha Xi Delta dark red brick',(.25,.07,.045)); brick2=mat('Brick variation',(.34,.095,.06)); stone=mat('Warm limestone',(.68,.60,.49)); dark=mat('Dark bronze trim',(.13,.095,.065)); glass=mat('Deep window glass',(.035,.09,.12),.28); roofmat=mat('Charcoal roof',(.11,.12,.13)); wood=mat('Recessed dark wood door',(.095,.045,.025)); foundation=mat('Stone base',(.4,.37,.32))
materials=[brick,brick2,stone,dark,glass,roofmat,wood,foundation]
V=[];F=[];MI=[]
def face(coords,mi):
 ids=[]
 for q in coords: ids.append(len(V));V.append(tuple(q))
 F.append(ids);MI.append(mi)
def box(cx,cy,cz,sx,sy,sz,mi):
 x0,x1=cx-sx/2,cx+sx/2;y0,y1=cy-sy/2,cy+sy/2;z0,z1=cz-sz/2,cz+sz/2
 a=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face([a[i] for i in ids],mi)
def prism(poly,z0,z1,mi):
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];face([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)],mi if i%6 else 1)
 face([(x,y,z1) for x,y in poly],mi);face([(x,y,z0) for x,y in reversed(poly)],mi)
def arch(cx,y,zbase,clear_w,clear_h,thick,depth,mi):
 # Limestone jambs and a segmented semicircular arch around recessed entrance.
 r=clear_w/2; centerz=zbase+clear_h
 box(cx-r-thick/2,y,centerz-clear_h/2,thick,depth,clear_h,mi);box(cx+r+thick/2,y,centerz-clear_h/2,thick,depth,clear_h,mi)
 n=9
 for i in range(n):
  a0=math.pi*i/n; a1=math.pi*(i+1)/n
  outer0=(cx+(r+thick)*math.cos(a0),centerz+(r+thick)*math.sin(a0));outer1=(cx+(r+thick)*math.cos(a1),centerz+(r+thick)*math.sin(a1))
  inner0=(cx+r*math.cos(a0),centerz+r*math.sin(a0));inner1=(cx+r*math.cos(a1),centerz+r*math.sin(a1))
  front=[(outer0[0],y,outer0[1]),(outer1[0],y,outer1[1]),(inner1[0],y,inner1[1]),(inner0[0],y,inner0[1])]
  back=[(x,y+depth,z) for x,_,z in front]
  face(front,mi);face(list(reversed(back)),mi)
  for j in range(4): face([front[j],front[(j+1)%4],back[(j+1)%4],back[j]],mi)
def window_south(x,y,z,w=1.8,h=1.55):
 box(x,y-.08,z,w,.14,h,4)
 for xx in (x-w/2-.13,x+w/2+.13):box(xx,y-.18,z,.18,.22,h+.28,3)
 for zz in (z-h/2-.13,z+h/2+.13):box(x,y-.18,zz,w+.44,.22,.18,3)
 box(x,y-.25,z,.08,.12,h,3)
 box(x,y-.25,z,w,.12,.07,3)
# Exact GIS outline extruded as the source wall footprint; two main facade levels are estimated from photo.
prism(pts,0,.55,7);prism(pts,.55,4.1,0);prism(pts,4.1,4.35,2);prism(pts,4.35,8.2,0)
# Hipped roof over the envelope. Height/form are estimates because the source photo crops out the roof.
rx0,rx1=minx+.8,maxx-.8;ry0,ry1=miny+.8,maxy-.8;cx=(rx0+rx1)/2;inset=min((ry1-ry0)*.23,(rx1-rx0)*.23); e=8.2;ridge=12.3
ls=(cx,ry0+inset,ridge);rs=(cx,ry1-inset,ridge)
face([(rx0,ry0,e),(rx1,ry0,e),rs,ls],5)
face([(rx1,ry0,e),(rx1,ry1,e),rs],5)
face([(rx1,ry1,e),(rx0,ry1,e),ls,rs],5)
face([(rx0,ry1,e),(rx0,ry0,e),ls],5)
# Front (south-facing GIS edge): photo is from southeast, looking northwest; entrance sits toward its west end.
front_y=miny+.05;front_x=minx+4.0; door_z=2.0
box(front_x,front_y-.18,door_z,2.0,.16,3.0,6)
arch(front_x,front_y-.35,.52,2.0,2.7,.42,.27,2)
# Upper transom/entry lintel and a shallow stone sill at threshold.
box(front_x,front_y-.48,3.48,2.95,.30,.32,2);box(front_x,front_y-.62,.55,2.65,.85,.22,2)
# Small wall lanterns framing the arch.
for lx in (front_x-1.85,front_x+1.85):
 box(lx,front_y-.42,2.35,.16,.18,.45,3);box(lx,front_y-.50,2.48,.34,.18,.13,2)
# Horizontal window bays seen in the archival recruitment photo.
for z in (2.45,6.25):
 for x in (minx+8.5,minx+12.7,minx+16.8,minx+20.0):
  if abs(x-front_x)>2.0: window_south(x,front_y,z,2.3 if z>4 else 1.9,1.5)
# Long dark horizontal belt/canopy band under upper-story windows, reflecting source facade rhythm.
box((minx+maxx)/2,front_y-.16,7.58,maxx-minx-1.2,.35,.40,3)
# Repeated east/west wall windows, kept simple and schematic where source views are unavailable.
for x,side in ((minx+.06,'west'),(maxx-.06,'east')):
 out=-1 if side=='west' else 1
 for y in [miny+4,miny+9,miny+14,miny+19,miny+24]:
  if y>maxy: continue
  for z in (2.45,6.25):
   box(x+out*.07,y,z,.14,1.65,1.5,4)
   for yy in (y-.92,y+.92):box(x+out*.15,yy,z,.22,.16,1.74,3)
   for zz in (z-.84,z+.84):box(x+out*.15,y,zz,.22,1.98,.16,3)
# Roof eave fascia.
box(cx,ry0,8.05,rx1-rx0,.35,.30,2);box(cx,ry1,8.05,rx1-rx0,.35,.30,2)
mesh=bpy.data.meshes.new('Alpha Xi Delta source-based exterior mesh');mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new('House_301841248',mesh);asset.objects.link(obj)
for m in materials:mesh.materials.append(m)
for p,mi in zip(mesh.polygons,MI):p.material_index=mi
obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
obj['building_name']='Alpha Xi Delta, Alpha Eta Chapter';obj['source_fid']=788;obj['official_address']='519 University St';obj['footprint_source']='Purdue BuildingShapesZip4 FID 788';obj['floor_count_status']='Two facade levels interpreted from the 2008 photo; GIS NUM_LEVELS=1 is undefined';obj['roof_status']='Estimated; roof cropped out of reference photo';obj['front_side_status']='Illustrative south-facing long GIS edge; camera is southeast of house and looks northwest.'
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print('SAVED',OUT,'verts',len(mesh.vertices),'faces',len(mesh.polygons),'bounds',minx,maxx,miny,maxy)
