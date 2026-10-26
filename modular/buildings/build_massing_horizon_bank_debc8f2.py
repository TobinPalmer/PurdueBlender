"""Rebuild the Horizon Bank asset from its 2018 LiDAR building footprint.

The asset keeps the campus-coordinate frame used by existing massing libraries.
Exterior form is informed by the current Google Street View pano; interior scene
is explicitly schematic because no as-built plan has been located.
Run with Blender 5.2: blender --background --python this_file.py
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_horizon_bank_debc8f2.blend"
EVIDENCE = ROOT / "audit/horizon_bank"
RAW_FOOTPRINT = EVIDENCE / "sources/indiana_footprint_objectid_430274_2026-10-26.json"
ASSET_ID = "massing_horizon_bank_debc8f2"
ASSET_COLLECTION = "Asset_" + ASSET_ID
ASSET_SCENE = "Building_" + ASSET_ID
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
LAT_M, LON_M = 111040.0, 84810.60416539927
WALL_H, ROOF_H = 4.55, 5.15


def campus_xy(lon, lat):
    return ((lon - ORIGIN_LON) * LON_M, (lat - ORIGIN_LAT) * LAT_M)


def material(name, color, roughness=.75, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    return m


def brick_material():
    m = material("Horizon | warm red-brown brick, procedural", (.34, .105, .061), .82)
    n = m.node_tree.nodes
    links = m.node_tree.links
    p = n.get("Principled BSDF")
    tex = n.new("ShaderNodeTexBrick")
    tex.inputs["Color1"].default_value = (.29, .074, .043, 1)
    tex.inputs["Color2"].default_value = (.44, .16, .09, 1)
    tex.inputs["Mortar"].default_value = (.55, .48, .39, 1)
    tex.inputs["Scale"].default_value = 3.2
    tex.inputs["Mortar Size"].default_value = .035
    tex.inputs["Mortar Smooth"].default_value = .01
    tex.inputs["Brick Width"].default_value = .5
    tex.inputs["Row Height"].default_value = .25
    coord = n.new("ShaderNodeTexCoord")
    links.new(coord.outputs["Generated"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], p.inputs["Base Color"])
    return m


def box(name, loc, dims, mat, collection):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    collection.objects.link(o)
    return o


def mesh_obj(name, verts, faces, mat, collection):
    me = bpy.data.meshes.new(name + "Mesh")
    me.from_pydata(verts, [], faces)
    me.materials.append(mat)
    me.update()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    return ob


def arch_mesh(name, cx, y, z0, width, straight_h, arch_h, mat, collection, thickness=.12):
    """Raised arched glazing/frame profile, front plane is X-Z, faces north."""
    n = 12
    r = width / 2
    profile = [(-r, z0), (r, z0), (r, z0 + straight_h)]
    for i in range(n + 1):
        a = math.pi * i / n
        profile.append((r * math.cos(a), z0 + straight_h + arch_h * math.sin(a)))
    profile.append((-r, z0))
    verts = []
    for yy in (y, y + thickness):
        verts.extend((cx + x, yy, z) for x, z in profile)
    k = len(profile)
    faces = [tuple(range(k)), tuple(range(k, 2*k))]
    faces += [(i, (i+1)%k, (i+1)%k+k, i+k) for i in range(k)]
    return mesh_obj(name, verts, faces, mat, collection)


def set_collection(obj, c):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    c.objects.link(obj)


def main():
    if not RAW_FOOTPRINT.exists():
        raise FileNotFoundError(RAW_FOOTPRINT)
    data = json.loads(RAW_FOOTPRINT.read_text(encoding="utf-8"))
    feat = next(f for f in data["features"] if int(f["properties"]["objectid"]) == 430274)
    ring = feat["geometry"]["coordinates"][0]
    footprint = [campus_xy(lon, lat) for lon, lat in ring[:-1]]
    if len(footprint) != 8:
        raise ValueError(f"Expected eight distinct LiDAR footprint vertices, got {len(footprint)}")
    xmin, xmax = min(x for x, _ in footprint), max(x for x, _ in footprint)
    ymin, ymax = min(y for _, y in footprint), max(y for _, y in footprint)
    cx, cy = sum(x for x, _ in footprint)/len(footprint), sum(y for _, y in footprint)/len(footprint)

    # Replace only contents in this owned asset file when run from a factory scene.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name != "Collection":
            bpy.data.collections.remove(c)
    main_scene = bpy.context.scene
    main_scene.name = ASSET_SCENE
    asset = bpy.data.collections.new(ASSET_COLLECTION)
    main_scene.collection.children.link(asset)
    detail = bpy.data.collections.new("Horizon_Bank_Exterior_Details")
    asset.children.link(detail)

    brick = brick_material()
    stone = material("Horizon | pale limestone trim", (.73, .68, .57), .72)
    roof = material("Horizon | charcoal standing-seam roof", (.105, .125, .14), .68, .12)
    glass = material("Horizon | blue-gray reflective glazing", (.045, .115, .15), .2, .48)
    frame = material("Horizon | dark bronze window frames", (.105, .09, .072), .4, .45)
    sign_green = material("Horizon | forest green sign", (.02, .19, .12), .4)
    white = material("Horizon | warm-white lettering", (.92, .88, .71), .5)
    concrete = material("Horizon | warm concrete plinth", (.47, .45, .41), .85)

    # LiDAR polygon walls and slab retain exact plan outline, rather than a box.
    N = len(footprint)
    wall_verts = [(x,y,0) for x,y in footprint] + [(x,y,WALL_H) for x,y in footprint]
    wall_faces = [(i, (i+1)%N, (i+1)%N+N, i+N) for i in range(N)]
    mesh_obj("Horizon_Bank_LiDAR_Footprint_Walls", wall_verts, wall_faces, brick, asset)
    mesh_obj("Horizon_Bank_Foundation_Slab", [(x,y,-.18) for x,y in footprint], [tuple(range(N))], concrete, asset)
    # Two shallow gable roofs cover the source polygon's main wing and return.
    # This makes the L footprint's roof legible without inventing a single pyramid.
    def gable(name, x0, x1, y0, y1, ridge_z):
        ym=(y0+y1)/2
        v=[(x0,y0,WALL_H),(x1,y0,WALL_H),(x0,y1,WALL_H),(x1,y1,WALL_H),
           (x0,ym,ridge_z),(x1,ym,ridge_z)]
        f=[(2,3,5,4),(0,1,5,4),(0,2,4),(1,3,5)]
        mesh_obj(name,v,f,roof,asset)
    gable("Horizon_Bank_Main_Wing_Gable_Roof",xmin,-729.30,ymin,ymax,ROOF_H)
    gable("Horizon_Bank_East_Return_Gable_Roof",-730.62,xmax,2251.72,2261.65,ROOF_H-.12)
    # Masonry eave fascia and corner quoins create a legible roof edge.
    for i,(x,y) in enumerate(footprint):
        x2,y2=footprint[(i+1)%N]
        length=math.hypot(x2-x,y2-y)
        if length < .5: continue
        angle=math.atan2(y2-y,x2-x)
        trim=box(f"Horizon_Eave_Fascia_{i+1}",((x+x2)/2,(y+y2)/2,WALL_H-.08),(length,.20,.25),stone,detail)
        trim.rotation_euler[2]=angle

    # North-facing entrance elevation: source Street View shows central brick tower,
    # tall arched entry glazing, green Horizon sign, pale stone pilasters and windows.
    front_y = max(y for _,y in footprint)
    north_edges=[]
    for i,(x,y) in enumerate(footprint):
        x2,y2=footprint[(i+1)%N]
        if abs(y-front_y)<.4 and abs(y2-front_y)<.4 and abs(x2-x)>5:
            north_edges.append((x,y,x2,y2))
    if not north_edges: raise RuntimeError("Could not identify north/front facade edge from LiDAR ring")
    fx0,fy0,fx1,fy1=max(north_edges,key=lambda e:abs(e[2]-e[0]))
    fmin,fmax=sorted((fx0,fx1)); fmid=(fmin+fmax)/2
    # The tower rises above the one-story wings and sits on the frontage centerline.
    tower_w=3.6
    box("Horizon_Central_Entry_Tower",(fmid,front_y+.12,(WALL_H+6.05)/2),(tower_w,.30,6.05-WALL_H),brick,detail)
    box("Horizon_Tower_Cornice",(fmid,front_y+.13,6.08),(tower_w+.3,.44,.22),stone,detail)
    # Full-height arch surround, dark door glazing and bronze door rails.
    arch_mesh("Horizon_Arched_Entry_Stone_Surround",fmid,front_y+.30,.18,1.62,2.55,.62,stone,detail,.15)
    arch_mesh("Horizon_Arched_Entry_Glazing",fmid,front_y+.47,.25,1.18,2.38,.48,glass,detail,.025)
    box("Horizon_Entry_Door_Stile",(fmid,front_y+.51,1.42),(.045,.035,2.35),frame,detail)
    box("Horizon_Entry_Threshold",(fmid,front_y+.38,.10),(1.9,.75,.20),stone,detail)
    # Logo board and modest dimensional lettering.
    box("Horizon_Green_Sign_Panel",(fmid,front_y+.33,5.45),(2.65,.14,.62),sign_green,detail)
    def text_obj(name, body, loc, size, mat):
        cu=bpy.data.curves.new(name,"FONT"); cu.body=body; cu.size=size; cu.align_x="CENTER"; cu.align_y="CENTER"; cu.extrude=.006
        ob=bpy.data.objects.new(name,cu); detail.objects.link(ob); ob.location=loc; ob.rotation_euler=(-math.pi/2,0,math.pi); cu.materials.append(mat); return ob
    text_obj("Horizon_Sign_Lettering","HORIZON",(fmid,front_y+.42,5.52),.29,white)
    # Four glazed bays with stone surrounds, brick spandrels, and slim bronze mullions.
    usable=(fmax-fmin)-tower_w-1.0
    bay_centers=[fmin+1.35, fmin+4.45, fmax-4.45, fmax-1.35]
    for j,x in enumerate(bay_centers):
        # Window backing, four-paned glazing, stone jamb/header/sill.
        wid=2.05; zc=2.20; h=2.30; y=front_y+.12
        box(f"Horizon_Front_Window_Glass_{j+1}",(x,y+.09,zc),(wid,.09,h),glass,detail)
        for xx in (x-wid/2-.08,x+wid/2+.08):
            box(f"Horizon_Front_Window_Stone_Jamb_{j+1}_{xx:.2f}",(xx,y+.13,zc),(.16,.28,h+.34),stone,detail)
        box(f"Horizon_Front_Window_Sill_{j+1}",(x,y+.15,zc-h/2-.08),(wid+.38,.34,.16),stone,detail)
        box(f"Horizon_Front_Window_Header_{j+1}",(x,y+.15,zc+h/2+.08),(wid+.38,.30,.16),stone,detail)
        for k in (-1,0,1):
            box(f"Horizon_Front_Mullion_{j+1}_{k}",(x+k*wid/3,y+.17,zc),(.045,.055,h-.05),frame,detail)
        box(f"Horizon_Front_Transom_{j+1}",(x,y+.18,zc+.30),(wid,.055,.045),frame,detail)
    # Simple side wall window rhythm mirrors the observed bank branch glazing.
    for i,(x,y) in enumerate(footprint):
        x2,y2=footprint[(i+1)%N]
        if abs(x2-x)<.4 and abs(y2-y)>5:
            sign=1 if x2>x else -1
            xx=(x+x2)/2
            for j,yy in enumerate([y+(y2-y)*.32,y+(y2-y)*.68]):
                ob=box(f"Horizon_Side_Glazing_{i}_{j}",(xx+sign*.10,yy,2.25),(.12,2.10,2.18),glass,detail)
                for dz in (-1.18,1.18):
                    box(f"Horizon_Side_Stone_Sill_{i}_{j}_{dz}",(xx+sign*.15,yy,2.25+dz),(.30,2.36,.14),stone,detail)
    # Schematic-only interior, separated into its own scene with explicit warning label.
    interior_scene=bpy.data.scenes.new("Horizon_Bank_Interior_Schematic_NOT_AS_BUILT")
    interior=bpy.data.collections.new("Horizon_Bank_Interior_Schematic_NOT_AS_BUILT")
    interior_scene.collection.children.link(interior)
    # Keep layout simplified: lobby, teller line, service rooms; not as-built claims.
    floor=material("Schematic interior | neutral floor",(.49,.45,.37),.84)
    furniture=material("Schematic interior | muted walnut",(.21,.11,.06),.72)
    pale=material("Schematic interior | off-white partitions",(.78,.75,.67),.82)
    box("SCHEMATIC_NOT_AS_BUILT_Lobby_Floor",(cx,cy,.01),(xmax-xmin-1.0,ymax-ymin-1.0,.05),floor,interior)
    box("SCHEMATIC_NOT_AS_BUILT_Teller_Counter",(fmid,cy+.5,1.05),(8.0,.85,1.35),furniture,interior)
    for i in range(3):
        box(f"SCHEMATIC_NOT_AS_BUILT_Service_Partition_{i+1}",(xmin+4+i*2.5,cy-5,1.45),(.14,4.8,2.9),pale,interior)
    for i in range(4):
        box(f"SCHEMATIC_NOT_AS_BUILT_Lobby_Seat_{i+1}",(cx-4+i*2.2,cy+5,.55),(1.2,.65,.55),furniture,interior)
    text_obj("SCHEMATIC_WARNING","SCHEMATIC INTERIOR - NOT AS BUILT",(cx,cy,7.0),.55,white)
    # The warning label is only meaningful within interior scene.
    label=bpy.data.objects.get("SCHEMATIC_WARNING")
    if label: set_collection(label,interior)

    # Correct asset collection membership and source metadata.
    asset["building_id"]=ASSET_ID
    asset["source_footprint_feature_id"]="Indiana Building Footprints 2016-2020 / objectid 430274"
    asset["footprint_lidaryear"]="2018"
    asset["interior_status"]="schematic only; not as-built"
    main_scene.render.engine="BLENDER_EEVEE"
    main_scene.render.resolution_x=1000; main_scene.render.resolution_y=720; main_scene.render.resolution_percentage=100
    main_scene.world.color=(.5,.5,.5)
    main_scene.world.use_nodes=True
    bg=main_scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value=(.55,.59,.65,1)
    bg.inputs["Strength"].default_value=.65
    main_scene.view_settings.view_transform="AgX"
    main_scene.view_settings.look="AgX - Medium High Contrast"
    # Preview camera and lighting live outside the exported asset collection.
    preview=bpy.data.collections.new("Horizon_Bank_Preview_Only")
    main_scene.collection.children.link(preview)
    bpy.ops.object.camera_add(location=(cx-35,front_y+40,24))
    cam=bpy.context.object; cam.name="Preview_Camera_Horizon_Bank"; cam.data.type="ORTHO"; cam.data.ortho_scale=42
    cam.rotation_euler=(Vector((cx,cy,2.4))-cam.location).to_track_quat("-Z","Y").to_euler(); set_collection(cam,preview); main_scene.camera=cam
    bpy.ops.object.light_add(type="AREA",location=(cx-10,front_y+20,28)); light=bpy.context.object; light.name="Preview_Key_Light"; light.data.energy=7800; light.data.shape="DISK"; light.data.size=18
    light.rotation_euler=(Vector((cx,cy,2))-light.location).to_track_quat("-Z","Y").to_euler(); set_collection(light,preview)
    bpy.ops.object.light_add(type="AREA",location=(cx+12,front_y+12,13)); fill=bpy.context.object; fill.name="Preview_Facade_Fill"; fill.data.energy=2600; fill.data.shape="DISK"; fill.data.size=14
    fill.rotation_euler=(Vector((cx,cy,2))-fill.location).to_track_quat("-Z","Y").to_euler(); set_collection(fill,preview)
    # Camera and lighting are hidden from viewport selection but render normally.
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active=None
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    main_scene.render.filepath=str(EVIDENCE/"horizon_bank_exterior_preview.png")
    bpy.ops.render.render(write_still=True)
    print("HORIZON_ASSET_SAVED", ASSET)
    print("FOOTPRINT_BOUNDS",xmin,xmax,ymin,ymax,"AREA_M2",feat["properties"].get("SHAPE__Area"))
    print("ASSET_OBJECTS",len(asset.all_objects),"INTERIOR_OBJECTS",len(interior.all_objects))


if __name__ == "__main__":
    main()
