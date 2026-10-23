import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'modular/buildings/peirce_hall.blend'
AUD=ROOT/'audit/peirce_hall'
MASS=ROOT/'modular/buildings/massing_pierce_hall_prce_e5f59eb.blend'
GIS=ROOT/'audit/official_purdue_buildings_wgs84.json'
ORIGIN_LON=-86.9137
ORIGIN_LAT=40.4274
LON_M=84810.60416539927
LAT_M=111040.0
HEIGHT=11.7
BASE=0.0
FLOORS=[0.35,3.95,7.65,11.35]

# Reset to a clean standalone file.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
basecol=bpy.data.collections.get('Collection')
if basecol: bpy.data.collections.remove(basecol)
scene=bpy.data.scenes.get('Scene')
scene.name='Building_peirce_hall'
asset=bpy.data.collections.new('Asset_peirce_hall'); scene.collection.children.link(asset)
qa=bpy.data.collections.new('QA_Views'); scene.collection.children.link(qa)
root=bpy.data.objects.new('AssetRoot_peirce_hall',None); asset.objects.link(root)
root.empty_display_type='PLAIN_AXES'; root.empty_display_size=1.5

# Project official Purdue GIS ring to the campus local metre frame and recenter it.
gis=json.loads(GIS.read_text(encoding='utf-8'))
feat=next(f for f in gis['features'] if f['attributes'].get('BLDG_ABBR')=='PRCE')
ring=feat['geometry']['rings'][0]
world=[((p[0]-ORIGIN_LON)*LON_M,(p[1]-ORIGIN_LAT)*LAT_M) for p in ring]
xs=[p[0] for p in world]; ys=[p[1] for p in world]
anchor=((min(xs)+max(xs))/2,(min(ys)+max(ys))/2)
poly=[(x-anchor[0],y-anchor[1]) for x,y in world[:-1]]
# Drop small survey jogs under 1m while retaining the measured main corners.
def simplify(points,tol=0.18):
    pts=list(points)
    changed=True
    while changed and len(pts)>3:
        changed=False; out=[]
        for i,p in enumerate(pts):
            a=pts[i-1]; b=pts[(i+1)%len(pts)]
            v1=Vector((p[0]-a[0],p[1]-a[1])); v2=Vector((b[0]-p[0],b[1]-p[1]))
            if v1.length<tol or v2.length<tol or (v1.length and v2.length and abs(v1.normalized().cross(v2.normalized()))<0.025 and v1.dot(v2)>0):
                changed=True; continue
            out.append(p)
        if len(out)>=3: pts=out
        else: break
    return pts
poly=simplify(poly)

# Materials: real-world scale brick courses in wall UVs, limestone, dark metal, glazing, interior.
def mat(name,color,rough=0.8,metal=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    return m
brick=bpy.data.materials.new('Peirce | fired red brick and pale mortar'); brick.diffuse_color=(0.38,0.12,0.075,1); brick.use_nodes=True
nt=brick.node_tree; nodes=nt.nodes; links=nt.links
bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Roughness'].default_value=.86
tex=nodes.new('ShaderNodeTexBrick'); tex.name='True scale running bond'; tex.inputs['Color1'].default_value=(0.43,0.15,0.095,1); tex.inputs['Color2'].default_value=(0.31,0.085,0.055,1); tex.inputs['Mortar'].default_value=(0.63,0.56,0.46,1); tex.inputs['Scale'].default_value=1; tex.inputs['Mortar Size'].default_value=.013; tex.inputs['Mortar Smooth'].default_value=.02; tex.inputs['Brick Width'].default_value=.62; tex.inputs['Row Height'].default_value=.205
uv=nodes.new('ShaderNodeTexCoord'); links.new(uv.outputs['UV'],tex.inputs['Vector']); links.new(tex.outputs['Color'],bs.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.32; bump.inputs['Distance'].default_value=.026; links.new(tex.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal'])
stone=mat('Peirce | warm buff limestone and precast',(.56,.51,.42),.82)
roofmat=mat('Peirce | weathered pale gray roof membrane',(.35,.37,.36),.92)
# Add subtle roof noise.
nt=roofmat.node_tree; bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'); noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=3.5; noise.inputs['Detail'].default_value=2; ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.22; ramp.color_ramp.elements[0].color=(.24,.27,.27,1); ramp.color_ramp.elements[1].position=.76; ramp.color_ramp.elements[1].color=(.42,.44,.43,1); nt.links.new(noise.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
glass=mat('Peirce | smoked blue gray glazing',(.085,.19,.24),.22,.16)
metal=mat('Peirce | dark bronze window and door frames',(.10,.115,.12),.34,.68)
brick_infill=mat('Peirce | deep recessed brick panel',(.23,.075,.055),.92)
floor_mat=mat('Interior | warm gray linoleum',(.56,.52,.44),.82)
wall_mat=mat('Interior | painted warm off white',(.81,.78,.72),.9)
wood=mat('Interior | oak veneer',(.35,.19,.095),.56)
sofa=mat('Interior | lounge upholstery',(.23,.37,.35),.78)

# Link objects to asset and parent under local root to keep linked collection in the campus frame.
def register(o,collection=asset):
    collection.objects.link(o)
    if collection==asset and o!=root:
        o.parent=root
    return o

def mesh_obj(name,verts,faces,material,uvfaces=None,collection=asset):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.update()
    if material: me.materials.append(material)
    o=bpy.data.objects.new(name,me); register(o,collection)
    if uvfaces:
        layer=me.uv_layers.new(name='FacadeUV')
        for pi,coords in enumerate(uvfaces):
            for li,uvco in zip(me.polygons[pi].loop_indices,coords): layer.data[li].uv=uvco
    return o

def cube(name,loc,size,material,rot=0,collection=asset,bevel=0):
    hx,hy,hz=(v/2 for v in size)
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
           (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); register(o,collection)
    o.location=loc; o.rotation_euler[2]=rot
    if material:o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Soft arris','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def outline_face(name,points,z,material,collection=asset):
    verts=[(x,y,z) for x,y in points]
    # concave n-gons use Blender triangulation by face tessellation at render time
    return mesh_obj(name,verts,[list(range(len(verts)))],material,collection=collection)

def add_box_basis(name, center, tangent, normal, width, depth, height, material, collection=asset, bevel=0.0):
    ang=math.atan2(tangent[1],tangent[0])
    return cube(name,center,(width,depth,height),material,rot=ang,collection=collection,bevel=bevel)

# A closed structural brick prism with a correctly oriented UV shell. Base/roof heights are estimated,
# while the perimeter is traced from the official GIS ring.
N=len(poly)
shell_verts=[(x,y,.35) for x,y in poly]+[(x,y,11.35) for x,y in poly]
shell_faces=[list(range(N)),list(reversed(range(N,2*N)))]
shell_uv=[[(x,y) for x,y in poly],[(x,y) for x,y in reversed(poly)]]
for i,p in enumerate(poly):
    q=poly[(i+1)%len(poly)]; dx=q[0]-p[0]; dy=q[1]-p[1]; L=math.hypot(dx,dy)
    if L<0.25: continue
    u=(dx/L,dy/L); n=(-u[1],u[0])
    j=(i+1)%N
    # Side faces point out from a clockwise GIS perimeter. UV units correspond to metres.
    shell_faces.append([i,i+N,j+N,j])
    shell_uv.append([(0,.35),(0,11.35),(L,11.35),(L,.35)])
    # Buff-stone plinth band at grade, and simple upper parapet coping.
    cube(f'Peirce stone plinth {i+1:02d}',((p[0]+q[0])/2+n[0]*.08,(p[1]+q[1])/2+n[1]*.08,.31),(L+.05,.22,.62),stone,rot=math.atan2(u[1],u[0]),bevel=.025)
    cube(f'Peirce parapet coping {i+1:02d}',((p[0]+q[0])/2+n[0]*.11,(p[1]+q[1])/2+n[1]*.11,11.55),(L+.08,.30,.28),stone,rot=math.atan2(u[1],u[0]),bevel=.025)
shell_obj=mesh_obj('Peirce structural brick shell | closed GIS envelope',shell_verts,shell_faces,brick,uvfaces=shell_uv)

# Roof surface projected from measured official perimeter; flat roof confirmed by Google satellite.
roof=outline_face('Peirce flat roof plane | GIS perimeter',poly,11.36,roofmat)
# Roof slab edge / parapet ring as outer vertical wall already capped by separate coping.

# Direction-aware façade bays on every perimeter segment.
facade_cutouts=[]
def panel(center,u,n,w,h,z,depth=.10,name='window',frame=metal,opaque=False,recessed=False):
    x,y=center
    # Main pane or infill sits behind the face in a real cut opening on the photographed elevation.
    inset=-.25 if recessed else .13
    c=(x+n[0]*inset,y+n[1]*inset,z)
    add_box_basis(name+' infill',c,u,n,w-.20,depth,h,brick_infill if opaque else glass,bevel=.015)
    if recessed:
        facade_cutouts.append((name,center,u,n,w+.04,.72,h+.08,z))
    # Perimeter frame strips double as a shallow reveal where the opening is recessed.
    fmat=stone if opaque else metal
    bar=.11 if opaque else .075
    frame_depth=.30 if recessed else .17
    frame_offset=.08 if recessed else .20
    for side in (-1,1):
        cc=(x+u[0]*(side*(w/2-bar/2))+n[0]*frame_offset,y+u[1]*(side*(w/2-bar/2))+n[1]*frame_offset,z)
        add_box_basis(name+f' jamb {side}',cc,u,n,bar,frame_depth,h+.10,fmat,bevel=.018)
    for side in (-1,1):
        zz=z+side*(h/2-bar/2)
        cc=(x+n[0]*frame_offset,y+n[1]*frame_offset,zz)
        add_box_basis(name+f' head sill {side}',cc,u,n,w,frame_depth,bar,fmat,bevel=.018)
    # Subtle central vertical mullion and horizontal rail on window glazing.
    if not opaque:
        mullion_offset=inset+.12 if recessed else .24
        cc=(x+n[0]*mullion_offset,y+n[1]*mullion_offset,z)
        add_box_basis(name+' central mullion',cc,u,n,.055,.075,h-.18,metal)
        cc=(x+n[0]*mullion_offset,y+n[1]*mullion_offset,z)
        cube(name+' transom',(cc[0],cc[1],z),(w-.18,.075,.045),metal,rot=math.atan2(u[1],u[0]))
        # Windowsill projects shallowly outward.
        sill_offset=.08 if recessed else .27
        c2=(x+n[0]*sill_offset,y+n[1]*sill_offset,z-h/2-.13)
        add_box_basis(name+' projecting sill',c2,u,n,w+.16,.28,.12,stone,bevel=.02)

# Loop along each straight-ish GIS boundary segment. Facade is designed with shallow inlays,
# consistently anchored to the GIS polygon rather than any guessed site edge.
for i,p in enumerate(poly):
    q=poly[(i+1)%len(poly)]; dx=q[0]-p[0]; dy=q[1]-p[1]; L=math.hypot(dx,dy)
    if L<3.0: continue
    u=(dx/L,dy/L); n=(-u[1],u[0]); angle=math.atan2(u[1],u[0])
    # Upper and ground windows. Main north (long) elevation is grouped in a steady 4m rhythm.
    if L>28: pitch=4.0
    elif L>15: pitch=4.6
    elif L>9: pitch=3.8
    else: pitch=4.0
    count=max(1,int((L-2.2)/pitch)+1)
    # The official Purdue Events north/front photo shows six upper sash groups and six tall bays.
    if i==0 and L>28: count=6
    xs=[-L/2 + (j+1)*(L/(count+1)) for j in range(count)]
    for j,d in enumerate(xs):
        # Non-photo elevations keep the same restrained sash rhythm but use shallow masonry reveals;
        # this is a finish treatment, not a claim that an unverified window schedule was measured.
        side_recess=(i!=0 and L>12)
        # Ground-floor windows with warm stone perimeter and restrained metal muntins.
        if L>7:
            z=1.75
            w=min(1.75,max(1.2,L/(count+1)*.48)); h=1.62
            # Keep two openings near the public entrance free; these are replaced with doors below.
            c=( (p[0]+q[0])/2+u[0]*d, (p[1]+q[1])/2+u[1]*d)
            if not (i==0 and abs(d)<3.2):
                panel(c,u,n,w,h,z,name=f'Ground window edge{i+1} bay{j+1}',recessed=(i==0 or side_recess))
        # Upper story grouped paired sash opening (the photo documents this rhythm on north face).
        if L>7:
            z=9.45; w=min(1.8,max(1.28,L/(count+1)*.5)); h=1.52
            c=((p[0]+q[0])/2+u[0]*d,(p[1]+q[1])/2+u[1]*d)
            panel(c,u,n,w,h,z,name=f'Upper window edge{i+1} bay{j+1}',recessed=(i==0 or side_recess))
        # The main photographed façade carries tall recessed, brick infill bays at the middle level.
        if i==0 and L>28:
            z=5.65; w=min(1.38,L/(count+1)*.55); h=2.5
            c=((p[0]+q[0])/2+u[0]*d,(p[1]+q[1])/2+u[1]*d)
            panel(c,u,n,w,h,z,name=f'Middle recessed bay {j+1}',opaque=True,recessed=True)
            # Narrow, dark lower inset visible within each tall recessed bay in the photo.
            # Bring the narrow inset slightly forward of the dark brick infill so it remains legible in the recess.
            slot=(c[0]-n[0]*.13,c[1]-n[1]*.13,4.67)
            add_box_basis(f'Middle recessed bay {j+1} lower inset slot',slot,u,n,.72,.075,.17,glass,bevel=0)
        elif L>12:
            # Secondary elevations receive restrained sash openings; detail level is lower where imagery is unavailable.
            z=5.7; w=min(1.35,max(1.0,L/(count+1)*.43)); h=1.55
            c=((p[0]+q[0])/2+u[0]*d,(p[1]+q[1])/2+u[1]*d)
            panel(c,u,n,w,h,z,name=f'Middle window edge{i+1} bay{j+1}',recessed=side_recess)
    # Mid-level belt line and a very fine parapet brick course on all measured walls.
    center=((p[0]+q[0])/2+n[0]*.08,(p[1]+q[1])/2+n[1]*.08)
    cube(f'Peirce belt course {i+1:02d}',(center[0],center[1],3.96),(L,.18,.12),stone,rot=angle,bevel=.01)

# Public north-facing entrance is treated as observed from the official photo; a smaller side door is inferred.
# First boundary edge is along the north side and its outward normal points north.
p,q=poly[0],poly[1]; dx=q[0]-p[0]; dy=q[1]-p[1]; L=math.hypot(dx,dy); u=(dx/L,dy/L); n=(-u[1],u[0]); mid=((p[0]+q[0])/2,(p[1]+q[1])/2)
def door_on_edge(name,d,width=2.1,height=2.65):
    subordinate=(name=='North secondary entry')
    x=mid[0]+u[0]*d-n[0]*.05; y=mid[1]+u[1]*d-n[1]*.05
    facade_cutouts.append((name,(x,y),u,n,width+.06,.82,height+.05,height/2+.35))
    add_box_basis(name+' glazed doors',(x,y,height/2+.35),u,n,width,.20,height,glass,bevel=.015)
    # dark bronze frame and twin leaves
    for s in (-1,1):
        cc=(x+u[0]*(s*(width/2+.08)),y+u[1]*(s*(width/2+.08)),height/2+.35)
        add_box_basis(name+f' jamb {s}',cc,u,n,.16,.28,height+.25,metal,bevel=.025)
    if subordinate:
        # Secondary location is an inference: keep only a small stone head and plain single-width glazing.
        cube(name+' small inferred lintel',(x,y,height+.43),(width+.28,.20,.12),stone,rot=math.atan2(u[1],u[0]),bevel=.02)
    else:
        cube(name+' header',(x,y,height+.55),(width+.35,.32,.20),stone,rot=math.atan2(u[1],u[0]),bevel=.025)
        cube(name+' canopy',(x+n[0]*.60,y+n[1]*.60,height+.45),(width+1.0,1.05,.16),stone,rot=math.atan2(u[1],u[0]),bevel=.035)
        # canopy brackets
        for s in (-1,1):
            cc=(x+u[0]*s*(width/2+.24)+n[0]*.35,y+u[1]*s*(width/2+.24)+n[1]*.35,height+.05)
            add_box_basis(name+f' canopy bracket {s}',cc,u,n,.10,.12,.75,metal)
        # Hall identification belongs with the photo-supported principal entrance.
        cube(name+' name plaque',(x+u[0]*(width/2+.60)+n[0]*.20,y+u[1]*(width/2+.60)+n[1]*.20,height+.7),(.82,.07,.34),stone,rot=math.atan2(u[1],u[0]),bevel=.025)
        t=bpy.data.curves.new(name+' lettering','FONT'); t.body='PEIRCE HALL'; t.size=.14; t.extrude=.002
        ob=bpy.data.objects.new(name+' lettering',t); register(ob); ob.rotation_euler[2]=math.atan2(u[1],u[0]); ob.location=(x+u[0]*(width/2+.20)+n[0]*.27,y+u[1]*(width/2+.20)+n[1]*.27,height+.62); t.materials.append(metal)

door_on_edge('North public entry',-4.1)
door_on_edge('North secondary entry',3.0,1.18,2.2)
# Cut the photographed elevation's windows, recessed bays, and entry doors into the solid shell.
# A single multi-box cutter makes real shallow reveals; glazing and infill remain behind the face.
cutverts=[]; cutfaces=[]
for cutname,center,tu,no,width,depth,height,cz in facade_cutouts:
    cx,cy=center; base=len(cutverts)
    for zsgn in (-1,1):
        for usgn,nsgn in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            cutverts.append((cx+tu[0]*usgn*width/2+no[0]*nsgn*depth/2,
                             cy+tu[1]*usgn*width/2+no[1]*nsgn*depth/2,
                             cz+zsgn*height/2))
    cutfaces.extend([[base+0,base+3,base+2,base+1],[base+4,base+5,base+6,base+7],
                     [base+0,base+1,base+5,base+4],[base+1,base+2,base+6,base+5],
                     [base+2,base+3,base+7,base+6],[base+3,base+0,base+4,base+7]])
cutmesh=bpy.data.meshes.new('Temporary north façade aperture cutters'); cutmesh.from_pydata(cutverts,[],cutfaces); cutmesh.update()
cutob=bpy.data.objects.new('Temporary north façade apertures',cutmesh); scene.collection.objects.link(cutob)
mod=shell_obj.modifiers.new('North façade real window and door recesses','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutob
bpy.ops.object.select_all(action='DESELECT'); shell_obj.select_set(True); bpy.context.view_layer.objects.active=shell_obj
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutob,do_unlink=True); bpy.data.meshes.remove(cutmesh)
# Entry landing/steps aligned with north-side doorway.
for k in range(4):
    cube(f'North entry step {k+1}',(-4.1,14.0+k*.28,.13+k*.12),(3.0,1.0,.24+k*.12),stone,bevel=.025)

# Roof parapet glazing, expansion line, and only low roof equipment visible in the satellite view.
for j,(loc,size) in enumerate([((-14,7.2,11.62),(2.1,1.3,.55)),((-5,7.4,11.58),(1.7,1.25,.48)),((6,5.0,11.62),(2.3,1.4,.55)),((13,7,11.6),(1.5,1.1,.5))]):
    cube(f'Roof mechanical unit {j+1}',loc,size,roofmat,bevel=.06)
for j,loc in enumerate([((-10,9,11.9)),((2,8,11.9)),((15,9,11.9))]):
    cube(f'Roof vent curb {j+1}',loc,(.55,.55,.45),metal,bevel=.05)
    cube(f'Roof vent cap {j+1}',(loc[0],loc[1],12.15),(.85,.85,.13),stone,bevel=.04)

# Interior: three floor plates and representative circulation/teaching spaces; upper lounge mural has photo evidence.
# Layout partitioning is interpretive because a current dimensioned floor plan was not publicly verified.
def floor_plate(name,z):
    return outline_face(name,poly,z,floor_mat)
for fl,z in enumerate([.35,3.95,7.65],1):
    floor_plate(f'Interior floor {fl} | GIS footprint',z)
# Interior partition walls stay in the footprint, use a calm neutral material and consistent wall height.
def int_wall(name,a,b,z=0.35,h=3.0,th=.14,material=wall_mat):
    dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
    # Actual wall gaps align with the three door leaves placed below on every floor.
    gaps=[]
    if abs(dy)<.001 and abs(a[1]-6.1)<.02:
        lo,hi=sorted([a[0],b[0]]); gaps=[(-10-.55,-10+.55),(4-.55,4+.55)]
        cuts=[lo]+[v for gap in gaps for v in gap]+[hi]
        spans=[(cuts[0],cuts[1]),(cuts[2],cuts[3]),(cuts[4],cuts[5])]
        segments=[cube(name+f' segment {idx+1}',((x0+x1)/2,(a[1]+b[1])/2,z+h/2),(x1-x0,th,h),material,rot=math.atan2(dy,dx),collection=asset,bevel=.015) for idx,(x0,x1) in enumerate(spans) if x1>x0]
        for door_x in (-10,4):
            cube(name+f' doorway header {door_x}',(door_x,a[1],z+h-.12),(1.10,th,.24),material,collection=asset,bevel=.01)
        return segments
    if abs(dx)<.001 and abs(a[0]+2.1)<.02 and min(a[1],b[1])<-1<max(a[1],b[1]):
        lo,hi=sorted([a[1],b[1]])
        spans=[(lo,-1-.55),(-1+.55,hi)]
        segments=[cube(name+f' segment {idx+1}',(a[0],(y0+y1)/2,z+h/2),(y1-y0,th,h),material,rot=math.pi/2,collection=asset,bevel=.015) for idx,(y0,y1) in enumerate(spans) if y1>y0]
        cube(name+' doorway header', (a[0],-1,z+h-.12),(th,1.10,.24),material,collection=asset,bevel=.01)
        return segments
    return cube(name,((a[0]+b[0])/2,(a[1]+b[1])/2,z+h/2),(L,th,h),material,rot=math.atan2(dy,dx),collection=asset,bevel=.015)
# Ground floor partitions along corridor + broad rooms. These locations are explicitly not plan-surveyed.
for fl,z in enumerate([.35,3.95,7.65],1):
    # Main cross-corridor through north bar and down the west spine.
    int_wall(f'Interior {fl} north corridor south partition',(-18.6,6.1),(18.1,6.1),z,h=2.75)
    int_wall(f'Interior {fl} north corridor north partition',(-18.6,9.0),(18.1,9.0),z,h=2.75)
    int_wall(f'Interior {fl} west spine east partition',(-2.1,5.9),(-2.1,-11.9),z,h=2.75)
    int_wall(f'Interior {fl} west spine west partition',(-16.1,5.9),(-16.1,-11.9),z,h=2.75)
    # Room dividers on the north bar and west/south wing, preserving 1m doorway gaps.
    for xpos in [-14,-9,-4,1,6,11,16]:
        int_wall(f'Interior {fl} north room partition {xpos}',(xpos,3.0),(xpos,5.9),z,h=2.75)
    for ypos in [1.5,-3.0,-7.0,-10.8]:
        int_wall(f'Interior {fl} west room partition {ypos}',(-2.1,ypos),( -16.1,ypos),z,h=2.75)
    # A simple oak door leaf at selected doors with subtle dark hardware.
    for d,(x,y,rot) in enumerate([(-10,6.1,0),(4,6.1,0),(-2.1,-1,math.pi/2)],1):
        cube(f'Interior {fl} door leaf {d}',(x,y,z+1.05),(.86,.06,2.1),wood,rot=rot,bevel=.015)
    # Corridor benches, desks or work surfaces vary by floor but remain schematic.
    for n,(x,y) in enumerate([(-13,7.55),(-5,7.55),(4,7.55),(13,7.55)],1):
        cube(f'Interior {fl} corridor bench {n}',(x,y,z+.48),(1.5,.42,.90),wood,bevel=.04)
        cube(f'Interior {fl} bench cushion {n}',(x,y,z+.96),(1.52,.43,.09),sofa,bevel=.03)
# Stair cores at west and northeast ends: floor landings, treads and two guard rails.
for idx,(cx,cy) in enumerate([(-17.0,-2.5),(17.0,5.0)],1):
    for fl,z in enumerate([.45,4.05,7.75],1):
        cube(f'Interior stair {idx} landing floor {fl}',(cx,cy,z),(3.8,2.9,.16),floor_mat)
    # visual stair runs between floors, each tread is deliberately open enough to read from cutaway renders.
    for fl,z in enumerate([.55,4.15],1):
        for k in range(12):
            xx=cx-1.45+k*.25; zz=z+k*.25
            cube(f'Interior stair {idx} flight {fl} tread {k+1}',(xx,cy,zz),(.32,1.9,.13),stone)
        for side in [-1,1]:
            cube(f'Interior stair {idx} rail {fl} {side}',(cx,cy+side*1.05,z+1.55),(3.15,.06,.09),metal,rot=0)
# Add restrained, evidence-informed fit-out: desks/chairs suggest offices and labs documented
# for PSY/PRCE; a small teaching room is interpretive, based on the historical PRCE 277 listing.
# Exact room assignments and furniture positions are illustrative, not taken from a measured plan.
def desk_set(prefix,x,y,z,rot=0):
    cube(prefix+' worktop',(x,y,z+.78),(1.35,.68,.10),wood,rot=rot,bevel=.035)
    for sx in (-.56,.56):
        for sy in (-.25,.25): cube(prefix+f' leg {sx} {sy}',(x+sx,y+sy,z+.39),(.07,.07,.76),metal,rot=rot)
    # simple low monitor and keyboard
    cube(prefix+' monitor',(x,y+.22,z+1.12),(.48,.09,.30),metal,rot=rot,bevel=.025)
    cube(prefix+' monitor screen',(x,y+.16,z+1.13),(.40,.025,.22),glass,rot=rot)
def chair(prefix,x,y,z,rot=0):
    cube(prefix+' seat',(x,y,z+.48),(.48,.48,.12),sofa,rot=rot,bevel=.04)
    cube(prefix+' back',(x,y-.20,z+.78),(.48,.10,.55),sofa,rot=rot,bevel=.04)
    cube(prefix+' stem',(x,y,z+.24),(.09,.09,.40),metal)
    for ang in range(0,360,90):
        a=math.radians(ang); cube(prefix+f' base {ang}',(x+.26*math.cos(a),y+.26*math.sin(a),z+.08),(.32,.055,.06),metal,rot=a)
for fl,z in enumerate([.35,3.95,7.65],1):
    # paired office/lab work points in rooms on the north bar, outside the corridor.
    office_points=[(-12,4.15),(-7,4.15),(-2,4.15),(3,4.15)] + ([(8,4.15),(14,4.15)] if fl>1 else [])
    for j,(x,y) in enumerate(office_points,1):
        desk_set(f'Interior {fl} office workstation {j}',x,y,z)
        chair(f'Interior {fl} office chair {j}',x,y-.72,z)
    # Shared lab/meeting table and chairs in the broad south-central area.
    cube(f'Interior {fl} shared work table',(5,-1.2,z+.77),(3.0,1.0,.12),wood,bevel=.05)
    for j,x in enumerate([4,5.7,7.4],1):
        chair(f'Interior {fl} shared table chair {j}',x,-2.0,z)
    # Filing/storage units set against the west wing wall.
    for j,y in enumerate([-2.0,-5.0,-8.5],1):
        cube(f'Interior {fl} storage cabinet {j}',(-14.3,y,z+1.0),(1.25,.48,2.0),wood,bevel=.035)
# A compact interpretive classroom layout, grounded in documented classroom use in PRCE 277.
for row,y in enumerate([3.55,4.65,5.65],1):
    for col,x in enumerate([8.0,10.0,12.0,14.0],1):
        desk_set(f'Interpretive PRCE classroom row{row} seat{col}',x,y,.35)
        chair(f'Interpretive PRCE classroom chair r{row}s{col}',x,y-.70,.35)
cube('Interpretive classroom teaching board',(15.7,4.65,2.0),(.12,2.3,1.2),metal)

# Third-floor break lounge; published Purdue arts report confirms a two-piece mural in a third-floor break lounge.
# Include mural panels, seating cluster, lamps and small work table. Exact room extent is inferred.
for idx,px in enumerate([(6.2,-6.18),(10.0,-6.18)],1):
    cube(f'Third-floor mural panel {idx}',(px[0],px[1],9.45),(3.4,.12,1.8),brick_infill,bevel=.02)
# Stylized two-person portrait/flower compositions, abstract colored shapes rather than copied artwork.
for idx,cx in enumerate([5.3,9.1],1):
    cube(f'Third-floor mural portrait face {idx}',(cx,-6.32,9.7),(.50,.08,.62),stone,bevel=.16)
    cube(f'Third-floor mural flower core {idx}',(cx+1.0,-6.32,9.55),(.18,.08,.18),glass,bevel=.08)
    for k in range(5):
        ang=k*2*math.pi/5
        cube(f'Third-floor mural flower petal {idx}-{k}',(cx+1.0+.25*math.cos(ang),-6.32,9.55+.25*math.sin(ang)),(.18,.06,.18),sofa,bevel=.06)
for idx,(x,y) in enumerate([(6.2,-4.0),(10.0,-4.0)],1):
    cube(f'Third-floor lounge sofa {idx}',(x,y,8.2),(2.8,.85,.65),sofa,bevel=.14)
    cube(f'Third-floor lounge sofa back {idx}',(x,y+.25,8.75),(2.8,.35,.55),sofa,bevel=.12)
    for s in [-1,1]: cube(f'Third-floor sofa arm {idx}-{s}',(x+s*1.27,y,8.62),(.25,.95,.65),wood,bevel=.06)
cube('Third-floor break lounge table',(8.1,-2.0,8.45),(2.4,1.0,.12),wood,bevel=.06)
for x in [7.2,9.0]: cube(f'Third-floor table leg {x}',(x,-2,8.15),(.11,.11,.55),metal)
# Small planters mark common lounge edges.
for idx,(x,y) in enumerate([(4.4,-4.8),(12.4,-4.8)],1):
    cube(f'Third-floor lounge planter {idx}',(x,y,8.25),(.55,.55,.55),wood,bevel=.04)
    cube(f'Third-floor planter leaves {idx}',(x,y,8.82),(.44,.44,.75),sofa,bevel=.14)

# Keep speculative and verified interior elements separately selectable inside the asset.
interior=bpy.data.collections.new('Interior_Interpretive')
asset.children.link(interior)
for obj in list(asset.objects):
    if obj.name.startswith(('Interior ','Third-floor ')):
        asset.objects.unlink(obj)
        interior.objects.link(obj)
interior['status']='Schematic interior; dimensions and partition plan not verified from a current plan.'
interior['verified_feature']='Third-floor break lounge with two-piece mural reported March 21, 2022.'
interior['source']='https://www.basedinlafayette.com/p/a-new-purdue-mural-from-all-angles'

# Assign explicit asset metadata for downstream coordinator review.
asset['placement_origin_xy_m']=[round(anchor[0],6),round(anchor[1],6)]
asset['coordinate_frame']='local; master placement marker supplies XY origin'
asset['official_building_code']='PRCE'
asset['official_building_name']='Peirce Hall'
asset['gis_feature_id']=feat['attributes'].get('OBJECTID',feat['attributes'].get('FID'))
asset['plan_source']='Official Purdue GIS building footprint, local audit snapshot; origin-centred local metres'
asset['height_status']='Estimated; GIS field Extrution=21 and NUM_LEVELS=3 retained in evidence, exact interpretation of Extrution is not confirmed; 11.7m roof selected from three visible levels/photo proportions.'
asset['facade_status']='North/front facade follows Purdue Events photo: six upper sash groups, six tall recessed bays, and narrow lower inset slots. Long side/back window reveals are shallow, generalized inferences; the smaller north-side door is explicitly inferred and visually subordinate.'
asset['entry_status']='Principal north entry and canopy follow photo cues. Smaller nearby north-side door is an inferred secondary opening, reduced to narrow glazing and a small lintel with no canopy or plaque.'
asset['interior_status']='Schematic current-use interior. Third-floor break lounge is supported by March 2022 report; room dimensions/layout, corridor, stair positions and furniture are illustrative/inferred due no current measured plan found.'
asset['placement_origin_note']='Center of projected official PRCE footprint bounds in campus local XY; marker placement is world XY center, model geometry is local around this point.'
root['asset_id']='peirce_hall'; root['placement_origin_xy_m']=[round(anchor[0],6),round(anchor[1],6)]
root['root_is_local']='True; geometry is parented to zeroed AssetRoot'
scene['placement_origin_xy_m']=[round(anchor[0],6),round(anchor[1],6)]
scene['coordinate_frame']='local; master placement marker supplies XY origin'
scene['purpose']='Detailed standalone linked asset; master and manifest not edited.'

# QA camera and lighting in a separate collection (not exported with Asset_peirce_hall).
def point_at(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('QA North facade 3-4 view'); cam=bpy.data.objects.new('QA North facade 3-4 view',cam_data); qa.objects.link(cam); cam.location=(29,39,21); point_at(cam,(0,0,5.5)); cam_data.type='ORTHO'; cam_data.ortho_scale=58
scene.camera=cam
for idx,(loc,power,size) in enumerate([((10,20,33),5600,24),((-25,12,20),2800,18),((0,-25,23),2400,16)],1):
    d=bpy.data.lights.new(f'QA area {idx}','AREA'); d.energy=power; d.shape='DISK'; d.size=size; ob=bpy.data.objects.new(f'QA area {idx}',d); qa.objects.link(ob); ob.location=loc; point_at(ob,(0,0,5))
world=bpy.data.worlds.new('QA soft sky'); world.use_nodes=True; scene.world=world
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.36,.40,.44,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1440; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.filepath=str(AUD/'peirce_exterior.png')
try: scene.view_settings.view_transform='AgX'
except: pass
# Save one native project scene; audit renders will be produced in a second invocation by qa.py.
OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print(json.dumps({'status':'SAVED','path':str(OUT),'features':feat['attributes'],'ring_vertices':len(poly),'anchor_xy':anchor,'local_bounds':[[min(p[0] for p in poly),max(p[0] for p in poly)],[min(p[1] for p in poly),max(p[1] for p in poly)],[0,11.7]],'asset_objects':len(asset.all_objects),'direct_asset_objects':len(asset.objects),'interior_objects':len(interior.objects),'total_objects':len(scene.objects)}))
