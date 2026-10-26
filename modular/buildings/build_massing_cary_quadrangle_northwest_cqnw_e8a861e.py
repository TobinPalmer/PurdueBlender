"""Rebuild CQNW massing from Purdue GIS, aerial, archival and lidar evidence.

The footprint is transformed with the documented campus conversion. Facade
openings and cross-gabled bays are schematic interpretations; heights are
estimates corroborated by a 2018 LiDAR normalized height model.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_cary_quadrangle_northwest_cqnw_e8a861e"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / ASSET_ID
SOURCE = EVIDENCE / "sources" / "purdue_building_shapes_fid647_2026-10-26.geojson"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

SIMPLIFY_TOLERANCE_M = 0.5
FOUNDATION_TOP = 0.85
WALL_TOP = 12.05
EAVES_Z = 12.2
RIDGE_Z = 14.9
FLOOR_BASES = (0.7, 3.55, 6.4, 9.25)
FLOOR_STEP = 2.85
FEET_TO_METERS = 1200.0 / 3937.0


def project_lon_lat(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def point_segment_distance(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    den = dx*dx + dy*dy
    t = 0.0 if den < 1e-12 else max(0.0, min(1.0, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))


def simplify_ring(points, tol):
    pts = list(points)
    while len(pts) > 8:
        distances = [point_segment_distance(p, pts[i-1], pts[(i+1) % len(pts)])
                     for i, p in enumerate(pts)]
        i = min(range(len(pts)), key=distances.__getitem__)
        if distances[i] > tol:
            break
        pts.pop(i)
    return pts


def signed_area(pts):
    return 0.5 * sum(pts[i][0]*pts[(i+1) % len(pts)][1] -
                     pts[(i+1) % len(pts)][0]*pts[i][1] for i in range(len(pts)))


def material(name, rgba, roughness=0.8):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgba, 1.0)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgba, 1.0)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    return m


def mesh_object(name, verts, faces, mat, collection):
    me = bpy.data.meshes.new(name + "Mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    me.materials.append(mat)
    return ob


def prism(name, pts, z0, z1, side_mat, top_mat, collection):
    n = len(pts)
    verts = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    faces = [(i, (i+1) % n, n+(i+1) % n, n+i) for i in range(n)]
    faces += [tuple(range(n, 2*n)), tuple(reversed(range(n)))]
    ob = mesh_object(name, verts, faces, side_mat, collection)
    ob.data.materials.append(top_mat)
    ob.data.polygons[-2].material_index = 1
    return ob


BOX_FACES = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))


def box_add(buf, center, width, depth, height, angle):
    cx, cy, cz = center
    c, s = math.cos(angle), math.sin(angle)
    verts = []
    for z in (-height/2, height/2):
        for y in (-depth/2, depth/2):
            for x in (-width/2, width/2):
                verts.append((cx+x*c-y*s, cy+x*s+y*c, cz+z))
    off = len(buf["verts"])
    buf["verts"].extend(verts)
    buf["faces"].extend(tuple(off+i for i in f) for f in BOX_FACES)


def box_batch(name, buf, mat, collection):
    if buf["verts"]:
        return mesh_object(name, buf["verts"], buf["faces"], mat, collection)


def gable_roof(name, u0, u1, v0, v1, eaves, ridge, u_axis, v_axis, mat, collection, overhang=0.55):
    u0 -= overhang; u1 += overhang
    v0 -= overhang; v1 += overhang
    vm = (v0+v1)/2
    def xyz(u, v, z): return (u_axis[0]*u+v_axis[0]*v, u_axis[1]*u+v_axis[1]*v, z)
    verts = [xyz(u0,v0,eaves),xyz(u0,vm,ridge),xyz(u0,v1,eaves),
             xyz(u1,v0,eaves),xyz(u1,vm,ridge),xyz(u1,v1,eaves)]
    faces = [(0,3,4,1),(1,4,5,2),(0,1,2),(3,5,4)]
    return mesh_object(name, verts, faces, mat, collection)


def gable_projection(name, u, side_v, side_sign, width, depth, base_z, peak_z,
                     u_axis, v_axis, brick, roof_mat, collection):
    """Conservative projecting cross-gable silhouette, placed along a long wall."""
    half = width/2
    outside = side_v + side_sign*0.25
    inside = side_v - side_sign*depth
    def xyz(uu, vv, zz): return (u_axis[0]*uu+v_axis[0]*vv, u_axis[1]*uu+v_axis[1]*vv, zz)
    front = [xyz(u-half,outside,base_z),xyz(u+half,outside,base_z),xyz(u,outside,peak_z)]
    back = [xyz(u-half,inside,base_z),xyz(u+half,inside,base_z),xyz(u,inside,peak_z)]
    mesh_object(name+"_Gable",front+back,[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)],brick,collection)
    roofverts=[xyz(u-half,outside,base_z),xyz(u,outside,peak_z),xyz(u+half,outside,base_z),
               xyz(u-half,inside,base_z),xyz(u,inside,peak_z),xyz(u+half,inside,base_z)]
    mesh_object(name+"_Roof",roofverts,[(0,3,4,1),(1,4,5,2)],roof_mat,collection)


def load_source():
    fc = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    feature = fc["features"][0]
    ring = feature["geometry"]["coordinates"][0]
    pts = [project_lon_lat(lon,lat) for lon,lat in ring]
    if math.dist(pts[0],pts[-1]) < 1e-6:
        pts.pop()
    return simplify_ring(pts, SIMPLIFY_TOLERANCE_M), feature, len(ring)-1


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    pts, feature, raw_n = load_source()
    brick = material("CQNW_Purdue_Brick_Interpretation", (0.38,0.105,0.075))
    dark_brick = material("CQNW_Shadow_Brick", (0.25,0.065,0.045))
    stone = material("CQNW_Stone_Trim_Interpretation", (0.66,0.62,0.53))
    foundation = material("CQNW_Stone_Base", (0.43,0.42,0.37))
    roof_mat = material("CQNW_Dark_Slate_Roof", (0.11,0.14,0.16))
    glass = material("CQNW_Window_Glass", (0.055,0.11,0.14), 0.32)
    door = material("CQNW_Entry_Door", (0.09,0.045,0.025))

    prism("CQNW_Stone_Foundation",pts,0,FOUNDATION_TOP,foundation,foundation,collection)
    prism("CQNW_Brick_Wall_Shell",pts,FOUNDATION_TOP,WALL_TOP,brick,brick,collection)

    # The official polygon's longest edge establishes an east-west long axis.
    longest=max(((b[0]-a[0],b[1]-a[1]) for a,b in zip(pts,pts[1:]+pts[:1])),key=lambda v:math.hypot(*v))
    u=Vector(longest).normalized()
    if u.x < 0: u=-u
    v=Vector((-u.y,u.x))
    us=[p[0]*u.x+p[1]*u.y for p in pts]
    vs=[p[0]*v.x+p[1]*v.y for p in pts]
    u0,u1=min(us),max(us); v0,v1=min(vs),max(vs)
    uc=(u0+u1)/2; vc=(v0+v1)/2
    u_axis=(u.x,u.y); v_axis=(v.x,v.y)

    # Roof type and repeated gabled interruptions are read from the 2023 aerial.
    gable_roof("CQNW_Main_Longitudinal_Gable_Roof",u0,u1,v0,v1,EAVES_Z,RIDGE_Z,u_axis,v_axis,roof_mat,collection)

    windows={"verts":[],"faces":[]}; trims={"verts":[],"faces":[]}; belts={"verts":[],"faces":[]}
    entry_details={"verts":[],"faces":[]}
    # Four visible window rows represent the GIS five-level count with the
    # basement/foundation included; exact floor convention is unverified.
    for side_v in (v0,v1):
        side_sign = -1 if side_v==v0 else 1
        for bay in range(21):
            uu=u0+3.15+(u1-u0-6.3)*(bay/20)
            for floor,base in enumerate(FLOOR_BASES):
                z=base+1.05
                box_add(windows,(u.x*uu+v.x*(side_v+side_sign*.09),u.y*uu+v.y*(side_v+side_sign*.09),z),1.48,.14,1.7,math.atan2(u.y,u.x))
                box_add(trims,(u.x*uu+v.x*(side_v+side_sign*.13),u.y*uu+v.y*(side_v+side_sign*.13),z-0.91),1.64,.22,.12,math.atan2(u.y,u.x))
                box_add(trims,(u.x*uu+v.x*(side_v+side_sign*.13),u.y*uu+v.y*(side_v+side_sign*.13),z+0.91),1.64,.22,.12,math.atan2(u.y,u.x))
        # Stone bands at approximate floor boundaries.
        for z in (3.45,6.30,9.15):
            uu=uc
            box_add(belts,(u.x*uu+v.x*(side_v+side_sign*.08),u.y*uu+v.y*(side_v+side_sign*.08),z),u1-u0,.15,.12,math.atan2(u.y,u.x))

    # Narrow end elevations get a smaller window group.
    for end_u, outward in ((u0,-1),(u1,1)):
        for bay in range(4):
            vv=v0+2.2+(v1-v0-4.4)*(bay/3)
            for base in FLOOR_BASES:
                z=base+1.05
                box_add(windows,(u.x*(end_u+outward*.09)+v.x*vv,u.y*(end_u+outward*.09)+v.y*vv,z),1.35,.14,1.68,math.atan2(v.y,v.x))

    # The aerial shows three repeated large roof interruptions per long side.
    # They are represented as shallow projecting gables, not exact measured bays.
    for side_v,side_sign in ((v0,-1),(v1,1)):
        for frac in (.16,.5,.84):
            uu=u0+(u1-u0)*frac
            gable_projection(f"CQNW_Roof_Gable_{side_sign}_{frac:.2f}",uu,side_v,side_sign,7.0,2.0,EAVES_Z,14.25,u_axis,v_axis,brick,roof_mat,collection)

    box_batch("CQNW_Repeated_Window_Glass",windows,glass,collection)
    box_batch("CQNW_Stone_Window_Sills_Lintels",trims,stone,collection)
    box_batch("CQNW_Story_Belt_Courses",belts,stone,collection)

    # A simple pointed-arch entrance faces south toward Cary's central court.
    # This orientation is an inferred site relationship, not a surveyed entrance.
    side_v=v0
    ec=(u.x*uc+v.x*(side_v-0.18),u.y*uc+v.y*(side_v-0.18))
    tang=(u.x,u.y); normal=(-v.x,-v.y); angle=math.atan2(tang[1],tang[0])
    def wall_panel(name, outline, mat, depth):
        verts=[]
        for d in (-depth/2,depth/2):
            for along,z in outline:
                verts.append((ec[0]+tang[0]*along+normal[0]*d,ec[1]+tang[1]*along+normal[1]*d,z))
        n=len(outline); faces=[tuple(range(n,2*n)),tuple(reversed(range(n)))]
        faces += [(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
        mesh_object(name,verts,faces,mat,collection)
    wall_panel("CQNW_Stone_Point_Arch",[(-1.5,.1),(1.5,.1),(1.5,2.45),(0,4),(-1.5,2.45)],stone,.28)
    wall_panel("CQNW_Dark_Entry",[(-1.1,.12),(1.1,.12),(1.1,2.25),(0,3.35),(-1.1,2.25)],door,.1)

    for i,z in enumerate((3.7,6.55,9.4)):
        box_add(entry_details,(ec[0]+normal[0]*.30,ec[1]+normal[1]*.30,z),2.55,.2,.11,angle)
    box_batch("CQNW_Entry_Transoms",entry_details,stone,collection)

    # The manifest contract exports one named building object in this library.
    # Join static pieces after modeling while preserving their mesh materials.
    bpy.ops.object.select_all(action="DESELECT")
    asset_meshes=[obj for obj in collection.objects if obj.type=="MESH"]
    for obj in asset_meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=asset_meshes[0]
    bpy.ops.object.join()
    asset_object=bpy.context.view_layer.objects.active
    asset_object.name="Cary Quadrangle Northwest (CQNW)"
    asset_object.data.name="Cary Quadrangle Northwest (CQNW) Mesh"
    asset_object["asset_id"]=ASSET_ID
    asset_object["source_feature"]="Purdue BuildingShapesZip4 FeatureServer FID 647; BLDG_ABBR=CQNW"
    asset_object["coordinate_contract"]="Campus world coordinates in meters; X east, Y north, Z up; identity transform."

    collection["asset_id"]=ASSET_ID
    collection["building_name"]="Franklin Levering Cary Quadrangle Northwest"
    collection["source_feature"]="Purdue BuildingShapesZip4 FeatureServer FID 647; BLDG_ABBR=CQNW"
    collection["coordinate_contract"]="Campus world coordinates in meters; X east, Y north, Z up; identity transforms."
    collection["height_status"]="Estimated: 14.9 m ridge; 2018 3DEP NDHM within the source polygon sampled median 45.94 ft (14.00 m), p10-p90 39.20-52.07 ft (11.95-15.87 m). Not a surveyed facade height."
    collection["architecture_status"]="Aerial-backed long gable roof and repeated gable interruptions; four visible facade rows plus basement band follow GIS five-level count as an interpretation. Brick/stone palette and pointed-arch entry are historic Cary context, not verified CQNW-specific details."

    # Preview-only presentation objects are outside the exported asset collection.
    preview=bpy.data.collections.new("CQNW_Preview_Setup")
    scene.collection.children.link(preview)
    ground_mat=material("CQNW_Preview_Ground",(.38,.4,.38))
    gx0,gx1=min(p[0] for p in pts)-45,max(p[0] for p in pts)+45
    gy0,gy1=min(p[1] for p in pts)-45,max(p[1] for p in pts)+45
    mesh_object("CQNW_Preview_Ground",[(gx0,gy0,-.2),(gx1,gy0,-.2),(gx1,gy1,-.2),(gx0,gy1,-.2)],[(0,1,2,3)],ground_mat,preview)
    world=bpy.data.worlds.new("CQNW_Preview_World"); world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(.68,.73,.78,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=.7; scene.world=world
    light_data=bpy.data.lights.new("CQNW_Preview_Key","AREA"); light_data.energy=12000; light_data.shape="DISK"; light_data.size=50
    light=bpy.data.objects.new("CQNW_Preview_Key",light_data); preview.objects.link(light); light.location=(uc-35,vc-50,65)
    cam_data=bpy.data.cameras.new("CQNW_Preview_Camera"); cam=bpy.data.objects.new("CQNW_Preview_Camera",cam_data); preview.objects.link(cam)
    target=Vector((uc,vc,7)); cam.location=(uc-67,vc-61,35); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat("-Z","Y").to_euler(); cam_data.lens=48; scene.camera=cam
    scene.render.engine="BLENDER_EEVEE_NEXT"; scene.render.resolution_x=1200; scene.render.resolution_y=850; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
    scene.view_settings.view_transform="Standard"; scene.view_settings.look="Medium High Contrast"
    scene.render.filepath=str(EVIDENCE/"cqnw_preview.png")
    bpy.ops.render.render(write_still=True)

    # Save an orthographic plan preview through camera rotation from overhead.
    scene.render.resolution_x=1400; scene.render.resolution_y=600
    scene.camera.data.type="ORTHO"; scene.camera.data.ortho_scale=max(u1-u0+12,(v1-v0+12)*scene.render.resolution_x/scene.render.resolution_y)
    world_center=Vector(((min(p[0] for p in pts)+max(p[0] for p in pts))/2,
                         (min(p[1] for p in pts)+max(p[1] for p in pts))/2,0.0))
    cam.location=(world_center.x,world_center.y,100)
    cam.rotation_euler=(world_center-Vector(cam.location)).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(EVIDENCE/"cqnw_top_preview.png")
    bpy.ops.render.render(write_still=True)

    ASSET_PATH.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(2)]
    return {"asset_id":ASSET_ID,"source_fid":feature["properties"]["FID"],"source_name":feature["properties"]["BUILDING_N"],
            "expected_object_name":"Cary Quadrangle Northwest (CQNW)","export_object_count":len(collection.objects),
            "raw_vertices":raw_n,"built_vertices":len(pts),"footprint_bounds_world_m":bounds,
            "plan_dimensions_m":[bounds[0][1]-bounds[0][0],bounds[1][1]-bounds[1][0]],
            "simplification_tolerance_m":SIMPLIFY_TOLERANCE_M,"foundation_top_m":FOUNDATION_TOP,
            "wall_top_estimate_m":WALL_TOP,"eaves_estimate_m":EAVES_Z,"ridge_estimate_m":RIDGE_Z,
            "visible_window_rows_interpretation":len(FLOOR_BASES),"roof_gable_projection_count":6,
            "asset_path":str(ASSET_PATH.relative_to(ROOT))}


if __name__ == "__main__":
    report=build()
    out=EVIDENCE/"build_report.json"
    out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
