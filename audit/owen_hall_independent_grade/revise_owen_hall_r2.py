"""Source-led facade and room-vignette refinement for Owen Hall."""
import bpy
import bmesh
import json
import math
from mathutils import Vector, Quaternion
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLEND = ROOT / "modular" / "buildings" / "owen_hall.blend"


def get_material(name, color, roughness=0.42, metallic=0.2):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    node.inputs["Base Color"].default_value = color
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Metallic"].default_value = metallic
    return mat


def make_mesh(name, boxes, mat, collection):
    """Build one mesh from (center, dimensions, rotation) box parts."""
    verts, faces = [], []
    unit = [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),
            (-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
    face_pattern = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for center, dims, rot in boxes:
        base = len(verts)
        c = Vector(center)
        d = Vector(dims)
        for x,y,z in unit:
            v = Vector((x*d.x, y*d.y, z*d.z))
            if rot is not None:
                v = rot @ v
            verts.append(tuple(c + v))
        faces.extend(tuple(base+i for i in face) for face in face_pattern)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def move_and_size(obj, xyz=None, dims=None):
    mat = obj.matrix_world.copy()
    if xyz is not None:
        mat.translation = Vector(xyz)
        obj.matrix_world = mat
    if dims is not None:
        obj.dimensions = dims


def run():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    asset = bpy.data.collections["Asset_owen_hall"]
    # Remove only this revision's generated groups, making the file repeatable.
    for name in ("Owen_R2_WindowFrames_All", "Owen_R2_WindowLouvers_All",
                 "Owen_R2_Entry_Rails", "Owen_R2_Entry_Stairs",
                 "Owen_R2_StandardRoom_Amenities", "Owen_R2_Room_Wall_Details"):
        obj = bpy.data.objects.get(name)
        if obj:
            data = obj.data if obj.type == "MESH" else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if data and data.users == 0:
                bpy.data.meshes.remove(data)
    for obj in [o for o in asset.objects if o.name.startswith("Owen_R2_StandardDouble_")]:
        data = obj.data if obj.type == "MESH" else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)

    # Exterior photo shows narrow, tall divided windows; repeated concrete bands;
    # and louver panels on some bays. These dimensions are visual refinements,
    # not surveyed measurements.
    glass_prefixes = (
        "Owen_Win_East_SE_", "Owen_Win_East_NE_", "Owen_Win_West_SW_",
        "Owen_Win_West_NW_", "Owen_Win_North_NW_", "Owen_Win_North_NE_",
        "Owen_Win_South_SW_", "Owen_Win_South_SE_",
    )
    frame_boxes, louver_boxes = [], []
    steel = get_material("Owen_R2_Aluminum_Window_Frame", (.40,.45,.49,1), .38, .48)
    side_sills = [o for o in asset.objects if o.name.startswith((
        "Owen_Sill_East_SE_", "Owen_Sill_East_NE_", "Owen_Sill_West_SW_", "Owen_Sill_West_NW_"))]
    end_sills = [o for o in asset.objects if o.name.startswith((
        "Owen_Sill_North_NW_", "Owen_Sill_North_NE_", "Owen_Sill_South_SW_", "Owen_Sill_South_SE_"))]
    for obj in list(asset.objects):
        if not obj.name.startswith(glass_prefixes):
            continue
        side = obj.name.startswith(("Owen_Win_East_", "Owen_Win_West_"))
        center = obj.matrix_world.translation.copy()
        sign = 1 if "East" in obj.name else -1
        if side:
            center.x = 40.88 if sign > 0 else -46.88
            dimensions = (.16, 1.18, 2.75)
        else:
            north = "North" in obj.name
            center.y = 55.55 if north else -51.93
            dimensions = (1.18, .16, 2.75)
        move_and_size(obj, tuple(center), dimensions)
        half_w = .59
        half_h = 1.375
        depth = .10
        if side:
            x = center.x + sign * .06
            frame_boxes.extend([
                ((x,center.y-half_w+.025,center.z),(depth,.05,2.72),None),
                ((x,center.y+half_w-.025,center.z),(depth,.05,2.72),None),
                ((x,center.y,center.z-half_h+.025),(depth,1.18,.05),None),
                ((x,center.y,center.z+half_h-.025),(depth,1.18,.05),None),
                ((x,center.y,center.z-.44),(depth,1.14,.035),None),
                ((x,center.y,center.z+.46),(depth,1.14,.035),None),
                ((x,center.y,center.z), (depth,.035,2.68),None),
            ])
            plane_axis = "x"
        else:
            y = center.y + (.06 if north else -.06)
            frame_boxes.extend([
                ((center.x-half_w+.025,y,center.z),(.05,depth,2.72),None),
                ((center.x+half_w-.025,y,center.z),(.05,depth,2.72),None),
                ((center.x,y,center.z-half_h+.025),(1.18,depth,.05),None),
                ((center.x,y,center.z+half_h-.025),(1.18,depth,.05),None),
                ((center.x,y,center.z-.44),(1.14,depth,.035),None),
                ((center.x,y,center.z+.46),(1.14,depth,.035),None),
                ((center.x,y,center.z),(.035,depth,2.68),None),
            ])
            plane_axis = "y"
        # The Purdue image shows louvered upper sections on a subset of bays.
        # Repeating one source-supported louvered form every third bay avoids
        # asserting that every existing window has the same operable panel.
        try:
            index = int(obj.name.rsplit("_",1)[1])
        except ValueError:
            index = 0
        if index % 3 == 0:
            if plane_axis == "x":
                for j in range(5):
                    z = center.z + .86 + j*.095
                    louver_boxes.append(((center.x+sign*.13,center.y,z),(.12,1.06,.035),None))
            else:
                sy = 1 if north else -1
                for j in range(5):
                    z = center.z + .86 + j*.095
                    louver_boxes.append(((center.x,center.y+sy*.13,z),(1.06,.12,.035),None))

    for sill in side_sills:
        c = sill.matrix_world.translation.copy()
        east = "East" in sill.name
        c.x = 40.91 if east else -46.91
        c.z = 1.1 + 3.8*round((c.z-1.52)/3.8)
        move_and_size(sill, tuple(c), (.25,1.30,.12))
    for sill in end_sills:
        c = sill.matrix_world.translation.copy()
        north = "North" in sill.name
        c.y = 55.58 if north else -51.96
        c.z = 1.1 + 3.8*round((c.z-1.52)/3.8)
        move_and_size(sill, tuple(c), (1.30,.25,.12))
    make_mesh("Owen_R2_WindowFrames_All", frame_boxes, steel, asset)
    make_mesh("Owen_R2_WindowLouvers_All", louver_boxes, steel, asset)

    # Add visible treads and handrails to the north entrance. The Purdue exterior
    # photo supports the steps/rails; all vertical dimensions here stay schematic.
    old_steps = bpy.data.objects.get("Owen_North_Entrance_Plinth_Stairs")
    if old_steps:
        bpy.data.objects.remove(old_steps, do_unlink=True)
    stone = bpy.data.materials.get("Indiana_Bedford_Limestone")
    steps = []
    cx = -2.89
    for i in range(5):
        rise = .10*(i+1)
        y = 29.2 - i*.48
        steps.append(((cx,y,rise/2),(6.4,.56,rise),None))
    steps.append(((cx,26.52,.52),(7.2,1.0,.12),None))
    make_mesh("Owen_R2_Entry_Stairs", steps, stone, asset)
    bronze = get_material("Owen_R2_Entry_Rail_Metal", (.22,.25,.27,1), .36, .62)
    rails=[]
    for sx in (-3.35,3.35):
        for i in range(5):
            y=29.05-i*.48
            z=.30+i*.10
            rails.append(((cx+sx,y,z+.02),(.055,.055,.60),None))
        # Sloping grasp rail, represented as a rotated rectangular beam.
        a=Vector((cx+sx,29.15,.65)); b=Vector((cx+sx,26.70,1.05))
        delta=b-a
        q=Vector((0,0,1)).rotation_difference(delta.normalized())
        rails.append(((a+b)*.5,(.07,.07,delta.length),q))
    make_mesh("Owen_R2_Entry_Rails", rails, bronze, asset)

    # The current Purdue standard double-room dimensions and furniture list are
    # published as approximate/reference illustrations. Refine the existing
    # room vignette to those published room/closet/mattress dimensions only.
    room_center=Vector((-36.89,-34.50,0.0))
    room_x, room_y = 4.8768, 3.4544
    def item(name): return bpy.data.objects.get(name)
    obj=item("Owen_Dorm_StandardRoom_Floor") or item("Owen_Dorm_Room216_Floor")
    move_and_size(obj,(-36.89,-34.50,.08),(room_x,room_y,.12))
    obj=item("Owen_Dorm_StandardRoom_Wall_N") or item("Owen_Dorm_Room216_Wall_N")
    move_and_size(obj,(-36.89,-34.50+room_y/2,1.9),(room_x,.20,3.8))
    obj=item("Owen_Dorm_StandardRoom_Wall_S") or item("Owen_Dorm_Room216_Wall_S")
    move_and_size(obj,(-36.89,-34.50-room_y/2,1.9),(room_x,.20,3.8))
    obj=item("Owen_Dorm_StandardRoom_Wall_E") or item("Owen_Dorm_Room216_Wall_E")
    move_and_size(obj,(-36.89+room_x/2,-34.50,1.9),(.20,room_y,3.8))
    obj=item("Owen_Dorm_StandardRoom_Door") or item("Owen_Dorm_Room216_Door")
    move_and_size(obj,(-36.89+room_x/2,-35.50,1.25),(.10,1.0,2.4))
    # Two standard mattresses and desk sets, shifted inward to fit the published room.
    for i,y in enumerate((-35.50,-33.50)):
        for part,dims in (("Bed_Frame",(2.05,1.00,.60)),("Bed_Mattress",(1.9558,.9144,.18)),("Bed_Pillow",(.50,.72,.14))):
            obj=item(f"Owen_Dorm_{part}_{i}")
            if obj:
                old=obj.matrix_world.translation.copy()
                x=-38.19 if part!="Bed_Pillow" else -38.94
                z={"Bed_Frame":.45,"Bed_Mattress":.72,"Bed_Pillow":.88}[part]
                move_and_size(obj,(x,y,z),dims)
        obj=item(f"Owen_Dorm_Desk_{i}")
        if obj: move_and_size(obj,(-35.34,y,.65),(1.20,.72,.76))
        obj=item(f"Owen_Dorm_Desk_Hutch_{i}")
        if obj: move_and_size(obj,(-34.89,y,1.40),(.30,.72,.80))
        obj=item(f"Owen_Dorm_Desk_Chair_{i}")
        if obj: move_and_size(obj,(-35.89,y,.55),(.58,.58,.82))
    obj=item("Owen_Dorm_Wardrobes")
    move_and_size(obj,(-36.09,-35.80,1.20),(1.2065,.762,2.20))

    oak=bpy.data.materials.get("Beering_Honey_Oak_Woodwork")
    dark=bpy.data.materials.get("Beering_Executive_Dark_Oak")
    white=bpy.data.materials.get("Tark_Appliance_White")
    small=[]
    # Purdue room guide lists dressers, bookshelves, desk lights, curtains,
    # network connections and waste baskets; this is a representative setup.
    for i,y in enumerate((-35.05,-33.95)):
        small.append(((-34.98,y,.47),(.68,.42,.90),None)) # dresser
        small.append(((-34.70,y,1.95),(.18,.72,.24),None)) # bookshelf
        small.append(((-35.05,y,.33),(.28,.28,.38),None)) # waste basket
        small.append(((-35.34,y,1.12),(.10,.10,.45),None)) # desk-light stem
        small.append(((-35.34,y,1.36),(.30,.18,.06),None)) # desk-light head
    make_mesh("Owen_R2_StandardRoom_Amenities",small,oak,asset)
    # A small metal wall plate represents the published network connection; one
    # towel rail and a simple curtain panel complete the listed room features.
    metal=get_material("Owen_R2_Interior_Detail_Metal",(.55,.57,.57,1),.45,.30)
    details=[((-34.43,-34.50,1.15),(.04,.13,.10),None),
             ((-39.15,-34.50,1.85),(.08,1.0,1.05),None)]
    make_mesh("Owen_R2_Room_Wall_Details",details,metal,asset)

    # Rename the former room-216 vignette so it no longer implies a verified
    # as-built room number. Duplicate the representative module to both wings
    # on all four stories. Its published dimensions/furniture are verified;
    # exact room placement and upper-floor partitions remain illustrative.
    for obj in asset.objects:
        if "Owen_Dorm_Room216_" in obj.name:
            obj.name = obj.name.replace("Owen_Dorm_Room216_", "Owen_Dorm_StandardRoom_")
        if "Owen_Dorm216_" in obj.name:
            obj.name = obj.name.replace("Owen_Dorm216_", "Owen_Dorm_StandardRoom_")
    camera = bpy.data.objects.get("Cam_31_Owen_Hall_Student_Dorm_Interior")
    if camera:
        camera.name = "Cam_31_Owen_Hall_Standard_Double_Room_Vignette"
    room_prefixes=("Owen_Dorm_StandardRoom_", "Owen_Dorm_Bed_", "Owen_Dorm_Desk_",
                   "Owen_Dorm_Wardrobes", "Owen_Dorm_Window_Box_Fan_",
                   "Owen_Light_Dorm216_Ceiling", "Owen_R2_StandardRoom_Amenities",
                   "Owen_R2_Room_Wall_Details")
    room_source=[o for o in asset.objects if o.name.startswith(room_prefixes)]
    room_parts=len(room_source)
    for floor in range(1,5):
        for side in ("West","East"):
            if floor == 1 and side == "West":
                continue # original room is the first west-side vignette
            dx=0.0 if side == "West" else 71.39
            dz=3.8*(floor-1)
            for original in room_source:
                duplicate=original.copy()
                if original.data is not None:
                    duplicate.data=original.data
                asset.objects.link(duplicate)
                world=original.matrix_world.copy()
                world.translation.x += dx
                world.translation.z += dz
                duplicate.matrix_world=world
                suffix=original.name.replace("Owen_Dorm_StandardRoom_","").replace("Owen_R2_StandardRoom_Amenities","Amenities").replace("Owen_R2_Room_Wall_Details","Wall_Details")
                duplicate.name=f"Owen_R2_StandardDouble_F{floor}_{side}_{suffix}"

    # No height setting is changed. Save only the Owen library.
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print(json.dumps({
        "saved":str(BLEND),"added_facade_assemblies":2,
        "refined_exterior_windows":len(frame_boxes)//7,
        "added_louvered_bays":len(louver_boxes)//5,
        "entrance_stair_parts":len(steps),"published_room_dimensions_m":[room_x,room_y],
        "illustrative_standard_room_modules":8,
        "objects_per_room_module":room_parts,
        "height_status":"unchanged; remains an estimate",
        "collection_object_count":len(asset.objects),
    },indent=2))


if __name__=="__main__":
    run()
