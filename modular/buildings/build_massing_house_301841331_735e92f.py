from __future__ import annotations
import json, math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'alpha_phi'
CFG=json.loads((AUDIT/'build_config.json').read_text(encoding='utf-8'))
FEATURE=json.loads((AUDIT/'sources'/'purdue_gis_fid764_raw.json').read_text(encoding='utf-8-sig'))['features'][0]
assert FEATURE['attributes']['FID']==764 and FEATURE['attributes']['BLDG_ABBR']=='SOAF'
ASSET=ROOT/'modular'/'buildings'/(CFG['asset_id']+'.blend')
COL=bpy.data.collections.get(CFG['collection_name']); OBJ=bpy.data.objects.get(CFG['object_name'])
if COL is None or OBJ is None or OBJ not in COL.objects[:]: raise RuntimeError('Assigned Alpha Phi collection/object missing')
if len(COL.objects)!=1: raise RuntimeError('Expected exactly one assigned building object')
ring=FEATURE['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
lat0,lon0=40.4274,-86.9137
pts=[Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0,0)) for lon,lat in ring]
area2=sum(pts[i].x*pts[(i+1)%len(pts)].y-pts[(i+1)%len(pts)].x*pts[i].y for i in range(len(pts)))
sign=1.0 if area2>0 else -1.0
edges=[]
for i,a in enumerate(pts):
 b=pts[(i+1)%len(pts)]; dv=b-a; length=dv.length; tang=Vector((dv.x,dv.y,0)).normalized(); norm=Vector((tang.y,-tang.x,0))*sign
 edges.append((a,b,length,tang,norm,i))
# Choose the longest mapped wall as the illustrative principal facade; orientation remains unverified.
front=max(edges,key=lambda e:e[2]); fa,fb,fl,ft,fn,fi=front
up=Vector((0,0,1)); center=Vector((sum(p.x for p in pts)/len(pts),sum(p.y for p in pts)/len(pts),0))
materials=[]
def material(name,color,rough=0.8,metal=0.0):
 m=bpy.data.materials.get('AP_'+name) or bpy.data.materials.new('AP_'+name)
 m.diffuse_color=(*color,1); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF')
 if bs: bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
 materials.append(m); return len(materials)-1
wall=material('Light_Masonry',CFG['wall_color']); trim=material('Horizontal_Stone_Bands',CFG['trim_color']); roof=material('Flat_Roof_Membrane',CFG['roof_color'],0.9); glass=material('Dark_Glazing',CFG['glass_color'],0.25); stone=material('Sign_Tower_Stone',CFG['stone_color']); door=material('Entry_Door',CFG['letter_color']); letters=material('Sign_Letters',CFG['letter_color'])
verts=[]; faces=[]; ids=[]
def face(points,mi):
 i=len(verts); verts.extend([tuple(p) for p in points]); faces.append(tuple(range(i,i+len(points)))); ids.append(mi)
def box(c,t,n,w,d,h,mi):
 c=Vector(c); t=Vector((t.x,t.y,0)).normalized(); n=Vector((n.x,n.y,0)).normalized(); hw,hd,hh=w/2,d/2,h/2
 offs=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]
 local=[c+t*x+n*y+up*z for x,y,z in offs]; idx=len(verts); verts.extend([tuple(p) for p in local])
 for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
  faces.append(tuple(idx+j for j in f)); ids.append(mi)
height=float(CFG['eaves_height_estimate_m']); floors=int(CFG['modeled_floors']); story=3.85; plinth=0.5
# Exact ground footprint walls, with horizontal massing bands.
for a,b,length,tangent,normal,idx in edges:
 a0,b0=a,b; a1,b1=a+up*plinth,b+up*plinth; topa,topb=a+up*height,b+up*height
 face((a0,b0,b1,a1),stone); face((a1,b1,topb,topa),wall)
 for floor in range(1,floors): box(a.lerp(b,0.5)+up*(plinth+story*floor),tangent,normal,length+0.02,0.12,0.28,trim)
 box(a.lerp(b,0.5)+up*(height-0.22),tangent,normal,length+0.18,0.26,0.30,trim)
 if length<5.0: continue
 count=max(1,int((length-2.8)//4.0)); spacing=length/(count+1)
 for floor in range(floors):
  z=plinth+story*(floor+0.48)
  for j in range(count):
   q=spacing*(j+1)/length; p=a.lerp(b,q)
   if idx==fi and abs((p-fa.lerp(fb,0.5)).dot(tangent))<2.4: continue
   w=min(1.45,spacing*0.55); h=2.0; c=p+normal*0.08+up*z
   box(c,tangent,normal,w,0.10,h,glass)
   box(c+normal*0.12+up*(h/2),tangent,normal,w+0.18,0.17,0.12,trim)
   box(c+normal*0.12-up*(h/2),tangent,normal,w+0.18,0.17,0.12,trim)
   box(c+normal*0.13,tangent,normal,0.08,0.17,h*0.90,trim)
# A flat cap follows the concave mapped footprint.
for tri in tessellate_polygon([pts]): face([pts[int(i)]+up*height for i in tri],roof)
# Centered entry, porch posts, canopy and stair flights.
entry=fa.lerp(fb,0.50)
box(entry+fn*0.11+up*1.65,ft,fn,2.25,0.15,3.30,door)
box(entry+fn*0.20+up*3.35,ft,fn,2.60,0.20,0.18,trim)
for side in (-1,1):
 for offset in (1.45,3.15): box(entry+ft*(side*offset)+fn*1.1+up*1.9,ft,fn,0.24,0.28,3.8,trim)
box(entry+fn*1.05+up*3.85,ft,fn,7.2,2.4,0.34,stone)
for step in range(3): box(entry+fn*(0.65+0.46*step)+up*(0.12+0.12*step),ft,fn,6.4+step*0.3,0.75,0.22,stone)
# Raised end sign wall shown in the exact-house artist drawing; its exact plan footprint is estimated.
tower_center=entry-ft*(fl*0.48)+fn*0.32+up*(height+2.0)
tower_w=min(9.2,fl*0.36); tower_h=float(CFG['sign_tower_height_estimate_m'])-height
box(tower_center,ft,fn,tower_w,1.15,tower_h,stone)
box(tower_center+fn*0.64+up*0.42,ft,fn,tower_w*0.82,0.08,tower_h*0.62,wall)
# Sign type is converted and joined into the assigned mesh so no extra collection object remains.
basis=Matrix((ft,up,fn)).transposed().to_4x4()
text_objects=[]
for name,body,size,zoff in (('Alpha_Phi_Greek_Sign','ΑΦ',min(2.6,tower_h*0.42),0.80),('Alpha_Phi_Name_Sign','Alpha Phi',min(1.0,tower_h*0.19),-0.72)):
 text_data=bpy.data.curves.new(name,'FONT'); text_data.body=body; text_data.size=size; text_data.extrude=0.012; text_data.align_x='CENTER'; text_data.align_y='CENTER'; text_data.materials.append(materials[letters])
 text_obj=bpy.data.objects.new(name,text_data); COL.objects.link(text_obj); text_obj.location=tower_center+fn*0.71+up*zoff; text_obj.rotation_euler=basis.to_euler(); text_obj.scale.x=-1.0; text_objects.append(text_obj)
mesh=bpy.data.meshes.new(CFG['object_name']+'_detailed'); mesh.from_pydata(verts,[],faces)
for m in materials: mesh.materials.append(m)
for poly,mi in zip(mesh.polygons,ids): poly.material_index=mi
mesh.update(); old=OBJ.data; OBJ.data=mesh; OBJ.location=(0,0,0); OBJ.rotation_euler=(0,0,0); OBJ.scale=(1,1,1)
if old.users==0: bpy.data.meshes.remove(old)
for text_obj in text_objects:
 bpy.ops.object.select_all(action='DESELECT'); text_obj.select_set(True); bpy.context.view_layer.objects.active=text_obj; bpy.ops.object.convert(target='MESH')
bpy.ops.object.select_all(action='DESELECT'); OBJ.select_set(True)
for text_obj in text_objects: text_obj.select_set(True)
bpy.context.view_layer.objects.active=OBJ; bpy.ops.object.join()

for image in list(bpy.data.images):
 if image.users==0: bpy.data.images.remove(image)
for m in list(bpy.data.materials):
 if m.users==0 and not m.name.startswith('AP_'): bpy.data.materials.remove(m)
OBJ.name=CFG['object_name']; OBJ.data.name=CFG['object_name']+'_detailed'
if len(COL.objects)!=1: raise RuntimeError('Expected only one object after text merge')
bpy.context.view_layer.objects.active=OBJ; OBJ.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('BUILD_RESULT_JSON='+json.dumps({'asset_id':CFG['asset_id'],'source_fid':764,'ring_vertices':len(pts),'faces':len(OBJ.data.polygons),'vertices':len(OBJ.data.vertices),'modeled_floors':floors,'eaves_estimate_m':height,'sign_tower_estimate_m':CFG['sign_tower_height_estimate_m'],'front_edge_index':fi,'collection_objects':len(COL.objects)},sort_keys=True))
