import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'audit/delta_gamma/sources/purdue_gis_fid783_raw.json';OUT=ROOT/'modular/buildings/massing_house_301840872_582df9d.blend'
f=json.load(open(RAW,encoding='utf8'))['features'][0];assert f['attributes']['FID']==783 and f['attributes']['BUILDING_N']=='Delta Gamma'
ring=f['geometry']['rings'][0][:-1];lat0=40.4274;lon0=-86.9137;pts=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring];assert len(pts)==14
xs=[p[0] for p in pts];ys=[p[1] for p in pts];minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.users==0:bpy.data.collections.remove(c)
scene=bpy.context.scene;scene.name='Building_massing_house_301840872_582df9d';asset=bpy.data.collections.new('Asset_massing_house_301840872_582df9d');scene.collection.children.link(asset)
def mat(n,c,r=.82):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=r;return m
brick=mat('Delta Gamma red brick',(.42,.105,.065));brick2=mat('Central bay brick',(.50,.145,.09));stone=mat('Warm pale stone',(.79,.70,.56));trim=mat('Light window trim',(.83,.78,.67));glass=mat('Blue-black glass',(.025,.075,.095),.28);roof=mat('Dark low roof',(.12,.13,.14));door_mat=mat('Deep blue entrance doors',(.035,.07,.095));gold=mat('Antique gold letters',(.68,.45,.13));foundation=mat('Retaining and base stone',(.44,.39,.31))
materials=[brick,brick2,stone,trim,glass,roof,door_mat,gold,foundation]
V=[];F=[];MI=[]
def face(c,mi):
 ids=[]
 for q in c:ids.append(len(V));V.append(tuple(q))
 F.append(ids);MI.append(mi)
def box(cx,cy,cz,sx,sy,sz,mi):
 x0,x1=cx-sx/2,cx+sx/2;y0,y1=cy-sy/2,cy+sy/2;z0,z1=cz-sz/2,cz+sz/2
 a=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face([a[i] for i in ids],mi)
def prism(poly,z0,z1,mi):
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];face([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)],mi if i%5 else 1)
 face([(x,y,z1) for x,y in poly],mi);face([(x,y,z0) for x,y in reversed(poly)],mi)
def arch_east(x,yc,zbase,w,h,thick,depth,mi):
 # Door or window opening in the east-facing plane (outer normal +X).
 r=w/2; spring=zbase+h
 box(x,yc-r-thick/2,spring-h/2,depth,thick,h,mi);box(x,yc+r+thick/2,spring-h/2,depth,thick,h,mi)
 n=12
 for i in range(n):
  a0=math.pi*i/n;a1=math.pi*(i+1)/n
  o0=(yc+(r+thick)*math.cos(a0),spring+(r+thick)*math.sin(a0));o1=(yc+(r+thick)*math.cos(a1),spring+(r+thick)*math.sin(a1));i0=(yc+r*math.cos(a0),spring+r*math.sin(a0));i1=(yc+r*math.cos(a1),spring+r*math.sin(a1))
  front=[(x,o0[0],o0[1]),(x,o1[0],o1[1]),(x,i1[0],i1[1]),(x,i0[0],i0[1])];back=[(x+depth,y,z) for _,y,z in front]
  face(front,mi);face(list(reversed(back)),mi)
  for j in range(4):face([front[j],front[(j+1)%4],back[(j+1)%4],back[j]],mi)
def arch_glass_east(x,yc,zbase,w,h,mi=4):
 spring=zbase+h;r=w/2
 poly=[(x,yc-r,spring),(x,yc+r,spring)]
 for i in range(13):
  a=math.pi*i/12;poly.append((x,yc+r*math.cos(a),spring+r*math.sin(a)))
 face(poly,mi)
def window_east(x,y,z,w=1.75,h=1.65):
 box(x,y,z,w,.10,h,4)
 for yy in (y-w/2-.12,y+w/2+.12):box(x+.13,yy,z,.22,.16,h+.25,3)
 for zz in (z-h/2-.12,z+h/2+.12):box(x+.13,y,zz,w+.42,.16,.18,3)
 box(x+.2,y,z,.12,.12,h,3);box(x+.2,y,z,w,.12,.09,3)
def beam_yz(x,y1,z1,y2,z2,t,depth,mi):
 dy=y2-y1;dz=z2-z1;l=math.hypot(dy,dz);py=-dz/l*t/2;pz=dy/l*t/2
 a=[(y1+py,z1+pz),(y2+py,z2+pz),(y2-py,z2-pz),(y1-py,z1-pz)]
 front=[(x,y,z) for y,z in a];back=[(x+depth,y,z) for y,z in a]
 face(front,mi);face(list(reversed(back)),mi)
 for j in range(4):face([front[j],front[(j+1)%4],back[(j+1)%4],back[j]],mi)
# Exact official GIS footprint: one wall volume, project campus coordinate frame preserved.
prism(pts,0,.5,8);prism(pts,.5,4.15,0);prism(pts,4.15,4.36,3);prism(pts,4.36,8.15,0)
# Wing roof cap follows the same perimeter; its low silhouette is an estimate from a cropped photo.
face([(x,y,8.2) for x,y in pts],5)
# central raised entry block centered on the stepped east frontage from the GIS footprint.
front_x=maxx+.05;cy=(miny+maxy)/2;central_width=9.8
box(maxx+.32,cy,9.35,.65,central_width,2.7,1)
box(maxx+.32,cy,10.75,.82,central_width+.35,.25,5)
# main double entry and stone arch; photo shows central steps and raised entrance bay.
door_base=.72;door_w=2.25;door_h=2.45
box(front_x+.08,cy,door_base+door_h/2, .16,door_w,door_h,6)
arch_glass_east(front_x+.18,cy,door_base,door_w,door_h,6)
arch_east(front_x+.24,cy,door_base,door_w,door_h,.42,.30,2)
# upper arched window panel and stone surround in raised central bay.
win_base=8.35;win_h=.7;win_w=3.65
box(front_x+.78,cy,win_base+win_h/2,.12,win_w,win_h,4)
arch_glass_east(front_x+.83,cy,win_base,win_w,win_h,4)
arch_east(front_x+.94,cy,win_base,win_w,win_h,.38,.18,2)
# vertical stone pilasters at center bay margins.
for yy in (cy-central_width/2,cy+central_width/2):box(front_x+.70,yy,5.2,.52,.36,9.7,2)
# stylized Delta and Gamma sign above entry.
zsign=5.15;xsign=front_x+.72
beam_yz(xsign,cy-1.0,zsign-.35,cy,zsign+.45,.13,.15,7);beam_yz(xsign,cy,zsign+.45,cy+1.0,zsign-.35,.13,.15,7);beam_yz(xsign,cy-1.0,zsign-.35,cy+1.0,zsign-.35,.13,.15,7)
beam_yz(xsign,cy+1.25,zsign+.42,cy+2.15,zsign+.42,.14,.15,7);beam_yz(xsign,cy+1.30,zsign+.42,cy+1.30,zsign-.36,.14,.15,7)
# Broad entrance stair flight, five source-visible treads; projecting elements are decorative.
for i in range(5):
 box(front_x+.48+i*.62,cy,.16+i*.23,.70,7.4,.30,8)
# stone cheek walls/rails flank the stair run.
for yy in (cy-3.95,cy+3.95):
 box(front_x+1.5,yy,.68,.22,.28,1.25,2)
 box(front_x+1.75,yy,1.36,.30,.35,.16,2)
# East facade windows symmetrically frame central bay on both stories.
for y in (miny+2.2,miny+5.9,maxy-5.9,maxy-2.2):
 for z in (2.35,6.25):window_east(front_x+.07,y,z,1.65,1.55)
# Side elevations: schematic windows on the long north/south faces.
for y,sgn in ((miny+.05,-1),(maxy-.05,1)):
 for xw in (minx+4,minx+9,minx+14,minx+19):
  for z in (2.35,6.25):
   box(xw,y+sgn*.07,z,1.55,.12,1.55,4)
   for xx in (xw-.86,xw+.86):box(xx,y+sgn*.15,z,.16,.2,1.85,3)
   for zz in (z-.88,z+.88):box(xw,y+sgn*.15,zz,1.88,.2,.16,3)
mesh=bpy.data.meshes.new('Delta Gamma source-based facade mesh');mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new('House_301840872',mesh);asset.objects.link(obj)
for m in materials:mesh.materials.append(m)
for p,mi in zip(mesh.polygons,MI):p.material_index=mi
obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
obj['building_name']='Delta Gamma, Beta Iota Chapter';obj['source_fid']=783;obj['official_address']='303 Waldron St';obj['footprint_source']='Purdue BuildingShapesZip4 FID 783';obj['floor_count_status']='Two facade levels visible in 2014 exterior photo; GIS NUM_LEVELS=1 conflicts';obj['roof_status']='Low roofline estimated; photo crop does not show full roof';obj['front_bearing_status']='Illustrative east-facing central frontage; photo not georeferenced'
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));print('SAVED',OUT,'verts',len(mesh.vertices),'faces',len(mesh.polygons),'bounds',minx,maxx,miny,maxy)
