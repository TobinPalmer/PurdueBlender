"""Build a detailed, evidence-led Wetherill Laboratory asset in its own library."""
import bpy, json, math, shutil
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
MASSING_ID = "massing_r_b_wetherill_laboratory_of_chemistry_wthr_1577024"
ASSET_ID = "wetherill_laboratory_of_chemistry"
SOURCE_FILE = ROOT / "modular" / "buildings" / f"{MASSING_ID}.blend"
ASSET_FILE = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
MASSING_COLLECTION_NAME = f"Asset_{MASSING_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
if not (AUDIT / "massing_before.blend").exists():
    shutil.copy2(SOURCE_FILE, AUDIT / "massing_before.blend")

bpy.ops.wm.open_mainfile(filepath=str(SOURCE_FILE))
sc = bpy.context.scene
sc.name = SCENE_NAME
asset = bpy.data.collections.get(MASSING_COLLECTION_NAME)
if asset is None:
    raise RuntimeError(f"Expected source collection {MASSING_COLLECTION_NAME}")
asset.name=COLLECTION_NAME
for c in list(bpy.data.collections):
    if c != asset:
        bpy.data.collections.remove(c)
for o in list(asset.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# Exact official WTHR ring and bounds are read from the preserved Purdue GIS
# conversion snapshot. The asset frame is centered on the structural envelope.
refdoc=json.loads((ROOT/"audit"/"official_building_references.json").read_text(encoding="utf-8"))
wthr_ref=next(r for r in refdoc["buildings"] if r["fid"]==257 and r["code"]=="WTHR")
minx,miny,maxx,maxy=wthr_ref["aabb_xy_m"]
anchor=Vector(((minx+maxx)/2,(miny+maxy)/2,0.0))
campus_outline=[tuple(p) for p in wthr_ref["rings_xy_m"][0][:-1]]
outline = [Vector((x-anchor.x, y-anchor.y, 0.0)) for x,y in campus_outline]
outline_center = sum((p for p in outline), Vector()) / len(outline)

def mat_principled(name, color, rough=0.72, metallic=0.0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    return m

brick = mat_principled("WTHR | red-brown running bond brick", (0.30,0.075,0.046), .84)
stone = mat_principled("WTHR | warm Indiana limestone", (0.50,0.43,0.33), .82)
stone_light = mat_principled("WTHR | carved limestone highlights", (0.59,0.51,0.39), .75)
engraved = mat_principled("WTHR | dark incised lettering", (0.018,0.014,0.009), .86)
roof = mat_principled("WTHR | weathered verdigris copper", (0.055,0.19,0.16), .38, .66)
roof_dark = mat_principled("WTHR | dark slate roof membrane", (0.075,0.085,0.083), .75)
frame = mat_principled("WTHR | dark bronze painted window frames", (0.12,0.13,0.12), .32, .55)
glass = mat_principled("WTHR | blue-grey reflective glazing", (0.095,0.18,0.23), .16, .36)
glass.node_tree.nodes.get("Principled BSDF").inputs["Metallic"].default_value = .45
glass.node_tree.nodes.get("Principled BSDF").inputs["IOR"].default_value = 1.46
display_screen = mat_principled("Interior | deep teal display glass", (0.012,0.055,0.062), .32, .08)
display_ink = mat_principled("Interior | warm display lettering", (0.92,0.78,0.48), .52)
floor_mat = mat_principled("Interior | warm terrazzo flooring", (0.34,0.32,0.27), .48)
ceiling_mat = mat_principled("Interior | warm white plaster", (0.76,0.74,0.67), .86)
partition_mat = mat_principled("Interior | pale painted laboratory partitions", (0.73,0.75,0.72), .8)
lab_top = mat_principled("Interior | laboratory phenolic worktops", (0.37,0.39,0.38), .4)
cabinet = mat_principled("Interior | laboratory casework", (0.55,0.57,0.53), .62)
steel = mat_principled("Interior | brushed stainless steel", (0.42,0.46,0.46), .28, .72)
wood = mat_principled("Interior | study tables, light oak", (0.47,0.29,0.14), .55)
green = mat_principled("Interior | Purdue accent green", (0.30,0.48,0.09), .56)
white = mat_principled("Interior | white ceramic", (0.80,0.81,0.77), .34)
led_cyan = mat_principled("Interior | molecular LED cyan", (0.02,0.58,0.68), .22)
led_cyan.node_tree.nodes.get("Principled BSDF").inputs["Emission Color"].default_value = (0.01,0.48,0.75,1)
led_cyan.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 1.4
led_green = mat_principled("Interior | molecular LED green", (0.12,0.55,0.32), .2)
led_green.node_tree.nodes.get("Principled BSDF").inputs["Emission Color"].default_value = (0.02,0.52,0.18,1)
led_green.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 1.1
led_red = mat_principled("Interior | molecular LED coral", (0.68,0.18,0.28), .24)
led_red.node_tree.nodes.get("Principled BSDF").inputs["Emission Color"].default_value = (0.75,0.035,0.12,1)
led_red.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 1.05

# Procedural brick relief and soft mineral color variation; no external texture files.
nt = brick.node_tree; nodes = nt.nodes; links = nt.links
p = nodes.get("Principled BSDF"); tex = nodes.new("ShaderNodeTexBrick")
tex.inputs["Color1"].default_value = (0.25,0.055,0.032,1)
tex.inputs["Color2"].default_value = (0.14,0.026,0.018,1)
tex.inputs["Mortar"].default_value = (0.25,0.22,0.18,1)
tex.inputs["Scale"].default_value = 1.0; tex.inputs["Mortar Size"].default_value = .035
tex.inputs["Mortar Smooth"].default_value = .008; tex.inputs["Brick Width"].default_value = .31
tex.inputs["Row Height"].default_value = .073
uv = nodes.new("ShaderNodeTexCoord")
def orient_brick_texture(material, along_axis):
    tree=material.node_tree; nd=tree.nodes; lk=tree.links
    texture=next(n for n in nd if n.bl_idname=="ShaderNodeTexBrick")
    coord=next(n for n in nd if n.bl_idname=="ShaderNodeTexCoord")
    for link in list(lk):
        if link.to_node==texture and link.to_socket==texture.inputs["Vector"]: lk.remove(link)
    split=nd.new("ShaderNodeSeparateXYZ"); combine=nd.new("ShaderNodeCombineXYZ")
    lk.new(coord.outputs["Object"],split.inputs["Vector"])
    if along_axis=="x":
        lk.new(split.outputs["X"],combine.inputs["X"]); lk.new(split.outputs["Z"],combine.inputs["Y"]); lk.new(split.outputs["Y"],combine.inputs["Z"])
    else:
        lk.new(split.outputs["Y"],combine.inputs["X"]); lk.new(split.outputs["Z"],combine.inputs["Y"]); lk.new(split.outputs["X"],combine.inputs["Z"])
    lk.new(combine.outputs["Vector"],texture.inputs["Vector"])
orient_brick_texture(brick,"x")
brick_y=brick.copy(); brick_y.name="WTHR | red-brown running bond brick, north-south elevations"
orient_brick_texture(brick_y,"y")
for link in list(links):
    if link.to_node==p and link.to_socket==p.inputs["Base Color"]: links.remove(link)
noise=nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value=4.5; noise.inputs["Detail"].default_value=2.0; noise.inputs["Roughness"].default_value=.7
links.new(uv.outputs["Object"],noise.inputs["Vector"])
ramp=nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.20; ramp.color_ramp.elements[0].color=(.055,.010,.006,1)
ramp.color_ramp.elements[1].position=.80; ramp.color_ramp.elements[1].color=(.12,.024,.012,1)
links.new(noise.outputs["Fac"],ramp.inputs["Fac"]); links.new(ramp.outputs["Color"],p.inputs["Base Color"])
bump = nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .18; bump.inputs["Distance"].default_value = .018
links.new(tex.outputs["Color"], bump.inputs["Height"]); links.new(bump.outputs["Normal"],p.inputs["Normal"])

def batch_object(name, material):
    return {"name":name,"material":material,"verts":[],"faces":[]}
batches = {}
def add_box(name, material, center, size, axes=None):
    key=(name,material.name)
    b=batches.setdefault(key,batch_object(name,material))
    c=Vector(center); sx,sy,sz=size
    if axes is None: axes=(Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
    U,N,Z=[Vector(a).normalized() for a in axes]
    pts=[]
    for iz in (-1,1):
        for iy in (-1,1):
            for ix in (-1,1):
                pts.append(c + U*(ix*sx/2) + N*(iy*sy/2) + Z*(iz*sz/2))
    base=len(b["verts"]); b["verts"].extend(tuple(v) for v in pts)
    # outward winding for the six box faces
    b["faces"].extend([tuple(base+i for i in f) for f in ((0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3))])

def add_poly_slab(name,z0,thick,material):
    pts=[(p.x,p.y,z0) for p in outline]; top=[(p.x,p.y,z0+thick) for p in outline]
    vecs=[Vector((p.x,p.y)) for p in outline]
    tris=tessellate_polygon([vecs])
    verts=pts+top; n=len(pts); faces=[]
    for tri in tris:
        ids=[int(i) for i in tri]
        faces.append(tuple(ids)); faces.append(tuple(n+i for i in reversed(ids)))
    for i in range(n): j=(i+1)%n; faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    ob=bpy.data.objects.new(name,mesh); asset.objects.link(ob)
    return ob

def basis_for_edge(a,b):
    u=(b-a).normalized(); mid=(a+b)*.5
    v=Vector((mid.x-outline_center.x,mid.y-outline_center.y,0)).normalized()
    return u,v,Vector((0,0,1))

def add_perimeter_wall(name,a,b,outward,depth,height,material):
    """Closed wall segment whose outside face is exactly the GIS polygon edge."""
    back_a=a-outward*depth; back_b=b-outward*depth
    verts=[(a.x,a.y,0),(b.x,b.y,0),(b.x,b.y,height),(a.x,a.y,height),
           (back_a.x,back_a.y,0),(back_b.x,back_b.y,0),
           (back_b.x,back_b.y,height),(back_a.x,back_a.y,height)]
    faces=[(0,1,2,3),(4,7,6,5),(3,2,6,7),(0,4,5,1),(0,3,7,4),(1,5,6,2)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    ob=bpy.data.objects.new(name,mesh); asset.objects.link(ob)
    return ob

story_h=3.2; total_h=16.0; wall_d=.70
edge_info=[]
# Continuous 5-story structural envelope on the saved GIS perimeter.
for ei,a in enumerate(outline):
    b=outline[(ei+1)%len(outline)]; L=(b-a).length
    u,n,zax=basis_for_edge(a,b); mid=(a+b)*.5
    edge_info.append((a,b,L,u,n,mid))
    # Main wall volume, with differentiated limestone base cladding and brick upper floors.
    wall_brick=brick if abs(u.x)>=abs(u.y) else brick_y
    add_perimeter_wall(f"WTHR_PerimeterWall_{ei+1:02d}",a,b,n,wall_d,total_h,wall_brick)
    add_box(f"WTHR_LimestoneBase_{ei+1:02d}", stone, (mid.x+n.x*.10,mid.y+n.y*.10,.62),(L,wall_d*.30,1.24),(u,n,zax))
    # Limestone water table and floor belt courses.
    for level in (1.2,3.18,6.38,9.58,12.78,15.72):
        add_box(f"WTHR_StringCourse_{ei+1:02d}",stone_light,(mid.x+n.x*.10,mid.y+n.y*.10,level),(L+.18,.18,.18),(u,n,zax))
    # Windows repeat in five measured-height-estimate storeys. Spacing scales by frontage.
    nwin=max(1,int(L/4.25)); spacing=L/(nwin+1)
    for k in range(1,nwin+1):
        pos=a+u*(spacing*k)
        w=min(2.05,spacing*.58); h=1.78
        for story in range(5):
            cz=.58+story*story_h+1.55
            # Broad limestone picture frame and deeply set glazing.
            for dx in (-w/2-.11,w/2+.11):
                add_box(f"WTHR_WindowStoneJamb_{ei+1:02d}",stone_light,(pos.x+u.x*dx+n.x*.10,pos.y+u.y*dx+n.y*.10,cz),(.18,.20,h+.30),(u,n,zax))
            for dz in (-h/2-.11,h/2+.11):
                add_box(f"WTHR_WindowStoneHeadSill_{ei+1:02d}",stone_light,(pos.x+n.x*.10,pos.y+n.y*.10,cz+dz),(w+.40,.20,.18),(u,n,zax))
            add_box(f"WTHR_WindowGlass_{ei+1:02d}",glass,(pos.x+n.x*.05,pos.y+n.y*.05,cz),(w,.055,h),(u,n,zax))
            # Dark metal sash and a classic 3-by-2 grid.
            for dx in (-w/2,w/2):
                add_box(f"WTHR_WindowSash_{ei+1:02d}",frame,(pos.x+u.x*dx+n.x*.10,pos.y+u.y*dx+n.y*.10,cz),(.055,.08,h),(u,n,zax))
            for dz in (-h/2,h/2):
                add_box(f"WTHR_WindowSash_{ei+1:02d}",frame,(pos.x+n.x*.10,pos.y+n.y*.10,cz+dz),(w,.08,.055),(u,n,zax))
            add_box(f"WTHR_WindowMullion_{ei+1:02d}",frame,(pos.x+n.x*.10,pos.y+n.y*.10,cz),(0.055,.085,h),(u,n,zax))
            for dz in (-h/6,h/6):
                add_box(f"WTHR_WindowMullion_{ei+1:02d}",frame,(pos.x+n.x*.10,pos.y+n.y*.10,cz+dz),(w,.085,.045),(u,n,zax))
    # Stone quoins and pilasters emphasize the classical bay rhythm.
    npiers=max(1,int(L/13.5))
    for k in range(npiers+1):
        pos=a+u*(L*k/npiers)
        add_box(f"WTHR_StonePilaster_{ei+1:02d}",stone_light,(pos.x+n.x*.18,pos.y+n.y*.18,total_h/2),(.78,.36,total_h),(u,n,zax))
        add_box(f"WTHR_PilasterBase_{ei+1:02d}",stone_light,(pos.x+n.x*.22,pos.y+n.y*.22,.72),(1.05,.46,1.36),(u,n,zax))
        for level in (3.12,6.32,9.52,12.72,15.90):
            add_box(f"WTHR_PilasterCapital_{ei+1:02d}",stone_light,(pos.x+n.x*.27,pos.y+n.y*.27,level),(.98,.48,.28),(u,n,zax))

# Floors, internal corridor partitions, service cores and lab interiors.
for floor in range(5):
    z=floor*story_h
    add_poly_slab(f"WTHR_InteriorFloor_{floor+1}",z+.08,.18,floor_mat)
    # Interior ceiling/soffit strips around typical corridor, warm acoustical finish.
    if floor < 4:
        add_poly_slab(f"WTHR_CeilingSlab_{floor+1}",z+story_h-.12,.12,ceiling_mat)
    # Main north-south corridor walls, deliberately broken by openings.
    for x in (-11.0,11.0):
        for seg in range(4):
            y0=-26+seg*13; yc=y0+5.2
            add_box(f"WTHR_CorridorPartition_F{floor+1}",partition_mat,(x,yc,z+story_h/2),(0.14,10.4,2.85))
    # East-west cross walls divide research suites from the central circulation.
    for y in (-17.0,17.0):
        add_box(f"WTHR_LabSuitePartition_F{floor+1}",partition_mat,(0,y,z+story_h/2),(21.8,.14,2.85))
    # Two stair/service cores, lift doors and landings.
    for x in (-27.0,27.0):
        add_box(f"WTHR_StairCoreWall_F{floor+1}",partition_mat,(x,-2,z+story_h/2),(6.0,.18,2.85))
        add_box(f"WTHR_ElevatorDoor_F{floor+1}",steel,(x,0,z+1.35),(1.15,.06,2.45))
        for step in range(9):
            add_box(f"WTHR_StairTread_F{floor+1}",stone_light,(x-1.8+step*.42,-4.0+step*.50,z+.20+step*.26),(.75,1.0,.13))
    # Repeated laboratory tables and casework in research bays.
    if floor != 1:
        for x in (-23,-16,16,23):
            for y in (-23,-8,8,23):
                add_box(f"WTHR_LabBaseCabinet_F{floor+1}",cabinet,(x,y,z+1.05),(4.4,.78,.78))
                add_box(f"WTHR_LabBenchTop_F{floor+1}",lab_top,(x,y,z+1.48),(4.65,.95,.18))
                # A representative framed chemical hood and glass sash at each bay.
                add_box(f"WTHR_FumeHoodBody_F{floor+1}",white,(x,y+2.1,z+1.45),(2.0,.80,1.95))
                add_box(f"WTHR_FumeHoodSash_F{floor+1}",glass,(x,y+1.68,z+1.60),(1.58,.045,1.35))
                add_box(f"WTHR_FumeHoodSill_F{floor+1}",steel,(x,y+1.63,z+.90),(1.7,.10,.12))
                for q in (-.55,.0,.55):
                    add_box(f"WTHR_FumeHoodMullion_F{floor+1}",frame,(x+q,y+1.61,z+1.62),(.04,.04,1.26))
    # Corridor ceiling lights at regular intervals.
    for y in (-20,-10,0,10,20):
        add_box(f"WTHR_CorridorLight_F{floor+1}",white,(0,y,z+story_h-.25),(2.2,.24,.08))

# Leighty Commons on the second floor outside the WTHR 200 lecture hall: public,
# source-supported room type, furniture and molecular light sculpture.
commons_z=story_h+.08
for x in (-7,-3,3,7):
    add_box("Leighty_Commons_StudyTable",wood,(x,-5,commons_z+.76),(2.5,1.0,.12))
    for lx in (-1.00,1.00):
        for ly in (-.34,.34):
            add_box("Leighty_Commons_TableLeg",steel,(x+lx,-5+ly,commons_z+.38),(.07,.07,.76))
    for sx in (-.78,.78):
        cx=x+sx; cy=-6.0
        add_box("Leighty_Commons_ChairSeat",green,(cx,cy,commons_z+.48),(.60,.58,.12))
        add_box("Leighty_Commons_ChairBack",green,(cx,cy-.25,commons_z+.82),(.60,.12,.62))
        for lx in (-.23,.23):
            for ly in (-.22,.22):
                add_box("Leighty_Commons_ChairLeg",steel,(cx+lx,cy+ly,commons_z+.20),(.055,.055,.40))
for x in (-9,9):
    add_box("Leighty_Commons_CafeCounter",wood,(x,2,commons_z+.62),(3.3,.78,.16))
    for j in range(4):
        add_box("Leighty_Commons_CafeStool",steel,(x-1.15+j*.76,1.12,commons_z+.42),(.48,.48,.82))
    if x > 0:
        add_box("Leighty_Commons_CafeSign",display_screen,(x,1.68,commons_z+1.70),(2.8,.14,.54))
        cafe_label=bpy.data.curves.new(f"Leighty_Commons_CafeLabel_{x}","FONT"); cafe_label.body="LEIGHTY CAFE"; cafe_label.size=.22; cafe_label.align_x='CENTER'; cafe_label.align_y='CENTER'; cafe_label.extrude=.004
        cafe_ob=bpy.data.objects.new(f"Leighty_Commons_CafeLabel_{x}",cafe_label); asset.objects.link(cafe_ob); cafe_ob.visible_shadow=False
        cafe_ob.location=(x,1.59,commons_z+1.70); cafe_ob.rotation_euler=(math.radians(90),0,0); cafe_label.materials.append(display_ink)
# Broad open lounge partition, charging cubby wall and display panels.
for j in range(9):
    cubby_x=-9.5+j*2.375
    add_box("Leighty_Commons_ChargingCubbies",cabinet,(cubby_x,8.0,commons_z+1.0),(2.22,.36,2.0))
    add_box("Leighty_Commons_CubbyDoor",steel,(cubby_x,7.78,commons_z+1.0),(1.95,.08,1.55))
    add_box("Leighty_Commons_CubbyHandle",frame,(cubby_x+.72,7.715,commons_z+1.0),(.085,.035,.18))
    cubby_tag=bpy.data.curves.new(f"Leighty_Commons_CubbyNumber_{j+1}","FONT"); cubby_tag.body=f"{j+1:02d}"; cubby_tag.size=.13; cubby_tag.align_x='CENTER'; cubby_tag.align_y='CENTER'
    tag_ob=bpy.data.objects.new(f"Leighty_Commons_CubbyNumber_{j+1}",cubby_tag); asset.objects.link(tag_ob); tag_ob.visible_shadow=False
    tag_ob.location=(cubby_x-.62,7.705,commons_z+.51); tag_ob.rotation_euler=(math.radians(90),0,0); cubby_tag.materials.append(engraved)
display_content=((-6,"HERBERT C. BROWN","NOBEL 1979"),(0,"EI-ICHI NEGISHI","NOBEL 2010"),(6,"PURDUE CHEMISTRY","RESEARCH & DISCOVERY"))
for x,title,subtitle in display_content:
    add_box("Leighty_Commons_MultimediaDisplay",frame,(x,7.55,commons_z+2.0),(2.5,.16,1.4))
    add_box("Leighty_Commons_DisplayScreen",display_screen,(x,7.43,commons_z+2.0),(2.30,.05,1.20))
    for line_name,line_text,size,zoff in (("Title",title,.22,.16),("Subtitle",subtitle,.16,-.16)):
        display_text=bpy.data.curves.new(f"Leighty_Commons_Display{line_name}_{x}","FONT")
        display_text.body=line_text; display_text.size=size; display_text.align_x='CENTER'; display_text.align_y='CENTER'; display_text.extrude=.004
        display_ob=bpy.data.objects.new(f"Leighty_Commons_Display{line_name}_{x}",display_text); asset.objects.link(display_ob); display_ob.visible_shadow=False
        display_ob.location=(x,7.35,commons_z+2.0+zoff); display_ob.rotation_euler=(math.radians(90),0,0); display_text.materials.append(display_ink)
# Published Commons sculpture is a 20 ft wide caffeine molecule. Build its
# 14 heavy-atom topology from caffeine's fused rings, carbonyls and three methyl
# branches (hydrogens omitted), then scale the full X envelope including LEDs to
# 6.096 m. Geometry is a stylized suspended light sculpture, not a bond-length model.
atom_xy={
    "Methyl_N7":("C",(2.10,1.10)), "N7":("N",(1.30,.80)),
    "C8":("C",(.80,1.50)), "N9":("N",(0.0,1.00)),
    "C4":("C",(0.0,0.0)), "C5":("C",(.90,0.0)),
    "C6":("C",(1.35,-.85)), "O6":("O",(2.10,-.90)),
    "N3":("N",(.90,-1.70)), "C2":("C",(0.0,-1.70)),
    "O2":("O",(-.90,-1.70)), "N1":("N",(-.45,-.85)),
    "Methyl_N1":("C",(-1.30,-1.00)), "Methyl_N3":("C",(1.45,-2.10)),
}
atom_list=list(atom_xy.items())
node_radius={"C":.20,"N":.22,"O":.23}
raw_x=[xy[0] for _,(_,xy) in atom_list]
xlo,xhi=min(raw_x),max(raw_x); xmid=(xlo+xhi)/2
ylo=min(xy[1] for _,(_,xy) in atom_list); yhi=max(xy[1] for _,(_,xy) in atom_list); ymid=(ylo+yhi)/2
mol_scale=(6.096-node_radius["C"]-node_radius["O"])/(xhi-xlo)
mol_nodes={name:( (xy[0]-xmid)*mol_scale,(xy[1]-ymid)*mol_scale,5.67+.10*(xy[1]-ymid)/(yhi-ylo)*2 ) for name,(_,xy) in atom_list}
mol_edges=[
    ("Methyl_N7","N7",1),("N7","C8",1),("C8","N9",2),("N9","C4",1),
    ("C4","C5",2),("C5","N7",1),("C5","C6",1),("C6","N3",1),
    ("N3","C2",1),("C2","N1",1),("N1","C4",1),("C6","O6",2),
    ("C2","O2",2),("N3","Methyl_N3",1),("N1","Methyl_N1",1),
]
for atom_a,atom_b,order in mol_edges:
    a=Vector(mol_nodes[atom_a]); b=Vector(mol_nodes[atom_b]); d=b-a
    for parallel in range(order):
        offset=Vector((0,0,(parallel-(order-1)/2)*.105))
        bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.045,depth=d.length,location=(a+b)*.5+offset)
        ob=bpy.context.object; ob.name="Leighty_Commons_MolecularSculpture_Rod"; ob.rotation_mode='QUATERNION'; ob.rotation_quaternion=Vector((0,0,1)).rotation_difference(d.normalized())
        for c in list(ob.users_collection): c.objects.unlink(ob)
        asset.objects.link(ob); ob.data.materials.append(frame)
for name,(element,_) in atom_list:
    co=mol_nodes[name]
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=node_radius[element],location=co)
    ob=bpy.context.object; ob.name=f"Leighty_Commons_MolecularLED_Node_{name}"; ob.data.materials.append({"C":led_cyan,"N":led_green,"O":led_red}[element]); ob["element"]=element
    for c in list(ob.users_collection): c.objects.unlink(ob)
    asset.objects.link(ob)

# The public source describes the Commons sculpture as suspended. Thin ceiling
# cables are a plausible support interpretation; exact attachment points are unknown.
for cable_x,cable_y in ((-2.55,-.38),(-2.55,.38),(2.55,-.38),(2.55,.38)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.018,depth=.72,location=(cable_x,cable_y,6.04))
    cable=bpy.context.object; cable.name="Leighty_Commons_MolecularSuspensionCable"; cable.visible_shadow=False
    for collection in list(cable.users_collection): collection.objects.unlink(cable)
    asset.objects.link(cable); cable.data.materials.append(steel)

# Main south entrance and institutional stonework. Geometry direction is set by
# the corresponding perimeter normals rather than a geographic guess elsewhere.
south_edges=[e for e in edge_info if e[5].y < -27]
best=max(south_edges,key=lambda e:e[2])
a,b,L,u,n,mid=best
entry_normal=n.copy()
# three doors under a broad limestone portico
entry_center=(a+b)*.5; entry_z=1.68
for dx in (-2.2,0,2.2):
    pos=entry_center+u*dx
    add_box("WTHR_MainEntry_Door",frame,(pos.x+n.x*.10,pos.y+n.y*.10,entry_z),(1.45,.12,2.7),(u,n,zax))
    add_box("WTHR_MainEntry_Glazing",glass,(pos.x+n.x*.18,pos.y+n.y*.18,entry_z),(1.15,.05,2.35),(u,n,zax))
    for side in (-.68,.68):
        add_box("WTHR_MainEntry_LimestoneJamb",stone_light,(pos.x+u.x*side+n.x*.20,pos.y+u.y*side+n.y*.20,entry_z),(0.18,.28,2.95),(u,n,zax))
    add_box("WTHR_MainEntry_Transom",stone_light,(pos.x+n.x*.20,pos.y+n.y*.20,3.10),(1.65,.3,.24),(u,n,zax))
# continuous entrance stair descending from south facade
for i in range(8):
    dist=.45+i*.42; z=.18-i*.09
    add_box("WTHR_MainEntry_LimestoneStep",stone_light,(entry_center.x+n.x*(1.0+dist),entry_center.y+n.y*(1.0+dist),z),(7.4,.90,.16),(u,n,zax))
for side in (-1,1):
    for i in range(8):
        dist=.55+i*.42; z=.42-i*.09
        p0=entry_center+n*(1.0+dist)+u*(side*4.15)
        add_box("WTHR_MainEntry_RailingPost",steel,(p0.x,p0.y,z+.34),(.10,.10,.68))
    p0=entry_center+n*2.9+u*(side*4.15)
    add_box("WTHR_MainEntry_Railing",steel,(p0.x,p0.y,.80),(.07,4.8,.08),(u,n,zax))
# Stone frieze, crest panel and main engraved-name text facing outward (-Y).
for dx in (-7.3,-4.0,4.0,7.3):
    pp=entry_center+u*dx+n*.28
    add_box("WTHR_MainEntry_GrandPier",stone_light,(pp.x,pp.y,5.15),(.70,.42,7.1),(u,n,zax))
    add_box("WTHR_MainEntry_PierBase",stone_light,(pp.x,pp.y,1.58),(1.05,.54,.40),(u,n,zax))
    add_box("WTHR_MainEntry_PierCapital",stone_light,(pp.x,pp.y,8.45),(1.15,.58,.38),(u,n,zax))
    for level in (2.0,3.7,5.45,7.2):
        add_box("WTHR_MainEntry_PierRustication",stone,(pp.x,pp.y,level),(1.02,.68,.09),(u,n,zax))
add_box("WTHR_MainEntry_CrowningCornice",stone_light,(entry_center.x+n.x*.34,entry_center.y+n.y*.34,8.75),(15.0,.48,.18),(u,n,zax))
add_box("WTHR_MainEntry_UpperFrieze",stone,(entry_center.x+n.x*.32,entry_center.y+n.y*.32,9.02),(14.6,.36,.34),(u,n,zax))
add_box("WTHR_MainEntry_UpperCornice",stone_light,(entry_center.x+n.x*.38,entry_center.y+n.y*.38,9.28),(14.9,.48,.14),(u,n,zax))
entry_p=entry_center+n*.28
add_box("WTHR_MainEntry_Entablature",stone_light,(entry_p.x,entry_p.y,8.05),(10.4,.34,.58),(u,n,zax))
plaque=bpy.data.objects.new("WTHR_EngravedName_Plaque",None); asset.objects.link(plaque)
plaque.empty_display_type='PLAIN_AXES'; plaque.location=(entry_center.x,entry_center.y+n.y*(wall_d/2+.50),8.05)
txt=bpy.data.curves.new("WTHR_EngravedName_Text","FONT"); txt.body="R. B. WETHERILL LABORATORY OF CHEMISTRY"; txt.size=.44; txt.align_x='CENTER'; txt.extrude=.005
to=bpy.data.objects.new("WTHR_EngravedName_Text",txt); asset.objects.link(to); to.visible_shadow=False; to.location=(entry_center.x,entry_center.y+n.y*.66,7.92); to.rotation_euler=(math.radians(90),0,0); txt.materials.append(engraved)
# Five limestone chemistry panels with legible labels. The historic relief designs
# are simplified; labels identify fields rather than claim exact portrait identities.
panel_titles=("ANALYTICAL","ORGANIC","INORGANIC","PHYSICAL","BIOLOGICAL")
for k,title in enumerate(panel_titles):
    off=(-5.4,-2.7,0,2.7,5.4)[k]; p0=entry_center+u*off+n*.52
    panel_z=7.05
    add_box("WTHR_ChemistryReliefPanel",stone,(p0.x,p0.y,panel_z),(1.95,.26,.96),(u,n,zax))
    add_box("WTHR_ChemistryReliefInset",stone_light,(p0.x+n.x*.15,p0.y+n.y*.15,7.29),(1.72,.05,.42),(u,n,zax))
    label=bpy.data.curves.new(f"WTHR_ChemistryField_{title}","FONT"); label.body=title; label.size=.29; label.align_x='CENTER'; label.extrude=.005
    label_ob=bpy.data.objects.new(f"WTHR_ChemistryField_{title}",label); asset.objects.link(label_ob); label_ob.visible_shadow=False
    face_u=Vector(u)
    if face_u.cross(Vector((0,0,1))).dot(Vector(n))<0: face_u=-face_u
    label_ob.location=tuple(p0+Vector(n)*.78+Vector((0,0,6.68)))
    label_ob.rotation_euler=Matrix((face_u,Vector((0,0,1)),Vector(n))).transposed().to_euler(); label.materials.append(engraved)
    relief=p0+Vector(n)*.72
    # restrained geometric relief motifs: analytic balance, tetrahedron, periodic grid etc.
    if k==0:
        add_box("WTHR_ChemistryCarvedBalance",stone_light,(relief.x,relief.y,7.24),(.82,.03,.05),(u,n,zax))
        add_box("WTHR_ChemistryCarvedBalance",stone_light,(relief.x,relief.y,7.28),(.05,.03,.22),(u,n,zax))
    elif k==1:
        for dx,dz in ((-.28,0),(.28,0),(0,.16),(0,-.16)):
            add_box("WTHR_ChemistryCarvedAtom",stone_light,(relief.x+u.x*dx,relief.y+u.y*dx,7.28+dz),(.10,.03,.10),(u,n,zax))
    elif k==2:
        for ix in range(3):
            for iz in range(2):
                add_box("WTHR_ChemistryPeriodicRelief",stone_light,(relief.x+u.x*(ix*.30-.30),relief.y+u.y*(ix*.30-.30),7.20+iz*.16),(.16,.03,.10),(u,n,zax))
    elif k==3:
        for dx in (-.55,0,.55):
            add_box("WTHR_ChemistryPhaseRelief",stone_light,(relief.x+u.x*dx,relief.y+u.y*dx,7.26),(.06,.03,.24),(u,n,zax))
    else:
        add_box("WTHR_ChemistryLeafRelief",stone_light,(relief.x,relief.y,7.26),(.18,.03,.26),(u,n,zax))

# Copper roof edge, flat slate roof, and small rooftop mechanical penthouses.
add_poly_slab("WTHR_RoofDeck",15.95,.28,roof_dark)
for a,b,L,u,n,mid in edge_info:
    add_box("WTHR_CopperCornice",roof,(mid.x+n.x*.30,mid.y+n.y*.30,16.05),(L+.85,.75,.52),(u,n,zax))
    add_box("WTHR_CorniceMolding",roof,(mid.x+n.x*.38,mid.y+n.y*.38,15.72),(L+.42,.34,.16),(u,n,zax))
# Satellite view shows an irregular central roof-plant cluster. Mix equipment
# footprints and heights; individual unit types remain informed visual estimates.
for idx,(x,y,w,d,h,kind) in enumerate(((-13,-8,7.2,4.2,1.45,"air"),(-3,-8,5.0,3.2,1.10,"air"),(7,-7,7.8,4.5,1.60,"chiller"),(15,-5,3.8,2.6,1.15,"cabinet"),(-12,2,4.2,3.3,1.05,"cabinet"),(-3,3,8.5,4.6,1.75,"chiller"),(8,3,4.4,3.1,1.30,"air"),(16,5,2.4,2.3,2.10,"exhaust"),(-7,11,2.2,2.0,2.35,"exhaust"),(2,11,5.6,2.8,.90,"fan"))):
    z=16.35+h/2
    add_box(f"WTHR_RooftopAirHandler_{idx+1:02d}",white,(x,y,z),(w,d,h))
    add_box(f"WTHR_RooftopLouver_{idx+1:02d}",steel,(x,y-d/2-.045,z),(w*.72,.09,h*.55))
    for j in range(5):
        add_box(f"WTHR_RooftopLouverSlat_{idx+1:02d}",frame,(x-w*.28+j*w*.14,y-d/2-.10,z),(0.035,.045,h*.47))
    add_box(f"WTHR_RooftopServiceLid_{idx+1:02d}",stone_light,(x,y,16.35+h+.06),(w+.14,d+.14,.12))
    if kind=="fan":
        for q in (-1.35,0,1.35):
            add_box(f"WTHR_RooftopFanBank_{idx+1:02d}",steel,(x+q,y,16.35+h+.15),(.95,.95,.10))
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.34, depth=.10, location=(x+q,y,16.35+h+.25))
            fan=bpy.context.object; fan.name=f"WTHR_RooftopFanHub_{idx+1:02d}"
            for c in list(fan.users_collection): c.objects.unlink(fan)
            asset.objects.link(fan); fan.data.materials.append(frame)
    if kind=="exhaust":
        add_box(f"WTHR_RooftopExhaustCowl_{idx+1:02d}",roof_dark,(x,y,16.35+h+.25),(w*1.35,d*1.35,.18))

# Create one mesh per detail family/material batch to keep the asset manageable.
for (family,mn),b in batches.items():
    mesh=bpy.data.meshes.new(family); mesh.from_pydata(b["verts"],[],b["faces"]); mesh.update()
    mesh.materials.append(b["material"])
    ob=bpy.data.objects.new(family,mesh); asset.objects.link(ob)
    ob["part_family"]=family

# Asset root stays local; campus marker must receive this footprint-bound center.
root=bpy.data.objects.new(f"AssetRoot_{ASSET_ID}",None); asset.objects.link(root); root.empty_display_type='PLAIN_AXES'; root.empty_display_size=2.5
members=[o for o in asset.objects if o != root]
for o in members:
    if o.name.startswith("Leighty_Commons_Molecular"):
        o.visible_shadow=False
    if o.name.startswith(("WTHR_MainEntry_", "WTHR_Chemistry", "WTHR_StonePilaster")) and o.type=='MESH':
        bevel=o.modifiers.new("Soft limestone arris",'BEVEL'); bevel.width=.025; bevel.segments=2; bevel.limit_method='ANGLE'; bevel.angle_limit=math.radians(30)
    world=o.matrix_world.copy(); o.parent=root; o.matrix_parent_inverse=root.matrix_world.inverted(); o.matrix_world=world
root.location=(0,0,0)
asset["coordinate_frame"]="local; master Placement marker supplies XY campus position"
asset["placement_origin_xy_m"]=[anchor.x,anchor.y]
asset["asset_id"]=ASSET_ID
asset["geometry_basis"]="official footprint polygon; exact saved horizontal perimeter, no horizontal rescale"
sc["coordinate_frame"]="local; master Placement marker supplies XY campus position"
sc["placement_origin_xy_m"]=[anchor.x,anchor.y]
sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1.0

# Presentation-only set is outside exported Asset collection.
presentation=bpy.data.collections.new("WTHR_Presentation_Only"); sc.collection.children.link(presentation)
def add_camera(name,loc,target,lens=42):
    data=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,data); presentation.objects.link(ob)
    ob.location=loc; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler(); data.lens=lens; return ob
def add_area(name,loc,target,power,size,color):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; data.color=color
    ob=bpy.data.objects.new(name,data); presentation.objects.link(ob); ob.location=loc; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler(); return ob
overviewcam=add_camera("WTHR_Building_Overview_Camera",(-35,-103,25),(0,0,7.2),43)
extcam=add_camera("WTHR_Exterior_Hero_Camera",tuple(entry_center+entry_normal*32+Vector((0,0,13))),tuple(entry_center+Vector((0,0,6.2))),40)
intcam=add_camera("WTHR_Interior_Commons_Camera",(0,-20,12),(0,1,5.0),45)
intcam.data.type='ORTHO'; intcam.data.ortho_scale=24
detailcam=add_camera("WTHR_Entrance_Detail_Camera",(entry_center.x+entry_normal.x*23,entry_center.y+entry_normal.y*23,8.2),(entry_center.x,entry_center.y,7.15),28)
add_area("WTHR_Exterior_Key",(-55,-68,48),(0,0,6),180,34,(1.0,.83,.65))
add_area("WTHR_Exterior_Fill",(38,-35,38),(0,0,6),100,28,(.70,.82,1.0))
add_area("WTHR_Interior_Key",(0,-4,12),(0,0,4),900,18,(1.0,.88,.72))
add_area("WTHR_Interior_Fill",(8,5,10),(0,0,4),650,14,(.72,.84,1.0))
world=sc.world or bpy.data.worlds.new("WTHR_StudioWorld"); sc.world=world; world.use_nodes=True
world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.38,.48,.60,1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.22
sc.render.engine='CYCLES'; sc.cycles.samples=24
sc.render.resolution_x=1400; sc.render.resolution_y=1000; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'; sc.view_settings.view_transform='AgX'
sc.camera=extcam; sc.render.filepath=str(AUDIT/"exterior_hero.png")
sc.render.film_transparent=False
sc.view_settings.exposure=-.65
# Discard unused materials inherited from the massing source. The detailed asset
# uses procedural materials only, so no external image texture is required.
for mesh in list(bpy.data.meshes):
    if mesh.users==0: bpy.data.meshes.remove(mesh)
for m in list(bpy.data.materials):
    if m.users==0: bpy.data.materials.remove(m)
for im in list(bpy.data.images):
    if im.users==0: bpy.data.images.remove(im)
bpy.context.view_layer.objects.active=None
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE))
print(json.dumps({"saved":str(ASSET_FILE),"asset_collection":asset.name,"asset_objects":len(asset.objects),"batches":len(batches),"placement_origin_xy_m":[anchor.x,anchor.y],"outline_points":len(outline),"interior_floors":5,"materials":len([m for m in bpy.data.materials if m.name.startswith('WTHR') or m.name.startswith('Interior') or m.name.startswith('Leighty')])},indent=2))

# Render hero and an isolated, bright Commons cutaway. Keep only the target floor
# and Commons furniture so upper floors do not occlude the room in the preview.
bpy.ops.render.render(write_still=True)
# Preserve a whole-building context view alongside the entrance-focused hero.
sc.camera=overviewcam; sc.render.resolution_x=1400; sc.render.resolution_y=1000
sc.render.filepath=str(AUDIT/"building_overview.png")
bpy.ops.render.render(write_still=True)
# Close elevation proof for the limestone entrance and chemistry relief plaques.
sc.camera=detailcam; sc.render.resolution_x=1200; sc.render.resolution_y=900
sc.render.filepath=str(AUDIT/"entrance_detail.png")
bpy.ops.render.render(write_still=True)
# Restore the hero camera before preparing the interior cutaway.
sc.camera=extcam; sc.render.resolution_x=1400; sc.render.resolution_y=1000
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,3.18))
cutground=bpy.context.object; cutground.name="WTHR_Commons_Cutaway_Preview_Floor"
for c in list(cutground.users_collection): c.objects.unlink(cutground)
presentation.objects.link(cutground); cutground.location=(0,1,3.18); cutground.dimensions=(22,18,.20)
cutground.data.materials.append(floor_mat)
cutground.hide_render=False
for o in asset.objects:
    keep = o.name.startswith(("Leighty_Commons_", "Leighty_Commons_Molecular"))
    o.hide_render = not keep
sc.view_settings.exposure=.15
sc.camera=intcam; sc.render.resolution_x=1400; sc.render.resolution_y=950; sc.render.filepath=str(AUDIT/"interior_commons_cutaway.png")
bpy.ops.render.render(write_still=True)
cutground.hide_render=True
for o in asset.objects: o.hide_render=False
sc.view_settings.exposure=0.0
sc.camera=extcam; sc.render.resolution_x=1400; sc.render.resolution_y=1000; sc.render.filepath=str(AUDIT/"exterior_hero.png")
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE))
