"""Build the Rossen-assigned Mann Hall asset from the Purdue GIS shell."""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ASSET_ID = "massing_mann_hall_2b4ebda"
COLLECTION_NAME = "Asset_massing_mann_hall_2b4ebda"
SCENE_NAME = "Building_massing_mann_hall_2b4ebda"
OBJECT_NAME = "Mann Hall"
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "audit" / ASSET_ID / "sources" / "purdue_building_gis_fid_635.json"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / ASSET_ID
PREVIEW = AUDIT / "preview" / "mann_hall_isometric.png"

FEET_TO_METERS = 0.3048
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137


def project_point(lon: float, lat: float) -> tuple[float, float]:
    """Use the documented PurdueBlender local approximation (X east, Y north)."""
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return x, y


class MeshBuilder:
    def __init__(self):
        self.vertices: list[tuple[float, float, float]] = []
        self.faces: list[tuple[int, ...]] = []
        self.materials: list[int] = []

    def face(self, points, material_index: int):
        start = len(self.vertices)
        self.vertices.extend(tuple(float(c) for c in p) for p in points)
        self.faces.append(tuple(range(start, start + len(points))))
        self.materials.append(material_index)

    def box(self, lo, hi, material_index: int):
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        pts = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
               (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
        start = len(self.vertices)
        self.vertices.extend(pts)
        for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
            self.faces.append(tuple(start + i for i in f))
            self.materials.append(material_index)


def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def build():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Required archived Purdue GIS snapshot missing: {SOURCE}")
    feature = json.loads(SOURCE.read_text(encoding="utf-8"))["features"][0]
    attrs = feature["attributes"]
    if attrs["FID"] != 635 or attrs["BLDG_ABBR"] != "MANN":
        raise RuntimeError("GIS snapshot identity mismatch; refusing to build the wrong asset")

    ring_ll = feature["geometry"]["rings"][0]
    ring = [project_point(lon, lat) for lon, lat in ring_ll]
    if len(ring) > 1 and math.dist(ring[0], ring[-1]) < 0.02:
        ring.pop()
    # Remove tiny repeated/near-repeated corners in the official polygon while
    # preserving all structural footprint turns.
    clean = []
    for p in ring:
        if not clean or math.dist(clean[-1], p) > 0.12:
            clean.append(p)
    if len(clean) > 2 and math.dist(clean[0], clean[-1]) < 0.12:
        clean.pop()
    ring = clean
    signed_area = sum(a[0]*b[1] - b[0]*a[1] for a,b in zip(ring, ring[1:] + ring[:1])) / 2
    ccw = signed_area > 0

    floor_2 = float(attrs["F02"]) * FEET_TO_METERS
    floor_3 = float(attrs["F03"]) * FEET_TO_METERS
    gis_roof = float(attrs["R"]) * FEET_TO_METERS
    # The building architect describes two stories plus a lower level. Purdue's
    # GIS records F02/F03 and roof elevations; we model two visible main stories,
    # a parapet and a compact roof enclosure at the registered roof maximum.
    ground = 0.0
    upper = floor_2
    main_roof = max(upper + 0.45, floor_3)
    parapet_top = min(main_roof + 0.50, gis_roof - 1.15)
    roof_screen_top = gis_roof

    mats = [
        make_material("Mann Hall | light limestone / metal cladding", (0.60,0.63,0.64), 0.42, 0.34),
        make_material("Mann Hall | deep blue architectural glazing", (0.055,0.20,0.29), 0.15, 0.16),
        make_material("Mann Hall | charcoal aluminum mullions", (0.035,0.047,0.055), 0.55, 0.28),
        make_material("Mann Hall | warm red-brown brick accent", (0.31,0.105,0.072), 0.0, 0.82),
        make_material("Mann Hall | pale canopy and trim", (0.72,0.75,0.75), 0.5, 0.28),
        make_material("Mann Hall | dark roof membrane", (0.16,0.18,0.19), 0.0, 0.78),
    ]
    CLAD, GLASS, FRAME, BRICK, CANOPY, ROOF = range(6)
    mb = MeshBuilder()

    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    xmid, ymid = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    xspan, yspan = max(xs)-min(xs), max(ys)-min(ys)
    edges = []
    for i, a in enumerate(ring):
        b = ring[(i+1) % len(ring)]
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx,dy)
        if length < 0.16:
            continue
        if ccw:
            nx, ny = dy/length, -dx/length
        else:
            nx, ny = -dy/length, dx/length
        edges.append((a,b,length,nx,ny))

    # Turn-by-turn facade shell: all wall faces sit directly on the official
    # structural polygon, so orientation and plan measurements stay evidence based.
    for a,b,length,nx,ny in edges:
        along = Vector((b[0]-a[0], b[1]-a[1], 0)).normalized()
        normal = Vector((nx,ny,0))
        is_glass = nx > 0.55 or ny < -0.55
        is_west = nx < -0.55
        for z0,z1 in ((ground,upper),(upper,main_roof)):
            mb.face([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)], CLAD)

        # Repeating glass modules on the open campus/south faces. Opaque walls
        # on west-facing core areas follow the architect's description.
        if is_glass or not is_west:
            width = 1.55 if is_glass else 1.0
            count = max(1, int((length - 0.45) // (width + 0.48)))
            gap = max(0.25, (length - count*width)/(count+1))
            for band,(z0,z1) in enumerate(((ground,upper),(upper,main_roof))):
                bottom = z0 + (0.62 if band == 0 else 0.48)
                top = z1 - (0.48 if band == 0 else 0.55)
                if top <= bottom + 0.45:
                    continue
                for j in range(count):
                    s0 = gap + j*(width+gap)
                    s1 = s0 + width
                    p0 = Vector((a[0],a[1],0)) + along*s0 + normal*0.025
                    p1 = Vector((a[0],a[1],0)) + along*s1 + normal*0.025
                    mb.face([(p0.x,p0.y,bottom),(p1.x,p1.y,bottom),(p1.x,p1.y,top),(p0.x,p0.y,top)], GLASS)
                    # Aluminum perimeter and central mullion bars are modeled as
                    # narrow colored bands on the window plane.
                    bar = 0.055
                    for s in (s0, s1-bar, (s0+s1-bar)/2):
                        q0 = Vector((a[0],a[1],0)) + along*s + normal*0.045
                        q1 = q0 + along*bar
                        mb.face([(q0.x,q0.y,bottom),(q1.x,q1.y,bottom),(q1.x,q1.y,top),(q0.x,q0.y,top)], FRAME)
                    for z in (bottom, top-bar):
                        q0 = Vector((a[0],a[1],0)) + along*s0 + normal*0.047
                        q1 = Vector((a[0],a[1],0)) + along*s1 + normal*0.047
                        mb.face([(q0.x,q0.y,z),(q1.x,q1.y,z),(q1.x,q1.y,z+bar),(q0.x,q0.y,z+bar)], FRAME)
        elif is_west and length > 2.5:
            # Small sparse windows through the west-facing metal-panel core.
            count = max(1, int(length // 4.2))
            width = min(1.10, (length-0.5)/count)
            for j in range(count):
                s = (j+0.5)*length/count - width/2
                bottom, top = upper+1.10, min(main_roof-0.85, upper+2.65)
                p0 = Vector((a[0],a[1],0)) + along*s + normal*0.03
                p1 = p0 + along*width
                mb.face([(p0.x,p0.y,bottom),(p1.x,p1.y,bottom),(p1.x,p1.y,top),(p0.x,p0.y,top)], GLASS)

    # A low parapet wraps the roof edge; roof and the compact rooftop plant
    # screen use the authoritative Purdue roof-height record (37 ft).
    for a,b,length,nx,ny in edges:
        mb.face([(a[0],a[1],main_roof),(b[0],b[1],main_roof),
                 (b[0],b[1],parapet_top),(a[0],a[1],parapet_top)], CLAD)
    mb.face([(x,y,parapet_top) for x,y in ring], ROOF)
    sw,sd = min(10.0, xspan*0.34), min(13.0, yspan*0.24)
    mb.box((xmid-sw/2, ymid-sd/2, parapet_top),
           (xmid+sw/2, ymid+sd/2, roof_screen_top), CLAD)
    mb.box((xmid-sw/2+0.55, ymid-sd/2+0.55, roof_screen_top-0.12),
           (xmid+sw/2-0.55, ymid+sd/2-0.55, roof_screen_top), ROOF)

    # Brick accent on a short west/south corner wall is directly visible in the
    # official Purdue photograph; material remains on the footprint wall plane.
    west_edges = [e for e in edges if e[3] < -0.65 and e[2] > 3.0]
    corner_edge = min(west_edges,
                      key=lambda e: abs((e[0][1]+e[1][1])/2-min(ys)),
                      default=None)
    if corner_edge:
        a,b,length,nx,ny = corner_edge
        along=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); normal=Vector((nx,ny,0))
        w=min(3.4,length*0.58); center=length*0.54
        p0=Vector((a[0],a[1],0))+along*(center-w/2)+normal*0.055
        p1=Vector((a[0],a[1],0))+along*(center+w/2)+normal*0.055
        mb.face([(p0.x,p0.y,0.15),(p1.x,p1.y,0.15),(p1.x,p1.y,main_roof),(p0.x,p0.y,main_roof)],BRICK)

    # Recessed entrance canopy and two posts on an east/south-facing facade.
    south_edges = [e for e in edges if e[4] < -0.60 and e[2] > 3.8]
    entry = min(south_edges, key=lambda e: abs((e[0][0]+e[1][0])/2-xmid), default=None)
    if entry:
        a,b,length,nx,ny=entry
        along=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); normal=Vector((nx,ny,0))
        w=min(4.6,length*0.55); center=length*0.52; base=Vector((a[0],a[1],0))+along*(center-w/2)
        door_w=1.85
        d0=Vector((a[0],a[1],0))+along*(center-door_w/2)+normal*0.055
        d1=d0+along*door_w
        mb.face([(d0.x,d0.y,0.10),(d1.x,d1.y,0.10),(d1.x,d1.y,2.65),(d0.x,d0.y,2.65)],GLASS)
        for s in (center-door_w/2, center-door_w/2+door_w-0.06, center-0.03):
            p=Vector((a[0],a[1],0))+along*s+normal*0.085
            q=p+along*0.06
            mb.face([(p.x,p.y,0.08),(q.x,q.y,0.08),(q.x,q.y,2.70),(p.x,p.y,2.70)],FRAME)
        # The shallow canopy projects from the photographed entrance; the structural
        # shell used for plan measurements remains the official GIS footprint.
        q0=base+normal*0.05+Vector((0,0,3.55)); q1=q0+along*w
        q2=q1+normal*1.35; q3=q0+normal*1.35
        mb.face([tuple(q0),tuple(q1),tuple(q2),tuple(q3)],CANOPY)
        for t in (0.12,0.88):
            p=base+along*(w*t)+normal*0.35
            mb.box((p.x-0.08,p.y-0.08,0.0),(p.x+0.08,p.y+0.08,3.52),CANOPY)

    # Reuse the manifest-named scene/collection and preserve its campus-frame mesh.
    scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        scene.collection.children.link(collection)
    else:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    mesh = bpy.data.meshes.new(f"{ASSET_ID}_mesh")
    mesh.from_pydata(mb.vertices, [], mb.faces)
    mesh.materials.clear()
    for mat in mats:
        mesh.materials.append(mat)
    for poly, idx in zip(mesh.polygons, mb.materials):
        poly.material_index = idx
    mesh.validate(clean_customdata=True)
    mesh.update()
    obj = bpy.data.objects.new(OBJECT_NAME, mesh)
    collection.objects.link(obj)
    obj["asset_id"] = ASSET_ID
    obj["source_feature"] = "Purdue ArcGIS BuildingShapesZip4 FID 635 / MANN"
    obj["source_footprint_crs"] = "EPSG:4326 transformed using modular/README.md local approximation"
    obj["source_roof_height_m"] = gis_roof
    obj["story_representation"] = "two visible main stories; architect source also documents lower level; GIS level fields conflict"
    obj["placement_frame"] = "campus coordinates retained; identity placement"
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.10,0.12,0.15)
    scene.view_settings.view_transform = "AgX"

    # Render from the photographed entrance corner for a reviewable preview.
    render_collection = bpy.data.collections.new("_MannHall_preview_only")
    scene.collection.children.link(render_collection)
    camera_data = bpy.data.cameras.new("_MannHallPreviewCamera")
    camera = bpy.data.objects.new("_MannHallPreviewCamera",camera_data)
    render_collection.objects.link(camera)
    camera.location=(xmid-96,ymid-122,42)
    target=Vector((xmid,ymid,4.8))
    camera.rotation_euler=(target-Vector(camera.location)).to_track_quat("-Z","Y").to_euler()
    camera.data.type="ORTHO"
    camera.data.ortho_scale=max(xspan*2.15,yspan*1.85)
    scene.camera=camera
    for i,(loc,power,size) in enumerate((((xmid+8,ymid-50,72),52000,58),((xmid-55,ymid+34,48),34000,52))):
        data=bpy.data.lights.new(f"_MannHallPreviewLight{i}","AREA"); data.energy=power; data.shape="DISK"; data.size=size
        lamp=bpy.data.objects.new(f"_MannHallPreviewLight{i}",data); render_collection.objects.link(lamp); lamp.location=loc
        lamp.rotation_euler=(target-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    PREVIEW.parent.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(PREVIEW)
    bpy.ops.render.render(write_still=True)
    scene.camera=None
    for obj in list(render_collection.objects):
        bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(render_collection)

    ASSET.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    report={
        "asset_id":ASSET_ID,"asset_path":str(ASSET.relative_to(ROOT)),"scene":SCENE_NAME,
        "collection":COLLECTION_NAME,"object_count":len(collection.objects),
        "vertices":len(mesh.vertices),"faces":len(mesh.polygons),
        "official_gis_feature":"FID 635 / MANN","source_ring_points":len(ring),
        "source_shape_area_native":attrs["Shape__Area"],"source_area_native_crs":"EPSG:3857",
        "projected_footprint_area_m2":abs(signed_area),"gis_levels":attrs["NUM_LEVELS"],
        "architect_visible_stories":2,"max_roof_height_m":gis_roof,
        "floor_2_elevation_m":floor_2,"gis_floor_3_elevation_m":floor_3,
        "main_shell_roof_m":main_roof,"uncertainty":"GIS field count (3) conflicts with architect's two-story-plus-lower-level description; GIS floor labels retained for record; basement not modeled.",
        "preview_path":str(PREVIEW.relative_to(ROOT))
    }
    (AUDIT/"build_summary.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("MANN_BUILD_SUMMARY",json.dumps(report))


build()
