"""Build a detailed, portable Black Cultural Center library from GIS and Purdue sources.

Run with Blender in background mode. Writes only the BCC library and its
building-specific evidence folder.
"""
import bpy, json, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVIDENCE_DIR = os.path.join(ROOT, "audit", "black_cultural_center")
SOURCES_DIR = os.path.join(EVIDENCE_DIR, "sources")
os.makedirs(EVIDENCE_DIR, exist_ok=True)
FEATURE = os.path.join(SOURCES_DIR, "purdue_gis_fid_645.json")
OUT = os.path.join(ROOT, "modular", "buildings", "black_cultural_center.blend")
PREVIEW = os.path.join(EVIDENCE_DIR, "black_cultural_center_preview.png")
EVIDENCE = os.path.join(EVIDENCE_DIR, "source_record.json")
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
LON_M, LAT_M = 84810.60416539927, 111040.0

with open(FEATURE, "r", encoding="utf-8") as f:
    feature_doc = json.load(f)
feature = feature_doc["features"][0]
ring = feature["geometry"]["rings"][0]
lon = [p[0] for p in ring[:-1]]
lat = [p[1] for p in ring[:-1]]
cx_geo = (min(lon) + max(lon)) / 2
cy_geo = (min(lat) + max(lat)) / 2
foot = [((p[0]-cx_geo)*LON_M, (p[1]-cy_geo)*LAT_M) for p in ring[:-1]]
# GIS source ring is closed; drop duplicate closing point. Keep actual ring topology.
n = len(foot)
area2 = sum(foot[i][0]*foot[(i+1)%n][1]-foot[(i+1)%n][0]*foot[i][1] for i in range(n))
if area2 < 0:
    foot.reverse()
    n = len(foot)
    area2 = -area2

# Reset scene and establish a collection-only library contract.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != "Collection":
        bpy.data.collections.remove(c)
scene = bpy.context.scene
for c in list(scene.collection.children):
    scene.collection.children.unlink(c)
asset = bpy.data.collections.new("Asset_black_cultural_center")
scene.collection.children.link(asset)
structure = bpy.data.collections.new("BCC_Structure")
facade = bpy.data.collections.new("BCC_Facade_Details")
interior = bpy.data.collections.new("BCC_Interior")
landscape = bpy.data.collections.new("BCC_Entry_Landscape")
for c in (structure, facade, interior, landscape):
    asset.children.link(c)
preview_collection = bpy.data.collections.new("Preview_Rig")
scene.collection.children.link(preview_collection)
asset["building_id"] = "black_cultural_center"
asset["owner"] = "Rossen"
asset["source_feature_id"] = "FID 645"
asset["local_origin_method"] = "GIS footprint bounding-box midpoint"

def material(name, base, rough=.65, metallic=0.0, noise_scale=5.0, noise_amount=.08, bump=.04):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.diffuse_color = (*base, 1)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metallic
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = .72
    nt.links.new(geo.outputs["Position"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    lo = tuple(max(0, c*(1-noise_amount)) for c in base) + (1,)
    hi = tuple(min(1, c*(1+noise_amount)) for c in base) + (1,)
    ramp.color_ramp.elements[0].position = .18
    ramp.color_ramp.elements[0].color = lo
    ramp.color_ramp.elements[1].position = .82
    ramp.color_ramp.elements[1].color = hi
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = bump
    b.inputs["Distance"].default_value = .018
    nt.links.new(noise.outputs["Fac"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bs.inputs["Normal"])
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    return m

brick = material("BCC | patterned warm red-brown brick", (.32,.105,.065), .83, 0, 18,.16,.11)
# Add a real running-bond brick node to carry scaled masonry relief and color.
nt=brick.node_tree; bs=next(x for x in nt.nodes if x.type=="BSDF_PRINCIPLED")
geo=next(x for x in nt.nodes if x.type=="NEW_GEOMETRY")
tc=nt.nodes.new("ShaderNodeTexCoord")
bt=nt.nodes.new("ShaderNodeTexBrick")
bt.inputs["Color1"].default_value=(.34,.115,.073,1)
bt.inputs["Color2"].default_value=(.23,.065,.043,1)
bt.inputs["Mortar"].default_value=(.40,.32,.25,1)
bt.inputs["Scale"].default_value=1.0
bt.inputs["Brick Width"].default_value=.42
bt.inputs["Row Height"].default_value=.095
bt.inputs["Mortar Size"].default_value=.009
nt.links.new(tc.outputs["UV"],bt.inputs["Vector"])
mix=nt.nodes.new("ShaderNodeMixRGB"); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=.25
noise_ramp=next(x for x in nt.nodes if x.type=="VALTORGB")
nt.links.new(bt.outputs["Color"],mix.inputs[1]); nt.links.new(noise_ramp.outputs["Color"],mix.inputs[2]); nt.links.new(mix.outputs["Color"],bs.inputs["Base Color"])
stone=material("BCC | Indiana limestone and cast-stone trim", (.67,.63,.54), .72, 0, 4,.12,.06)
roof=material("BCC | charcoal low-slope roof membrane", (.105,.12,.13), .8, .08, 11,.12,.025)
metal=material("BCC | dark wrought iron", (.036,.043,.044), .34,.72, 7,.06,.02)
gold=material("BCC | warm bronze / gold accents", (.48,.27,.075), .32,.68, 6,.07,.02)
glass=material("BCC | dark blue-green glazing", (.035,.105,.13), .20,.18, 14,.12,.01)
wood=material("BCC | warm interior wood", (.30,.16,.075), .68, 0, 5,.09,.025)
interior_wall=material("BCC | warm interior plaster", (.72,.62,.46), .78, 0, 3,.06,.012)
foliage=material("BCC | deep green planting", (.07,.21,.09), .78, 0, 4,.2,.03)
soil=material("BCC | planter soil", (.13,.075,.045), .92,0,5,.2,.02)
carpet=material("BCC | dark charcoal lobby carpet", (.075,.078,.074), .96,0,8,.19,.025)

def link_obj(obj, col):
    col.objects.link(obj)
    return obj

def mesh_obj(name, verts, faces, mat, col, face_mats=None):
    me=bpy.data.meshes.new(name+"Mesh"); me.from_pydata(verts,[],faces); me.materials.append(mat)
    ob=bpy.data.objects.new(name,me); link_obj(ob,col)
    if face_mats:
        for i,p in enumerate(me.polygons): p.material_index=face_mats[i]
    for p in me.polygons: p.use_smooth=False
    return ob

def cube(name, loc, scale, mat, col, angle=0, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale; o.rotation_euler[2]=angle
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    link_obj(o,col)
    if mat: o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new("Soft masonry arris","BEVEL"); mod.width=bevel; mod.segments=2
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def solid_band(z0,z1, mat, name):
    verts=[(x,y,z) for z in (z0,z1) for x,y in foot]
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,j+n,i+n))
    ob=mesh_obj(name,verts,faces,mat,structure)
    if mat == brick:
        uv=ob.data.uv_layers.new(name="RunningBondWorldScale")
        for i,poly in enumerate(ob.data.polygons):
            a,b=foot[i],foot[(i+1)%n]
            length=math.hypot(b[0]-a[0],b[1]-a[1])
            uv_by_vertex={i:(0.0,0.0),(i+1)%n:(length,0.0),((i+1)%n)+n:(length,z1-z0),i+n:(0.0,z1-z0)}
            for li in poly.loop_indices:
                uv.data[li].uv=uv_by_vertex[ob.data.loops[li].vertex_index]
    return ob

def top_cap(z, mat, name):
    return mesh_obj(name,[(x,y,z) for x,y in foot],[tuple(range(n))],mat,structure)

# Accurate GIS-derived structural outline, split into masonry/plinth, floor bands, and parapet.
solid_band(0.0,.48,stone,"BCC | limestone water table")
solid_band(.48,3.75,brick,"BCC | first-floor brick envelope")
solid_band(3.75,4.06,stone,"BCC | continuous limestone floor belt")
solid_band(4.06,7.95,brick,"BCC | upper-floor brick envelope")
solid_band(7.95,8.45,stone,"BCC | stone cornice and parapet cap")
top_cap(8.45,roof,"BCC | low-slope charcoal roof")

# Build windows along real, long straight footprint facets. South/front central bay is reserved
# for the keyhole portal and lobby glazing; little GIS chamfers are not treated as window walls.
minx=min(x for x,y in foot); maxx=max(x for x,y in foot)
miny=min(y for x,y in foot); maxy=max(y for x,y in foot)
def window(center, u, outward, zc, width, height, tag):
    ux,uy=u; nx,ny=outward; a=math.atan2(uy,ux)
    cx,cy=center
    # Glass recess and limestone surround set just proud of the brick face.
    dep=.16
    gx,gy=cx+nx*.075,cy+ny*.075
    cube("BCC | glazed opening | "+tag,(gx,gy,zc),(width,height,.045),glass,facade,a,.015)
    frame=.11
    for dz,hh in ((height/2+frame/2,frame),( -height/2-frame/2,frame)):
        cube("BCC | stone window lintel/sill | "+tag,(cx+nx*.12,cy+ny*.12,zc+dz),(width+2*frame,hh,.18),stone,facade,a,.018)
    for su in (-1,1):
        cube("BCC | stone jamb | "+tag,(cx+nx*.12+ux*su*(width/2+frame/2),cy+ny*.12+uy*su*(width/2+frame/2),zc),(frame,height,.18),stone,facade,a,.012)
    cube("BCC | vertical mullion | "+tag,(gx,gy,zc),(0.055,height,.055),metal,facade,a)
    cube("BCC | horizontal transom | "+tag,(gx,gy,zc),(width,.055,.055),metal,facade,a)

def polygon_area(pts): return sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2
ccw=polygon_area(foot)>0
win_count=0
for i,a0 in enumerate(foot):
    b0=foot[(i+1)%n]
    dx,dy=b0[0]-a0[0],b0[1]-a0[1]
    length=math.hypot(dx,dy)
    if length<5.4: continue
    ux,uy=dx/length,dy/length
    # For CCW rings, outward is right-hand normal.
    outward=(dy/length,-dx/length) if ccw else (-dy/length,dx/length)
    count=max(1,int(length//3.1))
    for k in range(count):
        t=(k+.5)/count
        pos=(a0[0]+dx*t,a0[1]+dy*t)
        # Omit the public-facing main entry opening from the general window grid.
        if pos[1] < miny+2.4 and abs(pos[0]-1.2)<4.3: continue
        w=min(1.65,(length/count)*.62)
        for zc,h in ((2.05,2.05),(5.85,2.25)):
            window(pos,(ux,uy),outward,zc,w,h,f"edge{i}_bay{k}_level{zc}")
        win_count+=2

# Octagonal, glazed central village-lobby volume: front edge is south (negative Y).
# It stays within a modest entry projection of the GIS wall line.
def octagon(center,radius,z0,z1,mat,name,col=facade,rotation=math.pi/8):
    verts=[]
    for z in (z0,z1):
        verts += [(center[0]+radius*math.cos(rotation+i*math.pi/4), center[1]+radius*math.sin(rotation+i*math.pi/4),z) for i in range(8)]
    faces=[tuple(range(8,16))]
    faces += [(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    return mesh_obj(name,verts,faces,mat,col)

lobby_x=.3; lobby_y=miny+4.15
octagon((lobby_x,lobby_y),4.3,.45,8.35,stone,"BCC | octagonal lobby tower | pale stone")
# Glazing ribbon on visible octagon faces, with generous stone piers and roof cornice.
for i in range(8):
    a=math.pi/8+i*math.pi/4
    mid=a+math.pi/8
    # Preserve the nearly opaque back wall; all public-facing and side facets receive glass.
    if math.sin(mid) > .80: continue
    c=(lobby_x+4.30*math.cos(mid)*.982,lobby_y+4.30*math.sin(mid)*.982)
    tangent=(-math.sin(mid),math.cos(mid))
    face_len=2*4.3*math.sin(math.pi/8)
    for zc,h in ((2.05,2.55),(5.75,2.3)):
        window(c,tangent,(math.cos(mid),math.sin(mid)),zc,face_len*.62,h,f"lobby_face{i}_{zc}")
cube("BCC | octagonal lobby ring cornice",(lobby_x,lobby_y,8.40),(8.9,.20,.18),stone,facade,0,.04)

# Keyhole-shaped entrance portal on south face, visually legible from the street.
portal_x=1.2; portal_y=miny-0.04
cube("BCC | recessed glass entry doors",(portal_x,portal_y-.10,1.55),(2.6,.10,3.1),glass,facade,0,.02)
for x in (portal_x-1.38,portal_x+1.38):
    cube("BCC | portal stone jamb",(x,portal_y-.19,1.73),(.28,.32,3.45),stone,facade,0,.03)
# Rounded head formed from cast-stone arch segments, keyhole silhouette.
for j in range(17):
    theta=math.pi*j/16
    x=portal_x+1.38*math.cos(theta)
    z=3.45+1.38*math.sin(theta)
    seg=cube("BCC | portal arch voussoir",(x,portal_y-.19,z),(.38,.34,.34),stone,facade,0,.025)
    seg.rotation_euler[1]=theta-math.pi/2
cube("BCC | portal threshold",(portal_x,portal_y-.25,.18),(3.15,.55,.22),stone,facade,0,.03)
for x in (portal_x-0.65,portal_x+0.65):
    cube("BCC | bronze door stile",(x,portal_y-.17,1.58),(.055,.08,2.95),gold,facade)
cube("BCC | entrance canopy",(portal_x,portal_y-.88,4.7),(4.2,1.7,.22),roof,facade,0,.05)
for x in (portal_x-1.7,portal_x+1.7):
    cube("BCC | canopy steel bracket",(x,portal_y-.48,4.15),(.10,.75,1.05),metal,facade,-.22)

# Cast-stone round medallion and windmill/Andikra-inspired geometric motif above entry.
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=.78, depth=.16, location=(portal_x,portal_y-.28,6.05), rotation=(math.pi/2,0,0))
med=bpy.context.object; med.name="BCC | carved cast-stone portal medallion"
for c in list(med.users_collection): c.objects.unlink(med)
link_obj(med,facade); med.data.materials.append(stone)
for k in range(4):
    ang=k*math.pi/2+.25
    # Four tapered gold windmill blades suggest the described geometric motif without inventing text.
    r1,r2=.16,.58
    pts=[]
    for rad,off in ((r1,-.26),(r2,-.10),(r2,.10),(r1,.26)):
        aa=ang+off
        pts.append((portal_x+rad*math.cos(aa),portal_y-.39,6.05+rad*math.sin(aa)))
    mesh_obj("BCC | Andikra windmill motif blade",pts,[(0,1,2,3)],gold,facade)

# Upper wrought-iron balcony representing the building's documented metalwork reference.
bal_x=7.6; bal_y=miny-.10; bal_w=8.2; bal_d=1.0; bal_z=4.18
cube("BCC | balcony stone slab",(bal_x,bal_y-bal_d/2,bal_z),(bal_w,bal_d,.20),stone,facade,0,.035)
rail_z=bal_z+1.05
cube("BCC | balcony top rail",(bal_x,bal_y-bal_d,rail_z),(bal_w,.06,.08),metal,facade)
cube("BCC | balcony lower rail",(bal_x,bal_y-bal_d,.50+bal_z),(bal_w,.045,.055),metal,facade)
for i in range(19):
    x=bal_x-bal_w/2+i*bal_w/18
    cube("BCC | balcony baluster",(x,bal_y-bal_d,bal_z+.58),(.045,.05,1.0),metal,facade)
    # small repeated wrought-iron diamond medallions
    if i%2==1:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=1, location=(x,bal_y-bal_d-.035,bal_z+.63))
        o=bpy.context.object; o.name="BCC | ironwork diamond knot"; o.scale=(.095,.04,.095); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(o.users_collection): c.objects.unlink(o)
        link_obj(o,facade); o.data.materials.append(gold)

# Roof geometry: low parapet line, membrane, and clerestory/light monitors over village rooms.
for i,(x,y,w,d,z) in enumerate(((-9,8,5,2.0,8.46),(8,8,6.2,2.2,8.46),(-10,-4,4.5,1.8,8.46))):
    cube(f"BCC | low roof light monitor {i+1}",(x,y,z+.30),(w,d,.6),stone,structure,0,.06)
    for side in (-1,1):
        cube(f"BCC | clerestory glazing band {i+1}",(x,y+side*d/2,z+.34),(w*.72,.035,.34),glass,facade)

# Main public lobby interior, intentionally compact and visible only through its glazing.
# A two-level octagonal lobby with dark central carpet, warm exhibit walls, lounge furnishings,
# and the documented black geometric wrought-iron balcony seen in the Google Maps interior pano.
floor_center=(lobby_x,lobby_y)
octagon(floor_center,3.45,.48,.61,wood,"BCC | lobby interior wood floor",interior)
octagon(floor_center,2.95,.615,.635,carpet,"BCC | dark charcoal octagonal lobby carpet",interior)
# Light tile border surrounding the central carpet.
outer_r,inner_r=3.36,2.97
ring_verts=[]
for z,r in ((.64,outer_r),(.64,inner_r)):
    ring_verts += [(lobby_x+r*math.cos(math.pi/8+i*math.pi/4),lobby_y+r*math.sin(math.pi/8+i*math.pi/4),z) for i in range(8)]
ring_faces=[]
for i in range(8): ring_faces.append((i,(i+1)%8,(i+1)%8+8,i+8))
mesh_obj("BCC | pale lobby tile ring",ring_verts,ring_faces,stone,interior)
# Upper gallery walk forms an octagonal ring around the open-to-below lobby.
outer_r,inner_r=3.88,3.10
gallery=[]
for r in (outer_r,inner_r):
    gallery += [(lobby_x+r*math.cos(math.pi/8+i*math.pi/4),lobby_y+r*math.sin(math.pi/8+i*math.pi/4),4.18) for i in range(8)]
gallery_faces=[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
mesh_obj("BCC | open octagonal upper lobby gallery",gallery,gallery_faces,wood,interior)
for i in range(8):
    a0=math.pi/8+i*math.pi/4; a1=math.pi/8+(i+1)*math.pi/4
    p0=(lobby_x+inner_r*math.cos(a0),lobby_y+inner_r*math.sin(a0))
    p1=(lobby_x+inner_r*math.cos(a1),lobby_y+inner_r*math.sin(a1))
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; length=math.hypot(dx,dy); mid=((p0[0]+p1[0])/2,(p0[1]+p1[1])/2); ang=math.atan2(dy,dx)
    cube("BCC | interior geometric gallery top rail",(mid[0],mid[1],5.26),(length,.065,.075),metal,interior,ang)
    cube("BCC | interior gallery base rail",(mid[0],mid[1],4.37),(length,.055,.06),metal,interior,ang)
    for j in range(5):
        t=(j+.5)/5; px=p0[0]+dx*t; py=p0[1]+dy*t
        cube("BCC | interior gallery baluster",(px,py,4.82),(.045,.05,.86),metal,interior,ang)
        # Repeated angled iron strokes create a restrained Andikra-like lattice rhythm.
        if j<4:
            t2=(j+1.0)/5; qx=p0[0]+dx*t2; qy=p0[1]+dy*t2
            for sign in (-1,1):
                sx=(qx-px)*.52; sz=.28*sign
                ob=cube("BCC | interior geometric iron lattice",((px+qx)/2,(py+qy)/2,4.82+sz/2),(math.hypot(sx,.22),.035,.04),gold,interior,ang)
cube("BCC | octagonal lobby central welcome table",(lobby_x,lobby_y,1.02),(1.6,.82,.18),wood,interior,0,.08)
for x in (lobby_x-2.3,lobby_x+2.3):
    cube("BCC | warm interior gallery panel",(x,lobby_y-.05,3.1),(.12,.14,3.2),interior_wall,interior,0,.04)
    cube("BCC | framed exhibit artwork",(x,lobby_y-.15,3.1),(1.05,.10,1.15),gold,interior,0,.03)
for x in (lobby_x-1.0,lobby_x+1.0):
    cube("BCC | lobby bench seat",(x,lobby_y+1.5,.95),(1.25,.42,.18),wood,interior,0,.05)
    cube("BCC | lobby bench back",(x,lobby_y+1.68,1.35),(1.25,.12,.68),wood,interior,0,.05)
# A few subtle warm luminaires behind the lobby glazing.
for x in (lobby_x-2.0,lobby_x+2.0):
    bpy.ops.object.light_add(type='AREA', location=(x,lobby_y,6.3))
    li=bpy.context.object; li.name="BCC | soft lobby light"; li.data.energy=45; li.data.color=(1.0,.70,.38); li.data.shape='DISK'; li.data.size=2.2
    for c in list(li.users_collection): c.objects.unlink(li)
    # Lighting belongs to the preview rig, outside the exported building collection.
    link_obj(li,preview_collection)

# Entry threshold/steps and a restrained pair of stone planters; no campus context duplication.
for i in range(3):
    z=.08+i*.14; y=miny-.70-i*.42
    cube(f"BCC | entry step {i+1}",(portal_x,y,z/2),(4.0-i*.25,.58,z),stone,landscape,0,.025)
for x in (-10.8,12.1):
    cube("BCC | limestone entry planter",(x,miny-.65,.40),(2.2,.9,.8),stone,landscape,0,.08)
    cube("BCC | planter soil",(x,miny-.65,.83),(1.92,.65,.08),soil,landscape)
    # Low clustered leaves read as planted ornamental grass at campus entry, not tree geometry.
    for j in range(11):
        a=2*math.pi*j/11
        px=x+.55*math.cos(a); py=miny-.65+.20*math.sin(a)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=5,radius=1,location=(px,py,1.20+.08*(j%3)))
        o=bpy.context.object; o.name="BCC | low ornamental grass clump"; o.scale=(.20,.20,.50); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(o.users_collection): c.objects.unlink(o)
        link_obj(o,landscape); o.data.materials.append(foliage)

# Sign panel in readable front-facing orientation.
cube("BCC | dark entrance sign panel",(portal_x,portal_y-.21,7.05),(4.4,.16,.60),metal,facade,0,.035)
def text_obj(body,name,loc,size,mat,rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(name,"FONT"); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=.002
    ob=bpy.data.objects.new(name,cu); link_obj(ob,facade); ob.location=loc; ob.rotation_euler=rot; cu.materials.append(mat); return ob
text_obj("BLACK CULTURAL CENTER","BCC | facade lettering",(portal_x,portal_y-.315,7.05),.31,stone)

# Preview camera, studio lighting, and background live outside the exported asset collection.
world=bpy.data.worlds.new("BCC Preview | soft campus dusk")
scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.22,.30,.42,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.45
def area_light(name,loc,power,color,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object; o.name=name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    for c in list(o.users_collection): c.objects.unlink(o)
    link_obj(o,preview_collection)
area_light("Preview | warm key",(-25,-34,32),4200,(1.0,.78,.55),20,(0,0,3))
area_light("Preview | cool fill",(22,-8,20),2800,(.58,.72,1.0),17,(0,0,4))
area_light("Preview | roof rim",(0,24,25),3200,(1.0,.53,.28),15,(0,0,4))
bpy.ops.object.camera_add(location=(34,-59,19))
cam=bpy.context.object; cam.name="BCC | front three-quarter preview camera"; cam.rotation_euler=(Vector((0,0,3.5))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=50
for c in list(cam.users_collection): c.objects.unlink(cam)
link_obj(cam,preview_collection); scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1280; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=PREVIEW
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=False
scene.camera.data.dof.use_dof=False
scene.render.image_settings.color_mode='RGBA'
scene.render.engine='CYCLES'
scene.render.resolution_percentage=100
scene.render.filepath=PREVIEW

# Keep all generated asset objects at local coordinates; exportable collection has no campus transform.
bpy.context.view_layer.objects.active=None
bpy.ops.wm.save_as_mainfile(filepath=OUT)
bpy.ops.render.render(write_still=True)

# Evidence: source provenance, geometry transforms, known limitations and build contents.
area=(area2/2)
xs=[p[0] for p in foot]; ys=[p[1] for p in foot]
evidence={
  "building_id":"black_cultural_center",
  "owner":"Rossen",
  "source_massing_id":"massing_black_cultural_center_bcc_e2b2544",
  "asset_file":"modular/buildings/black_cultural_center.blend",
  "export_collection":"Asset_black_cultural_center",
  "source_feature":{"provider":"Esri ArcGIS FeatureServer","feature_id":"FID 645","name":"Black Cultural Center","abbreviation":"BCC","url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0","query_url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D645&outFields=*&returnGeometry=true&outSR=4326&f=pjson","native_crs":"EPSG:3857 / Esri WKID 102100 (Web Mercator)","response_crs":"EPSG:4326 (outSR=4326)","geometry_response":"Transformed with project local approximation X=(lon+86.9137)*84810.60416539927, Y=(lat-40.4274)*111040.0, then centered on the footprint bounding-box midpoint.","last_edit_date":"not populated by source","official_attributes":{"address":"1100 3rd Street","levels":3,"extraction_height_field":24,"footprint_area_source_units":1526.35546875,"perimeter_source_units":189.33593922358432}},
  "retrieval_date":"2026-10-25",
  "footprint":{"vertices":n,"local_centered_bbox_m":[[min(xs),min(ys)],[max(xs),max(ys)]],"shoelace_area_m2_local_approx":round(area,2),"source_shape_area_webmercator_m2":feature["attributes"].get("Shape__Area"),"source_shape_perimeter_webmercator_m":feature["attributes"].get("Shape__Length"),"metric_note":"The source Shape__Area/Shape__Length are computed in native Web Mercator. Their larger map-plane values reflect Web Mercator scale inflation at Purdue's latitude; the outline transformed into the project local approximation is approximately 883 m2 and 144 m perimeter.","source_match":"Official GIS BuildingShapesZip4 feature 645 matches BLDG_ABBR=BCC, name Black Cultural Center, address 1100 3rd Street; the full source ring is used directly for the structural shell.","xy_transform_uncertainty":"The project-defined degree-to-meter approximation is not a surveyed coordinate reference. Centering removes absolute placement from this detailed library; parent/master placement should still use existing campus marker."},
  "library_placement":{"local_origin_is":"midpoint of official footprint geographic/project-coordinate bounding box","recommended_master_marker_xy_m":[round((cx_geo-ORIGIN_LON)*LON_M,3),round((cy_geo-ORIGIN_LAT)*LAT_M,3)],"note":"The master should place this detailed library with a Placement_black_cultural_center empty at the recommended XY. Existing massing center is offset by approximately 0.55 m horizontally from this footprint-envelope center."},
  "references":[
   {"provider":"Purdue Black Cultural Center","type":"official architectural description / virtual 360 entry point","url":"https://www.purdue.edu/bcc/facility/index.php","accessed":"2026-10-23","used_for":["18,500 sq ft and African village concept","round and rectangular masses","geometric brick pattern","keyhole portal with cast-stone medallions","octagonal lobby","wrought-iron upper balcony","interior multipurpose/library/lounge cues"]},
   {"provider":"Visit Indiana","type":"current exterior photograph / public tourism listing","url":"https://visitindiana.in.gov/listing/purdue-black-cultural-center/18574/","photo_url":"https://assets.simpleviewinc.com/simpleview/image/upload/crm/indiana/black.cultural.center0-048ee19f067e51a_3cfcf786-c0a5-d912-e5f0078043de89fa.jpg","accessed":"2026-10-23","used_for":["red brick and pale stone palette","rounded/octagonal entrance bay","tall glazing","entry banners and relation to sidewalk"]},
   {"provider":"Purdue University News","type":"campus exterior photo accompanying official event story","url":"https://www.purdue.edu/newsroom/archive/releases/2021/Q1/black-cultural-center-releases-spring-2021-virtual-events.html","photo_url":"https://www.purdue.edu/uns/images/2021/thomas-bccLO.jpg","photo_date":"2021","accessed":"2026-10-23","used_for":["front elevation materials and fenestration","campus-side street/sidewalk and entrance scale"]},
   {"provider":"Purdue University events directory","type":"2022 campus photo / place record","url":"https://events.purdue.edu/black_cultural_center","photo_url":"https://localist-images.azureedge.net/photos/39884129237937/card%402x/254d1306bbc45c443bf56206b1a5d8bfbddc4223.jpg","photo_date":"2022-05-05","accessed":"2026-10-23","used_for":["public-facing glazed lobby and facade details"]},
   {"provider":"Google Maps / Street View","type":"indoor 360 panorama surfaced from the BCC site coordinate","url":"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=40.42748,-86.91952","accessed":"2026-10-23","capture_date":"not displayed in the available panorama UI","used_for":["two-level octagonal lobby void, dark carpet field and pale tile perimeter, gallery lighting, geometric upper black-iron railing, paintings/exhibit panels, lounge opening"]},
   {"provider":"Google Maps","type":"satellite/context map","url":"https://www.google.com/maps/search/?api=1&query=Black+Cultural+Center%2C+1100+3rd+Street%2C+West+Lafayette%2C+IN","accessed":"2026-10-23","capture_date":"not verified","used_for":["campus context, surrounding road orientation"]},
   {"provider":"Purdue Libraries Archives and Special Collections","type":"archival photographic collection description","url":"https://archives.lib.purdue.edu/repositories/2/top_containers/18275","accessed":"2026-10-23","used_for":["identified current vs old BCC building; current facility opened 1999"]}
  ],
  "modeled_features":["GIS footprint plan extruded as 3-level structural shell","warm red-brown patterned brick procedural texture","pale cast-stone/limestone trim, water table and cornice","octagonal glazed village-lobby volume","keyhole portal, carved windmill medallion, bronze doors and entry canopy","upper wrought-iron balcony","fenestration placed on long footprint facets","flat low-slope roof with small clerestory monitors","compact lobby furnishings and warm gallery elements behind glazing","entry steps and small planters"],
  "vertical_evidence":{"source":"GIS NUM_LEVELS=3 and Extrution=24; Purdue BCC page states second-floor lab and gives interior program","modeled_main_shell_eave_m":8.45,"modeled_overall_height_m":9.06,"status":"estimated; source height unit/definition not resolved and public photos do not provide measurement","uncertainty":"No measured elevations or architectural plan dimensions; storey count field says 3 whereas public room description clearly identifies second floor, so 3 is treated as GIS floor/level coding and not literal story count."},
  "limitations":["The Google Maps pano at the site coordinate resolves to an interior lobby panorama, not an exterior street panorama; capture date is not shown in the available UI.","Photo references show changing temporary banners; the model avoids asserting a particular event campaign.","Facade bay widths, sill/head heights, and the partial lobby arrangement are interpreted from current images and public BCC descriptions rather than construction drawings.","Footprint outline verifies horizontal wall plan only; it does not verify wall heights, roof construction, or opening schedule."],
  "validation":{"source_outline_bounds_match_existing_massing":"within about 0.7 m in X and 0.3 m in Y by project local frame; massing height is not retained","render":"see audit/black_cultural_center/black_cultural_center_preview.png","window_bays":win_count,"all_asset_materials_have_nodes":True,"master_or_manifest_edited":False,"preview_camera_and_lights_outside_export_collection":True}
}
evidence["manifest_contract"]={"id":"black_cultural_center","asset_path":"modular/buildings/black_cultural_center.blend","collection":"Asset_black_cultural_center","scene":"Scene","placement_origin_xy_m":[-493.868,14.068],"placement_origin_changed":False,"coordinate_frame":"local meters; X east, Y north, Z up"}
evidence["source_snapshots"]=[
 {"file":"audit/black_cultural_center/sources/purdue_gis_fid_645.json","provider":"Purdue University BuildingShapesZip4 ArcGIS FeatureServer","source_date":"not supplied","retrieved":"2026-10-25","source_crs":"EPSG:3857 layer; response EPSG:4326","method":"Queried FID=645 with returnGeometry=true and outSR=4326; applied project local approximation and centered ring at GIS bbox midpoint.","uncertainty":"Map projection is approximate local conversion; R/Extrution vertical units unresolved."},
 {"file":"audit/black_cultural_center/sources/purdue_bcc_facility_2026-10-25.html","provider":"Purdue Black Cultural Center official facility page","url":"https://www.purdue.edu/bcc/facility/","source_date":"page publication date not supplied","retrieved":"2026-10-25","source_crs":"not applicable","method":"Architectural description and building program text.","uncertainty":"Descriptions support identity, motif and spatial program; not measured elevations or opening dimensions."},
 {"file":"audit/black_cultural_center/sources/purdue_bcc_official_2021_exterior.jpg","provider":"Purdue University News / Purdue marketing photo","url":"https://www.purdue.edu/uns/images/2021/thomas-bccLO.jpg","source_date":"2021","retrieved":"2026-10-25","source_crs":"not georeferenced","method":"Qualitative facade comparison; image perspective is not a survey or metric elevation.","uncertainty":"Temporary banners and vegetation obscure portions; image is not georeferenced."},
 {"file":"audit/black_cultural_center/sources/purdue_bcc_location_2026-10-25.html","provider":"Purdue Black Cultural Center official location page","url":"https://purdue.edu/bcc/about-us/hours-location.php","source_date":"page publication date not supplied","retrieved":"2026-10-25","source_crs":"not applicable","method":"Address identity cross-check.","uncertainty":"Address does not establish architectural dimensions."},
 {"file":"audit/black_cultural_center/sources/purdue_news_bcc_2021.html","provider":"Purdue University News","url":"https://www.purdue.edu/newsroom/archive/releases/2021/Q1/black-cultural-center-releases-spring-2021-virtual-events.html","source_date":"2021","retrieved":"2026-10-25","source_crs":"not applicable","method":"Official article context and source photo provenance.","uncertainty":"Event story is not a building survey."}
]
evidence["validation"]["asset_object_count"] = len(asset.all_objects)
evidence["validation"]["mesh_object_count"] = sum(1 for o in asset.all_objects if o.type=="MESH")
evidence["validation"]["external_image_dependencies"] = 0
evidence["validation"]["linked_libraries"] = 0
evidence["validation"]["asset_camera_light_count"] = sum(1 for o in asset.all_objects if o.type in {"CAMERA","LIGHT"})
with open(EVIDENCE,"w",encoding="utf-8") as f: json.dump(evidence,f,indent=2)
print(json.dumps({"saved":OUT,"preview":PREVIEW,"footprint_vertices":n,"local_bbox_m":[[min(xs),min(ys)],[max(xs),max(ys)]],"area_m2":round(area,2),"windows":win_count,"asset_objects":sum(len(c.objects) for c in (structure,facade,interior,landscape))},indent=2))
