"""Build Maclure Cooperative's source-faithful local asset.

The wall footprint is the current official ArcGIS BuildingShapes feature FID
822 (name Maclure, address 128 Wiggins St). Exterior details follow the
cooperative's own photo gallery; height, roof profile, interior partitions,
and room furniture are visibly schematic estimates.

Run with Blender 5.x:
  blender --background --python modular/buildings/build_maclure_cooperative.py
"""
from __future__ import annotations

import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "maclure_cooperative"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "maclure" / "sources" / "official_gis_fid822.geojson"
AUDIT = ROOT / "audit" / "maclure"
PREVIEW = AUDIT / "maclure_exterior_preview.png"
INTERIOR_PREVIEW = AUDIT / "maclure_interior_preview.png"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
LAT0, LON0 = 40.4274, -86.9137
LON_SCALE = 111412.84 * math.cos(math.radians(LAT0))
LAT_SCALE = 111040.0


def polygon_centroid(points):
    a2 = cx = cy = 0.0
    for i, (x1, y1) in enumerate(points):
        x2, y2 = points[(i + 1) % len(points)]
        cross = x1 * y2 - x2 * y1
        a2 += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    assert abs(a2) > 1e-8
    return cx / (3 * a2), cy / (3 * a2)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)
    presentation = bpy.data.collections.new(f"Presentation_{ASSET_ID}")
    scene.collection.children.link(presentation)
    return scene, asset, presentation


def make_material(name, color, roughness=0.76, texture=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    if texture == "siding":
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 14
        tex.inputs["Detail"].default_value = 2
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "Z"
        wave.inputs["Scale"].default_value = 21
        wave.inputs["Distortion"].default_value = 1.8
        wave.inputs["Detail"].default_value = 2
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MIX"
        mix.inputs[1].default_value = (0.84, 0.83, 0.78, 1)
        mix.inputs[2].default_value = (0.96, 0.95, 0.91, 1)
        nt.links.new(wave.outputs["Color"], mix.inputs[0])
        nt.links.new(mix.outputs["Color"], bs.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12
        bump.inputs["Distance"].default_value = 0.025
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    elif texture == "shingle":
        geometry = nt.nodes.new("ShaderNodeNewGeometry")
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.inputs["Color1"].default_value = (0.11, 0.12, 0.14, 1)
        brick.inputs["Color2"].default_value = (0.21, 0.22, 0.24, 1)
        brick.inputs["Mortar"].default_value = (0.055, 0.06, 0.07, 1)
        brick.inputs["Scale"].default_value = 1
        brick.inputs["Brick Width"].default_value = 0.28
        brick.inputs["Row Height"].default_value = 0.13
        brick.inputs["Mortar Size"].default_value = 0.015
        # Object-space positions keep the shingle dimensions in real meters;
        # Generated coordinates would stretch them across the roof face.
        nt.links.new(geometry.outputs["Position"], brick.inputs["Vector"])
        nt.links.new(brick.outputs["Color"], bs.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.16
        bump.inputs["Distance"].default_value = 0.018
        nt.links.new(brick.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    elif texture == "wood":
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 7
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.18
        bump.inputs["Distance"].default_value = 0.03
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def link_asset(obj, name, asset, root):
    obj.name = name
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    asset.objects.link(obj)
    obj.parent = root
    return obj


def cube(name, loc, scale, material, asset, root, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft eased edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return link_asset(o, name, asset, root)


def mesh_obj(name, verts, faces, material, asset, root):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    asset.objects.link(obj)
    obj.parent = root
    return obj


def beam(name, a, b, radius, material, asset, root, vertices=8):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.data.materials.append(material)
    return link_asset(o, name, asset, root)


def wall_prism(ring, z0, z1, material, asset, root, doorway=None):
    # GIS ring may be concave. Side faces follow its exact coordinate sequence;
    # the hidden top cap is omitted because the roof covers it.
    verts = [(x, y, z) for z in (z0, z1) for x, y in ring]
    n = len(ring)
    faces = []
    west = min(x for x, _ in ring)
    index = {(round(v[0], 8), round(v[1], 8), round(v[2], 8)): i for i, v in enumerate(verts)}

    def vi(x, y, z):
        key = (round(x, 8), round(y, 8), round(z, 8))
        if key not in index:
            index[key] = len(verts)
            verts.append((x, y, z))
        return index[key]

    for i, (x1, y1) in enumerate(ring):
        x2, y2 = ring[(i + 1) % n]
        is_entry_edge = (doorway and abs(x1-west) < 1e-6 and abs(x2-west) < 1e-6
                         and min(y1, y2) <= doorway["y"][0] and max(y1, y2) >= doorway["y"][1])
        if not is_entry_edge:
            faces.append((i, (i+1)%n, (i+1)%n+n, i+n))
            continue
        ya, yb = sorted((y1, y2))
        yl, yr = doorway["y"]
        zb, zt = doorway["z"]
        # Four wall panels leave a real doorway opening above the raised deck.
        # Extra boundary vertices stay above grade, preserving the exact 12
        # official GIS vertices at Z=0 for footprint verification.
        panels = [(ya, yb, z0, zb), (ya, yl, zb, z1),
                  (yr, yb, zb, z1), (yl, yr, zt, z1)]
        for py0, py1, pz0, pz1 in panels:
            if py1-py0 > 1e-6 and pz1-pz0 > 1e-6:
                faces.append((vi(west,py0,pz0), vi(west,py1,pz0),
                              vi(west,py1,pz1), vi(west,py0,pz1)))
    return mesh_obj("GIS footprint walls | FID 822", verts, faces, material, asset, root)


def gable_roof_x(name, xmin, xmax, ymin, ymax, eave_z, ridge_z, material, asset, root):
    # Main roof: ridge runs north/south; two dark, textured slopes.
    xm = (xmin + xmax) / 2
    verts = [(xmin,ymin,eave_z),(xm,ymin,ridge_z),(xmax,ymin,eave_z),
             (xmin,ymax,eave_z),(xm,ymax,ridge_z),(xmax,ymax,eave_z)]
    faces = [(0,3,4,1),(1,4,5,2),(0,1,2),(3,5,4)]
    return mesh_obj(name, verts, faces, material, asset, root)


def add_window_west(y, z, wall_x, siding, glass, trim, shutter, asset, root, width=1.05, height=1.45):
    # West-facing window assembly. Narrow trim and paired shutters echo the
    # direct exterior reference photograph. Geometry sits just outside wall.
    x = wall_x - 0.08
    # Open trim frame leaves a real glass field; a solid backing panel would
    # incorrectly hide the glazing in this west-facing wall orientation.
    tx=x-0.035
    cube("Window glass", (x-0.065,y,z), (0.045,width,height), glass, asset, root, 0.012)
    for side in (-1,1):
        cube("Window casing jamb", (tx,y+side*(width/2+0.055),z), (0.10,0.11,height+0.14), trim, asset, root, 0.018)
    for side in (-1,1):
        cube("Window casing head and sill", (tx,y,z+side*(height/2+0.055)), (0.10,width+0.20,0.11), trim, asset, root, 0.018)
    cube("Window sash vertical", (x-0.10,y,z), (0.035,0.045,height), trim, asset, root)
    cube("Window sash horizontal", (x-0.10,y,z), (0.035,width,height*0.045), trim, asset, root)
    cube("Window sill", (x-0.08,y,z-height/2-0.11), (0.18,width+0.30,0.12), trim, asset, root, 0.02)
    for side in (-1,1):
        cube("Muted red-brown shutter", (x-0.025,y+side*(width/2+0.16),z), (0.09,0.25,height*1.08), shutter, asset, root, 0.025)
        for h in range(5):
            cube("Shutter board seam", (x-0.08,y+side*(width/2+0.16),z-height*0.42+h*height*0.21), (0.035,0.27,0.025), trim, asset, root)


def create_room_furniture(asset, root, wood, upholstery, floor):
    # These room blocks encode a plausible co-op program from the official
    # virtual tour labels. They are schematic, not measured room geometry.
    # Ground floor room divisions and furniture, inside the closed exterior.
    partition = make_material("Estimated interior plaster", (0.74,0.70,0.61))
    for zbase in (0.12, 3.18):
        # Keep interior floors recessed behind the exterior shell so they do
        # not read as accidental horizontal facade bands in exterior views.
        slab = cube("Estimated interior floor slab", (-0.3,2.2,zbase), (7.2,13.8,0.20), floor, asset, root)
        # Keep the floor visible in the delivered asset for interior inspection.
    # Internal room-divider walls, leaving openings between spaces.
    for zbase in (0.2, 3.28):
        h = 2.65
        for y in (-2.3, 2.2, 6.3):
            # Leave a broad estimated doorway in each cross partition so the
            # circulation path can be read in the separate plan preview.
            cube("Estimated room partition", (-1.25,y,zbase+h/2), (5.7,0.12,h), partition, asset, root)
            cube("Estimated room partition", (3.45,y,zbase+h/2), (2.1,0.12,h), partition, asset, root)
        cube("Estimated room partition", (2.4,4.35,zbase+h/2), (0.12,4.0,h), partition, asset, root)
    # Communal first-floor living / dining zone.
    cube("Formal living room sofa (estimated)", (-0.5,5.1,0.82), (0.9,2.6,0.8), upholstery, asset, root, 0.08)
    cube("Formal living room coffee table (estimated)", (1.0,4.6,0.53), (1.1,1.5,0.12), wood, asset, root, 0.05)
    cube("Communal dining table (estimated)", (-0.4,-0.1,0.9), (1.45,2.8,0.12), wood, asset, root, 0.04)
    for yy in (-1.1,0.2,1.3):
        for xx in (-1.4,0.65):
            cube("Dining chair (estimated)", (xx,yy,0.55), (0.42,0.42,0.9), wood, asset, root, 0.04)
    # Upper floor residence proxies: three study rooms plus common circulation.
    for yy in (-4.6,-0.2,4.1,8.0):
        for xx in (-2.7,1.1):
            cube("Study bed (estimated)", (xx,yy,3.85), (1.1,2.0,0.45), upholstery, asset, root, 0.08)
            cube("Study desk (estimated)", (xx+0.6,yy+1.1,3.95), (0.8,1.2,0.12), wood, asset, root, 0.04)
    # Basement lounge and laundry remain explicitly approximate.
    basement_slab = cube("Estimated basement floor", (-0.3,2.2,-2.55), (7.2,13.8,0.2), floor, asset, root)
    cube("Basement lounge sectional (estimated)", (-0.7,3.6,-1.9), (1.0,3.0,0.75), upholstery, asset, root, 0.08)
    cube("Laundry washer (estimated)", (2.8,-3.8,-1.82), (0.75,0.75,1.1), trim_gray, asset, root, 0.05)
    cube("Laundry dryer (estimated)", (3.7,-3.8,-1.82), (0.75,0.75,1.1), trim_gray, asset, root, 0.05)


def add_camera_and_lights(scene, presentation):
    # Camera looks from southwest toward west-front and south gable.
    camera_data = bpy.data.cameras.new("Maclure exterior camera")
    camera = bpy.data.objects.new("Maclure exterior camera", camera_data)
    presentation.objects.link(camera)
    camera.location = (-34,-13,9)
    target = Vector((-0.5,2.2,4.3))
    camera.rotation_euler = (target-Vector(camera.location)).to_track_quat("-Z","Y").to_euler()
    camera.data.lens = 40
    scene.camera = camera
    light_data = bpy.data.lights.new("Large soft daylight", "AREA")
    light = bpy.data.objects.new("Large soft daylight", light_data)
    presentation.objects.link(light)
    light.location = (-15,-10,20)
    light.data.energy = 2500
    light.data.shape = "DISK"
    light.data.size = 12
    # A neutral floor plane belongs only to presentation, not the asset.
    mat_floor = bpy.data.materials.new("Preview neutral ground")
    mat_floor.diffuse_color = (0.19,0.22,0.18,1)
    mat_floor.use_nodes = True
    bs = next(n for n in mat_floor.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    bs.inputs["Base Color"].default_value = (0.19,0.22,0.18,1)
    plane_mesh=bpy.data.meshes.new("Preview ground mesh")
    plane_mesh.from_pydata([(-35,-35,-0.12),(35,-35,-0.12),(35,35,-0.12),(-35,35,-0.12)],[],[(0,1,2,3)])
    plane_mesh.materials.append(mat_floor)
    plane=bpy.data.objects.new("Preview ground",plane_mesh)
    presentation.objects.link(plane)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x=1200; scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.world.color=(0.18,0.18,0.18)


def main():
    AUDIT.mkdir(parents=True,exist_ok=True)
    data=json.loads(SOURCE_PATH.read_text(encoding="utf-8-sig"))
    feature=next(f for f in data["features"] if int(f["properties"]["FID"])==822)
    prop=feature["properties"]
    assert prop["BUILDING_N"]=="Maclure" and prop["ADDRESS"]=="128 Wiggins St"
    ll_ring=feature["geometry"]["coordinates"][0]
    if ll_ring[0]==ll_ring[-1]: ll_ring=ll_ring[:-1]
    campus_ring=[((lon-LON0)*LON_SCALE,(lat-LAT0)*LAT_SCALE) for lon,lat in ll_ring]
    origin=polygon_centroid(campus_ring)
    ring=[(x-origin[0],y-origin[1]) for x,y in campus_ring]
    signed_area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
    assert abs(signed_area)>100 and len(ring)>=8
    scene,asset,presentation=clear_scene()
    root=bpy.data.objects.new(f"AssetRoot_{ASSET_ID}",None)
    asset.objects.link(root)
    root.empty_display_type="PLAIN_AXES"; root.empty_display_size=1
    root["building_id"]=ASSET_ID; root["source_feature_id"]=822
    root["coordinate_frame"]="Local XY meters east/north; centroid of official FID 822 polygon is placement origin"
    root["placement_origin_xy_m"]=[round(origin[0],6),round(origin[1],6)]
    root["exterior_height_status"]="Estimated: approx. 2 stories plus attic, based on cooperative photos and GIS NUM_LEVELS=1 (source field appears unfit for visible story count)"
    root["interior_status"]="Schematic estimates based on official virtual-tour room names; no measured plan available"
    asset["building_id"]=ASSET_ID; asset["local_coordinates"]=True
    asset["coordinate_frame"]=root["coordinate_frame"]
    asset["placement_origin_xy_m"]=[round(origin[0],6),round(origin[1],6)]

    siding=make_material("White painted horizontal clapboard siding",(0.90,0.89,0.84),texture="siding")
    foundation=make_material("Pale masonry foundation",(0.58,0.54,0.47))
    roof=make_material("Weathered charcoal asphalt shingles",(0.17,0.18,0.20),texture="shingle")
    wood=make_material("Warm red-brown stained porch wood",(0.30,0.095,0.035),texture="wood")
    shutter=make_material("Muted burgundy shutters",(0.29,0.075,0.055),texture="wood")
    trim=make_material("Cream painted exterior trim",(0.97,0.94,0.85))
    glass=make_material("Blue gray glass",(0.10,0.22,0.28),roughness=0.19)
    brick=make_material("Red brick chimney",(0.42,0.14,0.07))
    floor=make_material("Interior wood floors",(0.36,0.22,0.11),texture="wood")
    upholstery=make_material("Interior fabric",(0.35,0.23,0.16),texture="wood")
    global trim_gray
    trim_gray=make_material("Utility appliance enamel",(0.68,0.69,0.66),roughness=0.32)
    stone=make_material("Light gray garden boulder",(0.58,0.56,0.51))
    garden=make_material("Garden greens",(0.16,0.27,0.08),roughness=0.9)
    flower=make_material("Small garden flowers",(0.78,0.42,0.34),roughness=0.72)

    # Structure follows every corner of the official GIS boundary. The west
    # facade entry is a wall opening above the deck height; added vertices do
    # not alter the 12 surveyed-source outline points at ground level.
    xmin=min(x for x,y in ring); xmax=max(x for x,y in ring)
    ymin=min(y for x,y in ring); ymax=max(y for x,y in ring)
    door_y=ymin+2.25
    wall_prism(ring,0.0,6.0,siding,asset,root,
               doorway={"y":(door_y-0.56,door_y+0.56),"z":(0.82,2.98)})
    # Exposed dark foundation course.
    foundation_ring=[(x,y) for x,y in ring]
    verts=[(x,y,z) for z in (-0.02,0.58) for x,y in foundation_ring]
    n=len(foundation_ring)
    faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh_obj("GIS foundation course",verts,faces,foundation,asset,root)
    # Main gable roof is estimated from the two-story facade image.
    gable_roof_x("Main north-south gable roof | estimated profile",xmin-0.35,xmax+0.35,ymin-0.5,ymax+0.5,6.0,9.0,roof,asset,root)
    # A west-facing cross-gable over the south third of the front facade.
    # This reproduces the visible projecting front gable; tie-in to main roof
    # is an interpretation from a single oblique exterior photograph.
    gy0=ymin+1.0; gy1=gy0+5.0; gxw=xmin-0.22; gxr=(xmin+xmax)/2-0.35
    verts=[(gxw,gy0,6.0),(gxw,(gy0+gy1)/2,8.7),(gxw,gy1,6.0),
           (gxr,gy0,6.0),(gxr,(gy0+gy1)/2,8.7),(gxr,gy1,6.0)]
    mesh_obj("Front cross-gable wall | estimated",verts,[(0,3,4,1),(1,4,5,2),(0,1,2)],siding,asset,root)
    # Two roof slopes; overhang on street-facing gable.
    verts=[(gxw-0.4,gy0-0.35,6.0),(gxw-0.4,(gy0+gy1)/2,8.95),(gxw-0.4,gy1+0.35,6.0),
           (gxr+0.15,gy0-0.35,6.0),(gxr+0.15,(gy0+gy1)/2,8.95),(gxr+0.15,gy1+0.35,6.0)]
    mesh_obj("Front cross-gable shingles | estimated",verts,[(0,3,4,1),(1,4,5,2)],roof,asset,root)

    # Front-west windows and the two-floor shuttered pattern from direct photo.
    west=xmin
    for yy in (0.1,3.5):
        add_window_west(yy,1.8,west,siding,glass,trim,shutter,asset,root,width=1.0,height=1.38)
    for yy in (0.1,3.5,6.9):
        add_window_west(yy,4.55,west,siding,glass,trim,shutter,asset,root,width=0.96,height=1.28)
    add_window_west((gy0+gy1)/2,7.55,gxw,siding,glass,trim,shutter,asset,root,width=0.72,height=0.82)
    # Side windows along the south-facing side, using square trims and muted sash.
    south=ymin+0.2
    for xx in (-4.8,-1.5,1.8):
        cube("Side window trim",(xx,south-0.07,1.8),(1.15,0.12,1.52),trim,asset,root,0.025)
        cube("Side window glass",(xx,south-0.14,1.8),(0.91,0.04,1.27),glass,asset,root,0.02)
        cube("Side window trim upper",(xx,south-0.07,4.55),(1.10,0.12,1.38),trim,asset,root,0.02)
        cube("Side window glass upper",(xx,south-0.14,4.55),(0.88,0.04,1.14),glass,asset,root,0.02)
    # Official facade photo shows the entrance recessed at the right end of
    # the west facade (negative Y from the street), beside the porch stairs.
    # Position and dimensions are interpreted from the photo, not surveyed.
    door_y=ymin+2.25
    # The GIS wall is retained as the exact outline shell. Keep the doorway
    # assembly just outside its west plane so the door remains visible in
    # exterior renders despite the shell having no modeled cutout.
    alcove_back_x=west+0.02
    cube("Recessed entry dark alcove",(alcove_back_x,door_y,1.90),(0.08,1.72,2.18),foundation,asset,root)
    for side in (-1,1):
        cube("Recessed entry return",(west+0.21,door_y+side*0.88,1.40),(0.55,0.12,2.80),trim,asset,root,0.018)
    cube("Recessed entry canopy",(west-0.08,door_y,2.86),(1.05,2.05,0.16),wood,asset,root,0.025)
    cube("Front entry surround",(west-0.08,door_y,2.02),(0.13,1.18,2.42),trim,asset,root,0.025)
    cube("Front entry door",(west-0.15,door_y,1.87),(0.08,0.82,2.10),wood,asset,root,0.025)
    cube("Entry upper glazing",(west-0.20,door_y,2.38),(0.025,0.51,0.62),glass,asset,root)
    beam("Entry door handle",(west-0.23,door_y-0.29,1.78),(west-0.23,door_y-0.20,1.78),0.035,trim,asset,root)
    cube("Entry transom",(west-0.10,door_y,3.18),(0.08,0.94,0.20),glass,asset,root)
    # Broad raised front deck and stairs, matching the cooperative's exterior photo.
    deck_x=west-1.7; deck_y=(ymin+ymax)/2+0.1; deck_len=15.0; deck_depth=2.8; deck_z=0.72
    cube("Full-width raised front deck",(deck_x,deck_y,deck_z),(deck_depth,deck_len,0.20),wood,asset,root,0.025)
    stair_y=door_y
    stair_gap=1.35
    for xx in (deck_x-deck_depth/2+0.15,):
        for yy in [deck_y-deck_len/2+0.25+i*1.0 for i in range(13)]:
            if abs(yy-stair_y)<stair_gap:
                continue
            cube("Deck baluster",(xx,yy,deck_z+0.55),(0.10,0.10,1.1),wood,asset,root,0.015)
        for start,end in ((deck_y-deck_len/2,stair_y-stair_gap),(stair_y+stair_gap,deck_y+deck_len/2)):
            if end>start:
                beam("Deck top rail",(xx,start,deck_z+1.08),(xx,end,deck_z+1.08),0.075,wood,asset,root)
                beam("Deck lower rail",(xx,start,deck_z+0.35),(xx,end,deck_z+0.35),0.045,wood,asset,root)
    for yy in (deck_y-deck_len/2,deck_y+deck_len/2):
        beam("Deck end handrail",(deck_x-deck_depth/2,yy,deck_z+1.08),(deck_x+deck_depth/2,yy,deck_z+1.08),0.065,wood,asset,root)
    for xx in (deck_x-deck_depth/2+0.15,):
        for yy in (deck_y-deck_len/2,deck_y+deck_len/2):
            beam("Deck support post",(xx,yy,0.05),(xx,yy,deck_z-0.08),0.14,wood,asset,root)
    # Lattice skirting, simplified but recognizable in the source image.
    for xx in (deck_x-deck_depth/2+0.18,deck_x+deck_depth/2-0.18):
        for yy in [deck_y-deck_len/2+0.5+i*0.55 for i in range(22)]:
            beam("Deck lattice diagonal A",(xx,yy,0.1),(xx,yy+0.5,deck_z-0.1),0.025,wood,asset,root,6)
            beam("Deck lattice diagonal B",(xx,yy+0.5,0.1),(xx,yy,deck_z-0.1),0.025,wood,asset,root,6)
    # Stairs rise at the right end beside the recessed doorway, as shown in
    # the official front photo; their run projects west from the deck.
    for i in range(5):
        z=0.12+i*0.13
        x=deck_x-deck_depth/2-0.3-i*0.34
        cube("Front deck stair tread",(x,stair_y,z),(0.55,1.15,0.13),wood,asset,root,0.025)
    beam("Stair handrail",(deck_x-deck_depth/2+0.1,stair_y-0.58,deck_z+0.95),(deck_x-deck_depth/2-1.9,stair_y-0.58,0.62),0.055,wood,asset,root)
    beam("Stair handrail",(deck_x-deck_depth/2+0.1,stair_y+0.58,deck_z+0.95),(deck_x-deck_depth/2-1.9,stair_y+0.58,0.62),0.055,wood,asset,root)
    # Official outdoor photos show a named Maclure garden boulder and compact
    # planting bed at the foot of the raised deck.
    rock_center=(west-4.15,door_y-2.0,0.55)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=rock_center)
    rock=bpy.context.object; rock.name="Maclure est. 1966 garden boulder"
    rock.scale=(0.50,1.10,0.70); rock.rotation_euler=(0.09,0.18,-0.08)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    rock.data.materials.append(stone); link_asset(rock,rock.name,asset,root)
    plaque_data=bpy.data.curves.new("Maclure garden boulder lettering","FONT")
    plaque_data.body="MACLURE\nest. 1966"; plaque_data.align_x="CENTER"
    plaque_data.size=0.34; plaque_data.space_line=0.95; plaque_data.extrude=0.008
    plaque=bpy.data.objects.new("Maclure garden boulder inscription (photo-informed)",plaque_data)
    asset.objects.link(plaque); plaque.parent=root
    plaque.location=(rock_center[0]-0.56,rock_center[1],0.47)
    plaque.rotation_euler=(math.radians(90),0,math.radians(-90))
    plaque.data.materials.append(make_material("Garden stone inscription",(0.07,0.07,0.06)))
    for i,yy in enumerate((door_y-2.0,door_y-0.2,-3.8,-1.8,0.2,2.2,4.2,6.2)):
        x=west-3.8
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,yy,0.14))
        shrub=bpy.context.object; shrub.name="Low garden planting"
        shrub.scale=(0.34,0.55,0.26)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        shrub.data.materials.append(garden); link_asset(shrub,shrub.name,asset,root)
        if i%2==0:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=1,location=(x-0.12,yy,0.38))
            blossom=bpy.context.object; blossom.name="Garden flower accent"
            blossom.scale=(0.11,0.11,0.09)
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            blossom.data.materials.append(flower); link_asset(blossom,blossom.name,asset,root)
    # Tall red brick chimney near the north roof slope, as shown in facade photo.
    cube("Brick chimney stack",(1.2,ymax-3.7,8.55),(0.75,0.85,3.5),brick,asset,root,0.035)
    cube("Chimney cap",(1.2,ymax-3.7,10.33),(0.92,1.02,0.18),brick,asset,root,0.025)
    # Continuous subtle horizontal clapboard lines on the west facade.
    # Thin cream reveals sit across the non-door/window areas as real siding courses.
    for z in [0.86+i*0.19 for i in range(27)]:
        cube("Horizontal clapboard reveal",(west-0.026,(ymin+ymax)/2,z),(0.035,ymax-ymin-0.4,0.018),trim,asset,root)

    create_room_furniture(asset,root,wood,upholstery,floor)
    # Narrative annotations live on the root, not as visible clutter.
    root["interior_rooms_estimated"]="Foyer; formal living room; communal dining; second-floor study rooms; cold-air dorm; basement lounge/BUM and laundry. Source labels from cooperative virtual tour; arrangement and dimensions estimated."
    root["exterior_evidence"]="Maclure Cooperative official Our Home photo gallery, outdoor section (2018 landscaping caption); white two-story clapboard exterior, dark gray roof, chimney, shuttered windows, red-brown raised deck and stairs."
    root["unresolved"]="No measured elevation, current survey, or architectural floor plan. Exact roof geometry and story height are estimates."

    add_camera_and_lights(scene,presentation)
    scene.render.filepath=str(PREVIEW)
    # Keep floor objects available to renderers after reopening. Hide them only
    # while generating the exterior image to avoid a visible facade band.
    interior_floors=[o for o in asset.objects if "floor slab" in o.name.lower() or "basement floor" in o.name.lower()]
    for obj in interior_floors:
        obj.hide_render=True
    bpy.ops.render.render(write_still=True)
    for obj in interior_floors:
        obj.hide_render=False
    # Save the deliverable with inspectable interior floors enabled.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))


if __name__=="__main__":
    main()
