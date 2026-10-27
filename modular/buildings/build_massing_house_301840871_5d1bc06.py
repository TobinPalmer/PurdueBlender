from __future__ import annotations
import json, math
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'kappa_kappa_gamma'
CONFIG=json.loads((AUDIT/'build_config.json').read_text(encoding='utf-8'))
FEATURE=json.loads((AUDIT/'sources'/'purdue_gis_fid782_raw.json').read_text(encoding='utf-8-sig'))['features'][0]
assert FEATURE['attributes']['FID']==782 and FEATURE['attributes']['BLDG_ABBR']=='SOKKG'
ASSET=ROOT/'modular'/'buildings'/(CONFIG['asset_id']+'.blend')
COL=bpy.data.collections.get(CONFIG['collection_name'])
OBJ=bpy.data.objects.get(CONFIG['object_name'])
if COL is None or OBJ is None or OBJ not in COL.objects[:]:
    raise RuntimeError('Assigned Kappa Kappa Gamma collection/object missing')
if len(COL.objects)!=1: raise RuntimeError('Expected exactly one assigned building object')

coords=FEATURE['geometry']['rings'][0]
if coords[0]==coords[-1]: coords=coords[:-1]
lat0,lon0=40.4274,-86.9137
pts=[Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0,0)) for lon,lat in coords]
area2=sum(pts[i].x*pts[(i+1)%len(pts)].y-pts[(i+1)%len(pts)].x*pts[i].y for i in range(len(pts)))
sign=1.0 if area2>0 else -1.0
cent=Vector((0,0))
for i,a in enumerate(pts):
    b=pts[(i+1)%len(pts)]; cross=a.x*b.y-b.x*a.y
    cent.x+=(a.x+b.x)*cross; cent.y+=(a.y+b.y)*cross
cent/=3.0*area2
edges=[]
for i,a in enumerate(pts):
    b=pts[(i+1)%len(pts)]; d=b-a; length=d.length
    tangent=Vector((d.x,d.y,0)).normalized()
    outward=Vector((tangent.y,-tangent.x,0))*sign
    edges.append((a,b,length,tangent,outward,i))
# The long west-facing boundary is used as an illustrative facade based on the historical long-view photograph; compass registration remains unverified.
front=max((e for e in edges if e[4].x< -0.25),key=lambda e:e[2])
fa,fb,front_len,front_tangent,front_n,front_index=front
up=Vector((0,0,1))
axis_u=up.cross(front_n).normalized()
if axis_u.dot(front_tangent)<0: axis_u.negate()
axis_v=front_n
proju=[(p-Vector((cent.x,cent.y,0))).dot(axis_u) for p in pts]
projv=[(p-Vector((cent.x,cent.y,0))).dot(axis_v) for p in pts]
hu=max(abs(v) for v in proju); hv=max(abs(v) for v in projv)

materials=[]
def mat(name,color,rough=0.8,metal=0.0):
    m=bpy.data.materials.get('KKG_'+name) or bpy.data.materials.new('KKG_'+name)
    m.diffuse_color=(*color,1.0); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs: bs.inputs['Base Color'].default_value=(*color,1.0); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    materials.append(m); return len(materials)-1
wall=mat('White_Rostone',CONFIG['wall_color'])
trim=mat('Warm_Stone_Trim',CONFIG['trim_color'])
roof=mat('Slate_Roof',CONFIG['roof_color'],0.92)
glass=mat('Dark_Window_Glass',CONFIG['glass_color'],0.24,0.03)
shutter=mat('Muted_Blue_Shutters',CONFIG['shutter_color'])
door=mat('Wood_Entry',CONFIG['door_color'])
stone=mat('Entry_Steps',CONFIG['trim_color'])
verts=[]; faces=[]; mids=[]
def face(points,mi):
    start=len(verts); verts.extend([tuple(p) for p in points]); faces.append(tuple(range(start,start+len(points)))); mids.append(mi)
def box(center,tangent,normal,width,depth,height,mi):
    c=Vector(center); t=Vector((tangent.x,tangent.y,0)).normalized(); n=Vector((normal.x,normal.y,0)).normalized(); z=up
    hw,hd,hh=width/2,depth/2,height/2
    offsets=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]
    local=[c+t*x+n*y+z*q for x,y,q in offsets]; idx=len(verts); verts.extend([tuple(p) for p in local])
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(idx+j for j in f)); mids.append(mi)

eaves=float(CONFIG['eaves_height_estimate_m']); ridge=float(CONFIG['ridge_height_estimate_m']); story=3.35; plinth=0.48
# Exact polygon-wall base; all map vertices retained at ground level.
for a,b,length,tangent,outward,_ in edges:
    a0,b0=a,b
    a1,b1=a+up*plinth,b+up*plinth
    atop,btop=a+up*eaves,b+up*eaves
    face((a0,b0,b1,a1),trim); face((a1,b1,btop,atop),wall)
    box((a.lerp(b,0.5)+up*(story-0.12)),tangent,outward,length,0.08,0.14,trim)
    box((a.lerp(b,0.5)+up*(2*story-0.12)),tangent,outward,length,0.08,0.14,trim)
    box((a.lerp(b,0.5)+up*(eaves-0.18)),tangent,outward,length+0.1,0.22,0.28,trim)
    # Repeat window bays around the principal walls. The photographed front gets shutters.
    if length < 7.0: continue
    count=max(1,int((length-2.2)//4.7))
    spacing=length/(count+1)
    for floor in range(2):
        z=plinth+story*(floor+0.53)
        for j in range(count):
            u=spacing*(j+1)/length
            point=a.lerp(b,u)
            if _==front_index and abs((point-fa.lerp(fb,0.5)).dot(tangent))<2.0: continue
            w=min(1.55,spacing*0.58); h=1.68
            c=point+outward*0.085+up*z
            box(c,tangent,outward,w,0.10,h,glass)
            box(c+outward*0.09+up*(h/2),tangent,outward,w+0.18,0.16,0.11,trim)
            box(c+outward*0.09-up*(h/2),tangent,outward,w+0.18,0.16,0.11,trim)
            box(c+outward*0.09+Vector((0,0,0)),tangent,outward,0.10,0.16,h,trim)
            # Small white center mullion is visible in the archival facade photo.
            box(c+outward*0.10,tangent,outward,0.045,0.17,h*0.92,trim)
            if _==front_index:
                for side in (-1,1):
                    box(c+tangent*(side*(w/2+0.22))+outward*0.10,tangent,outward,0.34,0.12,h*0.97,shutter)
# Raised front entry and shallow classical porch, matching the historical photograph's centered doorway.
entry=fa.lerp(fb,0.5)
box(entry+front_n*0.10+up*1.43,front_tangent,front_n,2.2,0.18,2.86,door)
for side in (-1,1):
    box(entry+front_tangent*(side*1.22)+front_n*0.22+up*2.05,front_tangent,front_n,0.18,0.26,4.1,trim)
box(entry+front_n*1.25+up*4.02,front_tangent,front_n,4.2,2.35,0.34,trim)
box(entry+front_n*1.20+up*3.80,front_tangent,front_n,4.45,2.55,0.12,stone)
for step in range(3):
    box(entry+front_n*(0.65+step*0.55)+up*(0.13+step*0.10),front_tangent,front_n,3.6+step*0.4,0.85,0.24,stone)
# Roof membrane follows the concave GIS outline; the principal steep roof is placed only over the largest solid rectangular wing.
for tri in tessellate_polygon([pts]):
    face([pts[int(i)]+up*eaves for i in tri],roof)
def inside_poly(x,y):
    inside=False
    for i,a in enumerate(pts):
        b=pts[(i+1)%len(pts)]
        if ((a.y>y)!=(b.y>y)) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x: inside=not inside
    return inside
xs=sorted({round(p.x,2) for p in pts})
rectangles=[]
for x0,x1 in zip(xs,xs[1:]):
    if x1-x0<0.15: continue
    xm=(x0+x1)*0.5; ys=[]
    for a,b in zip(pts,pts[1:]+pts[:1]):
        if (a.x<=xm<b.x) or (b.x<=xm<a.x): ys.append(a.y+(b.y-a.y)*(xm-a.x)/(b.x-a.x))
    ys.sort()
    for i in range(0,len(ys)-1,2):
        y0,y1=ys[i],ys[i+1]
        if y1-y0>1.0 and inside_poly(xm,(y0+y1)*0.5): rectangles.append((x0,x1,y0,y1))
if not rectangles: raise RuntimeError('Could not derive a principal roof wing from the GIS polygon')
rx0,rx1,ry0,ry1=max(rectangles,key=lambda r:(r[1]-r[0])*(r[3]-r[2]))
width=rx1-rx0; length=ry1-ry0; cx=(rx0+rx1)*0.5
# A long, steep hip roof with ridge aligned to the historical facade; dims are estimated.
hip= min(4.0,length*0.12); x0=rx0-0.15; x1=rx1+0.15; y0=ry0-0.15; y1=ry1+0.15; cr=(x0+x1)*0.5
left0=Vector((x0,y0,eaves)); left1=Vector((x0,y1,eaves)); right0=Vector((x1,y0,eaves)); right1=Vector((x1,y1,eaves))
ridge0=Vector((cr,y0+hip,ridge)); ridge1=Vector((cr,y1-hip,ridge))
face((left0,right0,ridge0),roof); face((right0,right1,ridge1,ridge0),roof); face((right1,left1,ridge1),roof); face((left1,left0,ridge0,ridge1),roof)
# Three small dormers project from the photographed long west slope. Heights and spacing are estimates.
front_axis=Vector((0,1,0)); west=Vector((-1,0,0))
for yy in (ry0+length*0.23,ry0+length*0.50,ry0+length*0.77):
    xx=rx0+width*0.31
    zz=eaves+(ridge-eaves)*(xx-rx0)/width+0.35
    c=Vector((xx,yy,zz+0.70))
    box(c,front_axis,west,2.0,1.15,1.45,wall)
    box(c+west*0.61,front_axis,west,0.92,0.10,0.96,glass)
    box(c+west*0.68+up*0.49,front_axis,west,1.10,0.12,0.10,trim)
    box(c+west*0.68-up*0.49,front_axis,west,1.10,0.12,0.10,trim)
    box(c+west*0.68,front_axis,west,0.10,0.12,0.94,trim)
    peak=c+up*1.52
    face((c-front_axis*1.04+up*0.70,peak,c+front_axis*1.04+up*0.70),roof)
    face((c-front_axis*1.04+up*0.70,c+west*0.70+up*0.70,peak),roof)
    face((peak,c+west*0.70+up*0.70,c+front_axis*1.04+up*0.70),roof)
# Merge mesh geometry into existing object while preserving ID, collection and identity transform.
mesh=bpy.data.meshes.new(CONFIG['object_name']+'_detailed')
mesh.from_pydata(verts,[],faces); mesh.materials.clear()
for m in materials: mesh.materials.append(m)
for poly,mi in zip(mesh.polygons,mids): poly.material_index=mi
mesh.update()
old=OBJ.data; OBJ.data=mesh
OBJ.location=(0,0,0); OBJ.rotation_euler=(0,0,0); OBJ.scale=(1,1,1)
if old.users==0: bpy.data.meshes.remove(old)
# Remove unused original-library image datablocks so the asset is self-contained.
for image in list(bpy.data.images):
    if image.users==0: bpy.data.images.remove(image)
# Remove stale unused placeholders from this library only.
for m in list(bpy.data.materials):
    if m.name.startswith('house_301840871_') and m.users==0: bpy.data.materials.remove(m)
# preserve linked object and save back to the assigned library file
bpy.context.view_layer.objects.active=OBJ; OBJ.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('BUILD_RESULT_JSON='+json.dumps({'asset_id':CONFIG['asset_id'],'source_fid':782,'ring_vertices':len(pts),'faces':len(mesh.polygons),'vertices':len(mesh.vertices),'modeled_main_floors':2,'eaves_estimate_m':eaves,'ridge_estimate_m':ridge,'front_edge_index':front_index,'collection_objects':len(COL.objects)},sort_keys=True))
