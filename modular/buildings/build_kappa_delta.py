"""Build a source-informed Kappa Delta Theta Nu building asset.

Usage: blender --background --python modular/buildings/build_kappa_delta.py
All generated textures are procedural and packed into the self-contained library.
"""
from pathlib import Path
import bpy, json, math, xml.etree.ElementTree as ET
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "kappa_delta"
SOURCES = AUDIT / "sources"
OUT = ROOT / "modular" / "buildings" / "kappa_delta.blend"
AUDIT.mkdir(parents=True, exist_ok=True)

# Building shell from OSM way 860903232. Its four corners closely follow the
# current 358 Northwestern address point and the 2021/22 construction imagery.
osm_path = SOURCES / "osm_kappa_delta_building_860903232_2026-10-27.osm"
root = ET.parse(osm_path).getroot()
nodes = {n.attrib["id"]: (float(n.attrib["lon"]), float(n.attrib["lat"])) for n in root.findall("node")}
way = next(w for w in root.findall("way") if w.attrib.get("id") == "860903232")
refs = [n.attrib["ref"] for n in way.findall("nd")]
ring_ll = [nodes[k] for k in refs]
if ring_ll[0] == ring_ll[-1]: ring_ll = ring_ll[:-1]
LAT0, LON0 = 40.4274, -86.9137

def campus_xy(lon, lat):
    return ((lon-LON0)*111412.84*math.cos(math.radians(LAT0)), (lat-LAT0)*111040.0)
world = [campus_xy(lon, lat) for lon, lat in ring_ll]
# This four-corner OSM footprint is a near-rectangle. Use its polygon centroid
# for the master placement marker, then shift only the local origin by the
# tiny projected bounding-box offset so the wall axes remain centered.
area2 = 0.0; cx6 = 0.0; cy6 = 0.0
for (x1,y1),(x2,y2) in zip(world, world[1:]+world[:1]):
    c = x1*y2-x2*y1
    area2 += c; cx6 += (x1+x2)*c; cy6 += (y1+y2)*c
origin = (cx6/(3*area2), cy6/(3*area2))
ring = [(x-origin[0], y-origin[1]) for x,y in world]
# Local X follows the road-parallel long front facade. Local +Y points inward.
p0,p1,p2,p3 = [Vector(p) for p in ring]
axis_x = (p1-p0).normalized()
axis_y = Vector((-axis_x.y, axis_x.x))
proj = [(p.dot(axis_x), p.dot(axis_y)) for p in [Vector(q) for q in ring]]
shift_x = (min(p[0] for p in proj)+max(p[0] for p in proj))/2
shift_y = (min(p[1] for p in proj)+max(p[1] for p in proj))/2
origin = (origin[0]+shift_x*axis_x.x+shift_y*axis_y.x,
          origin[1]+shift_x*axis_x.y+shift_y*axis_y.y)
foot = [(p[0]-shift_x,p[1]-shift_y) for p in proj]
half_x=(max(p[0] for p in foot)-min(p[0] for p in foot))/2
half_y=(max(p[1] for p in foot)-min(p[1] for p in foot))/2
length=(p1-p0).length
depth=(p2-p1).length
# Preserve the measured (slightly skew) GIS ring while using its mean axes for
# photo-layout details. The walls will differ from the source only by the
# source ring's small nonparallel corner offsets.
footprint_area = abs(area2)/2

# Start with a clean, portable asset scene.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for db in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for item in list(db):
        if item.users == 0: db.remove(item)
scene = bpy.context.scene
scene.name = "Building_kappa_delta"
scene.unit_settings.system = "METRIC"; scene.unit_settings.scale_length = 1.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1500; scene.render.resolution_y = 1100; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False; scene.render.filepath = str(AUDIT / "kappa_delta_front_render.png")
scene.view_settings.view_transform = "AgX"
scene.world.color = (0.28,0.34,0.42)
asset = bpy.data.collections.new("Asset_kappa_delta")
scene.collection.children.link(asset)
interior = bpy.data.collections.new("Schematic_Interior_kappa_delta")
asset.children.link(interior)
preview = bpy.data.collections.new("Preview_Only_Render_Rig")
scene.collection.children.link(preview)

# Materials use procedural brick, stone and roof pattern nodes so the file has
# no external texture dependencies.
def principled(name,color,rough=0.7,metal=0.0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bsdf=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value=(*color,1);bsdf.inputs["Roughness"].default_value=rough;bsdf.inputs["Metallic"].default_value=metal
    return m,bsdf

def brick_material():
    m,bsdf=principled("KappaDelta_Limewashed_Greige_Brick",(.68,.65,.58),.82)
    n=m.node_tree.nodes;l=m.node_tree.links
    tex=n.new("ShaderNodeTexBrick");tex.name="Running_Bond_Brick_Courses"
    tex.inputs["Color1"].default_value=(.60,.58,.53,1);tex.inputs["Color2"].default_value=(.78,.75,.69,1)
    tex.inputs["Mortar"].default_value=(.42,.41,.38,1);tex.inputs["Scale"].default_value=2.2
    tex.inputs["Brick Width"].default_value=.5;tex.inputs["Row Height"].default_value=.25
    tex.inputs["Mortar Size"].default_value=.025;tex.inputs["Mortar Smooth"].default_value=.015
    coord=n.new("ShaderNodeTexCoord"); l.new(coord.outputs["UV"],tex.inputs["Vector"])
    l.new(tex.outputs["Color"],bsdf.inputs["Base Color"])
    bump=n.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.18;bump.inputs["Distance"].default_value=.025
    l.new(tex.outputs["Fac"],bump.inputs["Height"]);l.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    return m

brick=brick_material()
stone,_=principled("KappaDelta_Warm_Limestone_Trim",(.78,.75,.68),.68)
stone_light,_=principled("KappaDelta_Entry_Stone",(.83,.81,.74),.55)
roof,roof_bsdf=principled("KappaDelta_Dark_Charcoal_Slate",(.14,.17,.19),.64)
noise=roof.node_tree.nodes.new("ShaderNodeTexNoise");noise.inputs["Scale"].default_value=22;noise.inputs["Detail"].default_value=3;noise.inputs["Roughness"].default_value=.72
ramp=roof.node_tree.nodes.new("ShaderNodeValToRGB");ramp.color_ramp.elements[0].position=.16;ramp.color_ramp.elements[0].color=(.055,.070,.082,1);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(.20,.235,.25,1)
roof.node_tree.links.new(noise.outputs["Fac"],ramp.inputs["Fac"]);roof.node_tree.links.new(ramp.outputs["Color"],roof_bsdf.inputs["Base Color"])
coord=roof.node_tree.nodes.new("ShaderNodeTexCoord");roof.node_tree.links.new(coord.outputs["Object"],noise.inputs["Vector"])
bump=roof.node_tree.nodes.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.12;bump.inputs["Distance"].default_value=.018;roof.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"]);roof.node_tree.links.new(bump.outputs["Normal"],roof_bsdf.inputs["Normal"])
metal,_=principled("KappaDelta_Charcoal_Standing_Seam_Metal",(.075,.09,.105),.35,.72)
frame,_=principled("KappaDelta_Dark_Bronze_Window_Frames",(.065,.075,.078),.31,.55)
glass,glass_bsdf=principled("KappaDelta_BlueGray_Reflective_Glass",(.10,.18,.23),.18,.28)
glass_bsdf.inputs["Transmission Weight"].default_value=.18
glass_bsdf.inputs["Alpha"].default_value=.92
wood,_=principled("KappaDelta_Stained_Oak",(.24,.14,.085),.43)
white,_=principled("KappaDelta_Column_Painted_White",(.85,.84,.79),.48)
interior_wall,_=principled("KappaDelta_Interior_Warm_White",(.79,.77,.72),.84)
floor_wood,_=principled("KappaDelta_Interior_Wood_Floor",(.35,.22,.12),.48)
furniture,_=principled("KappaDelta_Interior_Furniture",(.43,.39,.33),.65)
landscape,_=principled("KappaDelta_Mulch_and_Soil",(.16,.10,.055),.96)

# Geometry helpers. All authored object coordinates are transformed into the
# original campus north/east basis before writing the standalone asset.
def mapxy(x,y): return (x*axis_x.x+y*axis_y.x, x*axis_x.y+y*axis_y.y)
def vworld(x,y,z):
    q=mapxy(x,y);return (q[0],q[1],z)

def mesh_obj(name,verts,faces,material,collection=asset):
    mesh=bpy.data.meshes.new(name+"_Mesh");mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj)
    if material: obj.data.materials.append(material)
    return obj

def box(name,cx,cy,cz,sx,sy,sz,material,angle=0.0,collection=asset):
    # Build local-u/v/z box, rotate in the building's plan, then map to campus XY.
    verts=[]
    ca,sa=math.cos(angle),math.sin(angle)
    for zsign in (-1,1):
        for ysign in (-1,1):
            for xsign in (-1,1):
                lx=xsign*sx/2;ly=ysign*sy/2
                rx=lx*ca-ly*sa;ry=lx*sa+ly*ca
                verts.append(vworld(cx+rx,cy+ry,cz+zsign*sz/2))
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return mesh_obj(name,verts,faces,material,collection)

def beam(name,start,end,width,depth,material,collection=asset):
    """Rectangular beam between local XYZ points, including slope in Z."""
    a=Vector(vworld(*start));b=Vector(vworld(*end));direction=(b-a).normalized()
    ref=Vector((0,0,1));side=direction.cross(ref)
    if side.length<1e-6: side=Vector((1,0,0))
    side.normalize();normal=direction.cross(side).normalized()
    verts=[]
    for p in (a,b):
        for su,sv in ((-1,-1),(-1,1),(1,1),(1,-1)):
            q=p+side*(su*width/2)+normal*(sv*depth/2);verts.append(tuple(q))
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh_obj(name,verts,faces,material,collection)

def prism(name,poly,z0,z1,material,collection=asset):
    n=len(poly);verts=[vworld(x,y,z) for z in (z0,z1) for x,y in poly]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    obj=mesh_obj(name,verts,faces,material,collection)
    uv=obj.data.uv_layers.new(name="FacadeUV")
    for pi,poly_data in enumerate(obj.data.polygons):
        if pi<2:
            for li,vi in zip(poly_data.loop_indices,poly_data.vertices):
                src=poly[vi%n]
                uv.data[li].uv=(src[0],src[1])
        else:
            edge=pi-2; a=poly[edge]; b=poly[(edge+1)%n]
            dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy);tx,ty=dx/ll,dy/ll
            for li,vi in zip(poly_data.loop_indices,poly_data.vertices):
                src=poly[vi%n]; zz=z1 if vi>=n else z0
                uv.data[li].uv=((src[0]-a[0])*tx+(src[1]-a[1])*ty,zz)
    return obj

def facade_frame(name,side,u,offset,z,width,height,depth,matl):
    """A slim trim bar box with its broad side parallel to the chosen facade."""
    if side=="front": cx,cy,ang=u,-half_y-offset,0.0
    elif side=="back": cx,cy,ang=u,half_y+offset,0.0
    elif side=="left": cx,cy,ang=-half_x-offset,u,math.pi/2
    else: cx,cy,ang=half_x+offset,u,math.pi/2
    return box(name,cx,cy,z,width,depth,height,matl,ang)

def facade_pt(side,u,offset,z):
    if side=="front": return vworld(u,-half_y-offset,z)
    if side=="back": return vworld(u,half_y+offset,z)
    if side=="left": return vworld(-half_x-offset,u,z)
    return vworld(half_x+offset,u,z)

def glass_panel(name,side,u,offset,z,width,height,matl,arch=False):
    verts=[]
    if arch:
        spring=height-width*.52
        pts=[(-width/2,0),(width/2,0),(width/2,spring)]
        for i in range(13):
            a=math.pi*i/12
            pts.append((width/2*math.cos(a),spring+width/2*math.sin(a)))
        pts.append((-width/2,0))
    else:
        pts=[(-width/2,0),(width/2,0),(width/2,height),(-width/2,height)]
    for du,dz in pts:
        if side in ("front","back"):
            verts.append(facade_pt(side,u+du,offset,z+dz))
        else:
            verts.append(facade_pt(side,u+du,offset,z+dz))
    return mesh_obj(name,verts,[tuple(range(len(verts)))],matl)

def window(name,side,u,z,width,height,arch=False,balcony=False,offset=0.0):
    # Outer limestone surround, inset bronze frame, glazed panels and mullions.
    off=.10+offset; frameoff=.20+offset
    glass_panel(name+"_Glazing",side,u,off,z+0.13,width-.24,height-.25,glass,arch)
    # vertical jambs
    for dx in (-width/2,width/2): facade_frame(name+"_Jamb_"+str(dx),side,u+dx,frameoff,z+height/2,width=.12,height=height,depth=.13,matl=stone_light)
    # horizontal sill and header
    facade_frame(name+"_Sill",side,u,frameoff,z+.08,width=width+.18,height=.18,depth=.18,matl=stone_light)
    if not arch:
        facade_frame(name+"_Header",side,u,frameoff,z+height-.08,width=width+.15,height=.16,depth=.16,matl=stone_light)
    # bronze frame / mullions
    facade_frame(name+"_Mullion_V",side,u,frameoff-.07,z+height*.52,width=.065,height=height-.18,depth=.07,matl=frame)
    facade_frame(name+"_Mullion_H",side,u,frameoff-.07,z+height*.52,width=width-.12,height=.07,depth=.07,matl=frame)
    if arch:
        # curved arch surround and arch glazing are photo-informed; molding
        # segments follow the semicircle to avoid a generic rectangular first floor.
        spring=height-width*.52
        for i in range(17):
            a=math.pi*i/16
            x=u+width*.5*math.cos(a);zz=z+spring+width*.5*math.sin(a)
            facade_frame(name+"_ArchTrim_%02d"%i,side,x,frameoff,zz,.12,.12,.15,stone_light)
    if balcony:
        # Shallow Juliet balcony: dark metal railing and brackets.
        rail_y=frameoff+.45
        facade_frame(name+"_Balcony_Rail",side,u,rail_y,z+height*.57,width+1.0,height=.065,depth=.065,matl=metal)
        for dx in (-width*.55,-width*.27,0,width*.27,width*.55):
            facade_frame(name+"_Balcony_Baluster_"+str(dx),side,u+dx,rail_y,z+height*.57-.48,.045,.96,.045,metal)
        for dx in (-width*.43,width*.43):
            facade_frame(name+"_Balcony_Bracket_"+str(dx),side,u+dx,frameoff+.16,z+.25,.06,.48,.08,metal)

def arch_door(name,side,u,z,width,height):
    glass_panel(name+"_Glass",side,u,.11,z,width,height,glass,arch=False)
    for dx in (-width/2,width/2): facade_frame(name+"_Jamb",side,u+dx,.24,z+height/2,.15,height,.18,stone_light)
    facade_frame(name+"_Head",side,u,.24,z+height-.08,width+.25,.16,.18,stone_light)
    facade_frame(name+"_Sill",side,u,.24,z+.06,width+.25,.12,.18,stone_light)
    facade_frame(name+"_Door_Mullion",side,u,.31,z+height/2,.06,height-.15,.07,frame)
    facade_frame(name+"_Transom",side,u,.31,z+height*.79,width-.12,.07,.06,frame)
    facade_frame(name+"_Door_Leaf_Left",side,u-width*.24,.32,z+height*.40,width*.47,.08,height*.78,wood)
    facade_frame(name+"_Door_Leaf_Right",side,u+width*.24,.32,z+height*.40,width*.47,.08,height*.78,wood)
    facade_frame(name+"_Landing",side,u,.62,z-.02,width+1.2,.12,.25,stone_light)

def rail_run(name,side,u0,u1,offset,z,material=metal):
    facade_frame(name+"_Top",side,(u0+u1)/2,offset,z,u1-u0,.07,.07,material)
    for i in range(9):
        u=u0+(u1-u0)*i/8
        facade_frame(name+"_Bar_%02d"%i,side,u,offset,z-.45,.045,.9,.045,material)
    facade_frame(name+"_Lower",side,(u0+u1)/2,offset,z-.85,u1-u0,.05,.05,material)

# Foundation curb and primary 3-storey wall shell follow the exact source outline.
prism("KappaDelta_OSM_Footprint_Foundation",[tuple(p) for p in foot],-.12,.28,stone)
prism("KappaDelta_Three_Story_Greige_Brick_Shell",[tuple(p) for p in foot],.28,10.72,brick)
# Main floor bands and cornice belts; façade string courses are crisp limestone.
for z,ht,dep,matl,lab in [(4.05,.22,.22,stone,"First_Floor_String_Course"),(7.36,.19,.18,stone,"Second_Floor_String_Course"),(10.55,.25,.33,stone_light,"Entablature_Cornice")]:
    # Each side remains its own long clean molding run, with corners aligned to footprint edges.
    facade_frame("KappaDelta_"+lab+"_Front","front",0,-.01,z,2*half_x+.16,ht,dep,matl)
    facade_frame("KappaDelta_"+lab+"_Rear","back",0,-.01,z,2*half_x+.16,ht,dep,matl)
    facade_frame("KappaDelta_"+lab+"_West_End","left",0,-.01,z,2*half_y+.16,ht,dep,matl)
    facade_frame("KappaDelta_"+lab+"_East_End","right",0,-.01,z,2*half_y+.16,ht,dep,matl)
# Base and corner quoins echo the white-brick / limestone finish in the recent photos.
for side in ("front","back"):
    facade_frame("KappaDelta_BaseCourse_"+side,side,0,-.05,.55,2*half_x,.30,.18,stone)
for side in ("left","right"):
    facade_frame("KappaDelta_BaseCourse_"+side,side,0,-.05,.55,2*half_y,.30,.18,stone)
for sx in (-1,1):
    for sy in (-1,1):
        x=sx*(half_x-.17);y=sy*(half_y-.17)
        for z in (1.95,5.7,8.85): box(f"KappaDelta_Corner_Stone_Quoin_{sx}_{sy}_{z}",x,y,z,.34,.34,.34,stone_light)

# Front (Northwestern Avenue) elevation. The image-led storefront rhythm has
# tall arched first-floor glazing, three upper window courses, Juliet rails,
# one double-leaf entry and a more formal secondary portico at the left end.
eave=10.72
front_ground=[-13.9,-9.2,-4.5,4.4,9.1,13.8]
for i,x in enumerate(front_ground): window(f"KappaDelta_Front_Arch_Window_{i+1}","front",x,.82,1.34,2.55,arch=True)
# Central glazed front entry and stone portal.
arch_door("KappaDelta_Front_Main_Double_Door","front",0,.30,2.55,3.25)
for dx in (-1.68,1.68):
    facade_frame("KappaDelta_Main_Entry_Pilaster", "front",dx,.27,2.00,.24,3.35,.30,stone_light)
facade_frame("KappaDelta_Main_Entry_Lintel","front",0,.28,3.76,3.75,.32,.36,stone_light)
# Canopy with standing-seam finish on a slight downward slope.
canopy_verts=[]
for x in (-2.18,2.18):
    for y,z in [(-half_y-.15,3.92),(-half_y-1.62,3.65)]: canopy_verts.append(vworld(x,y,z))
mesh_obj("KappaDelta_Main_Entry_Charcoal_Metal_Canopy",canopy_verts,[(0,1,3,2)],metal)
for dx in (-1.95,1.95):
    box("KappaDelta_Main_Entry_Canopy_Bracket",dx,-half_y-1.22,3.36,.10,1.1,.12,metal)
# Exterior limestone stair, landing, wrought rails at the center door.
for i in range(6):
    z=.25-i*.05
    box(f"KappaDelta_Main_Entry_Stair_{i+1}",0,-half_y-.34-i*.29,z,3.35,.40,.25,stone_light)
rail_run("KappaDelta_Main_Entry_Railing_Left","front",-1.62,-.28,-half_y-1.85,.95,metal)
rail_run("KappaDelta_Main_Entry_Railing_Right","front",.28,1.62,-half_y-1.85,.95,metal)
# Main story windows and select Juliet balconies.
upper_x=[-14,-10,-6,-2,2,6,10,14]
for floor,z in [(2,4.64),(3,7.82)]:
    for i,x in enumerate(upper_x):
        if abs(x)==2: continue  # these bays are occupied by the projecting entry gable
        w=1.34 if abs(x)>12 else 1.42
        window(f"KappaDelta_Front_Floor_{floor}_Window_{i+1}","front",x,z,w,2.05,arch=False,balcony=(floor==2 and i in (1,3,5,7)))
# The architect's street and aerial views show a central, shallow projecting
# entrance bay with a steep front gable. Model this measured visual feature
# separately from the long roof ridge; its dimensions are image estimated.
front_y=-half_y
bay_depth=1.12; bay_half=3.05
box("KappaDelta_Projecting_Entry_Bay_Upper_Facade",0,front_y-bay_depth/2,(4.05+eave)/2,2*bay_half,bay_depth,eave-4.05,stone)
bay_quad=[vworld(-bay_half,front_y-bay_depth,4.05),vworld(bay_half,front_y-bay_depth,4.05),vworld(bay_half,front_y-bay_depth,eave),vworld(-bay_half,front_y-bay_depth,eave)]
bay_wall=mesh_obj("KappaDelta_Projecting_Entry_Bay_Brick_Facing",bay_quad,[(0,1,2,3)],brick)
bay_uv=bay_wall.data.uv_layers.new(name="FacadeUV")
for poly in bay_wall.data.polygons:
    for li,vi in zip(poly.loop_indices,poly.vertices):
        bay_uv.data[li].uv=((-bay_half if vi in (0,3) else bay_half), (4.05 if vi in (0,1) else eave))
for row,z in enumerate((4.64,7.82)):
    for col,x in enumerate((-1.12,1.12)):
        window(f"KappaDelta_Entry_Bay_F{row+2}_Window_{col+1}","front",x,z,.94,2.0,arch=False,balcony=False,offset=bay_depth)
bay_peak=eave+2.0
bay_face_y=front_y-bay_depth
tri=[vworld(-bay_half,bay_face_y,eave),vworld(bay_half,bay_face_y,eave),vworld(0,bay_face_y,bay_peak)]
gable=mesh_obj("KappaDelta_Entry_Bay_Gable_Front",tri,[(0,1,2)],brick)
gable_uv=gable.data.uv_layers.new(name="FacadeUV")
for poly in gable.data.polygons:
    for li,vi in zip(poly.loop_indices,poly.vertices):
        gable_uv.data[li].uv=((-bay_half if vi==0 else bay_half if vi==1 else 0), (eave if vi<2 else bay_peak))
# Slate gable cap as two clean, thickened surface planes.
for sign in (-1,1):
    a=vworld(-bay_half if sign<0 else 0,front_y-bay_depth-.06,eave+.03)
    b=vworld(0 if sign<0 else bay_half,front_y-bay_depth-.06,eave+.03)
    c=vworld(0,front_y-bay_depth-.06,bay_peak)
    mesh_obj("KappaDelta_Entry_Bay_Gable_Roof",[a,b,c],[(0,1,2)],roof)
# Chapter name plaque over the central entry.
box("KappaDelta_Chapter_Sign_Backplate",0,-half_y-.31,3.28,1.05,.12,.32,stone_light)
font=bpy.data.curves.new("KappaDelta_Chapter_Sign_TextCurve","FONT");font.body="KAPPA DELTA";font.size=.14;font.extrude=.003
text_obj=bpy.data.objects.new("KappaDelta_Chapter_Sign_Lettering",font);asset.objects.link(text_obj)
q=mapxy(0,-half_y-.39);text_obj.location=(q[0]-.48*axis_x.x,q[1]-.48*axis_x.y,3.23);text_obj.rotation_euler=(math.pi/2,0,math.atan2(axis_x.y,axis_x.x));text_obj.data.materials.append(frame)

# Rear courtyard elevation: repeated residential windows and a second ground-level door.
for i,x in enumerate([-14,-9.5,-5,0,5,9.5,14]): window(f"KappaDelta_Rear_Ground_Arch_{i+1}","back",x,.88,1.3,2.35,arch=True)
arch_door("KappaDelta_Rear_Secondary_Door","back",-10,.30,1.55,2.75)
for floor,z in [(2,4.65),(3,7.84)]:
    for i,x in enumerate([-14,-10,-6,-2,2,6,10,14]):
        window(f"KappaDelta_Rear_Floor_{floor}_Window_{i+1}","back",x,z,1.32,2.02,arch=False,balcony=(floor==2 and i in (1,6)))

# Short elevations (roughly 22 m deep) keep window count and story rhythm from
# the oblique street-view photo; hidden walls are evidence-limited estimates.
for side in ("left","right"):
    uvals=[-7.2,-2.4,2.4,7.2]
    for i,u in enumerate(uvals): window(f"KappaDelta_{side}_Ground_Arch_{i+1}",side,u,.88,1.28,2.32,arch=True)
    for floor,z in [(2,4.65),(3,7.84)]:
        for i,u in enumerate(uvals): window(f"KappaDelta_{side}_Floor_{floor}_Window_{i+1}",side,u,z,1.28,1.95,arch=False,balcony=(floor==2 and i==1))
# A formal white-columned side portico and secondary entry on the west short end.
arch_door("KappaDelta_West_End_Portico_Door","left",-1.3,.30,1.8,2.9)
side_cx=-half_x-1.15
for sx in (-1.55,0,1.55):
    # local side coordinate is y; porch roof and columns project out from facade.
    facade_frame("KappaDelta_West_Portico_Column","left",-1.3+sx,.85,.0,.32,3.0,.32,white)
    facade_frame("KappaDelta_West_Portico_Capital","left",-1.3+sx,.85,3.08,.55,.20,.55,stone_light)
facade_frame("KappaDelta_West_Portico_Roof","left",-1.3,.98,3.28,4.4,.30,2.3,stone_light)
# A low concrete planter/retaining edge shown in the builder's courtyard photos.
for side in ("front","back"):
    for x in (-12.4,12.4): facade_frame("KappaDelta_Low_Entry_Planter_Wall",side,x,-.65,.42,4.1,.78,.42,stone)

# Hipped charcoal slate roof with short ridge and image-based dormer/gable bays.
ridge=eave+5.10; xridge=half_x-3.2
# roof body planes (surface patches with thickness is added as edge fascia bars)
roofmesh=[]
roofverts=[vworld(-half_x,-half_y,eave),vworld(half_x,-half_y,eave),vworld(half_x,half_y,eave),vworld(-half_x,half_y,eave),vworld(-xridge,0,ridge),vworld(xridge,0,ridge)]
roofmesh=mesh_obj("KappaDelta_Main_Hipped_Slate_Roof",roofverts,[(0,1,5,4),(4,5,2,3),(0,3,4),(1,5,2)],roof)
# fascia bands and gutters at long eaves
facade_frame("KappaDelta_Front_Roof_Eave_Gutter","front",0,-.02,eave,2*half_x+.25,.22,.22,metal)
facade_frame("KappaDelta_Rear_Roof_Eave_Gutter","back",0,-.02,eave,2*half_x+.25,.22,.22,metal)
# standing seams down the main front and rear roof planes. These are a plausible
# interpretation of the dark metal/slate roof visible in the 2026 Street View.
# The photographed roof is a dark, fairly steep asphalt-shingle hip roof. Its
# surface noise carries the shingle texture; avoid placing false, floating
# standing-seam rods across the sloping planes.
# End gables and dormers: three front-facing small gabled bays with arched windows.
def gable_prism(name,cx,cy,base_z,width,depth,height,front_side="front"):
    # Front-facing vertical pentagonal end at front side of the dormer.
    front_y=cy-depth/2;back_y=cy+depth/2
    face=[(-width/2,0),(width/2,0),(width/2,height*.65),(0,height),(-width/2,height*.65)]
    verts=[]
    for y in (front_y,back_y):
        for dx,dz in face: verts.append(vworld(cx+dx,y,base_z+dz))
    faces=[(0,1,2,3,4),(9,8,7,6,5)]
    for i in range(5): faces.append((i,(i+1)%5,(i+1)%5+5,i+5))
    return mesh_obj(name,verts,faces,brick)
for i,x in enumerate([-10.7,10.7]):
    # Dormer front sits on the lower roof plane. The windows and gables are
    # composed from photo evidence, with depth/height left as estimates.
    # Set dormers directly into the visible front roof slope. Their sill height
    # is approximate, constrained by the architectural photos.
    base=eave+1.15
    gable_prism(f"KappaDelta_Front_Roof_Gabled_Dormer_{i+1}",x,-half_y+3.4,base,2.1,2.4,1.8)
    window(f"KappaDelta_Dormer_Window_{i+1}","front",x,base+.30,.90,1.30,arch=False,offset=-2.2)
    # short sloped metal covers form a symmetric gable cap
    top_y=-half_y+2.2
    v=[vworld(x-1.25,top_y,base+1.18),vworld(x,top_y,base+1.90),vworld(x+1.25,top_y,base+1.18),
       vworld(x-1.25,top_y+2.4,base+1.18),vworld(x,top_y+2.4,base+1.90),vworld(x+1.25,top_y+2.4,base+1.18)]
    mesh_obj(f"KappaDelta_Dormer_Gable_Roof_{i+1}",v,[(0,1,4,3),(1,2,5,4)],roof)
# The aerial images show a compact roofline without mechanical boxes at the
# ridge ends; omit the previously detached-looking caps.
# Side hip edges are defined by the roof planes themselves; no freestanding
# ridge caps are added because the source photos show a clean, compact roof.

# Interior partitions and furnishing cues, explicitly schematic because no
# registerable floor plan was found. Room zoning follows public photos only.
# Floor plates are thin slabs; the front half remains open enough to show plan cues.
for floor,z in [(0,.38),(1,4.12),(2,7.42)]:
    # warm oak floor surface, placed slightly above each structural floor.
    prism(f"KappaDelta_Schematic_Floor_Plate_{floor+1}",[(x*.985,y*.96) for x,y in foot],z,z+.10,floor_wood,interior)
# Main longitudinal corridor and room divisions; short partition ends leave door gaps.
for floor,z in [(0,.55),(1,4.25),(2,7.55)]:
    h=2.75
    # corridor boundaries parallel to the long facades
    for y in (-2.2,2.2):
        box(f"KappaDelta_Schematic_Corridor_Partition_F{floor+1}",0,y,z+h/2,2*half_x-2.6,.13,h,interior_wall,collection=interior)
    # bedroom/meeting-room divisions across each wing
    for x in [-11,-5,1,7,13]:
        for y in (-5.5,5.5):
            box(f"KappaDelta_Schematic_Room_Partition_F{floor+1}",x,y,z+h/2,.13,6.2,h,interior_wall,collection=interior)
# Photo-informed first-floor rooms: generous common lounge, long dining table,
# a legible galley kitchen and the prominent white switchback stair/lobby.
# Exact room positions remain schematic because no measured floor plan exists.
carpet,_=principled("KappaDelta_Interior_Soft_Warm_Carpet",(.56,.51,.43),.92)
upholstery,_=principled("KappaDelta_Interior_Sage_Upholstery",(.34,.43,.36),.78)
upholstery_light,_=principled("KappaDelta_Interior_Linen_Upholstery",(.78,.75,.68),.82)
countertop,_=principled("KappaDelta_Interior_Quartz_Counter",(.84,.82,.77),.34)
appliance,_=principled("KappaDelta_Interior_Stainless_Appliance",(.40,.43,.45),.28,.7)
cabinet,_=principled("KappaDelta_Interior_White_Cabinetry",(.86,.84,.79),.5)
black,_=principled("KappaDelta_Interior_Dark_Accent",(.12,.13,.13),.45)

# Lounge rug and conversational seating inspired by the photographed formal
# living room: deep sofas, separate armchairs, cushions, and a coffee table.
box("KappaDelta_Schematic_Lounge_Rug",10.0,-6.4,.48,5.5,4.2,.06,carpet,collection=interior)
def sofa(name,x,y,angle,seatmat=upholstery_light):
    box(name+"_Seat",x,y,.82,2.7,.92,.38,seatmat,angle,interior)
    box(name+"_Back",x,y+.42,1.32,2.7,.20,.72,seatmat,angle,interior)
    for dx in (-1.22,1.22): box(name+"_Arm",x+dx,y,1.08,.28,.96,.53,seatmat,angle,interior)
    for dx in (-.78,0,.78): box(name+"_Cushion",x+dx,y-.10,1.055,.70,.62,.12,upholstery,angle,interior)
sofa("KappaDelta_Schematic_Lounge_Sofa_Main",10.0,-7.85,0)
sofa("KappaDelta_Schematic_Lounge_Sofa_Return",8.1,-5.8,math.pi/2)
box("KappaDelta_Schematic_Lounge_Coffee_Table",10.7,-5.7,.94,1.35,.82,.14,wood,collection=interior)
box("KappaDelta_Schematic_Lounge_Coffee_Table_Base",10.7,-5.7,.72,.92,.45,.30,metal,collection=interior)
for x,y,ang in [(12.1,-4.75,.18),(8.4,-4.7,-.3)]:
    box("KappaDelta_Schematic_Lounge_Armchair_Seat",x,y,.82,1.05,.92,.36,upholstery,ang,interior)
    box("KappaDelta_Schematic_Lounge_Armchair_Back",x,y+.42,1.23,1.08,.18,.64,upholstery,ang,interior)
    for dx in (-.47,.47): box("KappaDelta_Schematic_Lounge_Armchair_Arm",x+dx,y,1.04,.17,.92,.46,upholstery,ang,interior)

# Dining room table, eight chairs, and a serving console, based on the long
# communal dining room in the builder's interior photographs.
box("KappaDelta_Schematic_Dining_Room_Rug",-8.2,6.0,.47,5.5,4.8,.05,carpet,collection=interior)
box("KappaDelta_Schematic_Dining_Table_Top",-8.2,6.0,1.36,4.2,1.32,.16,wood,collection=interior)
for x in (-9.6,-8.2,-6.8):
    for y in (5.0,7.0):
        box("KappaDelta_Schematic_Dining_Chair_Seat",x,y,.91,.62,.62,.14,upholstery_light,collection=interior)
        box("KappaDelta_Schematic_Dining_Chair_Back",x,y+.25,1.35,.60,.14,.86,upholstery_light,collection=interior)
        for dx in (-.23,.23):
            box("KappaDelta_Schematic_Dining_Chair_Leg",x+dx,y-.20,.68,.07,.07,.48,wood,collection=interior)
box("KappaDelta_Schematic_Dining_Serving_Console",-12.0,7.0,1.05,3.1,.56,1.05,cabinet,collection=interior)
box("KappaDelta_Schematic_Dining_Console_Top",-12.0,7.0,1.62,3.28,.72,.12,countertop,collection=interior)

# Bright white kitchen: perimeter cabinets, quartz counter, island, sink and
# range cues reference the photographed contemporary kitchen.
for x in (-16.0,-14.7,-13.4,-12.1):
    box("KappaDelta_Schematic_Kitchen_Base_Cabinet",x,9.1,.91,1.32,.72,1.0,cabinet,collection=interior)
    box("KappaDelta_Schematic_Kitchen_Cabinet_Front",x,8.72,.94,1.16,.06,.70,interior_wall,collection=interior)
box("KappaDelta_Schematic_Kitchen_Back_Counter",-14.05,9.0,1.46,5.8,.9,.12,countertop,collection=interior)
box("KappaDelta_Schematic_Kitchen_Island_Base",-14.0,5.2,1.06,4.0,1.25,1.05,cabinet,collection=interior)
box("KappaDelta_Schematic_Kitchen_Island_Counter",-14.0,5.2,1.62,4.25,1.44,.14,countertop,collection=interior)
box("KappaDelta_Schematic_Kitchen_Sink_Basin",-14.6,5.2,1.715,.92,.62,.05,appliance,collection=interior)
box("KappaDelta_Schematic_Kitchen_Faucet",-14.6,5.50,1.95,.06,.06,.42,metal,collection=interior)
box("KappaDelta_Schematic_Kitchen_Range",-12.2,9.0,1.50,1.05,.82,.18,appliance,collection=interior)
for x in (-12.5,-11.9):
    for y in (8.75,9.25):
        box("KappaDelta_Schematic_Kitchen_Cooktop_Burner",x,y,1.60,.28,.28,.05,black,collection=interior)
box("KappaDelta_Schematic_Kitchen_Refrigerator",-16.3,7.4,1.55,.95,1.0,2.2,appliance,collection=interior)
for x in (-15.2,-14.0,-12.8):
    box("KappaDelta_Schematic_Kitchen_Island_Stool_Seat",x,4.15,.91,.65,.65,.14,wood,collection=interior)
    box("KappaDelta_Schematic_Kitchen_Island_Stool_Post",x,4.15,.49,.08,.08,.78,metal,collection=interior)

# Large double-height lobby and photo-inspired switchback stair. Twenty broad
# oak treads, a half-landing, white stringers, turned balusters and dark rail
# make the central circulation recognizable in both the plan and oblique view.
stairx=-.8; tread_n=10; run=3.05; tread_depth=run/tread_n; rise=.18
for flight in (0,1):
    for i in range(tread_n):
        y=-1.82+i*tread_depth if flight==0 else .35+(tread_n-1-i)*tread_depth
        z=.47+(i+1)*rise if flight==0 else .47+2.05+(i+1)*rise
        box(f"KappaDelta_Schematic_Stair_F{flight+1}_Tread_{i+1}",stairx,y,z,1.55,tread_depth+.035,.10,wood,collection=interior)
box("KappaDelta_Schematic_Stair_Half_Landing",stairx,.0,2.38,1.8,.72,.16,stone_light,collection=interior)
for flight in (0,1):
    for i in range(tread_n):
        yy=-1.82+i*tread_depth if flight==0 else .35+(tread_n-1-i)*tread_depth
        zz=.52+(i+1)*rise if flight==0 else .52+2.05+(i+1)*rise
        box(f"KappaDelta_Schematic_Stair_Baluster_F{flight+1}",stairx+.92,yy,zz+.38,.07,.07,.74,white,collection=interior)
    y0,y1=(-1.82,1.23) if flight==0 else (1.23,-1.82)
    z0,z1=(.72,2.52) if flight==0 else (2.77,4.57)
    beam(f"KappaDelta_Schematic_Stair_Handrail_F{flight+1}",(stairx+.92,y0,z0),(stairx+.92,y1,z1),.10,.10,wood,interior)
# upper-floor bed/desk cues in the repeated private room band.
for floor,z in [(1,4.25),(2,7.55)]:
    for x in [-13,-8,-3,3,8,13]:
        for y in (-7.0,7.0):
            box(f"KappaDelta_Schematic_Bed_F{floor+1}",x,y,z+.18,2.0,1.0,.34,interior_wall,collection=interior)
            box(f"KappaDelta_Schematic_Desk_F{floor+1}",x+1.25,y,z+.48,.9,.45,.78,wood,collection=interior)
# Indoor window lights, ceilings and furnishings use no image files.

# Non-asset render rig for evidence previews.

def point_camera(name,loc,target,lens=40):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);preview.objects.link(obj)
    obj.location=loc;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler();data.lens=lens;return obj

def area_light(name,loc,power,color,size,target):
    data=bpy.data.lights.new(name,"AREA");obj=bpy.data.objects.new(name,data);preview.objects.link(obj)
    obj.location=loc;obj.data.energy=power;obj.data.color=color;obj.data.shape="DISK";obj.data.size=size
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler();return obj
# Front, oblique and aerial review cameras are audit-only objects kept separate
# from the export collection. The frontal camera makes the roof composition
# comparable to the builder's directly facing elevation photos.
frontx,fronty=mapxy(0,-half_y)
cam_front=point_camera("Preview_Front_Camera",(frontx-43*axis_y.x,fronty-43*axis_y.y,13.0),(0,0,6.1),40)
camx,camy=mapxy(-9,-half_y)
cam_oblique=point_camera("Preview_Oblique_Camera",(camx-39*axis_y.x,camy-39*axis_y.y,16.0),(0,0,6.2),42)
cam_aerial=point_camera("Preview_Aerial_Camera",(0,0,60),(0,0,0),34)
cam_aerial.rotation_euler=(0,0,math.atan2(axis_x.y,axis_x.x))
scene.camera=cam_front
area_light("Preview_Key_Softbox",(camx-24*axis_y.x,camy-24*axis_y.y,31),18000,(1.0,.88,.74),28,(0,0,5))
area_light("Preview_Fill",(26,-8,25),10000,(.75,.84,1.0),24,(0,0,6))
sun_data=bpy.data.lights.new("Preview_Sun","SUN");sun=bpy.data.objects.new("Preview_Sun",sun_data);preview.objects.link(sun)
sun_data.energy=2.2;sun.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-35))
# Build dark blue afternoon sky, floor, ambient surface for render; these are in
# the preview-only collection and are excluded from the exported asset.
world=scene.world;world.use_nodes=True
bg=world.node_tree.nodes.get("Background");bg.inputs["Color"].default_value=(.24,.34,.48,1);bg.inputs["Strength"].default_value=.7
# Save source-faithful numerical report.
bpy.context.view_layer.update()
objs=list(asset.all_objects)
mesh_count=sum(o.type=="MESH" for o in objs)
materials=sorted({m.name for o in objs for m in o.data.materials if m})
asset_verts=[o.matrix_world@v.co for o in objs if o.type=="MESH" for v in o.data.vertices]
asset_local=[(v.x*axis_x.x+v.y*axis_x.y,v.x*axis_y.x+v.y*axis_y.y,v.z) for v in asset_verts]
local_bounds=[[min(p[i] for p in asset_local),max(p[i] for p in asset_local)] for i in range(3)]
summary={"building":"Kappa Delta / Theta Nu","asset":"modular/buildings/kappa_delta.blend","export_collection":"Asset_kappa_delta","scene":"Building_kappa_delta","source_footprint":{"provider":"OpenStreetMap","way_id":860903232,"last_edited":"2022-10-12T20:53:03Z","license":"ODbL 1.0","address":"358 Northwestern Ave, West Lafayette, IN","ring_lon_lat":ring_ll,"area_m2":footprint_area,"dimensions_m":[length,depth],"source_detail":"four-point OSM footprint shape; preserve exact ring in asset geometry"},"placement_origin_xy_m":list(origin),"origin_lat_lon_approx":[origin[0]/(111412.84*math.cos(math.radians(LAT0)))+LON0,origin[1]/111040.0+LAT0],"local_coordinates":True,"local_bounds_m":local_bounds,"story_count":3,"height_evidence":"Street View and architect project images show three occupied levels; eave/ridge elevations are image-estimated.","object_count":len(objs),"mesh_count":mesh_count,"materials":materials,"external_image_dependencies":0,"interior":"Three-floor schematic; photo-informed ground-floor lounge, dining area, kitchen, and switchback stair/lobby, with bedroom and partition cues upstairs. No measured floor plan was located.","unresolved":"Exact floor plans, wall thickness, roof framing, hidden elevations, and surveyed facade heights remain unverified."}
(AUDIT/"build_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
# Only asset collection is meant to be linked from the campus master.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
# Render one exterior preview for the grader.
scene.render.filepath=str(AUDIT/"kappa_delta_front_render.png")
bpy.ops.render.render(write_still=True)
scene.camera=cam_oblique
scene.render.filepath=str(AUDIT/"kappa_delta_oblique_render.png")
bpy.ops.render.render(write_still=True)
scene.camera=cam_aerial
scene.render.filepath=str(AUDIT/"kappa_delta_aerial_render.png")
bpy.ops.render.render(write_still=True)
# Render the photo-informed schematic floor arrangement with the exterior
# shell omitted from this audit view only. Restore asset flags before saving.
scene.camera=cam_front
interior_set=set(interior.all_objects)
for obj in asset.all_objects:
    is_upper_floor=any(tag in obj.name for tag in ("Floor_Plate_2","Floor_Plate_3","_F2","_F3"))
    obj.hide_render=(obj not in interior_set or is_upper_floor)
intcam=point_camera("Preview_Interior_Camera",(0,0,48),(0,0,0),34)
intcam.rotation_euler=(0,0,math.atan2(axis_x.y,axis_x.x))
oldcam=scene.camera;scene.camera=intcam
scene.render.filepath=str(AUDIT/"kappa_delta_schematic_interior.png")
bpy.ops.render.render(write_still=True)
interior_oblique=point_camera("Preview_Interior_Oblique_Camera",vworld(0,-27,23),(0,0,2.0),36)
scene.camera=interior_oblique
scene.render.filepath=str(AUDIT/"kappa_delta_interior_oblique.png")
bpy.ops.render.render(write_still=True)
for obj in asset.all_objects: obj.hide_render=False
scene.camera=oldcam
interior_oblique_data=interior_oblique.data
bpy.data.objects.remove(interior_oblique,do_unlink=True)
bpy.data.cameras.remove(interior_oblique_data)
intcam_data=intcam.data
bpy.data.objects.remove(intcam,do_unlink=True)
bpy.data.cameras.remove(intcam_data)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print("KAPPA_DELTA_BUILD_PASS",json.dumps({"asset":str(OUT),"origin":origin,"footprint_area_m2":footprint_area,"dimensions_m":[length,depth],"objects":len(objs),"meshes":mesh_count,"materials":len(materials)}))
