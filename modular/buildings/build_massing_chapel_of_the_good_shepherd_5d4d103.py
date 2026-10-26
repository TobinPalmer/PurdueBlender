"""Rebuild the Chapel of the Good Shepherd from its mapped outline and photos.

The mapped OpenStreetMap perimeter is kept in campus coordinates using the
project's documented local WGS84 approximation. Exterior height and detailed
proportions are estimates from the church's own undated exterior photograph.
"""

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_chapel_of_the_good_shepherd_5d4d103"
ASSET_FILE = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE_FILE = ROOT / "audit" / "chapel_good_shepherd_5d4d103" / "sources" / "osm_way_869993661_2026-10-26.json"
PREVIEW_FILE = ROOT / "audit" / "chapel_good_shepherd_5d4d103" / "chapel_good_shepherd_preview.png"
RESULT_FILE = ROOT / "audit" / "chapel_good_shepherd_5d4d103" / "build_result.json"
SCENE_NAME = "Building_massing_chapel_of_the_good_shepherd_5d4d103"
COLLECTION_NAME = "Asset_massing_chapel_of_the_good_shepherd_5d4d103"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
LON_M = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
LAT_M = 111040.0
WALL_H = 4.35  # estimated from the church's own exterior photograph
EAVE_H = 5.55
RIDGE_H = 9.0


def local_xy(lon, lat):
    return ((lon - ORIGIN_LON) * LON_M, (lat - ORIGIN_LAT) * LAT_M)


def material(name, color, roughness=0.78):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


class MeshBuilder:
    def __init__(self):
        self.verts = []
        self.faces = []
        self.material_ids = []
        self.vertex_map = {}

    def vertex(self, point):
        xyz=tuple(float(c) for c in point)
        key=tuple(round(c,6) for c in xyz)
        if key not in self.vertex_map:
            self.vertex_map[key]=len(self.verts)
            self.verts.append(xyz)
        return self.vertex_map[key]

    def face(self, points, mat_id):
        ids = [self.vertex(p) for p in points]
        self.faces.append(tuple(ids))
        self.material_ids.append(mat_id)

    def box(self, center, axes, size, mat_id):
        c = Vector(center)
        ax, ay, az = (Vector(a).normalized() for a in axes)
        # The basis must be right-handed for the standard outward face winding.
        if ax.cross(ay).dot(az) < 0:
            ax=-ax
        sx, sy, sz = (v / 2.0 for v in size)
        points = [c + ax * (sx * x) + ay * (sy * y) + az * (sz * z)
                  for x, y, z in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                  (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
        for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
            self.face([points[i] for i in face], mat_id)

    def beam(self, a, b, width, depth, mat_id, normal=None):
        a, b = Vector(a), Vector(b)
        tangent = (b - a).normalized()
        if normal is None:
            normal = Vector((1, 0, 0)) if abs(tangent.x) < 0.95 else Vector((0, 1, 0))
        else:
            normal = Vector(normal).normalized()
        third = tangent.cross(normal).normalized()
        self.box((a + b) / 2, (tangent, normal, third), ((b-a).length, depth, width), mat_id)

    def window(self, center, tangent, normal, width=1.35, height=2.15, trim=4, glass=3):
        t, n = Vector(tangent).normalized(), Vector(normal).normalized()
        up = Vector((0, 0, 1))
        c = Vector(center)
        self.box(c, (t,n,up), (width,0.18,height), trim)
        gc = c + n * 0.105
        self.box(gc, (t,n,up), (width-0.20,0.035,height-0.22), glass)
        self.box(gc + t * (width * 0.10), (t,n,up), (0.055,0.035,height-0.28), trim)
        self.box(gc, (t,n,up), (width-0.23,0.035,0.055), trim)


def add_wall_shell(mb, footprint):
    n = len(footprint)
    bottom = [(x, y, 0.0) for x, y in footprint]
    top = [(x, y, WALL_H) for x, y in footprint]
    for i in range(n):
        j = (i + 1) % n
        mb.face([bottom[i], bottom[j], top[j], top[i]], 0)
    # Blender triangulates this planar concave perimeter during mesh update.
    mb.face(list(reversed(bottom)), 1)
    mb.face(top, 0)


def roof_main_gable(mb, x0, x1, y0, y1):
    xm, ym = (x0+x1)/2.0, (y0+y1)/2.0
    z0, zp = EAVE_H, RIDGE_H
    # Raised masonry above the common lower shell.
    for y in (y0, y1):
        mb.face([(x0,y,WALL_H),(x1,y,WALL_H),(x1,y,z0),(x0,y,z0)],0)
    for x in (x0, x1):
        mb.face([(x,y0,WALL_H),(x,y1,WALL_H),(x,y1,z0),(x,y0,z0)],0)
    # Triangular gable faces at the south (Meridian) and north ends.
    mb.face([(x0,y0,z0),(x1,y0,z0),(xm,y0,zp)],0)
    mb.face([(x1,y1,z0),(x0,y1,z0),(xm,y1,zp)],0)
    # Roof planes meet along a north-south ridge.
    mb.face([(x0,y0,z0),(xm,y0,zp),(xm,y1,zp),(x0,y1,z0)],2)
    mb.face([(xm,y1,zp),(xm,y0,zp),(x1,y0,z0),(x1,y1,z0)],2)
    # White fascia follows the south-facing gable profile.
    mb.beam((x0,y0-0.04,z0),(xm,y0-0.04,zp),0.20,0.16,4,normal=(0,-1,0))
    mb.beam((xm,y0-0.04,zp),(x1,y0-0.04,z0),0.20,0.16,4,normal=(0,-1,0))
    mb.beam((x0,y0-0.05,z0),(x1,y0-0.05,z0),0.16,0.14,4,normal=(0,-1,0))


def roof_lower_gable(mb, x0, x1, y0, y1, eave, ridge, along_x=True):
    # Low pitched wings seen at both ends of the main sanctuary volume.
    if along_x:
        ym = (y0+y1)/2.0
        mb.face([(x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave)],0)
        mb.face([(x0,y0,eave),(x1,y0,eave),(x1,ym,ridge),(x0,ym,ridge)],2)
        mb.face([(x0,y1,eave),(x0,ym,ridge),(x1,ym,ridge),(x1,y1,eave)],2)
        xm=(x0+x1)/2.0
        mb.face([(x0,y0,eave),(x1,y0,eave),(xm,y0,ridge)],0)
        mb.face([(x1,y1,eave),(x0,y1,eave),(xm,y1,ridge)],0)
        # Close the exposed east-west end profiles; without these the low
        # wings show triangular voids at their outer gable ends.
        mb.face([(x0,y0,eave),(x0,y1,eave),(x0,ym,ridge)],0)
        mb.face([(x1,y1,eave),(x1,y0,eave),(x1,ym,ridge)],0)
    else:
        xm = (x0+x1)/2.0
        mb.face([(x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave)],0)
        mb.face([(x0,y0,eave),(xm,y0,ridge),(xm,y1,ridge),(x0,y1,eave)],2)
        mb.face([(x1,y0,eave),(x1,y1,eave),(xm,y1,ridge),(xm,y0,ridge)],2)
        ym=(y0+y1)/2.0
        mb.face([(x0,y0,eave),(x0,y1,eave),(x0,ym,ridge)],0)
        mb.face([(x1,y1,eave),(x1,y0,eave),(x1,ym,ridge)],0)


def add_front_door(mb, x, y, z=1.62):
    # Meridian-facing south elevation: tangent runs east-west, normal points south.
    front_axes = ((1,0,0),(0,-1,0),(0,0,1))
    c = (x,y-0.09,z)
    mb.box(c,front_axes,(2.15,0.22,3.05),4)
    mb.box((x,y-0.23,z-0.03),front_axes,(1.72,0.07,2.72),7)
    mb.box((x,y-0.28,z+0.05),front_axes,(0.07,0.04,2.58),4)
    mb.box((x,y-0.28,z-0.10),front_axes,(1.56,0.04,0.07),4)
    mb.box((x-0.73,y-0.31,z+0.15),front_axes,(0.05,0.04,0.08),4)
    mb.box((x+0.73,y-0.31,z+0.15),front_axes,(0.05,0.04,0.08),4)
    # A restrained white entrance canopy with two square supports.
    mb.box((x,y-1.25,3.30),front_axes,(2.55,3.10,0.20),4)
    for xx in (x-1.14,x+1.14):
        mb.box((xx,y-2.55,1.67),front_axes,(0.22,0.22,3.26),4)
    # Four shallow masonry steps face Meridian Street.
    for i in range(3):
        # The top step meets the door; each lower tread projects about 0.35 m.
        mb.box((x,y-0.42-i*0.34,0.15+i*0.15),front_axes,(2.55,0.44,0.28),1)


def add_steeple(mb, x, y):
    # Small white louvered bell stage and tall, tapered spire; dimensions are
    # visual estimates from the official exterior photo, not survey values.
    mb.box((x,y,9.15),( (1,0,0),(0,1,0),(0,0,1) ),(3.15,3.15,1.10),4)
    for z in (8.95,9.25,9.65):
        for axis in (0,1):
            if axis == 0:
                mb.box((x,y-1.61,z),((1,0,0),(0,1,0),(0,0,1)),(2.35,0.07,0.045),3)
                mb.box((x,y+1.61,z),((1,0,0),(0,1,0),(0,0,1)),(2.35,0.07,0.045),3)
            else:
                mb.box((x-1.61,y,z),((0,1,0),(1,0,0),(0,0,1)),(2.35,0.07,0.045),3)
                mb.box((x+1.61,y,z),((0,1,0),(1,0,0),(0,0,1)),(2.35,0.07,0.045),3)
    mb.box((x,y,10.05),((1,0,0),(0,1,0),(0,0,1)),(2.55,2.55,0.36),4)
    # Four sloped white faces form an octagonal-looking steeple cap.
    base_z, tip_z, r = 10.23, 16.70, 1.65
    ring=[(x-r,y-r,base_z),(x+r,y-r,base_z),(x+r,y+r,base_z),(x-r,y+r,base_z)]
    tip=(x,y,tip_z)
    for i in range(4): mb.face([ring[i],ring[(i+1)%4],tip],4)
    mb.box((x,y,16.92),((1,0,0),(0,1,0),(0,0,1)),(0.18,0.18,0.55),4)
    mb.beam((x,y,17.15),(x,y,18.25),0.12,0.12,4)
    # Simple cross motif at the spire point, which is clearly visible in photo.
    mb.beam((x,y,18.05),(x,y,18.65),0.075,0.08,4)
    mb.beam((x-0.25,y,18.43),(x+0.25,y,18.43),0.075,0.08,4)


def add_gable_vent(mb, x, y, z):
    # Half-round louver and outer stone ring on the south gable.
    front_axes=((1,0,0),(0,-1,0),(0,0,1))
    mb.box((x,y,z),(front_axes[0],front_axes[1],front_axes[2]),(1.65,0.10,1.05),4)
    mb.box((x,y-0.07,z),(front_axes[0],front_axes[1],front_axes[2]),(1.26,0.06,0.70),3)
    for dz in (-0.22,0.0,0.22):
        mb.box((x,y-0.13,z+dz),(front_axes[0],front_axes[1],front_axes[2]),(1.05,0.04,0.045),4)


def main():
    data=json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    way=next(e for e in data["elements"] if e["type"]=="way" and e["id"]==869993661)
    nodes={e["id"]:e for e in data["elements"] if e["type"]=="node"}
    footprint=[local_xy(nodes[n]["lon"],nodes[n]["lat"]) for n in way["nodes"]]
    if footprint[0] == footprint[-1]: footprint.pop()
    assert len(footprint)==12 and way.get("tags",{}).get("name")=="Chapel of the Good Shepherd"

    for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
    for col in list(bpy.data.collections): bpy.data.collections.remove(col)
    for other in list(bpy.data.scenes):
        if other!=bpy.context.scene: bpy.data.scenes.remove(other)
    scene=bpy.context.scene; scene.name=SCENE_NAME
    asset=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(asset)
    rig=bpy.data.collections.new("Render_Setup"); scene.collection.children.link(rig)

    mats=[
        material("Warm red church brick",(0.43,0.13,0.075)),
        material("Pale limestone foundation and steps",(0.60,0.57,0.49)),
        material("Muted red-brown shingle roof",(0.28,0.12,0.10)),
        material("Dark blue-gray glazing and louvers",(0.11,0.20,0.23),0.28),
        material("White painted trim",(0.91,0.90,0.83)),
        material("Brass door hardware",(0.62,0.42,0.13),0.32),
        material("Brick courses",(0.34,0.09,0.055)),
        material("Deep red entrance doors",(0.67,0.03,0.15),0.45),
    ]
    mb=MeshBuilder()
    add_wall_shell(mb,footprint)

    # Main sanctuary occupies the north-south center, with its gable and
    # principal Meridian Street entrance facing south (minimum Y).
    x0,x1=13.30,23.49
    y0,y1=770.13,787.80
    roof_main_gable(mb,x0,x1,y0,y1)

    # Lower west room wing and long lower east wing follow the mapped outline.
    roof_lower_gable(mb,6.62,13.39,774.70,784.55,eave=WALL_H,ridge=5.55,along_x=True)
    roof_lower_gable(mb,23.00,40.58,772.45,785.55,eave=WALL_H,ridge=5.55,along_x=True)
    # Shallow connector roofs close the north and south joints without gaps.
    mb.face([(13.18,770.13,5.35),(23.49,770.13,5.35),(23.49,774.78,5.35),(13.18,774.78,5.35)],2)
    mb.face([(13.18,784.46,5.35),(23.00,784.62,5.35),(23.00,785.55,5.35),(13.18,785.70,5.35)],2)

    # Meridian Street porch and centered entrance below the south gable.
    front_x=(x0+x1)/2.0
    add_front_door(mb,front_x,y0)
    for dx in (-3.25,3.25):
        mb.window((front_x+dx,y0-0.035,2.85),(1,0,0),(0,-1,0),1.52,2.25)
    add_gable_vent(mb,front_x,y0-0.04,7.12)

    # Tall, regularly spaced sanctuary windows along the lower east wing.
    for xx in (26.0,30.4,34.8,38.2):
        mb.window((xx,785.58,2.65),(1,0,0),(0,1,0),1.45,2.65)
        mb.window((xx,772.42,2.65),(1,0,0),(0,-1,0),1.45,2.65)

    # The church site identifies a separate accessible entrance on its north
    # side. Its location is approximate within that facade; three steps mark it.
    n_axes=((1,0,0),(0,1,0),(0,0,1))
    mb.box((29.0,785.62,1.53),n_axes,(1.55,0.20,2.85),4)
    mb.box((29.0,785.74,1.53),n_axes,(1.20,0.05,2.56),7)
    for i in range(3):
        mb.box((29.0,785.95+i*0.38,0.13+i*0.14),n_axes,(2.25,0.48,0.24),1)

    # Lower wing window rhythm from the same photo; exact counts remain visual estimates.
    for xx in (8.6,11.4):
        if xx < 13.0:
            yy=774.66
            mb.window((xx,yy-0.035,2.20),(1,0,0),(0,-1,0),1.10,1.75)

    # A small round side window and white edge bands preserve the photo's
    # distinctive church silhouette without inventing decorative stonework.
    for x in (x0,x1):
        mb.beam((x, y0, 5.65),(x,y1,5.65),0.12,0.12,4,normal=(1,0,0))
    add_steeple(mb,(x0+x1)/2.0,(y0+y1)/2.0)

    mesh=bpy.data.meshes.new("Chapel mapped shell and photo-based massing")
    mesh.from_pydata(mb.verts,[],mb.faces); mesh.update()
    obj=bpy.data.objects.new("Chapel of the Good Shepherd",mesh); asset.objects.link(obj)
    for mat in mats: mesh.materials.append(mat)
    for poly,mi in zip(mesh.polygons,mb.material_ids): poly.material_index=mi
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)

    cx=sum(x for x,y in footprint)/len(footprint); cy=sum(y for x,y in footprint)/len(footprint)
    camera_data=bpy.data.cameras.new("Chapel preview camera")
    camera=bpy.data.objects.new("Chapel preview camera",camera_data); rig.objects.link(camera)
    camera.location=(cx+21,cy-47,26)
    target=Vector((cx,cy,7.5)); camera.rotation_euler=(target-Vector(camera.location)).to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO"; camera_data.ortho_scale=53.0; scene.camera=camera
    light_data=bpy.data.lights.new("Soft church key",type="AREA"); light_data.energy=12000; light_data.shape="DISK"; light_data.size=36
    light=bpy.data.objects.new("Soft church key",light_data); rig.objects.link(light)
    light.location=(cx+14,cy-28,43); light.rotation_euler=(Vector((cx,cy,4))-Vector(light.location)).to_track_quat("-Z","Y").to_euler()
    scene.render.engine="CYCLES"; scene.cycles.samples=24
    scene.render.resolution_x=1450; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.filepath=str(PREVIEW_FILE)
    scene.world.use_nodes=True; scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.54,0.62,0.72,1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.8
    scene.view_settings.view_transform="AgX"; scene.view_settings.look="AgX - Medium High Contrast"
    os.makedirs(PREVIEW_FILE.parent,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE))
    bpy.ops.render.render(write_still=True)

    bounds=[[min(v[i] for v in obj.bound_box),max(v[i] for v in obj.bound_box)] for i in range(3)]
    result={"asset":str(ASSET_FILE.relative_to(ROOT)).replace("\\","/"),"collection":COLLECTION_NAME,"scene":SCENE_NAME,
            "object_count":len(asset.objects),"mesh_vertices":len(mesh.vertices),"mesh_polygons":len(mesh.polygons),
            "bounds_world_m":bounds,"source_osm_way":869993661,"footprint_vertices":len(footprint),
            "wall_height_estimate_m":WALL_H,"main_eave_estimate_m":EAVE_H,"ridge_estimate_m":RIDGE_H,
            "steeple_tip_estimate_m":18.65,"preview":str(PREVIEW_FILE.relative_to(ROOT)).replace("\\","/")}
    RESULT_FILE.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
