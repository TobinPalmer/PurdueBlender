"""Build a source-backed detailed Twin Pines Cooperative library.

Coordinates stay in the source asset's campus frame. Only the assigned Twin
Pines asset is written; shared manifest/index/master files are coordinator-owned.
Run with Blender 4.5: blender -b <asset.blend> --python <this script>.
"""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_twin_pines_cooperative_8f606f9.blend"
AUDIT = ROOT / "audit/massing_twin_pines_cooperative_8f606f9"
RENDERS = AUDIT / "renders"
ASSET_ID = "massing_twin_pines_cooperative_8f606f9"
COLLECTION_NAME = "Asset_" + ASSET_ID
OBJECT_NAME = "Twin Pines Cooperative"

# OSM way 301934836, projected with modular/AGENTS.md's approximate campus
# conversion. The vertices preserve the asset's six-sided footprint exactly.
FOOTPRINT = [
    (-341.277871, 76.428832),
    (-341.379644, 65.691264),
    (-316.894822, 65.458080),
    (-316.767607, 78.871712),
    (-327.267159, 78.971648),
    (-327.292603, 76.284480),
]
XMIN, XMAX = -341.379644, -316.767607
YFRONT = 65.458080
YBACK = 78.971648
NOTCH_X = -327.28
NOTCH_Y = 76.35
ZFOUND = 0.35
ZEAVE = 6.45       # estimated from the two visible storeys in source photos
ZRIDGE = 9.05      # estimated, not a measured survey height


class MeshAssembler:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.material_ids = []

    def add(self, verts, faces, mat_id):
        base = len(self.vertices)
        self.vertices.extend(tuple(v) for v in verts)
        self.faces.extend(tuple(base + i for i in f) for f in faces)
        self.material_ids.extend([mat_id] * len(faces))

    def box(self, center, size, mat_id):
        x, y, z = center
        dx, dy, dz = (s * 0.5 for s in size)
        verts = [(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),
                 (x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),
                 (x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),
                 (x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)]
        faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),
                 (1,2,6,5),(2,3,7,6),(3,0,4,7)]
        self.add(verts, faces, mat_id)

    def cylinder(self, center, radius, depth, mat_id, sides=20):
        x, y, z = center
        verts = []
        for zz in (z-depth/2, z+depth/2):
            for i in range(sides):
                import math
                a = 2*math.pi*i/sides
                verts.append((x+radius*math.cos(a), y+radius*math.sin(a), zz))
        faces = [tuple(reversed(range(sides))), tuple(range(sides,2*sides))]
        faces.extend((i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides))
        self.add(verts, faces, mat_id)

    def footprint_prism(self, points, z0, z1, mat_id):
        n = len(points)
        verts = [(x,y,z0) for x,y in points] + [(x,y,z1) for x,y in points]
        faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
        faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
        self.add(verts, faces, mat_id)

    def quad_slab(self, top, thickness, mat_id):
        bottom = [(x,y,z-thickness) for x,y,z in top]
        verts = list(top) + bottom
        self.add(verts, [(0,1,2,3),(7,6,5,4),(0,4,5,1),
                         (1,5,6,2),(2,6,7,3),(3,7,4,0)], mat_id)

    def triangle(self, points, mat_id):
        self.add(points, [(0,1,2)], mat_id)

    def build(self, name, materials):
        mesh = bpy.data.meshes.new(name + "_UnifiedMesh")
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.materials.clear()
        for material in materials:
            mesh.materials.append(material)
        for poly, mat_id in zip(mesh.polygons, self.material_ids):
            poly.material_index = mat_id
        mesh.validate(verbose=False)
        mesh.update()
        return mesh


def material(name, color, roughness=0.72):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_south_window(m, x, z, width=1.1, height=1.55):
    # South-facing double-hung sash, white casing and historical black shutters.
    y = YFRONT - 0.045
    m.box((x,y,z), (width,0.10,height), 3)
    for dx in (-width/2-0.10, width/2+0.10):
        m.box((x+dx,y-0.085,z), (0.17,0.10,height+0.23), 2)
    for dz in (-height/2-0.09, height/2+0.09):
        m.box((x,y-0.095,z+dz), (width+0.35,0.12,0.16), 2)
    m.box((x,y-0.11,z), (0.055,0.035,height-0.10), 2)
    m.box((x,y-0.115,z), (width-0.06,0.035,0.055), 2)


def add_wall_window_x(m, xwall, y, z, direction, width=1.05, height=1.45):
    # Windows on the east and west short elevations.
    outward = -1 if direction == "west" else 1
    x = xwall + outward*0.05
    m.box((x,y,z),(0.10,width,height),3)
    for dy in (-width/2-0.1,width/2+0.1):
        m.box((x+outward*0.10,y+dy,z),(0.12,0.15,height+0.22),2)
    for dz in (-height/2-0.09,height/2+0.09):
        m.box((x+outward*0.11,y,z+dz),(0.13,width+0.34,0.15),2)
    m.box((x+outward*0.13,y,z),(0.035,0.05,height-0.12),2)
    m.box((x+outward*0.13,y,z),(0.04,width-0.06,0.05),2)


def add_wall_window_y(m, ywall, x, z, direction, width=1.0, height=1.45):
    outward = -1 if direction == "south" else 1
    y = ywall + outward*0.05
    m.box((x,y,z),(width,0.10,height),3)
    for dx in (-width/2-0.10,width/2+0.10):
        m.box((x+dx,y+outward*0.10,z),(0.15,0.12,height+0.22),2)
    for dz in (-height/2-0.09,height/2+0.09):
        m.box((x,y+outward*0.11,z+dz),(width+0.34,0.13,0.15),2)
    m.box((x,y+outward*0.13,z),(0.05,0.04,height-0.12),2)
    m.box((x,y+outward*0.13,z),(width-0.06,0.04,0.05),2)


def setup_scene(obj):
    scene = bpy.context.scene
    # Workbench is a robust cross-machine renderer and displays material
    # colors without external dependencies or a GPU/device assumption.
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.display.shading.curvature_ridge_factor = 1.2
    scene.display.shading.curvature_valley_factor = 0.8
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("Twin Pines World")
        scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.50,0.58,0.68,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65

    for name in ("TwinPines_Key", "TwinPines_Fill"):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = 2300 if name.endswith("Key") else 850
        data.shape = "DISK"
        data.size = 14 if name.endswith("Key") else 18
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = (-350, 50, 28) if name.endswith("Key") else (-310, 72, 22)
        light.rotation_euler = (Vector((-329, 71, 3.8))-light.location).to_track_quat("-Z","Y").to_euler()

    camera_data = bpy.data.cameras.new("TwinPines_Camera")
    camera = bpy.data.objects.new("TwinPines_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 34
    camera.location = (-354, 34, 14)
    camera.rotation_euler = (Vector((-329, 71, 4.0))-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.camera = camera
    return scene, camera


def render_views(scene, camera):
    RENDERS.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(RENDERS / "twin_pines_front_south.png")
    bpy.ops.render.render(write_still=True)

    # Top plan view to inspect coverage against the source wall footprint.
    camera.location = (-329, 72, 70)
    camera.rotation_euler = (Vector((-329,72,0))-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.ortho_scale = 34
    scene.render.filepath = str(RENDERS / "twin_pines_top.png")
    bpy.ops.render.render(write_still=True)

    # East end view reveals the gable and the estimated roof silhouette.
    camera.location = (-285, 72, 14)
    camera.rotation_euler = (Vector((-329,72,4))-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.ortho_scale = 24
    scene.render.filepath = str(RENDERS / "twin_pines_east.png")
    bpy.ops.render.render(write_still=True)


def main():
    if not ASSET.exists():
        raise FileNotFoundError(ASSET)
    collection = bpy.data.collections.get(COLLECTION_NAME)
    obj = bpy.data.objects.get(OBJECT_NAME)
    if collection is None or obj is None or obj.type != "MESH":
        raise RuntimeError("Expected existing Twin Pines collection/object missing")

    mats = [
        material("Twin Pines | pale sage lap siding", (0.48,0.55,0.49)),
        material("Twin Pines | white painted trim", (0.92,0.90,0.82)),
        material("Twin Pines | charcoal shutters and sash", (0.075,0.09,0.10)),
        material("Twin Pines | blue-gray glass", (0.18,0.30,0.36), 0.28),
        material("Twin Pines | dark asphalt shingles", (0.14,0.16,0.18)),
        material("Twin Pines | brick porch piers", (0.32,0.19,0.14)),
        material("Twin Pines | foundation stone", (0.28,0.29,0.28)),
        material("Twin Pines | entry door", (0.14,0.18,0.16)),
    ]
    m = MeshAssembler()

    # Retain the GIS-supported L-shaped ground footprint and use a low exposed
    # foundation. The elevation and floor levels are estimates based on imagery.
    m.footprint_prism(FOOTPRINT, 0.0, ZFOUND, 6)
    m.footprint_prism(FOOTPRINT, ZFOUND, ZEAVE, 0)

    # Projecting lap-board seams reproduce the siding visible in the current and
    # archived exterior photos; horizontal bands stay on the public elevations.
    for z in [0.78 + 0.22*i for i in range(25)]:
        m.box(((XMIN+XMAX)/2, YFRONT-0.07, z), (24.05,0.035,0.028), 1)
    for z in [0.78 + 0.22*i for i in range(25)]:
        m.box((XMAX+0.07, (YFRONT+YBACK)/2, z), (0.035,12.9,0.028), 1)

    # Two-storey front elevation. Entry placement and window counts are estimated
    # from the 2011 exterior and current official site porch image.
    front_windows = [-338.25, -334.75, -328.55, -324.55, -320.45]
    for x in front_windows:
        add_south_window(m, x, 4.93, 1.06, 1.48)
    for x in [-338.25, -328.55, -324.55, -320.45]:
        add_south_window(m, x, 2.02, 1.13, 1.55)

    # Front entrance, visible transom, casing and small address plaque.
    door_x = -333.45
    m.box((door_x,YFRONT-0.12,1.55),(1.02,0.12,2.35),7)
    for dx in (-0.62,0.62):
        m.box((door_x+dx,YFRONT-0.21,1.65),(0.13,0.11,2.65),1)
    m.box((door_x,YFRONT-0.21,2.97),(1.36,0.11,0.15),1)
    m.box((door_x,YFRONT-0.20,2.62),(0.92,0.045,0.35),3)
    m.cylinder((door_x+0.36,YFRONT-0.31,1.53),0.045,0.045,2,12)
    m.box((door_x,YFRONT-0.27,3.16),(1.15,0.08,0.23),1)
    # Address numerals are represented as understated plaques; text remains an
    # estimated visual cue, not an added detached asset.
    for i in range(3):
        m.box((door_x-0.22+i*0.22,YFRONT-0.33,3.16),(0.10,0.025,0.025),2)

    # South and east/north/west side windows. Counts are indicative only.
    for y in [68.2,72.0,75.7]:
        add_wall_window_x(m,XMAX,y,4.95,"east",1.0,1.45)
        add_wall_window_x(m,XMAX,y,2.03,"east",1.0,1.45)
    for y in [69.1,73.3]:
        add_wall_window_x(m,XMIN,y,4.95,"west",1.0,1.45)
    for x in [-324.9,-320.8]:
        add_wall_window_y(m,YBACK,x,4.95,"north",1.0,1.45)
        add_wall_window_y(m,YBACK,x,2.05,"north",1.0,1.45)

    # Rear northeast projection suggested by the GIS outline; it receives a
    # lower secondary shed roof rather than being treated as an independent block.
    # Primary gable roof: ridge parallel to the long (east-west) house axis.
    x0, x1 = XMIN-0.62, XMAX+0.62
    y0, y1 = YFRONT-0.67, NOTCH_Y+0.65
    yr = (y0+y1)/2
    m.quad_slab([(x0,y0,ZEAVE),(x1,y0,ZEAVE),(x1,yr,ZRIDGE),(x0,yr,ZRIDGE)],0.22,4)
    m.quad_slab([(x0,yr,ZRIDGE),(x1,yr,ZRIDGE),(x1,y1,ZEAVE),(x0,y1,ZEAVE)],0.22,4)
    # West/east gable triangles above the eaves, painted siding with trim verge.
    m.triangle([(XMIN-0.03,y0+0.3,ZEAVE),(XMIN-0.03,y1-0.3,ZEAVE),(XMIN-0.03,yr,ZRIDGE)],0)
    m.triangle([(XMAX+0.03,y0+0.3,ZEAVE),(XMAX+0.03,yr,ZRIDGE),(XMAX+0.03,y1-0.3,ZEAVE)],0)
    # Small attic gable vent at west end, intentionally plain and source-backed.
    m.box((XMIN-0.10,yr,7.45),(0.14,0.70,0.16),2)

    # Lower roof over the small rear/northeast wing. Height is estimated from
    # the exterior photo's two roof masses; no plan/elevation survey was found.
    m.quad_slab([(NOTCH_X,YBACK+0.28,ZEAVE+0.12),(XMAX+0.38,YBACK+0.28,ZEAVE+0.12),
                 (XMAX+0.38,NOTCH_Y-0.10,ZEAVE+0.45),(NOTCH_X,NOTCH_Y-0.10,ZEAVE+0.45)],0.16,4)

    # Deep front porch canopy/ceiling, landing, and four classical columns on
    # brick piers, railings, and entrance steps, as shown on the official house
    # photo and Purdue-published archival exterior.
    porch_x0, porch_x1 = -340.15, -327.3
    porch_y0, porch_y1 = YFRONT+0.03, YFRONT-2.15
    porch_z = 0.52
    m.box(((porch_x0+porch_x1)/2,(porch_y0+porch_y1)/2,porch_z),(porch_x1-porch_x0,porch_y0-porch_y1,0.25),6)
    m.box(((porch_x0+porch_x1)/2,(porch_y0+porch_y1)/2,3.55),(porch_x1-porch_x0+0.42,porch_y0-porch_y1+0.32,0.28),1)
    m.box(((porch_x0+porch_x1)/2,porch_y0-0.05,3.37),(porch_x1-porch_x0+0.5,0.16,0.14),1)
    post_xs = [-339.25,-335.25,-331.25,-327.25]
    post_y = YFRONT-1.82
    for px in post_xs:
        m.box((px,post_y,0.92),(0.86,0.83,0.90),5)
        m.box((px,post_y,1.39),(0.98,0.92,0.10),1)
        m.cylinder((px,post_y,2.42),0.22,2.0,1,24)
        m.cylinder((px,post_y,3.47),0.36,0.18,1,24)
        m.cylinder((px,post_y,3.34),0.30,0.12,1,24)
        m.cylinder((px,post_y,1.48),0.30,0.10,1,24)
    # White porch balustrade and evenly spaced balusters between brick piers.
    rail_y = YFRONT-2.02
    m.box(((-339.25-335.25)/2,rail_y,1.53),(3.50,0.10,0.10),1)
    m.box(((-331.25-327.25)/2,rail_y,1.53),(3.50,0.10,0.10),1)
    m.box(((-339.25-335.25)/2,rail_y,1.04),(3.50,0.10,0.10),1)
    m.box(((-331.25-327.25)/2,rail_y,1.04),(3.50,0.10,0.10),1)
    for a,b in [(-339.25,-335.25),(-331.25,-327.25)]:
        n=8
        for i in range(1,n):
            bx=a+(b-a)*i/n
            m.box((bx,rail_y,1.28),(0.08,0.08,0.40),1)
    # Central steps align with the front door.
    for i in range(3):
        width=1.70+i*0.35
        y=YFRONT-2.45-i*0.45
        z=0.38-i*0.12
        m.box((door_x,y,z),(width,0.55,0.22),6)

    # Build a single unified mesh and retain the original stable name/object,
    # collection, scene and campus position.
    old_location = obj.location.copy()
    old_rotation = obj.rotation_euler.copy()
    old_scale = obj.scale.copy()
    new_mesh = m.build(OBJECT_NAME, mats)
    old_mesh = obj.data
    obj.data = new_mesh
    obj.location = old_location
    obj.rotation_euler = old_rotation
    obj.scale = old_scale
    obj.name = OBJECT_NAME
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

    # Remove any previous render-only helpers before saving, then set up lights
    # and cameras for preview. They remain outside the exported building library.
    for name in ("TwinPines_Key","TwinPines_Fill","TwinPines_Camera"):
        helper = bpy.data.objects.get(name)
        if helper:
            bpy.data.objects.remove(helper, do_unlink=True)
    scene, camera = setup_scene(obj)
    # Save only the building asset with its original collection and object.
    # Render helpers are removed again before final save to keep export portable.
    render_views(scene,camera)
    for name in ("TwinPines_Key","TwinPines_Fill","TwinPines_Camera"):
        helper = bpy.data.objects.get(name)
        if helper:
            bpy.data.objects.remove(helper, do_unlink=True)
    if scene.camera and scene.camera.name == "TwinPines_Camera":
        scene.camera = None
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print("TWIN PINES BUILD SAVED", ASSET)
    print("COLLECTION", collection.name, "objects", len(collection.objects))
    print("VERTICES", len(new_mesh.vertices), "POLYGONS", len(new_mesh.polygons))
    print("BOUNDS", [round(v,3) for v in obj.dimensions])


main()
