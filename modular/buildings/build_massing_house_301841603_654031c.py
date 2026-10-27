"""Build the Alpha Sigma Phi (Alpha Pi) Purdue chapter-house asset.

The official Purdue GIS polygon is used directly in campus coordinates. The
vertical envelope and all interior planning are explicitly approximate because
no measured elevations or public floor plans were found.
"""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_house_301841603_654031c.blend"
SOURCE = ROOT / "audit/alpha_sigma_phi/sources/arcgis_fid763_feature.json"
ASSET_COLLECTION = "Asset_massing_house_301841603_654031c"
SCENE_NAME = "Building_massing_house_301841603_654031c"
ROOT_OBJECT = "House_301841603"
BUILDING_ID = "massing_house_301841603_654031c"


def material(name, color, roughness=0.7, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    return m


def procedural_brick(m):
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    bs = nodes.get("Principled BSDF")
    tex = nodes.new("ShaderNodeTexBrick")
    tex.name = "Subtle dark-brown running bond"
    tex.inputs["Color1"].default_value = (0.20, 0.105, 0.072, 1)
    tex.inputs["Color2"].default_value = (0.29, 0.16, 0.11, 1)
    tex.inputs["Mortar"].default_value = (0.23, 0.22, 0.20, 1)
    tex.inputs["Scale"].default_value = 1.0
    tex.inputs["Mortar Size"].default_value = 0.018
    tex.inputs["Mortar Smooth"].default_value = 0.08
    coord = nodes.new("ShaderNodeTexCoord")
    links.new(coord.outputs["UV"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], bs.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.035
    links.new(tex.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bs.inputs["Normal"])


def move_to(obj, col):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def mesh_object(name, verts, faces, mat, col):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.validate(verbose=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return obj


def add_box(name, center, dims, mat, col, angle=0.0):
    # Direct mesh construction avoids an expensive context/depsgraph update
    # for every sill, jamb, partition, and furniture block.
    hx, hy, hz = (d/2 for d in dims)
    co, si = math.cos(angle), math.sin(angle)
    verts = []
    for z in (-hz, hz):
        for y in (-hy, hy):
            for x in (-hx, hx):
                verts.append((center[0]+x*co-y*si,
                              center[1]+x*si+y*co,
                              center[2]+z))
    faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    return mesh_object(name, verts, faces, mat, col)


def add_window(name, p, q, t, zc, w, h, outward, angle, glass, trim, col):
    # A flat glazing panel and modest projecting aluminum/stone surround.
    mid = (p[0] + (q[0]-p[0])*t, p[1] + (q[1]-p[1])*t)
    c = (mid[0] + outward[0]*0.075, mid[1] + outward[1]*0.075, zc)
    add_box(name + "_glass", c, (w, 0.075, h), glass, col, angle)
    depth = 0.16
    xoff = w/2 + 0.045
    zoff = h/2 + 0.045
    for sx in (-1, 1):
        cc = (c[0] + math.cos(angle)*xoff*sx,
              c[1] + math.sin(angle)*xoff*sx, zc)
        add_box(name + "_jamb", cc, (0.09, depth, h+0.14), trim, col, angle)
    for sz in (-1, 1):
        cc = (c[0], c[1], zc + zoff*sz)
        add_box(name + "_head_sill", cc, (w+0.18, depth, 0.09), trim, col, angle)
    # One central vertical mullion and one horizontal transom.
    add_box(name + "_mullion", c, (0.045, 0.10, h), trim, col, angle)
    add_box(name + "_transom", c, (w, 0.10, 0.045), trim, col, angle)


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    features = data.get("features", [])
    if len(features) != 1 or features[0]["attributes"].get("FID") != 763:
        raise ValueError("Source does not contain the verified Alpha Sigma Phi FID 763 feature")
    attrs = features[0]["attributes"]
    ring = features[0]["geometry"]["rings"][0]
    # Match the project's documented geographic-to-campus approximation.
    pts = []
    for lon, lat in ring[:-1]:
        x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
        y = (lat - 40.4274) * 111040.0
        pts.append((x, y))
    area2 = sum(pts[i][0]*pts[(i+1)%len(pts)][1] - pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
    # Signed ring area determines which side of a boundary edge is exterior.
    orient = 1.0 if area2 > 0 else -1.0

    scene = bpy.data.scenes.get(SCENE_NAME)
    if scene is None:
        scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    scene.unit_settings.system = "METRIC"

    root = bpy.data.collections.get(ASSET_COLLECTION)
    if root is None:
        root = bpy.data.collections.new(ASSET_COLLECTION)
        scene.collection.children.link(root)
    else:
        # Remove only this asset's own prior geometry.
        for o in list(root.all_objects):
            bpy.data.objects.remove(o, do_unlink=True)
        for child in list(root.children):
            root.children.unlink(child)

    exterior = bpy.data.collections.new("Exterior_Alpha_Sigma_Phi")
    interior = bpy.data.collections.new("Interior_Schematic_Alpha_Sigma_Phi")
    roof_coll = bpy.data.collections.new("Roof_Alpha_Sigma_Phi")
    root.children.link(exterior)
    root.children.link(interior)
    root.children.link(roof_coll)

    brick = material("Alpha Sigma Phi | dark brown brick (visual estimate)", (0.24, 0.125, 0.088), 0.82)
    procedural_brick(brick)
    stone = material("Alpha Sigma Phi | warm gray architectural concrete", (0.47,0.45,0.40), 0.8)
    dark = material("Alpha Sigma Phi | charcoal metal", (0.055,0.065,0.072), 0.38, 0.55)
    glass = material("Alpha Sigma Phi | blue-gray glazing", (0.055,0.13,0.18), 0.22, 0.25)
    roofmat = material("Alpha Sigma Phi | gray roof membrane", (0.16,0.18,0.19), 0.88)
    intwall = material("Alpha Sigma Phi | warm painted interior walls", (0.70,0.68,0.61), 0.88)
    floor_mat = material("Alpha Sigma Phi | interior floor", (0.35,0.29,0.22), 0.78)
    wood = material("Alpha Sigma Phi | interior wood", (0.32,0.18,0.09), 0.72)
    carpet = material("Alpha Sigma Phi | social-room carpet (historic evidence, period unknown)", (0.34,0.16,0.12), 0.94)
    glass_case = material("Alpha Sigma Phi | trophy-case glass (schematic)", (0.12,0.28,0.32), 0.18, 0.12)
    brass = material("Alpha Sigma Phi | trophy display brass (schematic)", (0.63,0.43,0.14), 0.32, 0.7)
    white = material("Alpha Sigma Phi | pale trim", (0.72,0.70,0.64), 0.76)

    # 2018 Indiana 3DEP COPC data gives a 10.06 m median roof-surface proxy
    # above nearby class-2 ground returns. This is an estimate, not a survey;
    # see audit/alpha_sigma_phi/lidar_height_evidence_2018.json. GIS
    # Extrution=34 has no documented unit. GIS floor-count fields conflict,
    # so the three-level window rhythm remains a visual interpretation.
    wall_h = 10.06
    floor_h = wall_h / 3.0
    parapet_h = 0.38
    shell_verts, shell_faces = [], []
    for i, p in enumerate(pts):
        q = pts[(i+1) % len(pts)]
        base = len(shell_verts)
        shell_verts += [(p[0],p[1],0.0),(q[0],q[1],0.0),(q[0],q[1],wall_h),(p[0],p[1],wall_h)]
        # GIS ring is clockwise, so reverse its order to put normals outward.
        shell_faces.append((base,base+3,base+2,base+1))
    shell = mesh_object(ROOT_OBJECT, shell_verts, shell_faces, brick, exterior)
    uv = shell.data.uv_layers.new(name="FacadeBrickUV")
    for face_index, polygon in enumerate(shell.data.polygons):
        p, q = pts[face_index], pts[(face_index+1)%len(pts)]
        length = math.dist(p,q)
        uv_face = ((0.0,0.0),(0.0,wall_h),(length,wall_h),(length,0.0))
        for loop_index, uv_coord in zip(polygon.loop_indices, uv_face):
            uv.data[loop_index].uv = uv_coord
    shell["building_id"] = BUILDING_ID
    shell["source_footprint"] = "Purdue BuildingShapesZip4 FID 763, Alpha Sigma Phi, 951 David Ross Rd"
    shell["height_note"] = "10.06 m 2018 LiDAR-derived roof-height estimate above nearby ground returns; not a surveyed wall height; actual story count unresolved"
    shell["story_count_note"] = "Three facade window levels are an estimate; Purdue GIS NUM_LEVELS/CountOfFLO report 1 and conflict with this visual interpretation"
    shell["roof_form_note"] = "Aerial shows a flat-looking roof plan; LiDAR roof-proxy 5th-95th height spread is about 2.08 m with weak planar fit, so roof pitch/profile is not resolved"
    shell["placement_note"] = "GIS polygon transformed to direct campus coordinates with project approximate lat/lon transform"

    # Slab roof and its low parapet follow the GIS wall footprint.
    mesh_object("Roof_Slab_GIS_Footprint", [(x,y,wall_h) for x,y in pts], [tuple(reversed(range(len(pts))))], roofmat, roof_coll)
    for i,p in enumerate(pts):
        q=pts[(i+1)%len(pts)]
        dx,dy=q[0]-p[0],q[1]-p[1]
        length=math.hypot(dx,dy)
        if length < 1.2: continue
        angle=math.atan2(dy,dx)
        cx,cy=(p[0]+q[0])/2,(p[1]+q[1])/2
        # Parapet boxes are centered on the wall line. The roof outline is
        # intentionally simple because the aerial source cannot show slope.
        add_box(f"Parapet_{i+1:02d}",(cx,cy,wall_h+parapet_h/2),(length+0.05,0.30,parapet_h),stone,roof_coll,angle)

    # Facade bay rhythm: windows are an interpretation from Apr 2026 Street View.
    # Windows repeat at each of three estimated levels, with a public entrance
    # placed on the most easterly long wall (placement is not archival).
    east_edge = max(range(len(pts)), key=lambda i:(pts[i][0]+pts[(i+1)%len(pts)][0])/2)
    windows_n = 0
    for i,p in enumerate(pts):
        q=pts[(i+1)%len(pts)]
        dx,dy=q[0]-p[0],q[1]-p[1]
        length=math.hypot(dx,dy)
        if length < 2.8: continue
        tx,ty=dx/length,dy/length
        outward=(orient*ty,-orient*tx)
        angle=math.atan2(dy,dx)
        door_t=0.53 if i==east_edge else -2
        # Bay positions at roughly 2.6 m centers, leaving generous corner piers.
        count=max(1,int((length-2.4)/2.7))
        for j in range(count):
            t=(j+1)/(count+1)
            if i==east_edge and abs(t-door_t)<0.12: continue
            for level in range(3):
                zc=level*floor_h + 1.95
                if zc+0.9 >= wall_h-0.45: continue
                windows_n += 1
                add_window(f"Window_{windows_n:03d}",p,q,t,zc,1.18,1.55,outward,angle,glass,white,exterior)

    # A modest glazed entry and canopy anchor the public/street-facing wall.
    p=pts[east_edge]; q=pts[(east_edge+1)%len(pts)]
    dx,dy=q[0]-p[0],q[1]-p[1]
    length=math.hypot(dx,dy); tx,ty=dx/length,dy/length
    outward=(orient*ty,-orient*tx); angle=math.atan2(dy,dx); t=0.53
    mid=(p[0]+dx*t,p[1]+dy*t)
    doorc=(mid[0]+outward[0]*0.1,mid[1]+outward[1]*0.1,1.22)
    add_box("Main_Entry_Door",doorc,(1.45,0.12,2.38),dark,exterior,angle)
    add_box("Entry_Glazing",(doorc[0],doorc[1],2.02),(1.15,0.08,0.55),glass,exterior,angle)
    for sx in (-1,1):
        cc=(doorc[0]+math.cos(angle)*sx*0.80,doorc[1]+math.sin(angle)*sx*0.80,1.28)
        add_box("Entry_Stone_Jamb",cc,(0.12,0.24,2.62),stone,exterior,angle)
    canopyc=(mid[0]+outward[0]*0.72,mid[1]+outward[1]*0.72,2.65)
    add_box("Entry_Canopy",canopyc,(2.5,1.35,0.16),dark,exterior,angle)
    for n in range(3):
        stairc=(mid[0]+outward[0]*(0.55+n*0.34),mid[1]+outward[1]*(0.55+n*0.34),0.13+n*0.15)
        add_box(f"Entry_Step_{n+1}",stairc,(2.2,0.62,0.26+n*0.10),stone,exterior,angle)

    # Approximate floor plates and a deliberately schematic interior.
    # No source floor plans were found; layout is clearly labeled and not
    # presented as the real chapter-house room plan.
    area_faces=[tuple(reversed(range(len(pts))))]
    for level in range(3):
        z=0.16+level*floor_h
        mesh_object(f"Interior_Floor_{level+1}",[(x,y,z) for x,y in pts],area_faces,floor_mat,interior)

    # The L-shaped plan is divided into a commons branch and a bedroom wing.
    # Interior planning is schematic; no room layout was available publicly.
    # A principal axis follows the long GIS wing; perpendicular is the cross-wing.
    cx=sum(x for x,y in pts)/len(pts); cy=sum(y for x,y in pts)/len(pts)
    longest=max(range(len(pts)),key=lambda i:math.dist(pts[i],pts[(i+1)%len(pts)]))
    a,b=pts[longest],pts[(longest+1)%len(pts)]
    ux,uy=(b[0]-a[0]),(b[1]-a[1]); ul=math.hypot(ux,uy); ux,uy=ux/ul,uy/ul
    vx,vy=-uy,ux
    uangle=math.atan2(uy,ux); vangle=math.atan2(vy,vx)
    def xy(du,dv): return (cx+ux*du+vx*dv, cy+uy*du+vy*dv)
    def inside(x,y):
        hit=False; j=len(pts)-1
        for i,(xi,yi) in enumerate(pts):
            xj,yj=pts[j]
            if ((yi>y)!=(yj>y)) and x < (xj-xi)*(y-yi)/(yj-yi+1e-12)+xi: hit=not hit
            j=i
        return hit
    # Public-room functions are documented in Alpha Sigma Phi's 1976/1979
    # chapter reports (living-room carpeting, dining drapes, social-room floor,
    # trophy case, restroom redecoration). These objects illustrate the
    # documented uses and are not a measured or mapped floor plan.
    def room_box(name,du,dv,z,dims,mat,ang=uangle):
        x,y=xy(du,dv)
        if inside(x,y): add_box(name,(x,y,z),dims,mat,interior,ang)
    room_box("Dining_Table",-9,8,0.75,(5.2,1.4,0.15),wood)
    for i in range(4):
        for side in (-1,1):
            room_box(f"Dining_Chair_{i}_{side:+d}",-11.0+i*1.35,8+side*1.15,0.48,(0.42,0.42,0.85),wood)
    room_box("Kitchen_Island",1,8,0.65,(4.2,1.0,1.15),stone)
    room_box("Kitchen_Counter",-6,11.3,0.55,(7.5,0.65,1.0),wood)
    room_box("Commons_Sofa",4,-7,0.48,(3.0,0.9,0.8),wood,vangle)
    room_box("Commons_Sofa_2",4,-12,0.48,(3.0,0.9,0.8),wood,vangle)
    room_box("Commons_Coffee_Table",4,-9.5,0.45,(1.8,0.8,0.45),wood,vangle)
    # Historically documented social/living-room carpeting and a schematic
    # entry-to-commons corridor, shown only as representative spaces.
    room_box("Social_Room_Carpet_Pad",4,-9.5,0.205,(8.8,7.6,0.06),carpet,vangle)
    room_box("Hallway_Carpet_Runner",4,2.5,0.205,(13.0,1.65,0.045),carpet,uangle)
    # Hall partitions make an open passage with doorway gaps. Their positions
    # are approximate because no Alpha Pi plan was publicly available.
    room_box("Hall_Wall_Segment_A",4,1.45,1.15,(4.8,0.14,2.3),intwall,uangle)
    room_box("Hall_Wall_Segment_B",-1.7,1.45,1.15,(3.8,0.14,2.3),intwall,uangle)
    room_box("Hall_Wall_Segment_C",4,3.55,1.15,(6.4,0.14,2.3),intwall,uangle)
    room_box("Hall_Wall_Segment_D",-1.7,3.55,1.15,(3.8,0.14,2.3),intwall,uangle)
    # Trophy case: the 1979 chapter report says a new case was installed.
    # Model its frame, glass cabinet, and three display shelves schematically.
    def trophy_case(du,dv):
        x,y=xy(du,dv)
        if not inside(x,y): return
        case_angle=vangle
        room_box("Trophy_Case_Cabinet",du,dv,0.62,(2.7,0.52,0.78),wood,case_angle)
        room_box("Trophy_Case_Glazing",du,dv,1.42,(2.65,0.42,0.72),glass_case,case_angle)
        for j in range(3):
            z=1.18+j*0.22
            room_box(f"Trophy_Case_Shelf_{j+1}",du,dv,z,(2.4,0.36,0.035),brass,case_angle)
        for side in (-1,1):
            room_box(f"Trophy_Case_Stile_{side:+d}",du+side*1.29,dv,1.4,(0.09,0.52,1.62),wood,case_angle)
    trophy_case(8.5,-8.5)
    # Illustrative restroom suite reflects the 1979 report's redecorated
    # ladies' room. The actual room location and layout are unknown.
    room_box("Restroom_Illustrative_FloorMat",-15.0,8.0,0.21,(4.5,5.0,0.06),stone,vangle)
    room_box("Restroom_Illustrative_Partition_A",-15.0,5.8,1.1,(4.5,0.12,2.2),intwall,vangle)
    room_box("Restroom_Illustrative_Partition_B",-17.0,8.0,1.1,(4.0,0.12,2.2),intwall,uangle)
    room_box("Restroom_Illustrative_Vanity",-15.0,9.5,0.78,(1.8,0.55,0.85),stone,vangle)
    room_box("Restroom_Illustrative_Sink",-15.0,9.5,1.23,(0.68,0.42,0.12),glass_case,vangle)
    room_box("Restroom_Illustrative_Stall",-15.0,7.1,0.38,(0.75,0.78,0.72),white,vangle)
    # Add schematic partitions and student-room furniture upstairs in both
    # wings. Partitions are intentionally open at their ends to suggest doors.
    for level in range(3):
        zbase=0.18+level*floor_h
        if level > 0:
            for j,dv in enumerate((-13.0,-6.0,1.0)):
                x,y=xy(4.0,dv)
                if inside(x,y):
                    add_box(f"Level_{level+1}_Leg_Partition_{j}",(x,y,zbase+1.18),(10.8,0.12,2.36),intwall,interior,uangle)
            for j,du in enumerate((-14.0,-6.0,2.0)):
                x,y=xy(du,8.0)
                if inside(x,y):
                    add_box(f"Level_{level+1}_Cross_Partition_{j}",(x,y,zbase+1.18),(10.5,0.12,2.36),intwall,interior,vangle)
            room_centers=[(4.0,-15.5,vangle),(4.0,-8.7,vangle),(4.0,-1.5,vangle),(-15.0,8.0,uangle),(-7.0,8.0,uangle),(1.5,8.0,uangle)]
            for idx,(du,dv,ang) in enumerate(room_centers):
                x,y=xy(du,dv)
                if inside(x,y):
                    z=zbase+0.27
                    add_box(f"Level_{level+1}_Bed_{idx+1}",(x,y,z),(1.1,2.0,0.42),wood,interior,ang)
                    x2,y2=xy(du+1.8,dv)
                    if inside(x2,y2): add_box(f"Level_{level+1}_Desk_{idx+1}",(x2,y2,zbase+0.42),(1.2,0.62,0.8),wood,interior,ang)
        # Stair core anchors circulation across floors (approximate location).
        sx,sy=xy(4.0,0.0)
        if inside(sx,sy): add_box(f"Stair_Core_{level+1}",(sx,sy,zbase+floor_h*0.25),(2.5,4.0,0.45),dark,interior,uangle)

    # Keep child collections in their asset collection; tag all generated parts.
    for ob in root.all_objects:
        ob["building_id"] = BUILDING_ID
    scene["building_id"] = BUILDING_ID
    scene["source_fid"] = 763
    scene["address"] = "951 David Ross Road, West Lafayette, Indiana"
    # Set a useful review camera without changing the asset geometry frame.
    cam_data=bpy.data.cameras.new("Alpha_Sigma_Phi_Review_Camera")
    cam=bpy.data.objects.new("Alpha_Sigma_Phi_Review_Camera",cam_data)
    scene.collection.objects.link(cam)
    cam.location=(-974.0,818.0,39.0)
    target=(-1019.0,852.0,5.0)
    direction=__import__('mathutils').Vector(target)-__import__('mathutils').Vector(cam.location)
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    cam_data.lens=35
    scene.camera=cam
    scene.render.engine="CYCLES"
    scene.cycles.samples=24
    scene.render.resolution_x=1200
    scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    world=bpy.data.worlds.new("Alpha Sigma Phi Preview World") if scene.world is None else scene.world
    scene.world=world; world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.24,0.31,0.40,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.5
    ld=bpy.data.lights.new("Review_Sun","SUN"); lo=bpy.data.objects.new("Review_Sun",ld); scene.collection.objects.link(lo)
    lo.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-28)); ld.energy=2.0
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(ROOT/"audit/alpha_sigma_phi/previews/alpha_sigma_phi_exterior.png")
    ASSET.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print(json.dumps({"asset":str(ASSET),"building_id":BUILDING_ID,"fid":attrs["FID"],"name":attrs["BUILDING_N"],"address":attrs["ADDRESS"],"source_ring_vertices":len(pts),"modeled_height_m":round(wall_h,3),"window_bays":windows_n,"object_count":len(root.all_objects)}))


main()
