"""Build a source-traceable detailed St Thomas Aquinas Catholic Center asset."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
ASSET_PATH = ROOT / "modular/buildings/massing_st_thomas_aquinas_5535390.blend"
EVIDENCE_PATH = AUDIT / "projected_footprint_evidence.json"
ASSET_ID = "massing_st_thomas_aquinas_5535390"
COLLECTION_NAME = "Asset_massing_st_thomas_aquinas_5535390"
SCENE_NAME = "Building_massing_st_thomas_aquinas_5535390"

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
outline = [tuple(p) for p in evidence["local_outline_xy_m"][:-1]]
parts = {name: [tuple(p) for p in coordinates[:-1]]
         for name, coordinates in evidence["footprint_parts_local_xy_m"].items()}
origin_xy = evidence["project_origin_xy_m"]

def signed_area(points):
    return sum(points[i][0]*points[(i+1)%len(points)][1] - points[(i+1)%len(points)][0]*points[i][1]
               for i in range(len(points))) / 2

if signed_area(outline) < 0:
    outline.reverse()
for coordinates in parts.values():
    if signed_area(coordinates) < 0:
        coordinates.reverse()

scene = bpy.context.scene
if scene.name != SCENE_NAME:
    raise RuntimeError(f"Unexpected source scene {scene.name!r}; expected {SCENE_NAME!r}")
asset = bpy.data.collections.get(COLLECTION_NAME)
if asset is None:
    raise RuntimeError(f"Missing stable exported collection {COLLECTION_NAME}")
for obj in list(asset.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for child in list(asset.children):
    asset.children.unlink(child)
root = bpy.data.objects.new("AssetRoot_" + ASSET_ID, None)
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 1.0
asset.objects.link(root)
root["asset_id"] = ASSET_ID
root["coordinate_frame"] = "LOCAL METERS; campus placement origin supplied by modular manifest"
root["placement_origin_xy_m"] = list(origin_xy)
asset["asset_id"] = ASSET_ID
asset["GIS_feature_id"] = 852
asset["OSM_way_id"] = 117396617
asset["design_components"] = "original church; new church addition; office/classroom addition"

def material(name, color, roughness=0.75, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

def brick_material():
    mat = material("SOTAC_Procedural_Red_Brick", (0.34, 0.105, 0.065), 0.86)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.location = (620, 80)
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-820, 80)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-650, 80)
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    brick = nodes.new("ShaderNodeTexBrick")
    brick.location = (-400, 100)
    brick.inputs["Color1"].default_value = (0.42, 0.145, 0.085, 1)
    brick.inputs["Color2"].default_value = (0.26, 0.067, 0.045, 1)
    brick.inputs["Mortar"].default_value = (0.22, 0.19, 0.16, 1)
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Brick Width"].default_value = 0.28
    brick.inputs["Row Height"].default_value = 0.075
    brick.inputs["Mortar Size"].default_value = 0.018
    brick.inputs["Mortar Smooth"].default_value = 0.08
    links.new(mapping.outputs["Vector"], brick.inputs["Vector"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-390, -190)
    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 3.0
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.location = (360, -120)
    bump.inputs["Strength"].default_value = 0.24
    bump.inputs["Distance"].default_value = 0.075
    links.new(brick.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    return mat

def roof_material(name, base):
    mat = material(name, base, 0.68)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-620, 0)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 8.0
    noise.inputs["Detail"].default_value = 3.0
    links.new(texcoord.outputs["Object"], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.24
    ramp.color_ramp.elements[0].color = (*[v * 0.68 for v in base], 1)
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (*[min(v * 1.28, 1) for v in base], 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.18
    bump.inputs["Distance"].default_value = 0.035
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat

def glass_material(name, color, roughness=0.24, transmission=0.12):
    mat = material(name, color, roughness, 0.08)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Metallic"].default_value = 0.05
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = transmission
    return mat

brick = brick_material()
brick_tower = material("SOTAC_Tower_Brick", (0.31, 0.085, 0.052), 0.86)
stone = material("SOTAC_Limestone_Trim", (0.73, 0.68, 0.57), 0.62)
stone_dark = material("SOTAC_Stone_Base", (0.43, 0.42, 0.38), 0.82)
roof_red = roof_material("SOTAC_Clay_Slate_Roof", (0.22, 0.07, 0.045))
roof_dark = roof_material("SOTAC_Charcoal_Roof_Membrane", (0.095, 0.105, 0.115))
wood = material("SOTAC_Warm_Oak", (0.31, 0.16, 0.075), 0.48)
wood_light = material("SOTAC_Pew_Oak", (0.49, 0.29, 0.13), 0.48)
bronze = material("SOTAC_Bronze", (0.29, 0.19, 0.075), 0.36, 0.72)
gold = material("SOTAC_Sign_Lettering_Gold", (0.70, 0.49, 0.16), 0.36, 0.45)
dark = material("SOTAC_Recess_Shadow", (0.035, 0.043, 0.052), 0.72)
interior_wall = material("SOTAC_Interior_Warm_Plaster", (0.79, 0.76, 0.68), 0.84)
interior_brick = material("SOTAC_Interior_Exposed_Brick", (0.33, 0.16, 0.105), 0.88)
glass = glass_material("SOTAC_Glazing_Deep_Blue", (0.08, 0.16, 0.21), 0.23, 0.2)
stained = [glass_material(f"SOTAC_Stained_Glass_{n}", c, 0.27, 0.08) for n, c in enumerate(
    [(0.12, 0.27, 0.43), (0.46, 0.15, 0.12), (0.78, 0.55, 0.20), (0.17, 0.36, 0.24)])]
floor_mat = material("SOTAC_Interior_Limestone_Floor", (0.52, 0.51, 0.47), 0.7)
metal_dark = material("SOTAC_Dark_Metal", (0.105, 0.12, 0.125), 0.38, 0.62)

def link_mesh(name, verts, faces, mat, bevel=0.0, collection=asset):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate(clean_customdata=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = root
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Softened architectural edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        normal = obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
        normal.keep_sharp = True
    return obj

def poly_extrude(name, points, z0, z1, mat, bevel=0.035):
    pts = list(points)
    if len(pts) > 1 and math.hypot(pts[0][0]-pts[-1][0], pts[0][1]-pts[-1][1]) < 1e-5:
        pts.pop()
    if signed_area(pts) < 0:
        pts.reverse()
    n = len(pts)
    verts = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    faces = [tuple(range(n-1, -1, -1)), tuple(range(n, 2*n))]
    faces.extend((i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n))
    return link_mesh(name, verts, faces, mat, bevel)

def box_mesh(name, location, dimensions, mat, angle=0.0, bevel=0.025, collection=asset):
    x, y, z = (float(v) for v in dimensions)
    verts = [(-x/2,-y/2,-z/2),(x/2,-y/2,-z/2),(x/2,y/2,-z/2),(-x/2,y/2,-z/2),
             (-x/2,-y/2,z/2),(x/2,-y/2,z/2),(x/2,y/2,z/2),(-x/2,y/2,z/2)]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    obj = link_mesh(name, verts, faces, mat, bevel, collection)
    obj.location = location
    obj.rotation_euler.z = angle
    return obj

def beam(name, a, b, width, depth, mat, bevel=0.02):
    av, bv = Vector(a), Vector(b)
    delta = bv - av
    obj = box_mesh(name, (av+bv)*0.5, (width, depth, delta.length), mat, bevel=bevel)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    return obj

def ring_parapet(name, points, z0, height, thickness, mat):
    pts = list(points)
    if len(pts) > 1 and math.hypot(pts[0][0]-pts[-1][0], pts[0][1]-pts[-1][1]) < 1e-5:
        pts.pop()
    if signed_area(pts) < 0:
        pts.reverse()
    for i, p in enumerate(pts):
        q = pts[(i+1)%len(pts)]
        dx, dy = q[0]-p[0], q[1]-p[1]
        length = math.hypot(dx, dy)
        if length < 0.8:
            continue
        angle = math.atan2(dy, dx)
        n = Vector((dy/length, -dx/length, 0))
        mid = Vector(((p[0]+q[0])/2, (p[1]+q[1])/2, z0+height/2)) + n * (thickness*0.15)
        box_mesh(f"{name}_{i:02d}", mid, (length+0.07, thickness, height), mat, angle, 0.015)

def point_in_poly(point, polygon):
    x, y = point
    inside = False
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[i-1]
        if ((yi > y) != (yj > y)) and (x < (xj-xi) * (y-yi) / ((yj-yi) or 1e-12) + xi):
            inside = not inside
    return inside

def outer_frame_window(base, seg, idx, t, s, sill, width, height, stained_glass=False):
    p, q = Vector(seg[0]), Vector(seg[1])
    axis = (q-p).normalized()
    outward = Vector((axis.y, -axis.x))
    center = p.lerp(q, t)
    ang = math.atan2(axis.y, axis.x)
    center3 = Vector((center.x, center.y, sill+height/2)) + Vector((outward.x,outward.y,0))*0.12
    frame_t, side = 0.12, 0.10
    pane_mat = stained[idx % len(stained)] if stained_glass else glass
    box_mesh(f"SOTAC_Window_{base}_{idx:03d}_Glass", center3, (width-0.18, 0.08, height-0.18), pane_mat, ang, 0.012)
    for sx in (-1,1):
        pos = center3 + Vector((axis.x,axis.y,0))*sx*(width/2-side/2)
        box_mesh(f"SOTAC_Window_{base}_{idx:03d}_Jamb{sx}", pos, (side, frame_t, height), stone, ang, 0.018)
    for sz in (-1,1):
        pos = center3 + Vector((0,0,sz*(height/2-frame_t/2)))
        box_mesh(f"SOTAC_Window_{base}_{idx:03d}_HeadSill{sz}", pos, (width, frame_t, frame_t), stone, ang, 0.018)
    mullion_count = 2 if stained_glass else 1
    for m in range(1,mullion_count+1):
        pos = center3 + Vector((axis.x,axis.y,0))*(-width/2+width*m/(mullion_count+1))
        box_mesh(f"SOTAC_Window_{base}_{idx:03d}_Mullion{m}", pos, (0.045,0.08,height-0.22), bronze, ang, 0.006)
    if stained_glass:
        # Thin horizontal leading separates the color panes without overloading the facade.
        for zfraction in (0.34, 0.68):
            pos = center3 + Vector((0,0,(zfraction-0.5)*(height-0.18)))
            box_mesh(f"SOTAC_Window_{base}_{idx:03d}_Lead{zfraction}", pos, (width-0.2,0.075,0.035), bronze, ang, 0.004)

def add_front_entry():
    # North street frontage, near the central entrance recess shown in Purdue/WBAA photos.
    x, y = -6.8, max(p[1] for p in outline)-0.04
    # Stone surround and inset paired wood doors.
    box_mesh("SOTAC_MainEntry_DoorPair", (x,y-0.08,1.65), (2.25,0.18,3.1), wood, 0, 0.035)
    for side in (-1,1):
        box_mesh(f"SOTAC_MainEntry_DoorLeaf{side}", (x+side*0.55,y-0.19,1.66), (0.98,0.08,2.93), wood_light, 0, 0.025)
        box_mesh(f"SOTAC_MainEntry_Panel{side}", (x+side*0.55,y-0.245,1.64), (0.72,0.025,2.15), wood, 0, 0.018)
        beam(f"SOTAC_MainEntry_Handle{side}",(x+side*0.15,y-0.30,1.35),(x+side*0.15,y-0.30,1.75),0.04,0.04,bronze,0.01)
    for side in (-1,1):
        box_mesh(f"SOTAC_MainEntry_Pilaster{side}", (x+side*1.28,y-0.08,2.1), (0.28,0.35,4.1), stone, 0, 0.025)
    box_mesh("SOTAC_MainEntry_Lintel", (x,y-0.08,4.17), (2.8,0.45,0.34), stone, 0, 0.025)
    # Flat welcoming canopy with three discreet supports.
    box_mesh("SOTAC_MainEntry_Canopy", (x,y+0.72,4.55), (6.4,2.05,0.28), roof_dark, 0, 0.035)
    for px in (-2.55,2.55):
        beam(f"SOTAC_MainEntry_CanopyPost_{px}",(x+px,y+1.55,0.45),(x+px,y+1.55,4.4),0.12,0.12,metal_dark,0.015)
    # Two small accessibility ramp runs and restrained handrails, kept as recent parish context.
    ramp_y = y+3.0
    ramp = box_mesh("SOTAC_Accessible_Ramp",(x+4.2,ramp_y,0.24),(2.1,5.0,0.38),stone_dark,0.0,0.04)
    for side in (-1,1):
        beam(f"SOTAC_Ramp_Handrail_{side}",(x+4.2+side*0.92,ramp_y-2.3,0.65),(x+4.2+side*0.92,ramp_y+2.3,1.1),0.055,0.055,metal_dark)
    # Gold sign; text plane is oriented outward (+Y) and flipped vertically for an upright sign.
    text_data = bpy.data.curves.new("SOTAC_Facade_Sign_Text", "FONT")
    text_data.body = "ST. THOMAS AQUINAS\nTHE CATHOLIC CENTER AT PURDUE"
    text_data.size = 0.48
    text_data.space_line = 1.05
    text_data.align_x = "CENTER"
    text_data.align_y = "CENTER"
    text_data.extrude = 0.012
    text_data.bevel_depth = 0.003
    text_obj = bpy.data.objects.new("SOTAC_Facade_Sign_Lettering", text_data)
    asset.objects.link(text_obj)
    text_obj.parent = root
    text_obj.location = (x, y+0.08, 5.45)
    text_obj.rotation_euler.x = -math.pi/2
    text_obj.scale.y = -1
    text_data.materials.append(gold)

def add_bell_tower():
    # Photo-supported brick bell tower and cross; exact shaft dimensions remain unverified.
    tx, ty = -15.0, 24.5
    width = 5.8
    box_mesh("SOTAC_BellTower_Shaft",(tx,ty,7.3),(width,width,14.0),brick_tower,0.0,0.04)
    for z in (1.0,5.5,10.5,14.6):
        box_mesh(f"SOTAC_BellTower_StoneBand_{z}",(tx,ty,z),(width+0.28,width+0.28,0.25),stone,0,0.018)
    # Paired belfry recesses on four sides; dark inset glazing and stone archivolts suggest open bell bays.
    for side,ang in (("N",0),("S",0),("E",math.pi/2),("W",math.pi/2)):
        if side == "N":
            surf=(tx,ty+width/2+0.07); normal=(0,1)
        elif side == "S":
            surf=(tx,ty-width/2-0.07); normal=(0,-1)
        elif side == "E":
            surf=(tx+width/2+0.07,ty); normal=(1,0)
        else:
            surf=(tx-width/2-0.07,ty); normal=(-1,0)
        for j,offset in enumerate((-1.15,1.15)):
            center=Vector((surf[0],surf[1],13.4)) + Vector((normal[0],normal[1],0))*0.03
            axis=Vector((1,0,0)) if side in ("N","S") else Vector((0,1,0))
            center += axis*offset
            box_mesh(f"SOTAC_Belfry_{side}_{j}_Recess",center,(0.78,0.12,2.3),dark,ang,0.02)
            box_mesh(f"SOTAC_Belfry_{side}_{j}_Louver",center+Vector((0,0,0.07)),(0.5,0.15,1.35),wood,ang,0.015)
            for zz in (12.65,13.05,13.45,13.85,14.25):
                beam(f"SOTAC_Belfry_{side}_{j}_LouverBar_{zz}",
                     (center.x-0.27,center.y,zz),(center.x+0.27,center.y,zz),0.045,0.045,metal_dark)
    box_mesh("SOTAC_BellTower_Cornice",(tx,ty,15.1),(width+0.9,width+0.9,0.72),stone,0,0.035)
    # Compact hipped copper cap with four panels and a cross, not a monumental steeple.
    verts=[(tx-width/2-0.15,ty-width/2-0.15,15.5),(tx+width/2+0.15,ty-width/2-0.15,15.5),
           (tx+width/2+0.15,ty+width/2+0.15,15.5),(tx-width/2-0.15,ty+width/2+0.15,15.5),
           (tx,ty,18.0)]
    link_mesh("SOTAC_BellTower_CopperCap",verts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],roof_dark,0.015)
    beam("SOTAC_BellTower_Cross_Stem",(tx,ty,17.7),(tx,ty,20.1),0.18,0.12,bronze,0.02)
    beam("SOTAC_BellTower_Cross_Arms",(tx-0.78,ty,19.1),(tx+0.78,ty,19.1),0.16,0.12,bronze,0.02)

def add_sanctuary_interior():
    # The public chapel image supports pew rows, a raised altar, brick arch and warm beam ceiling.
    # Program and furniture layout remain schematic; the dimensions are not represented as surveyed.
    box_mesh("SOTAC_Interior_Sanctuary_Floor",(9.0,9.0,0.62),(23.0,30.0,0.10),floor_mat,0,0.0)
    # Worship space side piers and two-level brick wainscot.
    for x in (-2.0,20.0):
        for y in (-5.0,0.0,5.0,10.0,15.0,20.0,25.0):
            box_mesh(f"SOTAC_Interior_Sanctuary_Pier_{x}_{y}",(x,y,3.55),(0.45,0.5,5.8),interior_brick,0,0.025)
    # Two banks of oak pews with a broad central aisle.
    def pew_mesh(name, cx, cy, width=8.3):
        components=[]
        def add_box(x,y,z,dx,dy,dz):
            components.append((x,y,z,dx,dy,dz))
        add_box(cx,cy,0.92,width,0.46,0.16)
        add_box(cx,cy+0.19,1.45,width,0.13,1.0)
        add_box(cx-width*0.35,cy,0.48,0.12,0.28,0.85)
        add_box(cx+width*0.35,cy,0.48,0.12,0.28,0.85)
        verts=[]; faces=[]
        for x,y,z,dx,dy,dz in components:
            v=[(x-dx/2,y-dy/2,z-dz/2),(x+dx/2,y-dy/2,z-dz/2),(x+dx/2,y+dy/2,z-dz/2),(x-dx/2,y+dy/2,z-dz/2),
               (x-dx/2,y-dy/2,z+dz/2),(x+dx/2,y-dy/2,z+dz/2),(x+dx/2,y+dy/2,z+dz/2),(x-dx/2,y+dy/2,z+dz/2)]
            start=len(verts);verts.extend(v)
            faces.extend([tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
        return link_mesh(name,verts,faces,wood_light,0.035)
    row=0
    for y in (-3.5,-1.1,1.3,3.7,6.1,8.5,10.9,13.3,15.7,18.1):
        pew_mesh(f"SOTAC_Interior_Pew_Left_{row:02d}",4.3,y)
        pew_mesh(f"SOTAC_Interior_Pew_Right_{row:02d}",13.7,y)
        row+=1
    # Three stepped stone platform and timber altar table at the north end.
    box_mesh("SOTAC_Altar_Platform_1",(9.0,24.2,0.85),(13.0,4.0,0.5),stone_dark,0,0.03)
    box_mesh("SOTAC_Altar_Platform_2",(9.0,25.1,1.18),(10.0,2.2,0.4),stone,0,0.03)
    box_mesh("SOTAC_Altar_Table_Top",(9.0,26.0,1.8),(4.5,1.25,0.28),stone,0,0.025)
    box_mesh("SOTAC_Altar_Table_Base",(9.0,26.0,1.3),(0.32,0.95,0.78),wood,0,0.02)
    for x in (6.9,11.1):
        box_mesh(f"SOTAC_Altar_Candle_{x}",(x,25.75,2.55),(0.13,0.13,0.8),stone,0,0.012)
    box_mesh("SOTAC_Ambo_Base",(3.5,23.0,1.35),(0.85,0.75,1.25),wood,0,0.03)
    box_mesh("SOTAC_Ambo_Top",(3.5,23.0,2.05),(1.2,0.95,0.12),wood_light,0,0.025)
    # Brick arch ring at the altar wall, with a simple crucifix focal point.
    arch_y=28.0
    box_mesh("SOTAC_Altar_Arch_Left",(5.0,arch_y,4.45),(0.55,0.65,5.4),interior_brick,0,0.015)
    box_mesh("SOTAC_Altar_Arch_Right",(13.0,arch_y,4.45),(0.55,0.65,5.4),interior_brick,0,0.015)
    for i in range(12):
        a0=math.pi*i/12
        a1=math.pi*(i+1)/12
        p0=(9.0+4.0*math.cos(a0),arch_y,7.15+2.7*math.sin(a0))
        p1=(9.0+4.0*math.cos(a1),arch_y,7.15+2.7*math.sin(a1))
        beam(f"SOTAC_Altar_Arch_Voussoir_{i:02d}",p0,p1,0.67,0.55,interior_brick,0.015)
    box_mesh("SOTAC_Altar_Arch_Inset",(9.0,28.36,5.1),(7.0,0.08,7.0),interior_wall,0,0.0)
    # Stylized contemporary geometric altar panel and crucifix, guided by public ceremony photos.
    panel_colors=[material("SOTAC_Altar_Accent_Green",(0.24,0.39,0.23),0.6),
                  material("SOTAC_Altar_Accent_Gold",(0.65,0.42,0.13),0.56),
                  material("SOTAC_Altar_Accent_Charcoal",(0.11,0.12,0.12),0.62)]
    for i in range(7):
        xx=6.1+i*0.97
        box_mesh(f"SOTAC_Altar_AccentPanel_{i}",(xx,28.25,6.15),(0.72,0.05,1.5),panel_colors[i%3],0,0.015)
    beam("SOTAC_Interior_Crucifix_Stem",(9.0,27.95,6.2),(9.0,27.95,8.25),0.17,0.12,wood,0.025)
    beam("SOTAC_Interior_Crucifix_Arms",(8.2,27.95,7.55),(9.8,27.95,7.55),0.16,0.12,wood,0.025)
    # Exposed timber trusses and small pendant fittings make the worship volume legible.
    for j,y in enumerate((-3.0,2.0,7.0,12.0,17.0,22.0)):
        beam(f"SOTAC_CeilingTruss_{j}_Tie",(-1.0,y,7.7),(19.0,y,7.7),0.22,0.22,wood,0.025)
        beam(f"SOTAC_CeilingTruss_{j}_NorthSlope",(-1.0,y,7.7),(9.0,y,11.2),0.16,0.17,wood,0.02)
        beam(f"SOTAC_CeilingTruss_{j}_SouthSlope",(9.0,y,11.2),(19.0,y,7.7),0.16,0.17,wood,0.02)
        beam(f"SOTAC_CeilingTruss_{j}_WebA",(4.0,y,7.7),(9.0,y,9.45),0.09,0.09,bronze,0.01)
        beam(f"SOTAC_CeilingTruss_{j}_WebB",(14.0,y,7.7),(9.0,y,9.45),0.09,0.09,bronze,0.01)
        box_mesh(f"SOTAC_Sanctuary_Pendant_{j}",(9.0,y,8.2),(0.3,0.3,0.15),gold,0,0.02)
    # Small baptismal font at the entrance end.
    box_mesh("SOTAC_Baptismal_Font_Base",(17.2,-4.7,0.96),(0.85,0.85,0.62),stone,0,0.035)
    box_mesh("SOTAC_Baptismal_Font_Bowl",(17.2,-4.7,1.35),(1.25,1.25,0.24),stone,0,0.04)

def add_classroom_interior():
    # Office/classroom addition: schematic classrooms and a shared office/gathering corridor.
    zone=parts["office_classroom_addition_south"]
    xs=[p[0] for p in zone]; ys=[p[1] for p in zone]
    xmin,xmax,ymin,ymax=min(xs),max(xs),min(ys),max(ys)
    box_mesh("SOTAC_Interior_OfficeWing_Floor",((xmin+xmax)/2,(ymin+ymax)/2,0.63),(xmax-xmin-1,ymax-ymin-1,0.09),floor_mat,0,0.0)
    # Two light partition walls; all exact classroom divisions remain unverified.
    for x in (-3.6,5.0):
        box_mesh(f"SOTAC_Office_Interior_Partition_{x}",(x,(ymin+ymax)/2,2.7),(0.12,ymax-ymin-2,4.0),interior_wall,0,0.01)
    for i,y in enumerate((ymin+5.0,ymin+12.0,ymin+19.0)):
        box_mesh(f"SOTAC_Classroom_Table_{i}",(0.0,y,1.05),(3.0,1.2,0.15),wood_light,0,0.02)
        for side in (-1,1):
            for j in (-1,0,1):
                box_mesh(f"SOTAC_Classroom_Chair_{i}_{side}_{j}",(j*0.85,y+side*1.1,0.85),(0.52,0.52,0.75),wood,0,0.025)
    for x in (-7.0,11.5):
        box_mesh(f"SOTAC_Office_Bookcase_{x}",(x,ymin+3.5,1.9),(2.5,0.46,2.4),wood,0,0.035)
        for row in range(3):
            box_mesh(f"SOTAC_Office_BookcaseShelf_{x}_{row}",(x,ymin+3.5,1.1+row*0.65),(2.4,0.52,0.08),wood_light,0,0.01)

def add_site_trim():
    # Limestone base, understated street-side steps, wall lights, and planters.
    ring_parapet("SOTAC_Limestone_BaseBand",outline,0.52,0.35,0.22,stone)
    # Corner pilasters at the building's straight outer corners only.
    for i,p in enumerate(outline):
        prev=outline[i-1]; nxt=outline[(i+1)%len(outline)]
        a=Vector(p)-Vector(prev); b=Vector(nxt)-Vector(p)
        if a.length>5.0 and b.length>5.0:
            box_mesh(f"SOTAC_Corner_Pilaster_{i}",(p[0],p[1],3.15),(0.36,0.36,5.3),stone,0,0.018)
    for side in (-1,1):
        box_mesh(f"SOTAC_Entrance_Planter_{side}",(-10.2+side*3.9,max(p[1] for p in outline)+1.05,0.55),(1.35,0.72,0.62),stone_dark,0,0.04)
        for n in range(3):
            box_mesh(f"SOTAC_Entrance_Planter_Greenery_{side}_{n}",(-10.2+side*3.9+(n-1)*0.36,max(p[1] for p in outline)+1.05,1.05),(0.3,0.3,0.72),material("SOTAC_Leaf_Green",(0.12,0.25,0.11),0.82),0,0.12)
    # Narrow tower louver lights and brass sconces at the street entrance.
    for x in (-9.2,-4.4):
        box_mesh(f"SOTAC_Entrance_Wall_Sconce_{x}",(x,max(p[1] for p in outline)-0.18,4.0),(0.22,0.12,0.62),bronze,0,0.025)

# Architectural massing follows the exact GIS/OSM plan outline. The component split is an explicitly
# approximate architectural interpretation; the parish documents the three connected structures.
poly_extrude("SOTAC_Stone_Foundation_and_Plinth",outline,0.0,0.64,stone_dark,0.035)
poly_extrude("SOTAC_Continuous_Brick_Base_Shell",outline,0.64,6.15,brick,0.035)
west=parts["original_church_west"]
east=parts["new_church_addition_east"]
south=parts["office_classroom_addition_south"]
poly_extrude("SOTAC_Original_Church_Upper_Walls",west,6.05,8.35,brick,0.025)
poly_extrude("SOTAC_New_Church_Addition_Upper_Walls",east,6.05,8.35,brick,0.025)
poly_extrude("SOTAC_Office_Classroom_Upper_Walls",south,6.05,6.85,brick,0.025)

# West nave: shallow red sloped roof with ridge running north-south, eaves, gutters, and ridge cap.
west_bounds=(min(p[0] for p in west),min(p[1] for p in west),max(p[0] for p in west),max(p[1] for p in west))
wx0,wy0,wx1,wy1=west_bounds
ridge_x=(wx0+wx1)/2
eave=8.45
peak=12.2
over=0.38
left=[(wx0-over,wy0-over,eave),(ridge_x,wy0-over,peak),(ridge_x,wy1+over,peak),(wx0-over,wy1+over,eave)]
right=[(ridge_x,wy0-over,peak),(wx1+over,wy0-over,eave),(wx1+over,wy1+over,eave),(ridge_x,wy1+over,peak)]
link_mesh("SOTAC_Original_Church_Gable_Roof_West",left,[(0,1,2,3)],roof_red,0.02)
link_mesh("SOTAC_Original_Church_Gable_Roof_East",right,[(0,1,2,3)],roof_red,0.02)
beam("SOTAC_Original_Church_RidgeCap",(ridge_x,wy0-over,peak+0.04),(ridge_x,wy1+over,peak+0.04),0.22,0.22,metal_dark,0.02)
for side,x in (("W",wx0-over),("E",wx1+over)):
    beam(f"SOTAC_Original_Church_Eave_{side}",(x,wy0-over,eave),(x,wy1+over,eave),0.18,0.22,metal_dark,0.015)
    for y in (wy0+2.0,wy1-2.0):
        beam(f"SOTAC_Original_Church_Downspout_{side}_{y}",(x,y,0.75),(x,y,eave-0.05),0.10,0.10,metal_dark,0.01)

# New church roof and lower office roof: low-slope dark membranes with image-estimated parapets.
poly_extrude("SOTAC_New_Church_Roof_Slab",east,8.25,8.55,roof_dark,0.018)
ring_parapet("SOTAC_New_Church_Roof_Parapet",east,8.5,0.52,0.26,brick_tower)
poly_extrude("SOTAC_Office_Classroom_Roof_Slab",south,6.85,7.18,roof_dark,0.018)
ring_parapet("SOTAC_Office_Classroom_Roof_Parapet",south,7.15,0.45,0.22,brick_tower)

# Mark component joints and articulate parapets without asserting exact construction dates.
ring_parapet("SOTAC_New_Church_Stone_Coping",east,8.98,0.12,0.32,stone)
ring_parapet("SOTAC_Office_Wing_Coping",south,7.58,0.12,0.30,stone)

# Window placement follows the external GIS ring, not guessed rectangular bounding boxes.
zone_specs=[("original_church_west",west,True),("new_church_addition_east",east,True),
            ("office_classroom_addition_south",south,False)]
for seg_i,p in enumerate(outline):
    q=outline[(seg_i+1)%len(outline)]
    delta=Vector(q)-Vector(p)
    length=delta.length
    if length<3.1:
        continue
    mid=(Vector(p)+Vector(q))*0.5
    if mid.y < -8.05:
        zone_name="office_classroom_addition_south"; sanctuary=False
    elif mid.x < -3.05:
        zone_name="original_church_west"; sanctuary=True
    else:
        zone_name="new_church_addition_east"; sanctuary=True
    axis=delta.normalized()
    # Do not fill the north main-door bay with glass.
    nwin=max(1,int((length-1.8)//(3.5 if sanctuary else 3.0)))
    width=1.18 if sanctuary else 1.28
    height=3.15 if sanctuary else 1.45
    sill=1.75 if sanctuary else 1.15
    floors=[sill] if sanctuary else [sill,4.05]
    for floor_index,zbottom in enumerate(floors):
        for bay in range(nwin):
            t=(bay+1)/(nwin+1)
            center=Vector(p).lerp(Vector(q),t)
            # Main entry occupies a wider recess on the north-front edge.
            if abs(center.y-max(p[1] for p in outline))<0.4 and -9.2<center.x<-4.5:
                continue
            outer_frame_window(zone_name, (p,q), seg_i*10+floor_index*nwin+bay,
                               t, bay, zbottom, width, height, sanctuary and (seg_i%2==0))

add_front_entry()
add_bell_tower()
add_sanctuary_interior()
add_classroom_interior()
add_site_trim()

# Prepare a hierarchy, keep every model object in the stable exported collection, and retain an identity root.
for obj in list(asset.objects):
    if obj is not root and obj.parent is None:
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
root.location=(0.0,0.0,0.0)
root.rotation_euler=(0.0,0.0,0.0)
root.scale=(1.0,1.0,1.0)
scene.unit_settings.system="METRIC"
scene.unit_settings.scale_length=1.0
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1200
scene.render.resolution_y=850
scene.render.resolution_percentage=100
scene.camera=None
for obj in asset.objects:
    if obj.type=="MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = False

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
sha=hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
result={"status":"saved","asset":str(ASSET_PATH),"sha256":sha,"scene":scene.name,
        "collection":asset.name,"object_count":len(asset.all_objects),"mesh_count":sum(o.type=="MESH" for o in asset.all_objects),
        "materials":[m.name for m in bpy.data.materials if m.name.startswith("SOTAC_")],
        "identity_root":{"location":list(root.location),"rotation":list(root.rotation_euler),"scale":list(root.scale)},
        "placement_origin_xy_m":origin_xy,"geometry_changes":[
            "Replaced the one-piece 16m massing block with the exact FID 852 / OSM 117396617 plan outline in local coordinates.",
            "Added a brick foundation and continuous wall shell, photo-estimated west nave gable, low-slope east and south addition roofs, and brick bell tower/cross.",
            "Added exterior stone coursing, grouped glass bays, front sign/canopy/ramp, and schematic sanctuary/classroom interiors.",
            "Source-confirmed parish components are represented as three connected mass zones; their exact internal joints, heights, roof pitches and furniture remain estimated."]}
(AUDIT/"r1_build_record.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2,ensure_ascii=False))
