"""Add one photo-supported upper facade band and finish the lidar roof zone."""
import bpy, json, hashlib, os
from mathutils import Matrix

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET = os.path.join(ROOT, "modular", "buildings", "neil_armstrong_hall.blend")
OUT = os.path.join(ROOT, "audit", "complete_neil_armstrong")
R5 = os.path.join(OUT, "validation_r5.json")
with open(R5, encoding="utf-8") as f: r5 = json.load(f)
with open(ASSET, "rb") as f: before = hashlib.sha256(f.read()).hexdigest()
if before != r5["asset_sha256"]:
    raise RuntimeError("Neil asset no longer matches the validated R5 source")

bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
col = bpy.data.collections.get("Asset_neil_armstrong_hall")
root = bpy.data.objects.get("AssetRoot_neil_armstrong_hall")
if scene.name != "Building_neil_armstrong_hall" or col is None or root is None or len(col.objects) != 447:
    raise RuntimeError("Unexpected Neil source state")

# The photo record is geotagged northwest of the building; its visible view
# shows red brick walls, a continuous upper strip of glazing, an atrium curtain
# wall, and the dark red wing roof. It gives a directional cue but no camera
# bearing or measured wall registration, so this is a qualitative treatment.
brick = bpy.data.materials["ARMS_Purdue_Red_Brick"]
glass = bpy.data.materials["ARMS_Solar_Curtain_Glass"]
steel = bpy.data.materials["ARMS_Mullion_Steel"]
acm = bpy.data.materials["ARMS_Mayflower_Red_ACM"]

roof = bpy.data.objects["ARMS_R5_Coarse_LiDAR_roof_high"]
if acm.name not in [m.name for m in roof.data.materials if m]:
    roof.data.materials.append(acm)
acm_index = next(i for i, m in enumerate(roof.data.materials) if m and m.name == acm.name)
top_z = float(roof.get("modeled_top_height_m"))
for poly in roof.data.polygons:
    if all(abs(roof.data.vertices[i].co.z - top_z) < 1e-4 for i in poly.vertices):
        poly.material_index = acm_index
roof["roof_finish_note"] = "Mayflower Red ACM assigned to upper LiDAR roof zone as a qualitative finish cue; source documents this cladding on the high roof, but its exact plan boundary is not registered."

# Add a qualitative clerestory-style band to the candidate north-side edge of
# the coarse wing envelope. The geotag lies northwest of the GIS outline, and
# the existing local frame is north-oriented, but the photo has no bearing;
# the exact facade assignment therefore remains uncertain. The 5-ft NDHM mask
# supplies approximate plan limits only, not a measured window schedule.
for name in ("ARMS_R6_North_Clerestory_Glass", "ARMS_R6_North_Clerestory_Mullions"):
    if bpy.data.objects.get(name):
        raise RuntimeError("R6 facade geometry already exists; refusing duplicate build")

def box_mesh(name, boxes, material):
    verts, faces = [], []
    for cx, cy, cz, sx, sy, sz in boxes:
        x0, x1 = cx-sx/2, cx+sx/2
        y0, y1 = cy-sy/2, cy+sy/2
        z0, z1 = cz-sz/2, cz+sz/2
        base = len(verts)
        verts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                      (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
        faces.extend([(base+0,base+3,base+2,base+1),(base+4,base+5,base+6,base+7),
                      (base+0,base+1,base+5,base+4),(base+1,base+2,base+6,base+5),
                      (base+2,base+3,base+7,base+6),(base+3,base+0,base+4,base+7)])
    mesh = bpy.data.meshes.new(name+"_Mesh")
    mesh.from_pydata(verts, [], faces); mesh.materials.append(material); mesh.update()
    obj = bpy.data.objects.new(name, mesh); col.objects.link(obj)
    obj.parent = root; obj.matrix_parent_inverse = Matrix.Identity(4); obj.location = (0,0,0)
    return obj

facade_x_min, facade_x_max = -35.6, 22.3
facade_y = 17.24
z_bottom, z_top = 13.2, 14.75
panel_count = 22
pitch = (facade_x_max-facade_x_min)/panel_count
panel_width = pitch - .30
glass_boxes=[]
for i in range(panel_count):
    cx = facade_x_min + pitch*(i+.5)
    glass_boxes.append((cx, facade_y, (z_bottom+z_top)/2, panel_width, .05, z_top-z_bottom))
glass_obj = box_mesh("ARMS_R6_North_Clerestory_Glass", glass_boxes, glass)
glass_obj["source_basis"] = "Geotagged Commons 2016-03 exterior image shows an upper horizontal glazing band above red-brick facade. Added to the candidate north-side edge of the GIS-aligned envelope as a qualitative interpretation; camera bearing is unavailable."
glass_obj["registration_uncertainty"] = "The geotag places the camera northwest of the footprint, but photo bearing, focal calibration, exact facade assignment and band dimensions are unavailable; location/size are schematic and should not be read as a registered elevation."
glass_obj["evidence_url"] = "https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_03.jpg"

bar_boxes=[]
bar_y=17.30
bar_width=.09
for i in range(panel_count+1):
    cx=facade_x_min+pitch*i
    bar_boxes.append((cx,bar_y,(z_bottom+z_top)/2,bar_width,.10,z_top-z_bottom+.08))
bar_boxes.extend([
    ((facade_x_min+facade_x_max)/2,bar_y,z_bottom,(facade_x_max-facade_x_min)+.08,.10,.09),
    ((facade_x_min+facade_x_max)/2,bar_y,z_top,(facade_x_max-facade_x_min)+.08,.10,.09),
])
bars=box_mesh("ARMS_R6_North_Clerestory_Mullions",bar_boxes,steel)
bars["source_basis"]="Photo-supported narrow dark mullions and continuous horizontal clerestory band; spacing is an illustrative design rhythm, not a measured window schedule."
bars["evidence_url"]="https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_03.jpg"

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(json.dumps({"asset":ASSET,"objects_added":[glass_obj.name,bars.name],
                  "collection_count":len(col.objects),"roof_material":"ARMS_Mayflower_Red_ACM",
                  "window_panels":panel_count,"north_band_bounds_m":[facade_x_min,facade_x_max,facade_y,z_bottom,z_top],
                  "sha256_before":before},indent=2))
