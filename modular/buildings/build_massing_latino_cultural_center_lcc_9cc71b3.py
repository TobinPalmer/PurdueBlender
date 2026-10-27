"""Build the current Purdue Latino Cultural Center (FID 925, 426 Waldron St.).

The asset remains in the campus-coordinate frame used by its manifest entry.
GIS footprint vertices come from the Purdue BuildingShapesZip4 feature service.
Architectural elevations and the vivid front-facade colors are reconstructed
from Purdue's current LCC website images. Interior rooms are a schematic,
source-labeled interpretation of Purdue's published facility inventory.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_latino_cultural_center_lcc_9cc71b3"
ASSET_COLLECTION = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / "latino_cultural_center_lcc_9cc71b3"
SOURCES = AUDIT / "sources"
RENDERS = AUDIT / "renders"
GIS_PATH = SOURCES / "purdue_building_shapes_lcc_all.json"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137


def campus_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def clear_collection(collection: bpy.types.Collection) -> None:
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def material(name, color, roughness=0.72, metallic=0.0, texture=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    if texture == "brick":
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.inputs["Color1"].default_value = (*color, 1.0)
        brick.inputs["Color2"].default_value = (color[0] * 0.72, color[1] * 0.72, color[2] * 0.72, 1)
        brick.inputs["Mortar"].default_value = (0.12, 0.14, 0.14, 1)
        brick.inputs["Scale"].default_value = 18.0
        brick.inputs["Mortar Size"].default_value = 0.015
        brick.inputs["Mortar Smooth"].default_value = 0.004
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.16
        bump.inputs["Distance"].default_value = 0.035
        # Keep the facade's sampled pigment as the base color; use the brick
        # pattern only for shallow surface relief so the texture cannot wash
        # out the strongly colored exterior in distant campus renders.
        nt.links.new(brick.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    elif texture == "siding":
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 8.0
        noise.inputs["Detail"].default_value = 2.0
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12
        bump.inputs["Distance"].default_value = 0.018
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    elif texture == "roof":
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 38.0
        noise.inputs["Detail"].default_value = 2.0
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12
        bump.inputs["Distance"].default_value = 0.025
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return mat


def link_object(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def box(name, loc, dims, mat, collection, rotation=None):
    x, y, z = (v / 2 for v in dims)
    verts = [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
             (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    if rotation:
        obj.rotation_euler = rotation
    collection.objects.link(obj)
    return obj


def quad(name, points, mat, collection, solidify=0.0):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(points, [], [tuple(range(len(points)))])
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    # Keep generated wall and roof panels as plain two-sided meshes. Blender's
    # Solidify evaluator crashed on these GIS-driven quads in Blender 5.2.
    return obj


def beam_between(name, a, b, thickness, mat, collection):
    a, b = Vector(a), Vector(b)
    delta = b - a
    obj = box(name, (a + b) * 0.5, (thickness, thickness, delta.length), mat, collection)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    return obj


def cylinder(name, loc, radius, depth, mat, collection, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return link_object(obj, collection)


def sphere(name, loc, scale, mat, collection):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if mat:
        obj.data.materials.append(mat)
    return link_object(obj, collection)


def text_object(name, body, loc, size, mat, collection):
    curve = bpy.data.curves.new(name + "Text", "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.extrude = 0.0015
    obj = bpy.data.objects.new(name, curve)
    obj.rotation_euler[0] = math.radians(90)
    obj.location = loc
    obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj


def rectangle_floor(name, x0, x1, y0, y1, z, mat, collection):
    return box(name, ((x0+x1)/2, (y0+y1)/2, z), (x1-x0, y1-y0, 0.10), mat, collection)


def add_window(prefix, cx, y_front, z0, width, height, mats, collection):
    teal, yellow, white, glass, dark = mats
    frame_depth = 0.10
    # The dark glazing sits just outside the facade plane, with white sash bars.
    box(prefix + "_glazing", (cx, y_front - 0.105, z0 + height/2),
        (width-0.18, 0.055, height-0.16), glass, collection)
    outer = 0.13
    box(prefix + "_yellow_left", (cx-width/2, y_front-0.16, z0+height/2), (outer, frame_depth, height+0.20), yellow, collection)
    box(prefix + "_yellow_right", (cx+width/2, y_front-0.16, z0+height/2), (outer, frame_depth, height+0.20), yellow, collection)
    box(prefix + "_yellow_head", (cx, y_front-0.16, z0+height), (width+0.14, frame_depth, outer), yellow, collection)
    box(prefix + "_yellow_sill", (cx, y_front-0.16, z0), (width+0.16, frame_depth*1.2, outer), yellow, collection)
    inner_w, inner_h = width-0.18, height-0.16
    for xoff in (-inner_w/2, inner_w/2):
        box(prefix + "_sash_side", (cx+xoff, y_front-0.18, z0+height/2), (0.055, 0.075, inner_h), white, collection)
    for zoff in (-inner_h/2, inner_h/2):
        box(prefix + "_sash_rail", (cx, y_front-0.18, z0+height/2+zoff), (inner_w, 0.075, 0.055), white, collection)
    box(prefix + "_center_mullion", (cx, y_front-0.19, z0+height/2), (0.055, 0.08, inner_h), white, collection)
    box(prefix + "_cross_mullion", (cx, y_front-0.19, z0+height/2), (inner_w, 0.08, 0.055), white, collection)


def set_camera(name, location, target, lens, setup):
    data = bpy.data.cameras.new(name + "Data")
    obj = bpy.data.objects.new(name, data)
    setup.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    return obj


def add_area(name, location, energy, size, target, setup, color=(1.0,0.91,0.78)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    setup.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target)-Vector(location)).to_track_quat("-Z", "Y").to_euler()
    return obj


def main():
    AUDIT.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    with GIS_PATH.open("r", encoding="utf-8") as f:
        gis = json.load(f)
    feature = next(x for x in gis["features"] if x["attributes"]["FID"] == 925)
    ring = feature["geometry"]["rings"][0]
    footprint = [campus_xy(lon, lat) for lon, lat in ring[:-1]]
    xs, ys = zip(*footprint)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    front_y = sum(y for x, y in footprint if y < y0 + 0.12 and x < x1 - 5.0) / len(
        [1 for x, y in footprint if y < y0 + 0.12 and x < x1 - 5.0])
    main_east = x1 - 5.2
    main_west = x0 + 1.7
    main_north = y1 - 0.1
    main_south = y0 + 0.05
    ridge_y = (main_north + main_south) / 2

    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset = bpy.data.collections.get(ASSET_COLLECTION)
    if asset is None:
        asset = bpy.data.collections.new(ASSET_COLLECTION)
        scene.collection.children.link(asset)
    clear_collection(asset)
    setup = bpy.data.collections.get("LCC_Render_Setup") or bpy.data.collections.new("LCC_Render_Setup")
    if setup.name not in scene.collection.children:
        scene.collection.children.link(setup)
    for obj in list(setup.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # Exterior palette follows Purdue's current LCC hero photograph.
    teal = material("LCC_Turquoise_Painted_Brick", (0.015,0.78,0.54), 0.83, texture="brick")
    white_siding = material("LCC_White_Horizontal_Siding", (0.82,0.82,0.75), 0.8, texture="siding")
    siding_seam = material("LCC_Siding_Seam_Shadow", (0.67,0.68,0.62), 0.82)
    yellow = material("LCC_Golden_Yellow_Trim", (0.93,0.52,0.015), 0.48)
    pink = material("LCC_Magenta_Entry_Door", (0.75,0.018,0.25), 0.42)
    white_trim = material("LCC_White_Window_Trim", (0.95,0.94,0.87), 0.42)
    roof = material("LCC_Charcoal_Asphalt_Shingle", (0.045,0.058,0.072), 0.89, texture="roof")
    foundation = material("LCC_Painted_Foundation", (0.15,0.18,0.18), 0.9)
    glass = material("LCC_Glazing", (0.07,0.16,0.22), 0.16, 0.18)
    metal = material("LCC_Painted_Railing", (0.72,0.75,0.72), 0.36, 0.65)
    sign_black = material("LCC_Sign_Black", (0.018,0.025,0.028), 0.42)
    gold = material("LCC_Sign_Gold", (0.85,0.57,0.08), 0.38, 0.25)
    chimney_brick = material("LCC_Chimney_Brick", (0.36,0.12,0.075), 0.85, texture="brick")
    floor_wood = material("LCC_Interior_Walnut_Floor", (0.19,0.075,0.035), 0.5)
    ivory = material("LCC_Interior_Warm_White", (0.82,0.76,0.64), 0.78)
    warm_red = material("LCC_Interior_Coral_Red", (0.55,0.12,0.11), 0.82)
    deep_blue = material("LCC_Interior_Deep_Blue", (0.045,0.095,0.24), 0.8)
    wood = material("LCC_Furniture_Wood", (0.22,0.095,0.035), 0.42)
    fabric = material("LCC_Chair_Charcoal_Fabric", (0.10,0.12,0.13), 0.92)
    book_colors = [material("LCC_Library_Book_%02d"%i, c, 0.78) for i,c in enumerate(
        [(0.55,0.09,0.07),(0.08,0.26,0.38),(0.72,0.42,0.08),(0.16,0.38,0.22),(0.45,0.22,0.36)])]
    computer = material("LCC_Computer_Shell", (0.06,0.075,0.08), 0.35, 0.2)

    # Accurate GIS footprint foundation and restrained perimeter walls.
    floor = bmesh.new()
    verts = [floor.verts.new((x, y, 0.05)) for x, y in footprint]
    for i in range(len(verts)):
        try: floor.edges.new((verts[i], verts[(i+1)%len(verts)]))
        except ValueError: pass
    bmesh.ops.contextual_create(floor, geom=list(floor.edges))
    if floor.faces:
        bmesh.ops.triangulate(floor, faces=list(floor.faces))
    mesh = bpy.data.meshes.new("LCC_FID925_Footprint_FloorMesh")
    floor.to_mesh(mesh)
    floor.free()
    mesh.materials.append(floor_wood)
    floor_obj = bpy.data.objects.new("LCC_FID925_Footprint_Floor", mesh)
    asset.objects.link(floor_obj)

    eaves = 3.35
    for i, (ax, ay) in enumerate(footprint):
        bx, by = footprint[(i+1)%len(footprint)]
        # Main south wall is reconstructed with actual openings below.
        if abs(ay-front_y) < 0.18 and abs(by-front_y) < 0.18 and min(ax,bx) < main_east:
            continue
        mat = white_siding
        # South-facing side returns and the east wing remain white clapboard.
        quad(f"LCC_Exterior_Wall_{i:02d}", [(ax,ay,0.18),(bx,by,0.18),(bx,by,eaves),(ax,ay,eaves)], mat, asset, 0.12)
        # Foundation skirt follows each exterior face.
        quad(f"LCC_Foundation_Skirting_{i:02d}", [(ax,ay,0.18),(bx,by,0.18),(bx,by,0.48),(ax,ay,0.48)], foundation, asset, 0.025)
        edge_len=math.hypot(bx-ax,by-ay)
        if edge_len>1.2:
            ox=(by-ay)/edge_len*0.025; oy=-(bx-ax)/edge_len*0.025
            for row,z in enumerate([0.72+0.22*j for j in range(12)]):
                beam_between(f"LCC_Clapboard_Seam_{i:02d}_{row:02d}",
                    (ax+ox,ay+oy,z),(bx+ox,by+oy,z),0.018,siding_seam,asset)

    # Front feature wall with openings set between colored brick piers.
    facade_x0, facade_x1 = main_west, main_east
    facade_openings = [
        (x0+3.2, x0+4.25, 0.18, 2.42, "door"),
        (x0+6.2, x0+7.65, 1.08, 2.58, "window"),
        (x0+10.0, x0+11.45, 1.08, 2.58, "window"),
        (x0+13.7, x0+15.15, 1.08, 2.58, "window"),
    ]
    facade_openings = [(max(facade_x0+0.2,a),min(facade_x1-0.15,b),c,d,k) for a,b,c,d,k in facade_openings]
    xcuts = sorted({facade_x0, facade_x1, *[v for op in facade_openings for v in op[:2]]})
    for xa, xb in zip(xcuts, xcuts[1:]):
        mid = (xa+xb)/2
        opening = next((op for op in facade_openings if op[0] <= mid <= op[1]), None)
        if not opening:
            box(f"LCC_Teal_Facade_Pier_{xa:.2f}", (mid,front_y,eaves/2), (xb-xa,0.22,eaves-0.18), teal, asset)
        else:
            _,_,oz0,oz1,kind = opening
            if oz0 > 0.18:
                box(f"LCC_Facade_{kind}_Sill_Wall_{xa:.2f}", (mid,front_y,(0.18+oz0)/2), (xb-xa,0.22,oz0-0.18), teal, asset)
            if oz1 < eaves:
                box(f"LCC_Facade_{kind}_Header_Wall_{xa:.2f}", (mid,front_y,(oz1+eaves)/2), (xb-xa,0.22,eaves-oz1), teal, asset)
    # Fill the front-wall edges and all narrow intervals where the opening is taller/shorter.
    # Split full wall sections by openings to avoid a blank facade at the boundary.
    for op in facade_openings:
        a,b,z0,z1,kind=op
        if kind == "door":
            box("LCC_Magenta_Main_Entry_Door", ((a+b)/2,front_y-0.16,(z0+z1)/2), (b-a-0.12,0.10,z1-z0-0.08), pink, asset)
            for x in (a+0.08,b-0.08): box("LCC_Door_White_Jamb", (x,front_y-0.21,(z0+z1)/2), (0.10,0.12,z1-z0+0.08), white_trim, asset)
            box("LCC_Door_Upper_Glass", ((a+b)/2,front_y-0.225,z1-0.55), (0.38,0.035,0.82), glass, asset)
            box("LCC_Door_Lower_Panel", ((a+b)/2,front_y-0.23,z0+0.45), (b-a-0.34,0.035,0.66), pink, asset)
            cylinder("LCC_Door_Handle", (b-0.27,front_y-0.28,1.32), 0.035,0.045, gold, asset, 12)
            box("LCC_Door_Threshold", ((a+b)/2,front_y-0.27,0.23), (b-a+0.28,0.38,0.08), white_trim, asset)
        else:
            add_window(f"LCC_Front_Window_{facade_openings.index(op)+1}", (a+b)/2, front_y, z0, b-a, z1-z0,
                       (teal,yellow,white_trim,glass,foundation), asset)
    # Continuous golden fascia and bright window-band caps echo the official exterior image.
    box("LCC_Front_Golden_Cornice", ((facade_x0+facade_x1)/2,front_y-0.18,eaves-0.02), (facade_x1-facade_x0+0.15,0.32,0.20), yellow, asset)
    box("LCC_Front_Golden_Window_Band", ((facade_x0+facade_x1)/2,front_y-0.13,2.83), (facade_x1-facade_x0-0.18,0.09,0.18), yellow, asset)

    # Main gabled roof with projecting eaves and a small secondary east wing roof.
    roof_y_front, roof_y_back = main_south-0.38, main_north+0.38
    ridge_z, eave_z = 5.78, eaves+0.10
    ridge_y = (roof_y_front+roof_y_back)/2
    roof_south = quad("LCC_Main_Roof_South_Pitch", [(main_west-0.32,roof_y_front,eave_z),(main_east+0.25,roof_y_front,eave_z),
        (main_east+0.25,ridge_y,ridge_z),(main_west-0.32,ridge_y,ridge_z)], roof, asset, 0.12)
    roof_north = quad("LCC_Main_Roof_North_Pitch", [(main_west-0.32,ridge_y,ridge_z),(main_east+0.25,ridge_y,ridge_z),
        (main_east+0.25,roof_y_back,eave_z),(main_west-0.32,roof_y_back,eave_z)], roof, asset, 0.12)
    # Gable ends above the one-story walls; the west-facing profile is visible in the LCC photo.
    west_gable = quad("LCC_West_Gable_End", [(main_west,main_south, eaves),(main_west,main_north,eaves),
        (main_west,ridge_y,ridge_z)], white_siding, asset, 0.12)
    east_gable = quad("LCC_Main_East_Gable_End", [(main_east,main_south,eaves),(main_east,main_north,eaves),
        (main_east,ridge_y,ridge_z)], white_siding, asset, 0.12)
    # Subtle fascia boards along long roof edges.
    for y in (roof_y_front, roof_y_back):
        beam_between("LCC_White_Eave_Fascia", (main_west-0.38,y,eave_z),(main_east+0.28,y,eave_z),0.20,white_trim,asset)
    beam_between("LCC_Ridge_Cap",(main_west-0.32,ridge_y,ridge_z+0.04),(main_east+0.25,ridge_y,ridge_z+0.04),0.12,roof,asset)

    # Attached lower wing is kept distinct in roof slope and height.
    wing_x0, wing_x1 = main_east-0.05, x1+0.28
    wing_y0, wing_y1 = y0+0.42, y1-0.25
    wing_ridge_x = (wing_x0+wing_x1)/2
    wing_eave, wing_peak = 3.12, 4.92
    quad("LCC_East_Wing_Roof_West_Pitch", [(wing_x0,wing_y0,wing_eave),(wing_ridge_x,wing_y0,wing_peak),
        (wing_ridge_x,wing_y1,wing_peak),(wing_x0,wing_y1,wing_eave)], roof, asset, 0.10)
    quad("LCC_East_Wing_Roof_East_Pitch", [(wing_ridge_x,wing_y0,wing_peak),(wing_x1,wing_y0,wing_eave),
        (wing_x1,wing_y1,wing_eave),(wing_ridge_x,wing_y1,wing_peak)], roof, asset, 0.10)
    quad("LCC_East_Wing_South_Gable", [(wing_x0,wing_y0,2.95),(wing_x1,wing_y0,2.95),(wing_ridge_x,wing_y0,wing_peak)], white_siding, asset, 0.10)
    quad("LCC_East_Wing_North_Gable", [(wing_x1,wing_y1,2.95),(wing_x0,wing_y1,2.95),(wing_ridge_x,wing_y1,wing_peak)], white_siding, asset, 0.10)

    # Small attic dormer, brick chimney, and roof details visible in the current house imagery.
    dormer_x, dormer_y = main_east-3.2, (roof_y_front+ridge_y)/2
    dormer_base_z = 4.55
    box("LCC_Attic_Dormer_Front", (dormer_x,dormer_y-0.48,dormer_base_z+0.42), (2.35,0.22,0.92), white_siding, asset)
    quad("LCC_Attic_Dormer_Gable", [(dormer_x-1.18,dormer_y-0.60,dormer_base_z+0.86),(dormer_x+1.18,dormer_y-0.60,dormer_base_z+0.86),
        (dormer_x,dormer_y-0.60,dormer_base_z+1.50)], white_siding, asset, 0.06)
    quad("LCC_Attic_Dormer_Roof_Left", [(dormer_x-1.35,dormer_y-0.66,dormer_base_z+0.90),(dormer_x,dormer_y-0.66,dormer_base_z+1.56),
        (dormer_x,dormer_y+0.62,dormer_base_z+1.56),(dormer_x-1.35,dormer_y+0.62,dormer_base_z+0.90)], roof, asset, 0.08)
    quad("LCC_Attic_Dormer_Roof_Right", [(dormer_x,dormer_y-0.66,dormer_base_z+1.56),(dormer_x+1.35,dormer_y-0.66,dormer_base_z+0.90),
        (dormer_x+1.35,dormer_y+0.62,dormer_base_z+0.90),(dormer_x,dormer_y+0.62,dormer_base_z+1.56)], roof, asset, 0.08)
    box("LCC_Dormer_Window_Glass", (dormer_x,dormer_y-0.62,dormer_base_z+0.49), (1.28,0.045,0.60), glass, asset)
    for xo in (-0.72,0.72): box("LCC_Dormer_White_Jamb",(dormer_x+xo,dormer_y-0.67,dormer_base_z+0.49),(0.08,0.06,0.74),white_trim,asset)
    box("LCC_Dormer_Mullion",(dormer_x,dormer_y-0.68,dormer_base_z+0.49),(0.055,0.07,0.60),white_trim,asset)
    box("LCC_Brick_Chimney", (main_west+1.25,ridge_y+0.85,6.34), (0.72,0.78,2.05), chimney_brick, asset)
    box("LCC_Chimney_Cap", (main_west+1.25,ridge_y+0.85,7.39), (0.91,0.92,0.16), white_trim, asset)

    # Interior is a furnished schematic based on Purdue's room inventory and interior photographs.
    # It is intentionally named schematic because no dimensioned current floor plan was located.
    rectangle_floor("LCC_Interior_Wood_Floor",x0+0.35,x1-0.30,y0+0.38,y1-0.35,0.16,floor_wood,asset)
    partition_y = y0+5.05
    box("LCC_Interior_Partition_North_South",(main_west+7.1,partition_y,1.75),(0.16,0.16,3.10),ivory,asset)
    box("LCC_Interior_Partition_East_West",(main_west+3.5,y0+7.15,1.75),(7.1,0.16,3.10),ivory,asset)
    box("LCC_Interior_Gathering_Room_Accent_Wall",(main_west+6.9,y0+0.55,1.70),(0.12,0.11,2.85),warm_red,asset)
    box("LCC_Interior_Adjacent_Room_Blue_Wall",(main_west+7.45,y0+3.5,1.70),(0.12,0.11,2.85),deep_blue,asset)
    # French-door divider appears in Purdue's published Gathering Room photograph.
    for x in (main_west+6.82,main_west+7.38):
        box("LCC_Interior_French_Door_Glass",(x,y0+3.05,1.25),(0.45,0.045,1.70),glass,asset)
        box("LCC_Interior_French_Door_Stile",(x,y0+3.05,1.25),(0.05,0.075,1.85),white_trim,asset)
    # Main lounge: sofas, side tables and artwork.
    box("LCC_Lounge_Sofa_Base",(main_west+3.8,y0+3.0,0.62),(2.25,0.82,0.72),fabric,asset)
    box("LCC_Lounge_Sofa_Back",(main_west+3.8,y0+2.63,1.02),(2.25,0.18,0.82),fabric,asset)
    for x in (main_west+2.82,main_west+4.78):
        box("LCC_Lounge_Armrest",(x,y0+3.0,0.90),(0.22,0.84,0.65),fabric,asset)
    box("LCC_Lounge_Coffee_Table",(main_west+4.9,y0+4.28,0.56),(1.15,0.64,0.10),wood,asset)
    for x in (main_west+4.42,main_west+5.38): box("LCC_Lounge_Table_Leg",(x,y0+4.28,0.32),(0.08,0.08,0.45),wood,asset)
    box("LCC_Lounge_Wall_Art_Frame",(main_west+5.85,y0+0.58,2.15),(1.12,0.12,0.78),gold,asset)
    box("LCC_Lounge_Wall_Art_Color",(main_west+5.85,y0+0.50,2.15),(0.96,0.045,0.62),pink,asset)
    # Gathering room: round table with colorful top, six chairs, matching the official photo.
    table_x, table_y = main_west+11.0, y0+2.75
    cylinder("LCC_Gathering_Round_Table_Top",(table_x,table_y,0.86),0.86,0.12,wood,asset,48)
    cylinder("LCC_Gathering_Round_Table_Stem",(table_x,table_y,0.46),0.14,0.72,wood,asset,24)
    cylinder("LCC_Gathering_Round_Table_Base",(table_x,table_y,0.12),0.50,0.10,wood,asset,32)
    # Colored segments make the table's documented collage top legible in the model.
    palette=[pink,yellow,deep_blue,teal,book_colors[2],warm_red]
    for i,mat in enumerate(palette):
        angle=2*math.pi*i/6
        box(f"LCC_Table_Collage_Swatch_{i+1}",(table_x+0.38*math.cos(angle),table_y+0.38*math.sin(angle),0.932),(0.34,0.29,0.018),mat,asset,rotation=(0,0,angle))
    for i in range(6):
        angle=2*math.pi*i/6
        cx=table_x+1.22*math.cos(angle); cy=table_y+1.22*math.sin(angle)
        box(f"LCC_Gathering_Chair_Seat_{i+1}",(cx,cy,0.52),(0.60,0.57,0.13),fabric,asset,rotation=(0,0,angle))
        box(f"LCC_Gathering_Chair_Back_{i+1}",(cx,cy+0.25,0.94),(0.59,0.13,0.78),fabric,asset,rotation=(0,0,angle))
        for dx in (-0.22,0.22): box("LCC_Gathering_Chair_Leg",(cx+dx,cy,0.29),(0.06,0.06,0.48),metal,asset)
    # Conference room: long table, chairs, podium and wall display.
    conf_x, conf_y = main_west+3.5, y0+8.55
    box("LCC_Conference_Table_Top",(conf_x,conf_y,0.82),(4.4,1.22,0.13),wood,asset)
    for x in (conf_x-1.8,conf_x+1.8):
        for y in (conf_y-0.42,conf_y+0.42): box("LCC_Conference_Table_Leg",(x,y,0.43),(0.11,0.11,0.68),wood,asset)
    for side in (-1,1):
        for i in range(3):
            cx=conf_x-1.35+i*1.35; cy=conf_y+side*0.98
            box("LCC_Conference_Chair_Seat",(cx,cy,0.52),(0.58,0.55,0.13),fabric,asset)
            box("LCC_Conference_Chair_Back",(cx,cy+side*0.24,0.93),(0.58,0.13,0.74),fabric,asset)
    box("LCC_Conference_Podium",(conf_x+2.6,conf_y-1.3,0.62),(0.68,0.55,1.12),wood,asset)
    box("LCC_Conference_Display",(conf_x+0.5,y1-0.52,2.15),(1.35,0.10,0.80),computer,asset)
    # Library shelves and individually colored book spines.
    shelf_x=main_west+10.9; shelf_y=y0+7.95
    box("LCC_Library_Shelf_Back",(shelf_x,shelf_y,1.15),(3.8,0.22,2.05),wood,asset)
    for z in (0.55,1.12,1.70,2.25):
        box("LCC_Library_Shelf_Board",(shelf_x,shelf_y-0.18,z),(3.88,0.32,0.08),wood,asset)
        for i in range(15):
            bx=shelf_x-1.72+i*0.245
            h=0.32+0.11*((i*7)%4)
            box(f"LCC_Library_Book_{z:.2f}_{i:02d}",(bx,shelf_y-0.20,z+0.08+h/2),(0.16,0.22,h),book_colors[i%len(book_colors)],asset)
    # Three-station ITaP lab: desk surfaces, monitor screens, keyboards, task chairs.
    for i in range(3):
        cx=wing_x0+0.75+i*1.35; cy=y0+6.8
        box(f"LCC_ITaP_Desk_{i+1}",(cx,cy,0.78),(1.12,0.62,0.10),wood,asset)
        box(f"LCC_ITaP_Monitor_{i+1}",(cx,cy+0.18,1.28),(0.70,0.10,0.48),computer,asset)
        box(f"LCC_ITaP_Screen_{i+1}",(cx,cy+0.12,1.29),(0.56,0.035,0.34),glass,asset)
        box(f"LCC_ITaP_Keyboard_{i+1}",(cx,cy-0.16,0.85),(0.48,0.20,0.035),computer,asset)
        box(f"LCC_ITaP_Chair_{i+1}",(cx,cy-0.62,0.52),(0.50,0.48,0.12),fabric,asset)
    # Compact staff kitchenette and family-friendly restroom indicator.
    box("LCC_Kitchen_Counter",(wing_x0+1.9,y1-0.95,0.92),(2.0,0.62,0.16),white_trim,asset)
    box("LCC_Kitchen_Cabinet",(wing_x0+1.9,y1-0.95,0.50),(1.92,0.54,0.70),wood,asset)
    box("LCC_Kitchen_Sink",(wing_x0+1.6,y1-0.95,1.015),(0.50,0.34,0.025),metal,asset)
    box("LCC_Kitchen_Upper_Cabinet",(wing_x0+1.9,y1-0.60,1.95),(1.8,0.20,0.78),ivory,asset)

    # Front access platform/ramp and handrails; Purdue confirms ramp access on the first floor.
    door_center = x0+3.725
    landing_y = front_y-0.45
    box("LCC_Accessible_Entry_Landing",(door_center,landing_y,0.36),(2.25,0.95,0.16),metal,asset)
    ramp_x=door_center-0.25
    # Ramp deck is a sloped prism leading south from the landing.
    quad("LCC_Access_Ramp_Deck",[(ramp_x-0.62,landing_y-0.30,0.30),(ramp_x+0.62,landing_y-0.30,0.30),
         (ramp_x+0.62,landing_y-3.25,0.06),(ramp_x-0.62,landing_y-3.25,0.06)],metal,asset,0.08)
    for side in (-1,1):
        rx=ramp_x+side*0.68
        low=(rx,landing_y-3.22,0.90); high=(rx,landing_y-0.33,1.16)
        beam_between("LCC_Ramp_Handrail_Top",low,high,0.055,metal,asset)
        beam_between("LCC_Ramp_Handrail_Mid",(rx,landing_y-3.22,0.48),(rx,landing_y-0.33,0.74),0.035,metal,asset)
        for t in (0.05,0.5,0.95):
            y=landing_y-3.22+2.89*t; z=0.90+0.26*t
            beam_between("LCC_Ramp_Rail_Post",(rx,y,z-0.84),(rx,y,z),0.04,metal,asset)
    # Main steps beside the ramp, source-supported as a front entrance approach.
    for i in range(3):
        z=0.14+i*0.16; y=front_y-0.55-i*0.34
        box(f"LCC_Entry_Step_{i+1}",(door_center+1.28,y,z),(1.0,0.72,0.12),white_trim,asset)

    # Freestanding black and gold Purdue LCC sign from the official current exterior image.
    sign_x=facade_x1+1.10; sign_y=front_y-3.20
    cylinder("LCC_Sign_Post",(sign_x,sign_y,1.55),0.10,3.05,sign_black,asset,20)
    box("LCC_Sign_Gold_Border",(sign_x,sign_y-0.10,2.85),(1.65,0.17,0.92),gold,asset)
    box("LCC_Sign_Face",(sign_x,sign_y-0.20,2.85),(1.51,0.09,0.78),sign_black,asset)
    text_object("LCC_Sign_Purdue","PURDUE",(sign_x,sign_y-0.26,3.10),0.15,gold,asset)
    text_object("LCC_Sign_Latino","LATINO",(sign_x,sign_y-0.26,2.86),0.17,white_trim,asset)
    text_object("LCC_Sign_Cultural","CULTURAL CENTER",(sign_x,sign_y-0.26,2.64),0.112,white_trim,asset)

    # Garden bed and low plants are modest context. The official 2023 story confirms a garden.
    soil = material("LCC_Garden_Soil",(0.10,0.075,0.035),0.95)
    leaf = material("LCC_Garden_Leaf",(0.10,0.31,0.10),0.88)
    flower = material("LCC_Garden_Flower",(0.83,0.36,0.08),0.65)
    garden_x, garden_y = main_east-2.4, front_y-1.20
    box("LCC_Jardin_Semillas_Bed",(garden_x,garden_y,0.10),(3.2,0.85,0.18),soil,asset)
    for i in range(9):
        px=garden_x-1.28+(i%5)*0.62; py=garden_y-0.20+(i//5)*0.42
        cylinder("LCC_Garden_Stem",(px,py,0.43),0.035,0.58,leaf,asset,8)
        for j in range(3):
            ang=2*math.pi*j/3
            sphere("LCC_Garden_Leaf",(px+0.14*math.cos(ang),py+0.10*math.sin(ang),0.42+j*0.06),(0.15,0.07,0.045),leaf,asset)
        sphere("LCC_Garden_Flower",(px,py,0.76),(0.075,0.075,0.06),flower,asset)

    # Rendering environment, isolated outside the linked building collection.
    world = scene.world or bpy.data.worlds.new("LCC Preview World")
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.32,0.42,0.56,1)
    bg.inputs["Strength"].default_value = 0.45
    context = bpy.data.collections.get("LCC_Preview_Context") or bpy.data.collections.new("LCC_Preview_Context")
    if context.name not in scene.collection.children:
        scene.collection.children.link(context)
    for obj in list(context.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    grass = material("LCC_Preview_Grass",(0.11,0.17,0.085),0.95)
    concrete = material("LCC_Preview_Concrete",(0.34,0.35,0.33),0.87)
    box("LCC_Preview_Ground_Plane",(-331.2,177.0,-0.13),(80.0,95.0,0.16),grass,context)
    box("LCC_Preview_Front_Sidewalk",(-331.0,front_y-2.1,-0.02),(25.0,1.65,0.08),concrete,context)
    box("LCC_Preview_Walk_to_Ramp",(door_center,front_y-4.1,-0.02),(1.8,4.4,0.08),concrete,context)
    add_area("LCC_Sun_Key",(-347,163,18),1450,11,(-331,178,2.4),setup,(1.0,0.83,0.66))
    add_area("LCC_Fill",(-316,174,12),650,13,(-331,178,2.2),setup,(0.85,0.88,1.0))
    add_area("LCC_Rim",(-333,193,14),900,9,(-331,178,3.0),setup,(1.0,0.91,0.76))
    hero = set_camera("LCC_Exterior_Hero_Camera",(-331.2,150.5,2.65),(-331.3,178.2,2.25),38,setup)
    top = set_camera("LCC_Aerial_Camera",(-331.4,178.3,31),(-331.4,178.3,1.8),42,setup)
    inside = set_camera("LCC_Interior_Cutaway_Camera",(table_x-3.1,table_y-3.8,8.0),(table_x,table_y,0.75),46,setup)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    scene.camera = hero
    scene.render.filepath = str(RENDERS / "lcc_426_waldron_exterior.png")
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 48
    bpy.ops.render.render(write_still=True)

    # Roof-off cutaway documents the schematic interior; restore and save unchanged exterior asset.
    cutaway_prefixes=("LCC_Exterior_Wall_","LCC_Foundation_Skirting_","LCC_Teal_Facade_","LCC_Facade_",
      "LCC_Front_","LCC_White_Eave_","LCC_Main_Roof_","LCC_West_Gable_","LCC_Main_East_Gable_",
      "LCC_East_Wing_","LCC_Attic_","LCC_Brick_Chimney","LCC_Chimney_","LCC_Dormer_",
      "LCC_Access_","LCC_Ramp_","LCC_Entry_Step_","LCC_Sign_","LCC_Jardin_","LCC_Garden_",
      "LCC_Magenta_Main_Entry","LCC_Door_")
    old_hides = [(o,o.hide_render) for o in asset.objects if o.name.startswith(cutaway_prefixes)]
    for o,_ in old_hides: o.hide_render = True
    scene.camera = top
    scene.render.filepath = str(RENDERS / "lcc_426_waldron_aerial_cutaway.png")
    bpy.ops.render.render(write_still=True)
    for o,v in old_hides: o.hide_render = v
    scene.camera = inside
    for o,_ in old_hides: o.hide_render = True
    scene.render.filepath = str(RENDERS / "lcc_426_waldron_interior_schematic.png")
    bpy.ops.render.render(write_still=True)
    for o,v in old_hides: o.hide_render = v
    scene.camera = hero
    scene.render.filepath = str(RENDERS / "lcc_426_waldron_exterior.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    # Save a compact evidence record with explicit provenance and unverified items.
    world_coords = [o.matrix_world @ Vector(c) for o in asset.objects if o.type == "MESH" for c in o.bound_box]
    evidence = {
      "asset_id": ASSET_ID,
      "asset_file": str(ASSET_PATH.relative_to(ROOT)).replace("\\","/"),
      "collection": ASSET_COLLECTION,
      "source_feature": {"provider":"Purdue BuildingShapesZip4 ArcGIS FeatureServer", "fid":925,
        "feature_name":feature["attributes"]["BUILDING_N"],"address":feature["attributes"]["ADDRESS"],
        "crs":"EPSG:4326 input; converted with project local approximation to campus XY meters",
        "url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0",
        "retrieved":"2026-10-22","footprint_method":"transform each source ring vertex using modular/AGENTS.md project transform"},
      "official_identity_and_architecture": [
        {"provider":"Purdue University Latino Cultural Center","url":"https://www.purdue.edu/lcc/","page_modified":"2026-07-02","retrieved":"2026-10-26","evidence":"current page names 426 Waldron Street; current hero photo shows teal brick front, yellow window surrounds, pink entry, white clapboard wings, gray shingle roof and sign"},
        {"provider":"Purdue University Latino Cultural Center facility page","url":"https://www.purdue.edu/lcc/center/facility.php","page_date":"2021-08-24","retrieved":"2026-10-26","evidence":"published rooms include Maricela Alvarado lounge, Gathering Room, Conference Room, ITaP lab, library, kitchen and ramp access"},
        {"provider":"Purdue College of Agriculture","url":"https://ag.purdue.edu/news/2023/10/cocina-con-carina-how-a-garden-connects-agriculture-food-and-heritage.html","page_date":"2023-10-11","retrieved":"2026-10-26","evidence":"describes multicolored house and community garden; photos show garden and colored interior"},
        {"provider":"Purdue Campus Map and Resources","url":"https://www.purdue.edu/campus-map/","retrieved":"2026-10-26","evidence":"lists Latino Cultural Center at 426 Waldron Street"}
      ],
      "world_bounds_m": [[min(v.x for v in world_coords),max(v.x for v in world_coords)],
                          [min(v.y for v in world_coords),max(v.y for v in world_coords)],
                          [min(v.z for v in world_coords),max(v.z for v in world_coords)]],
      "estimated_dimensions_m": {"eave_height":eaves,"main_ridge_height":ridge_z,"east_wing_peak":wing_peak},
      "interior_status":"schematic, furnished interpretation; exact room positions/dimensions not sourced by a dimensioned floor plan",
      "uncertainties":["Official GIS confirms a one-level feature and footprint; no surveyed elevations or dimensioned current floor plan were available.","Roof pitches, dormer/chimney sizes, window dimensions and exact room layout are estimates from current and historic Purdue imagery.","The current LCC hero image has page context modified 2026-07-02; image capture date is not independently stated."],
      "renders":["renders/lcc_426_waldron_exterior.png","renders/lcc_426_waldron_aerial_cutaway.png","renders/lcc_426_waldron_interior_schematic.png"],
      "object_count":len(asset.objects)
    }
    (AUDIT/"model_evidence.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")


if __name__ == "__main__":
    main()
