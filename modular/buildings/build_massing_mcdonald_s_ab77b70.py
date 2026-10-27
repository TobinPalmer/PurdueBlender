"""Build the assigned Purdue McDonald's massing asset from the OSM store footprint.

The source footprint is OSM way 256640455, whose tags name McDonald's, give
605 Stadium Avenue, and link the official store page. Purdue's campus GIS has
no separate matching McDonald's feature; see audit/mcdonald_s/evidence.json.
"""
from __future__ import annotations
import bpy, json, math
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
BLEND = ROOT / "modular" / "buildings" / "massing_mcdonald_s_ab77b70.blend"
OSM_XML = ROOT / "audit" / "mcdonald_s" / "sources" / "osm_way_256640455_full.xml"
PREVIEW = ROOT / "audit" / "mcdonald_s" / "preview_exterior.png"
COLLECTION_NAME = "Asset_massing_mcdonald_s_ab77b70"
OBJECT_NAME = "McDonald's"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
LON_M = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
LAT_M = 111040.0
WALL_H = 4.15       # estimated; no measured elevation source found
PARAPET_H = 0.55    # visual estimate from aerial/typical single-story retail massing

# Store-specific front elevations come from the attributed USA Restaurants
# photo saved in the audit folder. Rear/side elevations remain unverified.
MAT = {
    "wall": (0.63, 0.64, 0.63, 1),
    "brick": (0.075, 0.085, 0.085, 1),
    "base": (0.18, 0.19, 0.19, 1),
    "fascia": (0.42, 0.46, 0.47, 1),
    "gold": (1.0, 0.78, 0.015, 1),
    "frame": (0.045, 0.055, 0.06, 1),
    "glass": (0.055, 0.11, 0.14, 1),
    "roof": (0.72, 0.74, 0.73, 1),
    "door": (0.09, 0.14, 0.16, 1),
    "text": (0.92, 0.93, 0.88, 1),
}


def load_ring():
    import xml.etree.ElementTree as ET
    root = ET.parse(OSM_XML).getroot()
    way = root.find("way")
    if way is None or way.get("id") != "256640455":
        raise RuntimeError("Expected OSM way 256640455 not found")
    nodes = {n.get("id"): (float(n.get("lon")), float(n.get("lat"))) for n in root.findall("node")}
    tags = {t.get("k"): t.get("v") for t in way.findall("tag")}
    if tags.get("name") != "McDonald's" or tags.get("addr:housenumber") != "605":
        raise RuntimeError(f"OSM identity mismatch: {tags}")
    refs = [nd.get("ref") for nd in way.findall("nd")]
    ring = [(nodes[r][0], nodes[r][1]) for r in refs]
    if ring[0] == ring[-1]:
        ring.pop()
    # Keep the published campus coordinate frame; this is a massing asset.
    xy = [((lon - ORIGIN_LON) * LON_M, (lat - ORIGIN_LAT) * LAT_M) for lon, lat in ring]
    return xy, tags


def new_material(name, color, roughness=0.76, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = color
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = color
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    return m


class MeshBuilder:
    def __init__(self):
        self.verts, self.faces, self.materials = [], [], []

    def face(self, verts, mat):
        base = len(self.verts)
        self.verts.extend(tuple(float(v) for v in p) for p in verts)
        self.faces.append(tuple(range(base, base + len(verts))))
        self.materials.append(mat)

    def box(self, center, axis_x, axis_y, length, depth, z0, z1, mat):
        c = Vector(center); x = Vector(axis_x).normalized(); y = Vector(axis_y).normalized()
        pts = []
        for z in (z0, z1):
            for sx, sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
                pts.append(c + x*(sx*length/2) + y*(sy*depth/2) + Vector((0,0,z)))
        # z0/z1 are relative to center.z; center.z stays at zero for this helper.
        self.face([pts[i] for i in (0,1,2,3)], mat)
        self.face([pts[i] for i in (4,7,6,5)], mat)
        for a,b in ((0,1),(1,2),(2,3),(3,0)):
            self.face((pts[a],pts[b],pts[b+4],pts[a+4]), mat)

    def panel(self, p1, p2, z0, z1, offset, mat):
        a, b = Vector(p1), Vector(p2)
        d = b-a; n = Vector((d.y, -d.x, 0)).normalized()  # refined to outward below if needed
        a += n*offset; b += n*offset
        self.face(((a.x,a.y,z0),(b.x,b.y,z0),(b.x,b.y,z1),(a.x,a.y,z1)), mat)


def assign_material(mesh, slots, face_mats):
    for material in slots:
        mesh.materials.append(material)
    for poly, idx in zip(mesh.polygons, face_mats):
        poly.material_index = idx


def remove_generated_helpers():
    for obj in list(bpy.data.objects):
        if obj.name.startswith("__mcd_preview_") or obj.name.startswith("__mcd_ground"):
            bpy.data.objects.remove(obj, do_unlink=True)


def main():
    xy, source_tags = load_ring()
    scene = bpy.context.scene
    asset = bpy.data.collections.get(COLLECTION_NAME)
    if asset is None:
        asset = bpy.data.collections.new(COLLECTION_NAME)
        scene.collection.children.link(asset)
    for obj in list(asset.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # Ensure only the assigned building is exported in this collection.
    mats = {k: new_material("MCD_"+k, v) for k,v in MAT.items()}
    slot_names = list(MAT.keys()); slot_index = {n:i for i,n in enumerate(slot_names)}
    b = MeshBuilder()
    area = sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy))) / 2
    ccw = area > 0
    n = len(xy)
    # Main wall shell and flat roof cap, using the exact OSM perimeter.
    # The photo shows a dark masonry entry bay adjoining a light metal/glass
    # storefront; OSM vertex 1 is the visible corner between those faces.
    for i, (x,y) in enumerate(xy):
        j = (i+1)%n; x2,y2 = xy[j]
        wall_mat = slot_index["brick"] if i == 0 else slot_index["wall"]
        b.face(((x,y,0),(x2,y2,0),(x2,y2,WALL_H),(x,y,WALL_H)), wall_mat)
    b.face([(x,y,WALL_H) for x,y in xy], slot_index["roof"])
    # Base plinth and low metal parapet around the exact roof perimeter.
    for i,(x,y) in enumerate(xy):
        x2,y2=xy[(i+1)%n]
        p1,p2=Vector((x,y,0)),Vector((x2,y2,0))
        d=p2-p1
        normal=Vector((d.y,-d.x,0)).normalized() if ccw else Vector((-d.y,d.x,0)).normalized()
        for z0,z1,mi in ((0.0,0.28,slot_index["base"]),(WALL_H,WALL_H+PARAPET_H,slot_index["fascia"])):
            # Faces create a thin outward strip on each exact boundary segment.
            a=p1+normal*0.035; c=p2+normal*0.035
            b.face(((a.x,a.y,z0),(c.x,c.y,z0),(c.x,c.y,z1),(a.x,a.y,z1)),mi)
    # Yellow roofline canopy is visible over the two adjoining photographed
    # front faces. Its detailed curvature and thickness are still estimated.
    for i in (0,1):
        x,y=xy[i]; x2,y2=xy[(i+1)%n]; p1=Vector((x,y,0)); p2=Vector((x2,y2,0)); d=p2-p1
        outward=Vector((d.y,-d.x,0)).normalized() if ccw else Vector((-d.y,d.x,0)).normalized()
        b.box(((p1.x+p2.x)/2+outward.x*0.35,(p1.y+p2.y)/2+outward.y*0.35,0),d.normalized(),outward,d.length,0.72,3.48,3.82,slot_index["gold"])
    # Storefront glazing follows the long photographed side (way edge 1).
    for i,(x,y) in enumerate(xy):
        if i != 1:
            continue
        x2,y2=xy[(i+1)%n]; p1=Vector((x,y,0)); p2=Vector((x2,y2,0)); d=p2-p1
        length=d.length
        along=d.normalized(); outward=Vector((d.y,-d.x,0)).normalized() if ccw else Vector((-d.y,d.x,0)).normalized()
        count=5
        for k in range(count):
            center=p1+d*((k+1)/(count+1))
            pane_w=min(4.2,(length-1.0)/count*0.82)
            zlo,zhi=0.55,2.65
            b.box((center.x+outward.x*0.075,center.y+outward.y*0.075,0),along,outward,pane_w,0.055,zlo,zhi,slot_index["frame"])
            b.box((center.x+outward.x*0.11,center.y+outward.y*0.11,0),along,outward,pane_w-0.20,0.035,zlo+0.12,zhi-0.12,slot_index["glass"])
            # Dark mullions separate broad storefront panes.
            b.box((center.x+outward.x*0.14,center.y+outward.y*0.14,0),along,outward,0.07,0.025,zlo+0.12,zhi-0.12,slot_index["frame"])
            b.box((center.x+outward.x*0.14,center.y+outward.y*0.14,0),along,outward,pane_w-0.20,0.025,(zlo+zhi)/2-0.035,(zlo+zhi)/2+0.035,slot_index["frame"])
    # The attributed storefront photo shows the entry on the short face
    # adjoining the long glazed storefront (OSM way edge 0).
    front_i=0
    x,y=xy[front_i]; x2,y2=xy[(front_i+1)%n]
    front_axis=Vector((x2-x,y2-y,0)).normalized()
    front_normal=Vector((front_axis.y,-front_axis.x,0)) if ccw else Vector((-front_axis.y,front_axis.x,0))
    mid=(Vector((x,y,0))+Vector((x2,y2,0)))/2
    door_center=mid+front_normal*0.20
    b.box((door_center.x,door_center.y,0),front_axis,front_normal,2.15,0.12,0.0,2.65,slot_index["frame"])
    b.box((door_center.x+front_normal.x*0.08,door_center.y+front_normal.y*0.08,0),front_axis,front_normal,1.82,0.055,0.12,2.50,slot_index["door"])
    # Dark entry sign panel and the photographed "Welcome" legend.
    sign_center=mid+front_normal*0.14
    b.box((sign_center.x,sign_center.y,0),front_axis,front_normal,7.2,0.10,2.88,3.42,slot_index["brick"])
    # Small golden arches emblem on the storefront face; size/offset are estimated.
    sx,sy=xy[1]; ex,ey=xy[2]; d=Vector((ex-sx,ey-sy,0)); storefront_axis=d.normalized()
    storefront_normal=Vector((d.y,-d.x,0)).normalized() if ccw else Vector((-d.y,d.x,0)).normalized()
    panel_center=(Vector((sx,sy,0))+Vector((ex,ey,0)))/2
    b.box((panel_center.x+storefront_normal.x*0.16,panel_center.y+storefront_normal.y*0.16,0),storefront_axis,storefront_normal,3.4,0.12,2.72,3.42,slot_index["brick"])
    width,height=1.75,0.58; base_z=2.78
    def arch(cx):
        pts=[]
        for q in range(15):
            t=q/14; theta=math.pi*t
            xx=cx + (width/4)*math.cos(theta)
            zz=base_z + height*math.sin(theta)
            pts.append(Vector((panel_center.x+storefront_axis.x*xx+storefront_normal.x*0.68,panel_center.y+storefront_axis.y*xx+storefront_normal.y*0.68,zz)))
        for p,q in zip(pts,pts[1:]):
            perp=storefront_axis*0.10
            b.face((p-perp,q-perp,q+perp,p+perp),slot_index["gold"])
    arch(-width/4); arch(width/4)

    mesh=bpy.data.meshes.new("McDonalds_OSM_footprint_mesh")
    mesh.from_pydata(b.verts,[],b.faces); mesh.update()
    assign_material(mesh,[mats[k] for k in slot_names],b.materials)
    obj=bpy.data.objects.new(OBJECT_NAME,mesh); asset.objects.link(obj)
    obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
    # The source photo labels the entry canopy "Welcome". Convert the default
    # Blender text to mesh and join it so the export remains one portable mesh.
    curve=bpy.data.curves.new("MCD_Welcome_text_curve","FONT")
    curve.body="Welcome"; curve.size=0.62; curve.align_x="CENTER"; curve.extrude=0.012
    text_obj=bpy.data.objects.new("__mcd_welcome_text",curve); asset.objects.link(text_obj)
    text_basis=Matrix(((front_axis.x,0,front_normal.x),(front_axis.y,0,front_normal.y),(0,1,0)))
    text_obj.rotation_mode="QUATERNION"; text_obj.rotation_quaternion=text_basis.to_quaternion()
    text_obj.location=Vector((sign_center.x,sign_center.y,2.94))+front_normal*0.12
    text_obj.data.materials.append(mats["text"])
    bpy.context.view_layer.objects.active=text_obj
    text_obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    text_obj=bpy.context.object
    bpy.ops.object.select_all(action="DESELECT"); obj.select_set(True); text_obj.select_set(True); bpy.context.view_layer.objects.active=obj
    bpy.ops.object.join()
    obj["building_id"]="massing_mcdonald_s_ab77b70"
    obj["source_footprint"]="OpenStreetMap way 256640455; retrieved 2026-10-26; identity tags include McDonald's, 605 Stadium Avenue, and official store page"
    obj["footprint_status"]="Exact OSM way ring; Purdue BuildingShapesZip4 contains no separate matching McDonald's feature"
    obj["height_status"]="Estimated 4.70 m total; no measured elevation source"
    obj["floors_status"]="One visible story modeled as an estimate; exact McDonald's way has no building:levels tag"
    obj["coordinate_frame"]="Campus coordinates, identity transform; project approximate geographic conversion"

    # Produce a camera/lighting setup temporarily. Helpers are removed before
    # saving so the exported collection contains exactly one portable mesh.
    for datablock in list(bpy.data.objects):
        if datablock != obj and datablock.name not in {"Camera", "Light"}:
            # keep only the assigned mesh and remove legacy render/campus objects
            bpy.data.objects.remove(datablock, do_unlink=True)
    # Aim from outside the photographed corner so the entry face and long
    # glazed storefront are both visible in the audit render.
    def edge_outward(i):
        p=Vector((xy[i][0],xy[i][1],0)); q=Vector((xy[(i+1)%n][0],xy[(i+1)%n][1],0)); d=q-p
        return Vector((d.y,-d.x,0)).normalized() if ccw else Vector((-d.y,d.x,0)).normalized()
    corner=Vector((xy[1][0],xy[1][1],0)); corner_dir=(edge_outward(0)+edge_outward(1)).normalized()
    camera_location=corner+corner_dir*52+Vector((0,0,25))
    bpy.ops.object.camera_add(location=camera_location)
    cam=bpy.context.object; cam.name="__mcd_preview_camera"
    target=Vector((45.2,405.0,1.8)); direction=target-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler(); cam.data.type="ORTHO"; cam.data.ortho_scale=58
    scene.camera=cam
    for name,loc,power,size in (("__mcd_preview_key",(20,385,28),9000,18),("__mcd_preview_fill",(66,420,22),7000,15),("__mcd_preview_rim",(40,432,17),4500,12)):
        bpy.ops.object.light_add(type="AREA", location=loc); light=bpy.context.object; light.name=name; light.data.energy=power; light.data.shape="DISK"; light.data.size=size; light.rotation_euler=(Vector((45,405,0))-light.location).to_track_quat("-Z","Y").to_euler()
    scene.render.engine="BLENDER_EEVEE"; scene.render.resolution_x=1280; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.filepath=str(PREVIEW)
    scene.render.film_transparent=False
    scene.view_settings.exposure=0.2
    scene.view_settings.gamma=1.0
    scene.world.use_nodes=True
    scene.world.node_tree.nodes.get("Background").inputs[0].default_value=(0.50,0.52,0.56,1)
    scene.world.node_tree.nodes.get("Background").inputs[1].default_value=0.32
    bpy.ops.mesh.primitive_plane_add(size=180, location=(45.2,405.0,-0.10))
    ground=bpy.context.object
    ground.name="__mcd_ground_plane"
    ground.data.materials.append(new_material("MCD_preview_ground",(0.34,0.35,0.34,1)))
    bpy.ops.render.render(write_still=True)
    scene.camera=None
    remove_generated_helpers()
    # Remove all temporary camera and light objects and non-asset collections.
    for ob in list(bpy.data.objects):
        if ob != obj: bpy.data.objects.remove(ob,do_unlink=True)
    for coll in list(bpy.data.collections):
        if coll != asset and coll.name != "Collection":
            bpy.data.collections.remove(coll)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print(json.dumps({"asset":str(BLEND),"preview":str(PREVIEW),"ring_vertices":len(xy),"mesh_vertices":len(mesh.vertices),"mesh_faces":len(mesh.polygons),"collection":asset.name,"object":obj.name,"source_tags":source_tags},indent=2))

if __name__ == "__main__":
    main()

