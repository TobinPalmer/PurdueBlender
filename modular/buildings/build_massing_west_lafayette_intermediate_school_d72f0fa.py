"""Source-backed detailed library for West Lafayette Intermediate School.

The connected ground outline is taken from OSM way 772742586 and transformed
with the PurdueMap local approximation documented in modular/AGENTS.md. The
school is a mostly single-storey, broad campus building; the central learning
node/clerestory, gym, and entry are modelled taller based on architect imagery.
Exact elevations and interior room locations were not published in the sources
found, so vertical dimensions and the schematic classroom arrangement remain
explicit estimates. All materials are procedural and self-contained.
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_west_lafayette_intermediate_school_d72f0fa.blend")
SOURCE = os.path.join(ROOT, "audit", "west_lafayette_intermediate_school", "sources", "osm_way_772742586_full.json")
AUDIT = os.path.join(ROOT, "audit", "west_lafayette_intermediate_school")
SCENE_NAME = "Building_massing_west_lafayette_intermediate_school_d72f0fa"
ASSET_COLLECTION = "Asset_massing_west_lafayette_intermediate_school_d72f0fa"
BUILDING = "West Lafayette Intermediate School"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137


def campus_xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def material(name, color, roughness=0.75, metallic=0.0, procedural=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if procedural == "brick":
        tex = nodes.new("ShaderNodeTexBrick")
        tex.inputs["Color1"].default_value = (0.37, 0.105, 0.062, 1)
        tex.inputs["Color2"].default_value = (0.25, 0.058, 0.035, 1)
        tex.inputs["Mortar"].default_value = (0.56, 0.51, 0.43, 1)
        tex.inputs["Scale"].default_value = 8.0
        tex.inputs["Mortar Size"].default_value = 0.025
        tex.inputs["Mortar Smooth"].default_value = 0.01
        tex.inputs["Brick Width"].default_value = 0.48
        tex.inputs["Row Height"].default_value = 0.22
        coord = nodes.new("ShaderNodeTexCoord")
        links.new(coord.outputs["Generated"], tex.inputs["Vector"])
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.16
        bump.inputs["Distance"].default_value = 0.04
        links.new(tex.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    elif procedural == "metal_panel":
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 48.0
        tex.inputs["Detail"].default_value = 2.0
        coord = nodes.new("ShaderNodeTexCoord")
        links.new(coord.outputs["Generated"], tex.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.24
        ramp.color_ramp.elements[0].color = (color[0]*0.84,color[1]*0.84,color[2]*0.84,1)
        ramp.color_ramp.elements[1].position = 0.76
        ramp.color_ramp.elements[1].color = (min(color[0]*1.13,1),min(color[1]*1.13,1),min(color[2]*1.13,1),1)
        links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    elif procedural == "tile":
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 26.0
        noise.inputs["Detail"].default_value = 2.0
        coord = nodes.new("ShaderNodeTexCoord")
        links.new(coord.outputs["Generated"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.1
        bump.inputs["Distance"].default_value = 0.012
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def make_collections():
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        if col.name != scene.collection.name:
            bpy.data.collections.remove(col)
    root = bpy.data.collections.new(ASSET_COLLECTION)
    scene.collection.children.link(root)
    cols = {"Shell": bpy.data.collections.new("WLIS_Exterior_Shell"),
            "Facade": bpy.data.collections.new("WLIS_Facade_Detail"),
            "Interior": bpy.data.collections.new("WLIS_Schematic_Interior"),
            "Roof": bpy.data.collections.new("WLIS_Roof_Equipment"),
            "Entry": bpy.data.collections.new("WLIS_Main_Entry")}
    for col in cols.values():
        root.children.link(col)
    return scene, root, cols


def make_box(name, loc, dims, mat, col, rot=0.0, bevel=0.0):
    dx, dy, dz = [v*0.5 for v in dims]
    verts = [(-dx,-dy,-dz),(dx,-dy,-dz),(dx,dy,-dz),(-dx,dy,-dz),
             (-dx,-dy,dz),(dx,-dy,dz),(dx,dy,dz),(-dx,dy,dz)]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    mesh = bpy.data.meshes.new(name+"_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = loc
    obj.rotation_euler[2] = rot
    if bevel:
        mod = obj.modifiers.new("Small softened edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def make_mesh(name, verts, faces, mat, col, secondary=None, secondary_indices=()):
    mesh = bpy.data.meshes.new(name+"_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    if secondary is not None:
        mesh.materials.append(secondary)
    mesh.update()
    for index in secondary_indices:
        if index < len(mesh.polygons):
            mesh.polygons[index].material_index = 1
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return obj


def make_curve(name, points, radius, mat, col):
    curve = bpy.data.curves.new(name+"_curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co,1)
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def make_ring():
    data = json.load(open(SOURCE, encoding="utf8"))
    way = next(e for e in data["elements"] if e["type"] == "way" and e["id"] == 772742586)
    nodes = {e["id"]: e for e in data["elements"] if e["type"] == "node"}
    coords = [campus_xy(nodes[n]["lon"], nodes[n]["lat"]) for n in way["nodes"]]
    if coords[0] == coords[-1]:
        coords.pop()
    return coords


def add_shell(ring, brick, roof, col):
    n = len(ring)
    wall_h = 4.75
    verts = [(x,y,z) for z in (0.0,wall_h) for x,y in ring]
    faces = [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    faces += [tuple(range(n-1,-1,-1)), tuple(range(n,2*n))]
    shell = make_mesh("GIS 772742586 | exact connected school footprint", verts, faces, brick, col,
                      secondary=roof, secondary_indices=(n+1,))
    shell["source_feature"] = "OpenStreetMap way 772742586"
    shell["wall_height_m"] = wall_h
    shell["height_status"] = "estimated; facade photographs show a low single-storey mass"
    # Low, broad main roof and a continuous light parapet band.
    xs, ys = [x for x,y in ring], [y for x,y in ring]
    cx, cy = (min(xs)+max(xs))*0.5, (min(ys)+max(ys))*0.5
    for i,(a,b) in enumerate(zip(ring, ring[1:]+ring[:1])):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        if length < 1.0: continue
        ang=math.atan2(dy,dx)
        nx,ny=dy/length,-dx/length
        mx,my=(a[0]+b[0])*0.5,(a[1]+b[1])*0.5
        # Outward normal is right of the CCW source ring.
        make_box(f"Roof fascia segment {i+1:02d}",(mx,my,wall_h-0.12),(length+0.04,0.16,0.38),roof,col,ang)
    return shell


def facade(ring, brick, glass, trim, metal, col):
    for edge_id,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1]),start=1):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        if length < 5.8: continue
        ang=math.atan2(dy,dx)
        nx,ny=dy/length,-dx/length
        modules=max(1,int(length//4.2))
        spacing=length/modules
        for j in range(modules):
            along=(j+0.5)*spacing
            px=a[0]+dx*along/length+nx*0.10
            py=a[1]+dy*along/length+ny*0.10
            # High, landscape classroom windows and thin metal frames.
            ww=min(2.7,spacing*0.72)
            make_box(f"Facade glazing {edge_id:02d}-{j+1:02d}",(px,py,2.12),(ww,0.10,1.72),glass,col["Facade"],ang)
            for s in (-1,1):
                make_box(f"Window jamb {edge_id:02d}-{j+1:02d}-{s}",(px+s*(ww*0.5-0.035)*math.cos(ang),py+s*(ww*0.5-0.035)*math.sin(ang),2.12),(0.075,0.16,1.95),trim,col["Facade"],ang)
            make_box(f"Window head {edge_id:02d}-{j+1:02d}",(px,py,3.08),(ww+0.08,0.18,0.09),trim,col["Facade"],ang)
            make_box(f"Window sill {edge_id:02d}-{j+1:02d}",(px,py,1.18),(ww+0.10,0.19,0.10),trim,col["Facade"],ang)
            if ww > 1.4:
                make_box(f"Window mullion {edge_id:02d}-{j+1:02d}",(px,py,2.12),(0.055,0.13,1.70),trim,col["Facade"],ang)
        # Warm pale metal spandrel and selective high clerestory ribbon. The
        # award photos support this material language; exact bays are estimates.
        make_box(f"Light metal spandrel {edge_id:02d}",((a[0]+b[0])*0.5,(a[1]+b[1])*0.5,3.91),(length,0.10,0.50),metal,col["Facade"],ang)
        if edge_id % 2 == 0:
            make_box(f"Exterior clerestory ribbon {edge_id:02d}",((a[0]+b[0])*0.5,(a[1]+b[1])*0.5,4.48),(length*0.72,0.10,0.42),glass,col["Facade"],ang)


def structural_volumes(ring, brick, panel, glass, steel, roof, col):
    xs,ys=[x for x,y in ring],[y for x,y in ring]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    # Elevated central learning commons and clerestory node. Both masses sit
    # inside the existing broad footprint; exact roof dimensions are estimated.
    hub=(95.0,1958.0)
    hub_angle=math.radians(45)
    make_box("Central learning commons | compact clerestory node",(hub[0],hub[1],5.85),(20.0,16.0,2.2),panel,col["Shell"],hub_angle,0.08)
    # Four glazed clerestory ribbons and red mullions sit on the outside faces
    # of the raised node, following the architect's bright corridor imagery.
    for side in (-1,1):
        for axis,span,offset,angle in [(0,19.2,side*7.86,hub_angle),(1,15.2,side*9.86,hub_angle+math.pi/2)]:
            center=(hub[0]-math.sin(angle)*offset,hub[1]+math.cos(angle)*offset,5.92)
            make_box(f"Central commons clerestory glass band {axis}-{side}",center,(span,0.14,1.22),glass,col["Facade"],angle)
            for m in range(1,5):
                along=-span*0.5+m*span/5
                mullion=(center[0]+math.cos(angle)*along,center[1]+math.sin(angle)*along,5.92)
                make_box(f"Central commons red steel mullion {axis}-{side}-{m}",mullion,(0.13,0.19,1.35),steel,col["Facade"],angle)
    make_box("Central commons clerestory roof cap",(hub[0],hub[1],7.03),(20.6,16.6,0.26),roof,col["Shell"],hub_angle,0.05)
    # Gym volume: architect photographs show the only very tall roof, exposed
    # open-web steel trusses, clerestory windows, and red folding bleachers.
    gym=(156.0,1911.0)
    gym_w,gym_l=27.0,31.0
    make_box("Gymnasium | tall masonry and panel volume",(gym[0],gym[1],6.7),(gym_w,gym_l,4.0),brick,col["Shell"],math.radians(-35))
    make_box("Gymnasium standing-seam roof",(gym[0],gym[1],8.82),(gym_w+0.6,gym_l+0.6,0.24),roof,col["Shell"],math.radians(-35))
    # Gym clerestory strip and industrial daylight glazing.
    make_box("Gymnasium clerestory glazing",(gym[0],gym[1]-gym_l*0.42,7.8),(gym_w*0.72,0.12,1.05),glass,col["Facade"],math.radians(-35))
    # South-east extension for cafeteria / multipurpose room in the reused
    # Burtsfield gym wing; lower than the new gym and finished in brick/panels.
    caf=(145.0,1892.0)
    make_box("Cafeteria multipurpose extension",(caf[0],caf[1],3.1),(25.0,20.0,2.85),panel,col["Shell"],math.radians(-35))
    make_box("Cafeteria clerestory ribbon",(caf[0],caf[1],4.42),(20.0,0.12,0.48),glass,col["Facade"],math.radians(-35))
    # Roof articulation informed by the Esri overhead view: the school has
    # broad, intersecting low-slope classroom wings, a central connection,
    # and a deeper southeast multipurpose/gym cluster. These low roof plates
    # are set on the GIS shell top and stay inside its broad silhouette.
    # The north-west/east classroom bars and south-west arm create visible
    # stepped transitions instead of one undifferentiated roof polygon.
    roof_plates = [
        # Two roof bars cross at the central learning node, matching the
        # diagonal NW-SE and SW-NE classroom wings visible in the aerial.
        (85.0, 1967.0, 110.0, 16.0, math.radians(-44)),
        (95.0, 1960.0, 72.0, 12.0, math.radians(52)),
        # The aerial shows a wider, irregular southeast gym/multipurpose wing.
        (145.0, 1917.0, 36.0, 22.0, math.radians(-35)),
        (145.0, 1895.0, 24.0, 18.0, math.radians(-35)),
    ]
    for i, (rx, ry, length, width, angle) in enumerate(roof_plates, 1):
        make_box(f"Classroom wing roof plate {i:02d}", (rx, ry, 4.88),
                 (length, width, 0.18), roof, col["Roof"], angle, 0.07)
        # Narrow perimeter coping creates a crisp edge visible at aerial scale.
        make_box(f"Classroom wing roof coping {i:02d}", (rx, ry, 4.99),
                 (length + 0.35, width + 0.35, 0.07), panel, col["Roof"], angle, 0.025)
    # Low rooftop daylight monitors and small mechanical housings are visible
    # in the overhead reference. Their dimensions are schematic, not surveyed.
    for i, (vx, vy) in enumerate([(56,1998),(83,1970),(101,1958),(124,1933),(147,1909)], 1):
        make_box(f"Roof monitor {i:02d} | glazed curb", (vx,vy,5.18),
                 (3.2,1.2,0.34), glass, col["Roof"], math.radians(-43), 0.04)
    for i, (vx, vy) in enumerate([(136,1923),(151,1905),(143,1892)], 1):
        make_box(f"Roof mechanical screen {i:02d}", (vx,vy,5.32),
                 (3.0,2.2,0.65), panel, col["Roof"], math.radians(-43), 0.06)
    # Five open-web red steel trusses, matching the documented gym imagery.
    # The source only establishes exposed trusses; exact spacing is estimated.
    def gym_world(x,y,z):
        ang=math.radians(-35)
        return (gym[0]+x*math.cos(ang)-y*math.sin(ang),
                gym[1]+x*math.sin(ang)+y*math.cos(ang),z)
    for k in range(5):
        local_y=-gym_l*0.38+k*gym_l*0.19
        points=[gym_world(-gym_w*0.44,local_y,7.95),
                gym_world(0.0,local_y,8.55),
                gym_world(gym_w*0.44,local_y,7.95)]
        make_curve(f"Gym red steel roof truss {k+1}",points,0.085,steel,col["Interior"])


def point_in_ring(x,y,ring):
    inside=False
    for (x1,y1),(x2,y2) in zip(ring,ring[1:]+ring[:1]):
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:
            inside=not inside
    return inside


def classroom_sites(ring):
    # The original radial layout placed a number of rooms in OSM cut-outs.
    # Pack 36 small schematic rooms on a 45-degree grid, in three broad
    # source-supported classroom wings (NW, SW and NE). Check all four room
    # corners against the GIS polygon before accepting any center.
    angle=math.radians(45)
    u=Vector((math.cos(angle),math.sin(angle),0))
    v=Vector((-math.sin(angle),math.cos(angle),0))
    origin=Vector((108.0,1950.0,0))
    spacing=5.3
    half=2.12
    groups=[[],[],[]]
    for i in range(-24,25):
        for j in range(-24,25):
            p=origin+u*(i*spacing)+v*(j*spacing)
            corners=[p+u*a+v*b for a in (-half,half) for b in (-half,half)]
            if not all(point_in_ring(q.x,q.y,ring) for q in corners):
                continue
            if p.x<100 and p.y>=1950: group=0
            elif p.x<100 and p.y<1950: group=1
            elif p.x>=100 and p.y>=1950: group=2
            else: continue
            groups[group].append((p.copy(),angle))
    targets=[Vector((62,1980,0)),Vector((60,1925,0)),Vector((140,1980,0))]
    sites=[]
    for wing,(candidates,target) in enumerate(zip(groups,targets),1):
        chosen=[]
        while candidates and len(chosen)<12:
            if not chosen:
                item=min(candidates,key=lambda q:(q[0]-target).length)
            else:
                item=max(candidates,key=lambda q:(min((q[0]-c[0]).length for c in chosen),q[0].x,q[0].y))
            chosen.append(item)
            candidates.remove(item)
        if len(chosen)!=12:
            raise RuntimeError(f"Wing {wing} has only {len(chosen)} GIS-contained room sites")
        sites.extend((p,angle,wing) for p,angle in chosen)
    return sites


def classroom_interior(ring, floor, partition, glass, red, furniture, board, col):
    floor_ring=[(x,y,0.24) for x,y in ring]
    make_mesh("Main finished floor | GIS clipped footprint",floor_ring,[tuple(range(len(floor_ring)))],floor,col["Interior"])
    sites=classroom_sites(ring)
    if len(sites)!=36:
        raise RuntimeError(f"Expected 36 contained classrooms, got {len(sites)}")
    room_half=2.05
    for room_id,(rc,angle,wing) in enumerate(sites,1):
        ray=Vector((math.cos(angle),math.sin(angle),0))
        perp=Vector((-ray.y,ray.x,0))
        def pos(a,b,z):
            q=rc+ray*a+perp*b
            return (q.x,q.y,z)
        # Each bay is a compact 4.1 m square schematic room fully inside the
        # OSM roof shell; three partition walls and a corridor-side door wall
        # make the room perimeter legible in both plan and close review renders.
        left=make_box(f"Classroom {room_id:02d} | corridor partition",pos(-1.25,-room_half,1.65),(1.6,0.14,3.05),partition,col["Interior"],angle)
        left["classroom_center_xy"]=(float(rc.x),float(rc.y))
        left["classroom_wing"]=("NW","SW","NE")[wing-1]
        left["footprint_source"]="OSM way 772742586"
        make_box(f"Classroom {room_id:02d} | corridor door panel",pos(0,-1.97,1.13),(0.88,0.15,2.12),red,col["Interior"],angle,0.025)
        make_box(f"Classroom {room_id:02d} | corridor partition right",pos(1.25,-room_half,1.65),(1.6,0.14,3.05),partition,col["Interior"],angle)
        make_box(f"Classroom {room_id:02d} | rear partition",pos(0,room_half,1.65),(4.1,0.14,3.05),partition,col["Interior"],angle)
        make_box(f"Classroom {room_id:02d} | side partition left",pos(-room_half,0,1.65),(4.1,0.14,3.05),partition,col["Interior"],angle+math.pi/2)
        make_box(f"Classroom {room_id:02d} | side partition right",pos(room_half,0,1.65),(4.1,0.14,3.05),partition,col["Interior"],angle+math.pi/2)
        # Narrow clerestory glazing on the corridor divider is supported by
        # award photography; exact position and glazing dimensions are estimates.
        make_box(f"Classroom {room_id:02d} | clerestory interior lite",pos(0,-1.97,2.54),(1.95,0.075,0.52),glass,col["Interior"],angle)
        for q,a in enumerate((-1.15,0,1.15),1):
            make_box(f"Classroom {room_id:02d} | student table {q}",pos(a,0.28,0.79),(0.86,0.66,0.10),furniture,col["Interior"],angle,0.035)
            make_box(f"Classroom {room_id:02d} | student chair seat {q}",pos(a,-0.62,0.60),(0.42,0.42,0.08),red,col["Interior"],angle,0.035)
            make_box(f"Classroom {room_id:02d} | student chair back {q}",pos(a,-0.82,0.88),(0.40,0.08,0.55),red,col["Interior"],angle,0.025)
        make_box(f"Classroom {room_id:02d} | teacher desk",pos(0,1.26,0.82),(1.25,0.62,0.12),furniture,col["Interior"],angle,0.04)
        make_box(f"Classroom {room_id:02d} | teaching board",pos(0,1.98,2.22),(2.7,0.08,1.0),board,col["Interior"],angle,0.025)

    # Central media center and book-wall/book-island forms from project photos.
    hub=Vector((95.0,1958.0,0))
    for i in range(7):
        xx=hub.x-8.0+i*2.6
        make_box(f"Media center | bookcase {i+1}",(xx,hub.y+4.7,1.15),(2.1,0.42,1.9),partition,col["Interior"])
    # Photo-supported gym features: folding red bleachers, court markings and
    # hoops. Their exact wall positions remain schematic.
    gym=(156.0,1911.0)
    gym_angle=math.radians(-35)
    def gym_local(x,y,z):
        return (gym[0]+x*math.cos(gym_angle)-y*math.sin(gym_angle),
                gym[1]+x*math.sin(gym_angle)+y*math.cos(gym_angle),z)
    gym_floor=material("WLIS | gymnasium maple sport floor",(0.39,0.25,0.13),0.42)
    make_box("Gymnasium | maple court floor",gym_local(0,0,0.31),(24.4,21.2,0.12),gym_floor,col["Interior"],gym_angle,0.03)
    for row in range(5):
        pos=gym_local(0.0,12.4-row*0.72,0.48+row*0.26)
        make_box(f"Gymnasium | folding bleacher tier {row+1}",pos,(17.0,0.52,0.22),red,col["Interior"],gym_angle,0.035)
    line_material=material("WLIS | gym court stripe warm white",(0.96,0.92,0.78),0.4)
    for x in (-12.2,12.2):
        make_curve(f"Gym court | end boundary {x}",[gym_local(x,-10.5,0.39),gym_local(x,10.5,0.39)],0.065,line_material,col["Interior"])
    for y in (-10.5,10.5):
        make_curve(f"Gym court | sideline {y}",[gym_local(-12.2,y,0.39),gym_local(12.2,y,0.39)],0.065,line_material,col["Interior"])
    # Key and center circle are schematic markings for a standard school court.
    for cx in (-8.2,8.2):
        make_box(f"Gym court | key outline {cx}",gym_local(cx,0,0.40),(7.6,0.065,0.035),line_material,col["Interior"],gym_angle)
    circle_pts=[gym_local(2.2*math.cos(2*math.pi*i/48),2.2*math.sin(2*math.pi*i/48),0.40) for i in range(49)]
    make_curve("Gym court | center circle",circle_pts,0.055,line_material,col["Interior"])
    for side in (-1,1):
        make_box(f"Gymnasium | basketball backboard {side}",gym_local(side*11.1,0.0,3.25),(1.8,0.14,1.12),partition,col["Interior"],gym_angle)
        hoop=gym_local(side*10.45,0.0,2.78)
        points=[(hoop[0]+0.23*math.cos(2*math.pi*i/24),hoop[1]+0.23*math.sin(2*math.pi*i/24),hoop[2]) for i in range(25)]
        make_curve(f"Gymnasium | hoop rim {side}",points,0.035,red,col["Interior"])
    # Cafeteria service counter and multipurpose stage.
    make_box("Cafeteria | service counter",(145.0,1892.0,1.0),(12.0,1.2,1.7),partition,col["Interior"],math.radians(-35))


def main_entry(ring, brick, red, glass, roof, col):
    xs,ys=[x for x,y in ring],[y for x,y in ring]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    # Public photographs identify the south-facing entry by its exposed red
    # steel tower and asymmetric glazed canopy. Cardinal placement is estimated.
    ex,ey=145.0,1872.0
    for i,dx in enumerate((-5.6,5.6),1):
        make_box(f"Entry tower red steel column {i}",(ex+dx,ey-1.0,4.1),(0.28,0.30,8.2),red,col["Entry"])
        make_box(f"Entry tower brick pier {i}",(ex+dx,ey-0.40,1.9),(0.90,0.90,3.8),brick,col["Entry"])
    # The photographed entry has a tall red open-web portal, a sloped canopy,
    # masonry piers, and a broad glazed vestibule behind the steel structure.
    canopy_w=12.6
    make_box("Entry canopy front beam",(ex,ey-5.5,7.12),(canopy_w,0.28,0.28),red,col["Entry"])
    make_box("Entry canopy rear beam",(ex,ey+1.0,6.15),(canopy_w,0.26,0.26),red,col["Entry"])
    for i in range(9):
        xx=ex-(canopy_w*0.5-0.4)+i*(canopy_w-0.8)/8
        make_box(f"Entry canopy red rafter {i+1}",(xx,ey-2.25,6.65),(0.15,6.8,0.18),red,col["Entry"],math.radians(-8))
    # Triangulated red open-web trusses are visible from the pedestrian approach.
    for side in (-1,1):
        x=ex+side*(canopy_w*0.5-0.45)
        make_curve(f"Entry open-web red truss chord {side}",[(x,ey-5.4,7.12),(x,ey+0.9,6.15)],0.09,red,col["Entry"])
        for k in range(5):
            yy=ey-5.0+k*1.15
            z=7.06-k*0.17
            make_curve(f"Entry open-web red truss diagonal {side}-{k}",[(x,yy,z),(x,yy+1.15,z-0.18)],0.065,red,col["Entry"])
    make_box("Entry canopy translucent sloped roof",(ex,ey-2.25,6.78),(12.2,6.8,0.14),glass,col["Entry"],math.radians(-8))
    make_box("Entry glass vestibule",(ex,ey+0.18,2.55),(9.6,0.20,4.8),glass,col["Entry"])
    for s in range(11):
        xx=ex-4.75+s*0.95
        make_box(f"Vestibule mullion {s+1}",(xx,ey+0.05,2.55),(0.075,0.12,4.55),red,col["Entry"])
    # Flagpole and footpath/crosswalk directly in front of the entry.
    pole_x,pole_y=ex-8.0,ey-11.0
    make_box("Main entry flagpole",(pole_x,pole_y,6.1),(0.12,0.12,12.2),roof,col["Entry"])
    flag_white=material("WLIS | flag white",(0.93,0.92,0.85),0.55)
    flag_blue=material("WLIS | flag blue",(0.035,0.10,0.31),0.5)
    for stripe in range(7):
        stripe_mat=red if stripe%2==0 else flag_white
        make_box(f"American flag | stripe {stripe+1}",(pole_x+1.25,pole_y,10.20+stripe*0.155),(2.5,0.055,0.155),stripe_mat,col["Entry"])
    make_box("American flag | blue canton",(pole_x+0.46,pole_y-0.04,11.02),(0.92,0.06,0.58),flag_blue,col["Entry"])
    make_box("Front entry walk",(ex,ey-8.0,0.08),(8.0,16.0,0.16),roof,col["Entry"])


def camera_at(scene, name, position, target, lens=50):
    cam_data=bpy.data.cameras.new(name)
    cam=bpy.data.objects.new(name,cam_data)
    scene.collection.objects.link(cam)
    cam.location=position
    direction=Vector(target)-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    cam_data.lens=lens
    return cam


def setup_render(scene, ring, render_helpers):
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=1200
    scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGBA"
    scene.render.film_transparent=False
    scene.view_settings.view_transform="AgX"
    world=bpy.data.worlds.new("WLIS daylight sky") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world=world
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.33,0.45,0.62,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.42
    grass=material("WLIS | temporary render-only campus lawn",(0.18,0.25,0.12),0.92)
    # Presentation-only context plane for previews; it is deleted before the
    # standalone building library is saved.
    ground=make_box("PREVIEW ONLY | lawn ground plane",((min(x for x,y in ring)+max(x for x,y in ring))*0.5,
                     (min(y for x,y in ring)+max(y for x,y in ring))*0.5,-0.20),(420.0,420.0,0.20),grass,render_helpers)
    sun_data=bpy.data.lights.new("Large soft afternoon sun","SUN")
    sun=bpy.data.objects.new("Large soft afternoon sun",sun_data)
    scene.collection.objects.link(sun)
    sun.location=(200,1800,300)
    sun.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-25))
    sun_data.energy=2.0
    sun_data.angle=math.radians(18)
    for loc,power,size in [((120,1840,95),80000,75),((260,1970,75),55000,65)]:
        light_data=bpy.data.lights.new("Architectural fill","AREA")
        light=bpy.data.objects.new("Architectural fill",light_data)
        scene.collection.objects.link(light)
        light.location=loc
        light_data.energy=power
        light_data.shape="DISK"
        light_data.size=size
        light.rotation_euler=(0,0,0)
    xs,ys=[x for x,y in ring],[y for x,y in ring]
    target=((min(xs)+max(xs))*0.5,(min(ys)+max(ys))*0.5,3.2)
    return target


def render_views(scene, target, cols, ring):
    xs,ys=[x for x,y in ring],[y for x,y in ring]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    entry=(145.0,1872.0,3.4)
    gym_target=(156.0,1911.0,5.2)
    nw_target=(x0+46.0,y0+110.0,3.2)
    specs=[("preview_r3_aerial.png",(target[0],target[1],300),target,36),
           ("preview_r3_main_entry.png",(entry[0]+1,entry[1]-31,11),entry,48),
           ("preview_r3_northwest.png",(nw_target[0]-75,nw_target[1]+72,35),nw_target,48),
           ("preview_r3_gym.png",(gym_target[0]+52,gym_target[1]-45,23),gym_target,48)]
    cam=camera_at(scene,"WLIS review camera",specs[0][1],specs[0][2])
    scene.camera=cam
    for filename,pos,view_target,lens in specs:
        cam.location=pos
        cam.data.lens=lens
        direction=Vector(view_target)-cam.location
        cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=os.path.join(AUDIT,filename)
        bpy.ops.render.render(write_still=True)
    # Cutaway view uses the same asset but temporarily hides its exterior so
    # the source-informed gym/classroom schematic can be reviewed from above.
    hidden_cols=[cols[k] for k in ("Shell","Facade","Roof","Entry")]
    for c in hidden_cols: c.hide_render=True
    floor_obj=bpy.data.objects.get("Main finished floor | GIS clipped footprint")
    if floor_obj: floor_obj.hide_render=True
    scene.camera=cam
    cam.location=(target[0]+18,target[1]-28,95)
    cam.data.lens=56
    direction=Vector((target[0],target[1],0))-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=os.path.join(AUDIT,"preview_r3_interior_cutaway.png")
    bpy.ops.render.render(write_still=True)
    # Close, near-plan review views isolate the source-supported classroom
    # furniture and gym court so the schematic arrangement is clearly visible.
    # Trusses stay in the saved model and exterior view, but are hidden for the
    # interior renders so they do not obscure the court below.
    trusses=[o for o in cols["Interior"].objects if o.name.startswith("Gym red steel roof truss")]
    for o in trusses: o.hide_render=True
    representative=classroom_sites(ring)[0][0]
    interior_specs=[
        ("preview_r3_classroom_interior.png",(representative.x,representative.y,12),(representative.x,representative.y,0.4),8.8),
        ("preview_r3_gym_interior.png",(156,1911,29),(156,1911,0.3),31.0)]
    for filename,pos,view_target,scale in interior_specs:
        if floor_obj: floor_obj.hide_render=False
        cam.location=pos
        cam.data.type="ORTHO"
        cam.data.ortho_scale=scale
        if filename in ("preview_r3_classroom_interior.png","preview_r3_gym_interior.png"):
            cam.rotation_euler=(0.0,0.0,0.0)
        else:
            direction=Vector(view_target)-cam.location
            cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=os.path.join(AUDIT,filename)
        bpy.ops.render.render(write_still=True)
    cam.data.type="PERSP"
    for o in trusses: o.hide_render=False
    for c in hidden_cols: c.hide_render=False
    if floor_obj: floor_obj.hide_render=False
    bpy.data.objects.remove(cam,do_unlink=True)


def remove_render_helpers(scene, root):
    asset_objects=set(root.all_objects)
    for obj in list(scene.objects):
        if obj not in asset_objects:
            bpy.data.objects.remove(obj,do_unlink=True)


def main():
    os.makedirs(AUDIT,exist_ok=True)
    scene,root,cols=make_collections()
    render_helpers=bpy.data.collections.new("WLIS temporary preview context")
    scene.collection.children.link(render_helpers)
    ring=make_ring()
    mats={
        "brick":material("WLIS | red-brown running-bond brick",(0.38,0.11,0.065),0.86,0.0,"brick"),
        "roof":material("WLIS | charcoal low-slope roof membrane",(0.62,0.65,0.63),0.82),
        "panel":material("WLIS | warm light-gray metal panels",(0.68,0.68,0.63),0.62,0.18,"metal_panel"),
        "glass":material("WLIS | blue-gray glazing",(0.12,0.22,0.28),0.22,0.48),
        "trim":material("WLIS | pale aluminum window frames",(0.75,0.78,0.77),0.4,0.55),
        "steel":material("WLIS | exposed structural crimson steel",(0.72,0.025,0.035),0.35,0.62),
        "floor":material("WLIS | terrazzo and classroom floor",(0.56,0.54,0.48),0.7,0.0,"tile"),
        "partition":material("WLIS | warm white interior partitions",(0.82,0.80,0.73),0.82),
        "furniture":material("WLIS | maple classroom furniture",(0.43,0.25,0.10),0.58),
        "board":material("WLIS | dark classroom teaching board",(0.055,0.12,0.13),0.65),
    }
    add_shell(ring,mats["brick"],mats["roof"],cols["Shell"])
    facade(ring,mats["brick"],mats["glass"],mats["trim"],mats["panel"],cols)
    structural_volumes(ring,mats["brick"],mats["panel"],mats["glass"],mats["steel"],mats["roof"],cols)
    classroom_interior(ring,mats["floor"],mats["partition"],mats["glass"],mats["steel"],mats["furniture"],mats["board"],cols)
    main_entry(ring,mats["brick"],mats["steel"],mats["glass"],mats["roof"],cols)
    target=setup_render(scene,ring,render_helpers)
    scene.render.resolution_percentage=75
    render_views(scene,target,cols,ring)
    bpy.data.collections.remove(render_helpers)
    remove_render_helpers(scene,root)
    scene.render.resolution_percentage=100
    # Keep the stable expected collection and scene names. Geometry remains
    # in campus-world coordinates because this manifest entry is a massing type.
    scene.render.filepath="//"
    bpy.ops.wm.save_as_mainfile(filepath=ASSET)
    print("WLIS_BUILD_COMPLETE",ASSET,"OBJECTS",len(root.all_objects),"RING",len(ring))


if __name__ == "__main__":
    main()
