import bpy, math, os, re, json
from mathutils import Vector

BLEND = os.path.abspath(r"modular/buildings/rawls_hall.blend")
OUT = os.path.dirname(__file__)
bpy.ops.wm.open_mainfile(filepath=BLEND)
col = bpy.data.collections["Asset_rawls_hall"]
origin = (323.6582336425781, -409.62242126464844)

def ensure_mat(name, color, roughness=0.65, metallic=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    m.diffuse_color = (*color, 1)
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    return m

wall = ensure_mat("RAWL_Interior_WarmWhite", (0.78, 0.76, 0.69), 0.82)
trim = ensure_mat("RAWL_Interior_DoorTrim", (0.32, 0.18, 0.09), 0.48)
wood = ensure_mat("RAWL_Interior_Wood", (0.29, 0.13, 0.055), 0.46)
seatmat = ensure_mat("RAWL_Interior_Graphite_Upholstery", (0.075, 0.09, 0.105), 0.72)
metal = bpy.data.materials.get("RAWL_Dark_Bronze_Metal") or ensure_mat("RAWL_Dark_Bronze_Metal", (0.12,0.105,0.08), 0.42, 0.68)

def color_ramp(node, c1, c2):
    ramp = node.color_ramp
    ramp.elements[0].position = 0.18
    ramp.elements[0].color = (*c1, 1)
    ramp.elements[1].position = 0.82
    ramp.elements[1].color = (*c2, 1)
    return ramp

# Furniture scale wood grain: long grain runs with the long edge of the desk top.
nt = wood.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
p = nt.nodes.new("ShaderNodeBsdfPrincipled")
p.inputs["Roughness"].default_value = 0.46
tc = nt.nodes.new("ShaderNodeTexCoord")
mapping = nt.nodes.new("ShaderNodeMapping")
mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 1.25
noise.inputs["Detail"].default_value = 3.0
noise.inputs["Roughness"].default_value = 0.58
ramp = nt.nodes.new("ShaderNodeValToRGB")
color_ramp(ramp, (0.25,0.105,0.04), (0.33,0.16,0.065))
bump = nt.nodes.new("ShaderNodeBump")
mapping.inputs["Scale"].default_value = (0.7, 15.0, 3.0)
bump.inputs["Strength"].default_value = 0.08
bump.inputs["Distance"].default_value = 0.0005
nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
wood.diffuse_color = (0.3,0.14,0.055,1)

# A distinct upholstery material reads better than the carpet-colored chair blocks.
for o in col.all_objects:
    if o.type == "MESH" and ("1086_Chair" in o.name or "ChairBack" in o.name):
        o.data.materials.clear()
        o.data.materials.append(seatmat)

# Remove the earlier rough partition lines and closed door leaves. The furniture stays.
preserve_tokens = ("_Desk", "_Chair", "DeskSupport", "ChairLeg", "ChairBack")
for o in list(col.all_objects):
    if o.name.startswith("RAWL_2026_") and not any(t in o.name for t in preserve_tokens):
        bpy.data.objects.remove(o, do_unlink=True)

# Replace two broad desk panels with four slim floor-contact steel legs per desk.
for o in list(col.all_objects):
    if "DeskSupport" in o.name or "DeskLeg" in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

def make_box(name, center, dims, material, angle=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object
    o.name = "RAWL_2026_" + name
    o.dimensions = dims
    o.rotation_euler.z = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft edge", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new("Weighted corners", "WEIGHTED_NORMAL")
    return o

desks = [o for o in col.all_objects if o.type == "MESH" and "1086_Desk" in o.name]
for desk in desks:
    x,y,_ = desk.location
    for sx in (-0.53,0.53):
        for sy in (-0.21,0.21):
            make_box("DeskLeg", (x+sx,y+sy,0.375), (0.042,0.042,0.71), metal, bevel=0.008)
    # Keep top and legs in contact; the desk datum remains the previous plan-derived placement.

# Build registered partition wall lines from the published 2024 plan. Pixel to local
# transformation and 1-2 m registration uncertainty match the previous source record.
def xy(pt):
    px,py = pt
    return Vector((399.0 - 0.12*py - origin[0], -384.0 - 0.12*px - origin[1]))

def box_between(name, a, b, z, height, thickness, material):
    d = b-a
    if d.length < 0.08:
        return
    mid = (a+b)*0.5
    angle = math.atan2(d.y,d.x)
    make_box(name, (mid.x,mid.y,z), (d.length,thickness,height), material, angle)

def wall_path(name, pts, gaps=None, height=3.55, thickness=0.16):
    gaps = gaps or {}
    for i,(pa,pb) in enumerate(zip(pts,pts[1:])):
        a,b = xy(pa),xy(pb)
        d=b-a
        length=d.length
        cuts=[]
        for t,width_m in gaps.get(i,[]):
            half=min(width_m/(2*length),0.48)
            cuts.append((max(0.0,t-half),min(1.0,t+half)))
        cuts.sort()
        cursor=0.0
        pieces=[]
        for lo,hi in cuts:
            if lo>cursor+0.001: pieces.append((cursor,lo))
            cursor=max(cursor,hi)
        if cursor<1.0-0.001: pieces.append((cursor,1.0))
        for j,(lo,hi) in enumerate(pieces):
            box_between(name+"_%02d_%02d"%(i,j),a+d*lo,a+d*hi,height/2,height,thickness,wall)
        for j,(lo,hi) in enumerate(cuts):
            # Wood jambs and a short lintel frame the clear opening; no door leaf blocks it.
            p0=a+d*lo; p1=a+d*hi
            for side,pv in (("A",p0),("B",p1)):
                n=Vector((-d.y,d.x)).normalized()
                jamb_center=pv+n*(thickness*0.16)
                make_box(name+"_Jamb_%02d_%s"%(i,side),(jamb_center.x,jamb_center.y,1.02),(0.06,thickness*1.15,2.04),trim,math.atan2(d.y,d.x),bevel=0.008)
            box_between(name+"_Header_%02d"%i,p0,p1,2.10,0.14,thickness,wall)

def cubic(p0,p1,p2,p3,steps=36):
    result=[]
    for i in range(steps+1):
        t=i/steps
        result.append(tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in range(2)))
    return result

# Classroom 1086, including the plan's lower boundary opening to the 1062 area.
wall_path("Plan1086",[(127,318),(120,295),(245,256),(301,437),(176,475),(131,333),(127,318)],
          {3:[(0.93,0.95)],5:[(0.50,0.95)]})
# Room 1071 and its documented access opening.
wall_path("Plan1071",[(77,536),(88,457),(142,457),(169,545),(83,551),(77,536)],
          {3:[(0.50,0.95)]})
# Room 1057; curved perimeter is sampled from the source plan's drawn arc.
wall_path("Plan1057",[(68,551),(169,545),(191,607),(200,660)],{1:[(0.35,0.95)],2:[(0.22,0.95)]})
curve = cubic((200,660),(122,663),(67,620),(68,551))
wall_path("Plan1057_Curve",curve)
# Room 1062 shares its north edge with 1086 and follows the broad curved boundary.
wall_path("Plan1062",[(184,500),(216,605)],{0:[(0.22,0.95)]})
curve = cubic((216,605),(287,589),(320,538),(306,462))
wall_path("Plan1062_Curve",curve)
# Room 1054 follows the oblique southeast side of the first-floor plan.
wall_path("Plan1054",[(306,462),(326,555),(356,647),(241,678),(216,605)],
          {0:[(0.94,0.95)],2:[(0.92,0.95)],3:[(0.18,0.95)]})
# South lecture/meeting room 1011: only its interior partition is added; exterior sides
# are already represented by the GIS-derived shell. The plan shows a wide doorway.
wall_path("Plan1011",[(112,756),(233,756)],{0:[(0.50,1.65)]})
# Washroom/core partitions and circulation walls visible on the published plan.
wall_path("PlanCoreNorth",[(240,655),(305,655),(385,655)],{0:[(0.48,0.90)]})
wall_path("PlanCoreWest",[(240,655),(240,732)],{0:[(0.82,0.90)]})
wall_path("PlanCoreDividerA",[(305,655),(305,732)],{0:[(0.78,0.90)]})
wall_path("PlanCoreDividerB",[(347,655),(347,732)],{0:[(0.77,0.90)]})
wall_path("PlanCoreSouth",[(240,732),(385,732)],{0:[(0.18,0.90),(0.80,0.90)]})
# Small north room 1098 and adjoining stair/corridor enclosure; door opening retained.
wall_path("Plan1098",[(121,215),(190,215),(190,246),(121,246),(121,215)],{2:[(0.48,0.95)]})
wall_path("PlanNorthStair",[(130,259),(170,259),(170,289),(130,289),(130,259)],{3:[(0.60,0.90)]})
# Northwest vestibule partitions and the small enclosed room shown beneath 1098.
wall_path("PlanNWUpperRoom",[(54,273),(93,273),(93,338)],{1:[(0.62,0.90)]})
wall_path("PlanNWVestibule",[(88,338),(121,338),(121,457),(88,457),(88,338)],{1:[(0.22,0.90)],2:[(0.50,0.90)]})

# Confirm every plan-based desk and chair centroid lies in the registered structural polygon.
fp = bpy.data.objects["RAWL_FloorSlab_L1_Ground"]
poly = [fp.matrix_world @ fp.data.vertices[i].co for i in range(29)]
poly = [(p.x,p.y) for p in poly]
def inside(x,y):
    c=False
    j=len(poly)-1
    for i in range(len(poly)):
        xi,yi=poly[i]; xj,yj=poly[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:c=not c
        j=i
    return c
furniture=[]
for o in col.all_objects:
    if o.type=="MESH" and ("1086_Desk" in o.name or "1086_Chair" in o.name):
        x,y,_=o.matrix_world.translation
        furniture.append((o.name,round(x,3),round(y,3),inside(x,y)))

# Route the active facade color branch through a true two-axis projection. The prior
# helper graph existed but the connected Brick Texture still received X/Z only.
brick=bpy.data.materials.get("RAWL_Purdue_Red_Brick")
brick_notes=[]
if brick and brick.use_nodes:
    nt=brick.node_tree;nodes=nt.nodes;links=nt.links
    bsdf=next(n for n in nodes if n.type=="BSDF_PRINCIPLED")
    tex=next(n for n in nodes if n.type=="TEX_BRICK" and any(l.to_node==bsdf and l.to_socket.name=="Base Color" for l in n.outputs["Color"].links))
    coord=nodes.new("ShaderNodeTexCoord");coord.label="Metric facade projection"
    sepcoord=nodes.new("ShaderNodeSeparateXYZ");geom=nodes.new("ShaderNodeNewGeometry")
    sepnormal=nodes.new("ShaderNodeSeparateXYZ");absx=nodes.new("ShaderNodeMath");absx.operation="ABSOLUTE"
    xz=nodes.new("ShaderNodeCombineXYZ");yz=nodes.new("ShaderNodeCombineXYZ")
    mix=nodes.new("ShaderNodeMixRGB");mix.blend_type="MIX"
    links.new(coord.outputs["Object"],sepcoord.inputs["Vector"])
    links.new(geom.outputs["Normal"],sepnormal.inputs["Vector"])
    links.new(sepnormal.outputs["X"],absx.inputs[0])
    links.new(sepcoord.outputs["X"],xz.inputs["X"]);links.new(sepcoord.outputs["Z"],xz.inputs["Y"])
    links.new(sepcoord.outputs["Y"],yz.inputs["X"]);links.new(sepcoord.outputs["Z"],yz.inputs["Y"])
    links.new(absx.outputs[0],mix.inputs["Fac"])
    links.new(xz.outputs["Vector"],mix.inputs["Color1"]);links.new(yz.outputs["Vector"],mix.inputs["Color2"])
    for l in list(tex.inputs["Vector"].links):links.remove(l)
    links.new(mix.outputs["Color"],tex.inputs["Vector"])
    brick_notes=["active Brick Texture vector blends X/Z and Y/Z projections using abs(surface normal X)","metric brick width 0.215m; course height 0.075m"]

asset_root=bpy.data.objects.get("AssetRoot_rawls_hall")
evidence_text=bpy.data.texts.get("RAWL_2026_EVIDENCE")
if not evidence_text:evidence_text=bpy.data.texts.new("RAWL_2026_EVIDENCE")
evidence_text.clear()
evidence_text.write("BATCH 4 Rawls Hall first-floor refinement. Plan: Purdue Road School, 2024 Rawls Hall first-floor PDF, https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf (accessed 2026-10-23). Approximate pixel registration X=399-.12*pixelY, Y=-384-.12*pixelX, then local-origin subtraction; plan has no CRS; about 1-2 m registration uncertainty. Existing mapped furniture is illustrative, not a surveyed inventory. Interior finish cues: Purdue e-Archives PPBUC03065, David Umberger, 2003-07-25, https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/3050/ ; historical image only supports a warm ochre / pale wall / wood / dark floor palette. Google Maps checked 2026-10-23: Rawls Hall result location 40.4237823,-86.9099567; satellite attribution Airbus / Maxar ©2026 (image capture date not shown). Street View at 357 W State St, capture May 2026; viewpoint is nearby and not a dimensioned facade survey. Exact source imagery visible in map UI; geometry/height remains uncertain. Upper-floor voids and room layouts remain unverified. First-floor door gaps are kept open; lintels and jambs are modelled. Asset/local origin and placement marker/manifest are unchanged.\n")

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
report={"collection":"Asset_rawls_hall","objects":len(col.all_objects),"desk_count":len([o for o in col.all_objects if o.type=='MESH' and '1086_Desk' in o.name]),"chair_count":len([o for o in col.all_objects if o.type=='MESH' and '1086_Chair' in o.name]),"furniture_centroids_inside_ground_shell":sum(r[3] for r in furniture),"furniture_centroid_count":len(furniture),"outside_furniture":[r for r in furniture if not r[3]],"root_location":list(asset_root.location) if asset_root else None,"root_rotation":list(asset_root.rotation_euler) if asset_root else None,"brick_nodes":brick_notes,"first_floor_registration_uncertainty_m":[1,2],"google_street_view_capture":"May 2026"}
with open(os.path.join(OUT,"round1_model_check.json"),"w") as f:json.dump(report,f,indent=2)
print("ROUND1",json.dumps(report))
