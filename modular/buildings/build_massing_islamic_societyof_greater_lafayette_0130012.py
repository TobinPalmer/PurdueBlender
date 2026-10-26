"""Build the Islamic Society of Greater Lafayette massing asset.

Footprint: Purdue GIS BuildingShapesZip4 FID 771 (SOMSA), transformed into
the repository campus coordinate frame. The GIS calls the building Muslim
Student Association and lists 1021 First Street; ISGL's own site lists 1022
1st Street at the First/Russell corner. An archived labeled exterior photo
and the current orthophoto support this match. Geometry beyond the GIS shell,
including eaves, story heights, roof rise and entry canopy, is estimated.
Run from Blender with this file as --python.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ASSET_ID = "massing_islamic_societyof_greater_lafayette_0130012"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
OBJECT_NAME = "Islamic Society of Greater Lafayette"
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "audit" / ASSET_ID / "sources" / "purdue_gis_FID771_SOMSA.json"
ASSET = ROOT / "modular" / "buildings" / (ASSET_ID + ".blend")
RENDERS = ROOT / "audit" / ASSET_ID / "renders"
EVIDENCE = ROOT / "audit" / ASSET_ID / "evidence_record.json"
INSPECTION = ROOT / "audit" / ASSET_ID / "review" / "build_measurements.json"
RETRIEVED_UTC = "2026-10-26"

LAT0 = 40.4274
LON0 = -86.9137


def lonlat_to_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def polygon_centroid(points):
    twice_area = 0.0
    cx = cy = 0.0
    for i, p in enumerate(points):
        q = points[(i + 1) % len(points)]
        cross = p[0] * q[1] - q[0] * p[1]
        twice_area += cross
        cx += (p[0] + q[0]) * cross
        cy += (p[1] + q[1]) * cross
    return (cx / (3.0 * twice_area), cy / (3.0 * twice_area))


def make_material(name, color, roughness=0.72):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


MATERIALS = {}
GEO_COLL = None


def add_box(name, center, dimensions, yaw, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = dimensions
    ob.rotation_euler[2] = yaw
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    for coll in list(ob.users_collection):
        coll.objects.unlink(ob)
    GEO_COLL.objects.link(ob)
    return ob


def add_roof_dome(name, center, yaw, radius_u, radius_v, base_z, rise, material):
    # Small half-ellipsoid canopy dome, supported by columns below.
    n = 20
    rings = 6
    verts = []
    for j in range(rings + 1):
        phi = (math.pi * 0.5) * j / rings
        ru = radius_u * math.cos(phi)
        rv = radius_v * math.cos(phi)
        z = base_z + rise * math.sin(phi)
        for i in range(n):
            theta = 2.0 * math.pi * i / n
            u = ru * math.cos(theta)
            v = rv * math.sin(theta)
            x = center[0] + u * math.cos(yaw) - v * math.sin(yaw)
            y = center[1] + u * math.sin(yaw) + v * math.cos(yaw)
            verts.append((x, y, z))
    faces = []
    for j in range(rings):
        for i in range(n):
            a = j * n + i
            b = j * n + (i + 1) % n
            c = (j + 1) * n + (i + 1) % n
            d = (j + 1) * n + i
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    GEO_COLL.objects.link(ob)
    return ob


def add_hip_roof(name, x0, x1, y0, y1, eave_z, ridge_z, ridge_axis, material, overhang=0.20):
    """Create an explicit four-plane hip roof over an estimated wing envelope."""
    x0 -= overhang
    x1 += overhang
    y0 -= overhang
    y1 += overhang
    corners = [(x0, y0, eave_z), (x1, y0, eave_z),
               (x1, y1, eave_z), (x0, y1, eave_z)]
    if ridge_axis == "y":
        half = min((x1-x0) * 0.38, (y1-y0) * 0.5)
        ridge = [((x0+x1)*0.5, (y0+y1)*0.5-half, ridge_z),
                 ((x0+x1)*0.5, (y0+y1)*0.5+half, ridge_z)]
    else:
        half = min((y1-y0) * 0.38, (x1-x0) * 0.5)
        ridge = [((x0+x1)*0.5-half, (y0+y1)*0.5, ridge_z),
                 ((x0+x1)*0.5+half, (y0+y1)*0.5, ridge_z)]
    verts = corners + ridge
    # Use the appropriate ridge corner ordering so all roof planes share the
    # ridge seam and leave a visible break between the two intersecting wings.
    if ridge_axis == "y":
        faces = [(0, 1, 4), (2, 3, 5), (0, 4, 5, 3), (1, 2, 5, 4)]
    else:
        faces = [(0, 3, 4), (1, 2, 5), (3, 4, 5, 2), (0, 1, 5, 4)]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    GEO_COLL.objects.link(ob)
    return ob


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_view(name, camera_location, target, ortho_scale, resolution=(1200, 900)):
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("TEMP_" + name + "Camera")
    cam = bpy.data.objects.new("TEMP_" + name + "Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = camera_location
    aim(cam, target)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = ortho_scale
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(RENDERS / (name + ".png"))
    bpy.ops.render.render(write_still=True)
    scene.camera = None
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.cameras.remove(cam_data)


def main():
    global GEO_COLL
    RENDERS.mkdir(parents=True, exist_ok=True)
    INSPECTION.parent.mkdir(parents=True, exist_ok=True)
    with SOURCE.open("r", encoding="utf-8") as f:
        feature = json.load(f)["features"][0]
    attrs = feature["attributes"]
    if attrs.get("FID") != 771 or attrs.get("BLDG_ABBR") != "SOMSA":
        raise RuntimeError("Unexpected GIS identity; expected FID 771 SOMSA")
    ring_ll = feature["geometry"]["rings"][0]
    if ring_ll[0] == ring_ll[-1]:
        ring_ll = ring_ll[:-1]
    ring = [lonlat_to_xy(lon, lat) for lon, lat in ring_ll]
    cx, cy = polygon_centroid(ring)
    signed_area = sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring))) * 0.5

    # Clear all inherited massing, textures and collections to guarantee a portable library.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in list(bpy.data.collections):
        if coll.users == 0:
            bpy.data.collections.remove(coll)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.display.shading.curvature_ridge_factor = 1.1
    scene.display.shading.curvature_valley_factor = 1.0
    scene.display.shading.background_type = "WORLD"
    scene.world.color = (0.20, 0.22, 0.25)
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    asset_coll = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset_coll)
    geo_coll = bpy.data.collections.new("TEMP_ISGL_Geometry")
    scene.collection.children.link(geo_coll)
    GEO_COLL = geo_coll

    MATERIALS.update({
        "brick": make_material("ISGL | red-brown brick", (0.38, 0.105, 0.065)),
        "brick_dark": make_material("ISGL | brick pilaster", (0.29, 0.075, 0.045)),
        "limestone": make_material("ISGL | warm limestone", (0.72, 0.64, 0.48)),
        "glass": make_material("ISGL | blue-gray glazing", (0.10, 0.23, 0.29), 0.3),
        "roof": make_material("ISGL | charcoal gray hipped roof", (0.13, 0.16, 0.18)),
        "canopy": make_material("ISGL | pale peach domed entry canopy", (0.74, 0.48, 0.36)),
        "sign": make_material("ISGL | dark entrance sign", (0.12, 0.10, 0.08)),
    })

    wall_h = 6.0  # Estimate from exterior photo / orthophoto; GIS level fields conflict.
    roof_eave_z = 6.05
    roof_peak_z = 8.15
    n = len(ring)
    verts = [(x, y, z) for z in (0.0, wall_h) for x, y in ring]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new("ISGL_GIS_Shell_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(MATERIALS["brick"])
    mesh.update()
    shell = bpy.data.objects.new("ISGL GIS structural wall shell", mesh)
    geo_coll.objects.link(shell)

    # Orthophoto shows multiple roof planes/ridge breaks instead of one apex.
    # The GIS outline has a long west wing and a shorter east wing; independent
    # hips approximate that silhouette. Eave offsets and ridge elevations are
    # still estimates because no elevation drawing or survey is available.
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    x_west_break = min(x for x in xs if x > min(xs) + 8.0)
    x_east_start = x_west_break - 0.30
    y_east_south = min(y for x, y in ring if x > x_west_break - 0.5) + 0.2
    add_hip_roof("Estimated primary west-wing hip roof",
                 min(xs)+0.25, x_east_start,
                 min(ys)+0.5, max(ys)-0.35,
                 roof_eave_z, roof_peak_z-0.65, "y", MATERIALS["roof"])
    add_hip_roof("Estimated intersecting east-wing hip roof",
                 x_east_start, max(xs)-0.25,
                 y_east_south, max(ys)-0.35,
                 roof_eave_z, roof_peak_z, "x", MATERIALS["roof"])

    # Faint limestone horizontal bands and repeated windows around each perimeter edge.
    ccw = signed_area > 0
    candidate_edges = []
    for i, p in enumerate(ring):
        q = ring[(i+1) % n]
        length = math.hypot(q[0]-p[0], q[1]-p[1])
        if length >= 5.0:
            candidate_edges.append(((p[1]+q[1])*0.5, i))
    north_entry_edge_index = max(candidate_edges)[1]
    for i, p in enumerate(ring):
        q = ring[(i+1) % n]
        dx, dy = q[0]-p[0], q[1]-p[1]
        length = math.hypot(dx, dy)
        if length < 1.0:
            continue
        ux, uy = dx/length, dy/length
        # Outward normal from the polygon's winding.
        nx, ny = ((uy, -ux) if ccw else (-uy, ux))
        yaw = math.atan2(uy, ux)
        mx, my = (p[0]+q[0])*0.5, (p[1]+q[1])*0.5
        # Continuous horizontal string courses add the photo-backed stone band rhythm.
        for z in (3.0, 5.82):
            add_box("Limestone horizontal facade band", (mx+nx*0.05, my+ny*0.05, z), (max(0.4,length-0.15), 0.14, 0.14), yaw, MATERIALS["limestone"])
        # One or two bay rows; counts and spacing are interpretive, not surveyed.
        margin = 1.0
        usable = max(0.0, length-2*margin)
        count = max(1, int(usable / 3.0)) if length >= 4.8 else 0
        for k in range(count):
            along = margin + usable * (k+0.5)/count
            # Leave a centered opening for the inferred portal, while retaining bays beside it.
            if i == north_entry_edge_index and abs(along-length*0.5) < 2.7:
                continue
            wx, wy = p[0]+ux*along+nx*0.055, p[1]+uy*along+ny*0.055
            # Ground-floor glazing is broader, matching the labeled exterior photo.
            add_box("Ground floor glazed bay", (wx, wy, 1.48), (min(2.0,usable/count*0.58), 0.075, 1.85), yaw, MATERIALS["glass"])
            # Repeated second-level windows are an estimate; source photo shows upper windows.
            add_box("Upper-level window", (wx, wy, 4.45), (min(1.35,usable/count*0.44), 0.075, 1.25), yaw, MATERIALS["glass"])
            # Pale sills/lintels frame the upper opening without implying a measured module.
            w = min(1.35, usable/count*0.44)
            for z in (3.80, 5.10):
                add_box("Upper window limestone trim", (wx, wy+ny*0.025, z), (w+0.12, 0.08, 0.075), yaw, MATERIALS["limestone"])

    # Entry is placed on the longest north-facing perimeter segment, inferred from site context.
    edges = []
    for i, p in enumerate(ring):
        q = ring[(i+1) % n]
        dx, dy = q[0]-p[0], q[1]-p[1]
        length = math.hypot(dx,dy)
        if length < 5.0:
            continue
        ux, uy = dx/length, dy/length
        nx, ny = ((uy,-ux) if ccw else (-uy,ux))
        mx,my=(p[0]+q[0])*0.5,(p[1]+q[1])*0.5
        edges.append((my, length, p, q, ux, uy, nx, ny, math.atan2(uy,ux), mx, my))
    # Highest-Y midpoint is the probable side facing the parking/site approach.
    chosen=max(edges,key=lambda e:e[0])
    _, entry_len, p, q, ux, uy, nx, ny, yaw, mx, my = chosen
    entry_center=(mx+nx*0.40,my+ny*0.40)
    # Shallow pale stone portal occupies a modest part of the shell and projects toward approach.
    add_box("Estimated limestone entrance portal", (entry_center[0],entry_center[1],1.70), (min(4.6,entry_len*0.46), 1.0, 3.35), yaw, MATERIALS["limestone"])
    front=(mx+nx*1.00,my+ny*1.00)
    add_box("Glazed main entrance doors", (front[0],front[1],1.27), (1.55,0.10,2.42), yaw, MATERIALS["glass"])
    # Four slender columns support the small dome-like entry canopy visible in the source photo.
    for along in (-1.65,1.65):
        for depth in (0.48,1.78):
            x=mx+ux*along+nx*depth
            y=my+uy*along+ny*depth
            add_box("Domed entry canopy column", (x,y,1.60), (0.16,0.16,3.2), yaw, MATERIALS["limestone"])
    dome_center=(mx+nx*1.12,my+ny*1.12,3.20)
    dome=add_roof_dome("Small domed entrance canopy", dome_center, yaw, 1.95, 0.92, 3.20, 0.82, MATERIALS["canopy"])

    # Entrance sign slab is qualitative source detail; exact wording/dimensions are not modeled.
    add_box("Entrance sign plaque", (mx+nx*0.915,my+ny*0.915,2.86), (3.0,0.10,0.34), yaw, MATERIALS["sign"])

    # Join every building element into the one expected portable mesh object.
    meshes=[ob for ob in geo_coll.objects if ob.type=="MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for ob in meshes:
        ob.select_set(True)
    bpy.context.view_layer.objects.active=shell
    bpy.ops.object.join()
    building=bpy.context.object
    building.name=OBJECT_NAME
    building.data.name="Islamic_Society_GIS_Massing_Mesh"
    # Move the joined object out of temp geometry collection and into export collection.
    for c in list(building.users_collection):
        c.objects.unlink(building)
    asset_coll.objects.link(building)
    bpy.data.collections.remove(geo_coll)
    building["building_id"]=ASSET_ID
    building["footprint_source"]="Purdue BuildingShapesZip4 FID 771, BLDG_ABBR SOMSA, address 1021 FIRST ST; ISGL official address 1022 1st St at the same First/Russell corner"
    building["height_status"]="Estimated from exterior photograph and aerial; GIS Extrution=12 units undocumented and GIS NUM_LEVELS=1 conflicts with visible upper facade"
    building["roof_eave_overhang_estimate_m"]=0.35

    # Preview renders use temporary cameras; the saved library remains clean.
    scene.render.engine="BLENDER_WORKBENCH"
    scene.render.resolution_percentage=100
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.show_cavity=True
    scene.display.shading.show_shadows=True
    scene.display.shading.background_type="WORLD"
    scene.world.color=(0.20,0.22,0.25)
    span=max(max(x for x,y in ring)-min(x for x,y in ring),max(y for x,y in ring)-min(y for x,y in ring))
    target=(cx,cy,3.9)
    render_view("isgl_exterior_approach",(cx+span*1.18,cy+span*1.55,11.0),target,span*1.85)
    render_view("isgl_front_elevation",(cx+span*0.12,cy+span*2.0,5.2),target,span*1.8)
    render_view("isgl_roof_plan",(cx,cy,span*2.6),target,span*1.55)

    # Remove unused meshes/materials inherited from initial file to keep library portable.
    for ob in list(bpy.data.objects):
        if ob.type in {"CAMERA","LIGHT"}:
            bpy.data.objects.remove(ob,do_unlink=True)
    bpy.context.scene.camera=None
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

    verts=[building.matrix_world @ v.co for v in building.data.vertices]
    bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
    report={
        "asset":str(ASSET.relative_to(ROOT)).replace("\\","/"),
        "scene":SCENE_NAME,"collection":COLLECTION_NAME,"object":building.name,
        "object_count":len(asset_coll.objects),"vertices":len(building.data.vertices),"faces":len(building.data.polygons),
        "bounds_world_m":bounds,"gis_ring_vertices":len(ring),"gis_fid":attrs["FID"],
        "roof_eave_height_estimate_m":roof_eave_z,
        "roof_ridge_height_estimates_m":{"west_wing":roof_peak_z-0.65,"east_wing":roof_peak_z},
        "roof_form":"Two intersecting estimated hip roofs corresponding to the west and east GIS wing envelopes; plane breaks are an interpretation of the Indiana 2022-2025 orthophoto.",
        "external_images":[],"linked_libraries":[],
        "renders":["audit/"+ASSET_ID+"/renders/isgl_exterior_approach.png","audit/"+ASSET_ID+"/renders/isgl_front_elevation.png","audit/"+ASSET_ID+"/renders/isgl_roof_plan.png"]
    }
    INSPECTION.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
