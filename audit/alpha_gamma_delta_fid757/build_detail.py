import bpy, json, math, os, sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
ASSET = ROOT / 'modular' / 'buildings' / 'massing_house_301841608_d56a4c4.blend'
GIS = AUDIT / 'purdue_gis_fid757_2026-10-27.json'
asset_id = 'massing_house_301841608_d56a4c4'
collection_name = 'Asset_' + asset_id
scene_name = 'Building_' + asset_id
object_name = 'House_301841608'

# Continue from the stable library so scene/collection/object identities remain unchanged.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.data.scenes[scene_name]
coll = bpy.data.collections[collection_name]
obj = bpy.data.objects[object_name]
assert len(coll.objects) == 1 and obj.type == 'MESH'

# Current official Purdue feature 757 polygon -> project's local campus approximation.
record = json.loads(GIS.read_text(encoding='utf-8-sig'))['features'][0]
assert record['attributes']['FID'] == 757 and record['attributes']['BUILDING_N'] == 'Alpha Gamma Delta'
origin_lat, origin_lon = 40.4274, -86.9137
def xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(origin_lat)), (lat-origin_lat)*111040.0)
ring = [xy(p[0],p[1]) for p in record['geometry']['rings'][0][:-1]]

# Clean near-collinear survey vertices but preserve every structural corner.
def dist_line(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=math.hypot(dx,dy)
    return math.hypot(p[0]-a[0],p[1]-a[1]) if den < 1e-9 else abs(dy*p[0]-dx*p[1]+b[0]*a[1]-b[1]*a[0])/den
def rdp(points, eps):
    if len(points) < 3: return points[:]
    a,b=points[0],points[-1]
    imax=max(range(1,len(points)-1),key=lambda i:dist_line(points[i],a,b))
    if dist_line(points[imax],a,b)>eps:
        return rdp(points[:imax+1],eps)[:-1]+rdp(points[imax:],eps)
    return [a,b]
def simplify_closed(pts, eps):
    # Split the ring at a farthest pair to avoid dropping the closing corner.
    ia=0; ib=max(range(1,len(pts)),key=lambda i:(pts[i][0]-pts[ia][0])**2+(pts[i][1]-pts[ia][1])**2)
    path1=pts[ia:ib+1]
    path2=pts[ib:]+pts[:ia+1]
    one=rdp(path1,eps); two=rdp(path2,eps)
    out=one[:-1]+two[:-1]
    # Remove duplicated near-neighbors and ensure CCW.
    clean=[]
    for p in out:
        if not clean or math.dist(p,clean[-1])>.05: clean.append(p)
    if len(clean)>2 and math.dist(clean[0],clean[-1])<.05: clean.pop()
    area=sum(clean[i][0]*clean[(i+1)%len(clean)][1]-clean[(i+1)%len(clean)][0]*clean[i][1] for i in range(len(clean)))/2
    if area < 0: clean.reverse()
    return clean
poly=simplify_closed(ring,1.2)
assert len(poly)>=8

# Single joined mesh builder; the asset stays one mesh object in the original collection.
verts=[]; faces=[]; face_mat=[]
MAT={}
def face(points, material):
    ids=[]
    for p in points:
        ids.append(len(verts)); verts.append(tuple(p))
    faces.append(tuple(ids)); face_mat.append(MAT[material])
def box_local(p0,p1,u0,u1,n0,n1,z0,z1,material):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; length=math.hypot(dx,dy)
    if length<1e-4 or u1-u0<1e-4 or z1-z0<1e-4 or n1-n0<1e-4:return
    ux,uy=dx/length,dy/length
    nx,ny=uy,-ux  # outward normal for CCW ring
    def pt(u,n,z): return (p0[0]+ux*u+nx*n,p0[1]+uy*u+ny*n,z)
    a,b,c,d=pt(u0,n0,z0),pt(u1,n0,z0),pt(u1,n0,z1),pt(u0,n0,z1)
    e,f,g,h=pt(u0,n1,z0),pt(u1,n1,z0),pt(u1,n1,z1),pt(u0,n1,z1)
    face((a,b,c,d),material); face((f,e,h,g),material)
    face((e,a,d,h),material); face((b,f,g,c),material)
    face((d,c,g,h),material); face((e,f,b,a),material)
def flat_poly(pts,z,material):
    coords=[Vector((p[0],p[1],0)) for p in pts]
    tris=tessellate_polygon([coords])
    for tri in tris:
        face([(coords[i].x,coords[i].y,z) for i in tri],material)
def prism_plan(pts,z0,z1,material):
    flat_poly(pts,z0,material); flat_poly(list(reversed(pts)),z1,material)
    for i,a in enumerate(pts):
        b=pts[(i+1)%len(pts)]
        # standalone rectangular vertical shell along each segment
        box_local(a,b,0,math.dist(a,b),-.13,.13,z0,z1,material)

def add_rect_xy(cx,cy,dx,dy,z0,z1,material,rot=0):
    c,s=math.cos(rot),math.sin(rot)
    pts=[]
    for x,y in [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,dy/2),(-dx/2,dy/2)]:
        pts.append((cx+x*c-y*s,cy+x*s+y*c))
    prism_plan(pts,z0,z1,material)
def add_rod(a,b,r,material,steps=8):
    a,b=Vector(a),Vector(b); axis=(b-a).normalized()
    ref=Vector((0,0,1)) if abs(axis.z)<.9 else Vector((0,1,0))
    u=axis.cross(ref).normalized(); v=axis.cross(u).normalized()
    ring1=[]; ring2=[]
    for i in range(steps):
        ang=2*math.pi*i/steps; off=(u*math.cos(ang)+v*math.sin(ang))*r
        ring1.append(a+off); ring2.append(b+off)
    for i in range(steps): face([ring1[i],ring1[(i+1)%steps],ring2[(i+1)%steps],ring2[i]],material)
    face(ring1,material);face(list(reversed(ring2)),material)
def window_edge(a,b,floor,lo,hi,walltop,door=False):
    length=math.dist(a,b)
    if length<2.6:
        box_local(a,b,0,length,-.14,.14,floor,walltop,'stucco'); return
    holes=[]
    if door:
        width=min(2.5,length*.38); center=length*.5
        holes=[(center-width/2,center+width/2,floor,min(floor+2.65,walltop-.15))]
    else:
        count=max(1,min(6,int(length//4.3)))
        width=min(1.45,length/(count+1)*.54)
        for k in range(count):
            center=(k+1)*length/(count+1)
            holes.append((center-width/2,center+width/2,lo,hi))
    xs=sorted(set([0.0,length]+[q for h in holes for q in h[:2]]))
    zs=sorted(set([floor,walltop]+[q for h in holes for q in h[2:]]))
    for ui in range(len(xs)-1):
        u0,u1=xs[ui],xs[ui+1]
        if u1-u0<.025: continue
        for zi in range(len(zs)-1):
            z0,z1=zs[zi],zs[zi+1]
            if z1-z0<.025: continue
            um,zm=(u0+u1)/2,(z0+z1)/2
            if any(h[0]<um<h[1] and h[2]<zm<h[3] for h in holes): continue
            box_local(a,b,u0,u1,-.14,.14,z0,z1,'stucco')
    for u0,u1,z0,z1 in holes:
        if door:
            # Solid red double-leaf door with small glazed transom, matching the chapter illustration.
            leaf_top=z1-.34; mid=(u0+u1)/2
            box_local(a,b,u0+.05,mid-.035,-.035,.04,z0+.08,leaf_top,'red')
            box_local(a,b,mid+.035,u1-.05,-.035,.04,z0+.08,leaf_top,'red')
            box_local(a,b,u0+.07,u1-.07,-.02,.035,leaf_top+.03,z1-.04,'glass')
            box_local(a,b,u0,u0+.08,-.11,.12,z0,z1,'trim')
            box_local(a,b,u1-.08,u1,-.11,.12,z0,z1,'trim')
            box_local(a,b,mid-.035,mid+.035,-.11,.12,z0,z1,'trim')
            for handle_u in (u0+(u1-u0)*.43,u0+(u1-u0)*.57):
                x=a[0]+(b[0]-a[0])*handle_u/length; y=a[1]+(b[1]-a[1])*handle_u/length
                add_rod((x,y,z0+.95),(x,y,z0+1.08),.025,'gold')
        else:
            # Dark glazing sits inside genuine wall openings; light stone/painted surrounds and mullions.
            box_local(a,b,u0+.08,u1-.08,-.025,.025,z0+.08,z1-.08,'glass')
            frame=.10
            box_local(a,b,u0-frame/2,u0+frame/2,-.12,.12,z0,z1,'trim')
            box_local(a,b,u1-frame/2,u1+frame/2,-.12,.12,z0,z1,'trim')
            box_local(a,b,u0-.04,u1+.04,-.12,.12,z0,z0+.13,'trim')
            box_local(a,b,u0-.04,u1+.04,-.12,.12,z1-.12,z1,'trim')
            box_local(a,b,u0+.05,u1-.05,-.08,.06,(z0+z1)/2-.035,(z0+z1)/2+.035,'trim')
            box_local(a,b,u0-.14,u1+.14,-.12,.12,z0-.03,z0+.03,'trim')

# Materials.
def make_mat(name,color,rough=.75,metal=0):
    m=bpy.data.materials.get('AGD_'+name) or bpy.data.materials.new('AGD_'+name)
    m.diffuse_color=(*color,1);m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    return m,bs
def texture_noise(mat,bs,scale,detail,bump):
    nt=mat.node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=detail;noise.inputs['Roughness'].default_value=.7;nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');base=bs.inputs['Base Color'].default_value[:];ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=tuple(v*.84 for v in base[:3])+(1,);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=tuple(min(1,v*1.13+.015) for v in base[:3])+(1,);nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=bump;nt.links.new(noise.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])

for key in ['stucco','trim','brick','roof','glass','wood','red','gold','floor','interior','rug','upholstery','leather','dark']:
    MAT[key]=len(MAT)
materials=[]
for key,color,rough,metal in [
    ('stucco',(.54,.44,.32),.88,0),('trim',(.84,.77,.65),.68,0),('brick',(.29,.075,.035),.9,0),('roof',(.035,.038,.045),.72,0),('glass',(.012,.045,.075),.2,.05),('wood',(.25,.12,.055),.48,0),('red',(.64,.025,.025),.38,0),('gold',(.65,.42,.11),.32,.55),('floor',(.29,.17,.09),.55,0),('interior',(.78,.74,.66),.8,0),('rug',(.46,.36,.27),.95,0),('upholstery',(.68,.64,.57),.82,0),('leather',(.36,.008,.02),.4,0),('dark',(.035,.04,.045),.5,0)]:
    m,bs=make_mat(key,color,rough,metal);materials.append(m)
    if key in ('stucco','brick','roof','wood','floor'):
        texture_noise(m,bs,40 if key in ('stucco','brick') else 20,3,.025 if key=='stucco' else .04)
    if key=='glass':
        bs.inputs['Alpha'].default_value=.72
        bs.inputs['Transmission Weight'].default_value=.18
        if hasattr(m,'surface_render_method'): m.surface_render_method='DITHERED'

# Main shell: two full levels based on the campus GIS footprint, with a taller central volume.
# The GIS record reports 40 ft (12.19 m) extrusion; 2-level wings and raised central block are inferred from the house illustration / capacity, not measured.
base=0.0; floor1=3.35; floor2=6.70; top=7.35
bounds=(min(p[0] for p in poly),max(p[0] for p in poly),min(p[1] for p in poly),max(p[1] for p in poly))
minx,maxx,miny,maxy=bounds
# Flat occupied floor planes and structural perimeter walls.
flat_poly(poly,.22,'floor'); flat_poly(poly,floor1,'floor'); flat_poly(poly,floor2,'floor')
# Mark one southwest front edge for double doors and the projecting entry; orientation is not georeferenced.
front_i=min(range(len(poly)),key=lambda i: ((poly[i][0]+poly[(i+1)%len(poly)][0])/2 - (minx+maxx)/2)**2 + ((poly[i][1]+poly[(i+1)%len(poly)][1])/2-miny)**2)
for i,a in enumerate(poly):
    b=poly[(i+1)%len(poly)]; length=math.dist(a,b)
    door=(i==front_i and length>3.4)
    for z0,z1 in [(0.22,floor1),(floor1,floor2)]:
        if door and z0==.22:
            window_edge(a,b,z0,z0,z0+2.25,z1,True)
        else:
            winlo=z0+.88;winhi=min(z0+2.35,z1-.42)
            window_edge(a,b,z0,winlo,winhi,z1,False)
    # brick plinth plus projecting pale horizontal floor bands
    box_local(a,b,0,length,-.24,.20,.22,.62,'brick')
    box_local(a,b,0,length,-.22,.20,floor1-.12,floor1+.05,'trim')
    box_local(a,b,0,length,-.22,.20,floor2-.12,floor2+.05,'trim')
    box_local(a,b,0,length,-.25,.20,top-.06,top+.12,'trim')
# parapet and flat roof on main wings, with softened stepped edge
flat_poly(poly,top,'roof')
for i,a in enumerate(poly):
    b=poly[(i+1)%len(poly)]; length=math.dist(a,b)
    box_local(a,b,0,length,-.32,.22,top,top+.48,'trim')
    box_local(a,b,0,length,-.28,.20,top+.48,top+.56,'roof')

# Tall three-storey sign tower/core located within the footprint; its exact position and volume are estimated.
# Use a conservative rectangle tested against the official ring.
def inside(pt):
    x,y=pt; hit=False
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]
        if ((a[1]>y)!=(b[1]>y)) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1]+1e-12)+a[0]:hit=not hit
    return hit
core=None
for dx,dy in [(18,11),(16,10),(14,9),(12,8)]:
    candidates=[]
    for cx in [minx+dx/2+k*.5 for k in range(int((maxx-minx-dx)/.5)+1)]:
        for cy in [miny+dy/2+k*.5 for k in range(int((maxy-miny-dy)/.5)+1)]:
            samples=[(cx+sx*dx/2,cy+sy*dy/2) for sx in (-.85,0,.85) for sy in (-.85,0,.85)]
            if all(inside(p) for p in samples):
                # favor upper-western quadrant per the address-side illustration's tall block composition
                candidates.append((cx,cy))
    if candidates:
        cx,cy=min(candidates,key=lambda p:(p[0]-(minx+maxx)/2+2)**2+(p[1]-(miny+maxy)/2-2)**2)
        core=(cx,cy,dx,dy);break
if core:
    cx,cy,dx,dy=core
    x0,x1=cx-dx/2,cx+dx/2;y0,y1=cy-dy/2,cy+dy/2
    # Raised central block with genuine punched upper windows; the illustrated third level is an estimate.
    corepoly=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    flat_poly(corepoly,top-.02,'floor')
    for i,a in enumerate(corepoly):
        b=corepoly[(i+1)%4];L=math.dist(a,b)
        window_edge(a,b,top-.02,top+.88,9.98,10.65,False)
        # vertical facade frame features like the source drawing
        for u in [L*.08,L*.92]:
            box_local(a,b,u-.16,u+.16,-.25,.18,top,10.65,'trim')
    # Low-pitch gable on the taller central block, directly supported by cream gable ends.
    rise=1.35; roof_y0=y0-.5; roof_y1=y1+.5; ridge_y=(y0+y1)/2
    face([(x0-.45,roof_y0,10.65),(x1+.45,roof_y0,10.65),(x1+.45,ridge_y,10.65+rise),(x0-.45,ridge_y,10.65+rise)],'roof')
    face([(x0-.45,ridge_y,10.65+rise),(x1+.45,ridge_y,10.65+rise),(x1+.45,roof_y1,10.65),(x0-.45,roof_y1,10.65)],'roof')
    face([(x0,y0,10.65),(x0,y1,10.65),(x0,ridge_y,10.65+rise)],'stucco')
    face([(x1,y1,10.65),(x1,y0,10.65),(x1,ridge_y,10.65+rise)],'stucco')
    # Eave fascia and ridge cap articulate the roof silhouette.
    add_rect_xy(cx,cy,dx+1.0,dy+1.0,10.56,10.70,'trim')
    add_rect_xy(cx,cy,dx+.35,.32,10.65+rise-.05,10.65+rise+.08,'roof')
    # The source elevation drawing shows a circular upper-story window above the
    # chapter mark. Its front elevation is not georeferenced, so put this
    # illustration-informed feature on the south-facing core wall without
    # claiming a measured diameter.
    circle_y=y0-.205; circle_z=9.72; circle_r=1.02; circle_n=32
    disk=[(cx+circle_r*math.cos(i*2*math.pi/circle_n),circle_y,circle_z+circle_r*math.sin(i*2*math.pi/circle_n)) for i in range(circle_n)]
    for i in range(circle_n):
        face([(cx,circle_y-.005,circle_z),disk[i],disk[(i+1)%circle_n]],'glass')
    for r0,r1,mat_key in [(1.03,1.16,'trim'),(1.16,1.21,'roof')]:
        for i in range(circle_n):
            a0=i*2*math.pi/circle_n;a1=(i+1)*2*math.pi/circle_n
            face([(cx+r0*math.cos(a0),circle_y-.025,circle_z+r0*math.sin(a0)),(cx+r1*math.cos(a0),circle_y-.025,circle_z+r1*math.sin(a0)),(cx+r1*math.cos(a1),circle_y-.025,circle_z+r1*math.sin(a1)),(cx+r0*math.cos(a1),circle_y-.025,circle_z+r0*math.sin(a1))],mat_key)
    # Alpha Gamma Delta plaque on the same elevation below the circular window.
    # This feature is supported by the building illustration; exact facade
    # alignment is unknown.
    bpy.ops.object.text_add(location=(cx,cy-dy/2-.20,8.05))
    text_obj=bpy.context.object;text_obj.name='AGD_sign_tmp';text_obj.data.body='ΑΓΔ';text_obj.data.align_x='CENTER';text_obj.data.align_y='CENTER';text_obj.data.size=1.25;text_obj.data.extrude=.02
    text_obj.rotation_euler=(math.radians(90),0,0)
    # material assign then convert to mesh, collect later
    # High-contrast metal/plaque lettering keeps the chapter identifier legible on the light facade.
    text_obj.data.materials.append(materials[12]);bpy.ops.object.convert(target='MESH')
else:
    core=(minx+maxx/2,miny+maxy/2,12,8)

    

# Portico with paired red entry leaves, pale columns, canopy and broad approach steps.
a=poly[front_i];b=poly[(front_i+1)%len(poly)];L=math.dist(a,b);ux=(b[0]-a[0])/L;uy=(b[1]-a[1])/L; nx=uy;ny=-ux
cx=(a[0]+b[0])/2;cy=(a[1]+b[1])/2
# offset front side, overhang toward outward face
portico_center=(cx+nx*1.65,cy+ny*1.65)
add_rect_xy(portico_center[0],portico_center[1],5.2,3.7,.22,.52,'brick',math.atan2(uy,ux))
# steps, each lower and wider than the landing
for i in range(3):
    ww=4.8+i*.55; dep=.44; z0=.22-i*.12; z1=.52-i*.12
    px=portico_center[0]+nx*(1.7+i*.48);py=portico_center[1]+ny*(1.7+i*.48)
    add_rect_xy(px,py,ww,dep,z0,z1,'trim',math.atan2(uy,ux))
# columns as stone shafts and capitals
for side in [-1,1]:
    for along in [-1.85,1.85]:
        px=cx+ux*along+nx*1.8;py=cy+uy*along+ny*1.8
        add_rect_xy(px,py,.48,.48,.45,3.0,'trim',math.atan2(uy,ux))
        add_rect_xy(px,py,.72,.72,2.96,3.22,'trim',math.atan2(uy,ux))
# broad canopy and pitched low pyramidal-looking portico lid
add_rect_xy(portico_center[0],portico_center[1],6.2,4.7,3.22,3.48,'trim',math.atan2(uy,ux))
# A low hipped entrance roof echoes the small peaked portico in the illustration.
# Its dimensions and orientation are interpretive because the illustration is not georeferenced.
hw,hd,eave,ridge=2.95,2.2,3.48,4.18
def port_pt(along,depth,z):
    return (portico_center[0]+ux*along+nx*depth,portico_center[1]+uy*along+ny*depth,z)
c1=port_pt(-hw,-hd,eave);c2=port_pt(hw,-hd,eave);c3=port_pt(hw,hd,eave);c4=port_pt(-hw,hd,eave)
r1=port_pt(-.72,0,ridge);r2=port_pt(.72,0,ridge)
face((c1,c2,r2,r1),'roof');face((c2,c3,r2),'roof');face((c3,c4,r1,r2),'roof');face((c4,c1,r1),'roof')
# Red wall panels/doors on both leaves behind columns at entrance floor.
for sign in (-1,1):
    wx=cx+ux*sign*.47+nx*.02;wy=cy+uy*sign*.47+ny*.02
    add_rect_xy(wx,wy,.78,.16,.24,2.5,'red',math.atan2(uy,ux))
# If sign differs from actual core facade, retain the entry marker as a low-key architectural cue.

# Interior schematic: open social/dining area, small room divisions, circulation core, actual photo-informed furnishings.
# Room partitions are intentionally schematic: official plans are not available; curated photos document finishes and room functions.
mx=(minx+maxx)/2;my=(miny+maxy)/2
# partitions within polygon bounds, laid out as 4 zones
for x in [mx-7.5,mx+6.5]:
    add_rect_xy(x,my,0.15,14,.22,3.1,'interior')
for y in [my-5.5,my+5.5]:
    add_rect_xy(mx-1.0,y,13,.15,.22,3.1,'interior')
# floor two partitions on core-adjacent west and east sections
for x in [mx-6,mx+6]: add_rect_xy(x,my+1,0.13,12,3.36,6.5,'interior')
# stair flights: two landings and repeated treads at center-west
stairx=mx-2.7;stairy=my-1.2
for i in range(13):
    z=.28+i*.20
    add_rect_xy(stairx,stairy+i*.34,2.4,.29,z,z+.14,'wood')
# handrails
add_rod((stairx-1.05,stairy-.3,.55),(stairx-1.05,stairy+4.2,3.05),.045,'trim')
add_rod((stairx+1.05,stairy-.3,.55),(stairx+1.05,stairy+4.2,3.05),.045,'trim')
# Lower-level TV lounge centered in west room: rug, sofa and two chairs, tables.
add_rect_xy(mx-7.0,my-6.4,7.4,4.7,.24,.29,'rug')
def couch(cx,cy,rot=0,color='leather'):
    add_rect_xy(cx,cy,2.65,.92,.31,.72,color,rot)
    add_rect_xy(cx,cy+.38,2.65,.22,.66,1.42,color,rot)
    for side in [-1,1]: add_rect_xy(cx+side*1.22,cy,.22,.95,.35,1.02,color,rot)
    for k in [-.75,0,.75]: add_rect_xy(cx+k,cy+.18,.48,.13,.74,1.1,'trim',rot)
couch(mx-7.0,my-7.65,0)
couch(mx-8.75,my-5.7,math.radians(90))
add_rect_xy(mx-5.55,my-5.6,1.45,1.2,.31,.75,'wood')
# low coffee tabletop plus legs
add_rect_xy(mx-5.55,my-5.6,1.75,1.45,.72,.82,'wood')
# Dining hall: four long communal tables with chair blocks.
for row in range(2):
    ty=my+6.8+row*3.25
    for col in range(2):
        tx=mx+7.4+col*3.8
        add_rect_xy(tx,ty,3.0,1.05,.3,.38,'wood')
        for seat in [-1,1]:
            for side in [-1,1]: add_rect_xy(tx+side*1.05,ty+seat*.78,.46,.43,.29,.82,'wood')
# Study/conversation nook in northeast zone: round table approximated by faceted mesh and chairs.
def cylinder(cx,cy,r,z0,z1,material,n=16):
    pts=[(cx+r*math.cos(i*2*math.pi/n),cy+r*math.sin(i*2*math.pi/n)) for i in range(n)]
    prism_plan(pts,z0,z1,material)
cylinder(mx+8,my-2.3,.62,.30,.82,'wood',20)
for i in range(4):
    ang=i*math.pi/2;qx=mx+8+1.15*math.cos(ang);qy=my-2.3+1.15*math.sin(ang)
    add_rect_xy(qx,qy,.58,.56,.3,.83,'upholstery',ang)
# Lounge study tables second story
for x in [mx-7,mx+7]:
    add_rect_xy(x,my+1,2.2,1.0,3.42,3.52,'wood')
    for side in [-1,1]: add_rect_xy(x+side*1.35,my+1,.4,.4,3.4,4.05,'upholstery')
# A few interior pendant fixtures along dining hall, each as rod and warm small globe.
for x in [mx+5,mx+11]:
    for y in [my+5.5,my+9.3]:
        add_rod((x,y,6.35),(x,y,6.78),.025,'gold')
        cylinder(x,y,.13,6.18,6.38,'gold',12)

# compile geometry and preserve single exported mesh object
mesh=bpy.data.meshes.new('Alpha_Gamma_Delta_Detailed_GIS_Shell')
mesh.from_pydata(verts,[],faces);mesh.update()
for m in materials: mesh.materials.append(m)
for p,mi in zip(mesh.polygons,face_mat): p.material_index=mi
# Correct normals for closed details.
import bmesh
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free();mesh.update()
old=obj.data;obj.data=mesh;obj.name=object_name
if old.users==0:bpy.data.meshes.remove(old)
# Bring converted Greek sign into the building mesh, then remove the helper object.
text_obj=bpy.data.objects.get('AGD_sign_tmp')
if text_obj:
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);text_obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.join()
    obj.name=object_name
# New UVs: physical meters across facades for readable procedural materials.
uv=obj.data.uv_layers.get('FacadeUV') or obj.data.uv_layers.new(name='FacadeUV')
for p in obj.data.polygons:
    n=p.normal.normalized()
    u=Vector((-n.y,n.x,0)).normalized() if abs(n.z)<.8 else Vector((1,0,0))
    v=Vector((0,0,1)) if abs(n.z)<.8 else Vector((0,1,0))
    for li in p.loop_indices:
        co=obj.matrix_world @ obj.data.vertices[obj.data.loops[li].vertex_index].co
        uv.data[li].uv=(co.dot(u),co.dot(v))
# UV mapped brick veneer/plinth and roof are pattern-based procedural surface nodes.
# Portable one-file library has no image dependencies.
obj['building_name']='Alpha Gamma Delta (Beta Xi)'
obj['source_feature_id']=757
obj['source_address']='1010 David Ross Rd, West Lafayette, IN'
obj['source_outline']='Purdue BuildingShapesZip4 FID 757; WGS84 converted with project local approximation'
obj['height_evidence']='40 ft GIS extrusion attribute; articulated 2-level wings plus raised core inferred from source illustration; not a surveyed roof height'
obj['interior']='Schematic common, dining, lounge and study zones; furnishings informed by Purdue AGD housing and PDR Interiors property-specific photos'
obj['uncertainty']='Entrances, facade orientation, roof form, raised core and internal partition layout are not survey/as-built verified'
obj['source_ring_vertices']=len(ring)
obj['wall_polygon_vertices']=len(poly)
obj['core_bounds_estimated']=list(core) if core else None
# Make sure all materials are retained and relative library paths stable.
# This is a single self-contained library mesh. Merge exact duplicate vertices
# generated by the face helper so adjacent surfaces are connected in the saved
# mesh rather than merely overlapping in the viewport.
bm=bmesh.new();bm.from_mesh(obj.data)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0001)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(obj.data);bm.free();obj.data.update()
# The original massing file carried unused external reference textures. This
# detailed asset uses procedural materials, so discard unused image datablocks
# and leave no fragile absolute or missing file dependencies.
for image in list(bpy.data.images):
    if image.users == 0:
        bpy.data.images.remove(image)
bpy.context.view_layer.objects.active=obj
bpy.ops.wm.save_as_mainfile(filepath=str(AUDIT/'candidate_alpha_gamma_delta.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('AGD_BUILD_REPORT='+json.dumps({'asset':asset_id,'object':obj.name,'collection_objects':len(coll.objects),'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'source_ring_vertices':len(ring),'wall_outline_vertices':len(poly),'bounds':[(min(v[i] for v in (obj.matrix_world@Vector(c) for c in obj.bound_box)),max(v[i] for v in (obj.matrix_world@Vector(c) for c in obj.bound_box))) for i in range(3)],'core':core,'source_attributes':record['attributes']}))
