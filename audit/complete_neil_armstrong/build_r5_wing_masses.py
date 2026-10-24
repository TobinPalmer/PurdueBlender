"""Add only coarse, source-derived wing envelope masses to Neil's asset."""
import bpy, json, hashlib, os
from mathutils import Matrix

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET = os.path.join(ROOT, "modular", "buildings", "neil_armstrong_hall.blend")
OUT = os.path.join(ROOT, "audit", "complete_neil_armstrong")
ZONES = os.path.join(OUT, "sources", "lidar_wing_zones_r5.json")
EXPECTED = "ce7660ebca1144dd72dee106ae0ddf9b9ce8336a58768bf3d3d31bc106456ecb"

with open(ASSET, "rb") as f:
    before = hashlib.sha256(f.read()).hexdigest()

bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
collection = bpy.data.collections.get("Asset_neil_armstrong_hall")
root = bpy.data.objects.get("AssetRoot_neil_armstrong_hall")
if not collection or not root or scene.name != "Building_neil_armstrong_hall":
    raise RuntimeError("Unexpected building asset identity")
if tuple(root.location) != (0.0, 0.0, 0.0):
    raise RuntimeError("Unexpected source asset state")
# Rebuild safely from either the unchanged R4 source or our previous R5 output.
for name in ["ARMS_R5_Coarse_LiDAR_wing_low", "ARMS_R5_Coarse_LiDAR_wing_mid", "ARMS_R5_Coarse_LiDAR_roof_high"]:
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
if len(collection.objects) != 444:
    raise RuntimeError(f"Expected original 444-object collection after R5 cleanup, got {len(collection.objects)}")

with open(ZONES, encoding="utf-8") as f:
    data = json.load(f)
material = bpy.data.materials.get("ARMS_Purdue_Red_Brick")
if material is None:
    raise RuntimeError("Source-supported Purdue brick material missing")

def mesh_for_feature(feature):
    props = feature["properties"]
    z = float(props["median_top_height_m"])
    verts, faces = [], []
    def vid(x, y, height, lookup):
        key = (round(float(x), 5), round(float(y), 5), round(float(height), 5))
        if key not in lookup:
            lookup[key] = len(verts)
            verts.append(key)
        return lookup[key]
    for part in props["parts"]:
        # Keep disconnected polygons as separate closed shells. If two
        # raster components only touch at a point, sharing a vertex would
        # make a 4-face nonmanifold edge even though the geometry is valid.
        lookup, boundary = {}, {}
        for tri in part["triangles"]:
            top = [vid(x, y, z, lookup) for x, y in tri]
            bottom = [vid(x, y, 0.04, lookup) for x, y in tri]
            faces.append(tuple(top))
            faces.append(tuple(reversed(bottom)))
            for i, a in enumerate(tri):
                b = tri[(i + 1) % 3]
                key = tuple(sorted(((round(a[0], 5), round(a[1], 5)),
                                    (round(b[0], 5), round(b[1], 5)))) )
                boundary[key] = boundary.get(key, 0) + 1
        # The triangulated cap may subdivide simplified perimeter edges
        # differently from the polygon rings; derive sides from cap boundary
        # edges so every shell edge shares exact cap vertices.
        for key, count in boundary.items():
            if count != 1:
                continue
            a, b = key
            faces.append((vid(a[0], a[1], 0.04, lookup), vid(b[0], b[1], 0.04, lookup),
                          vid(b[0], b[1], z, lookup), vid(a[0], a[1], z, lookup)))
    dedup, seen = [], set()
    for face in faces:
        key = tuple(sorted(face))
        if key not in seen:
            seen.add(key)
            dedup.append(face)
    me = bpy.data.meshes.new("R5_NDHM_Coarse_Wing_Mass_Mesh")
    me.from_pydata(verts, [], dedup)
    me.materials.append(material)
    me.update()
    # Ensure consistent outward normals on the closed envelope shells.
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()
    return me

names = []
for feature in data["features"]:
    cls = feature["properties"]["class"]
    name = "ARMS_R5_Coarse_LiDAR_" + cls
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    obj = bpy.data.objects.new(name, mesh_for_feature(feature))
    collection.objects.link(obj)
    # Vertices are already in the building-local meter frame. Keep the root and
    # other assets untouched, while making the new geometry an identity child.
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = (0.0, 0.0, 0.0)
    obj["evidence_status"] = "schematic_source_derived_envelope"
    obj["height_source"] = "Indiana 3DEP / Purdue Digital Forestry 2018 Tippecanoe NDHM"
    obj["height_source_crs_units"] = "EPSG:2968; US survey feet converted to meters"
    obj["height_band_m"] = feature["properties"]["ndhm_threshold_m"]
    obj["modeled_top_height_m"] = feature["properties"]["median_top_height_m"]
    obj["height_samples"] = feature["properties"]["sample_cells_outside_shell"]
    obj["footprint_basis"] = "Official Purdue GIS BuildingShapesZip4 feature FID 642"
    obj["uncertainty"] = "Coarse connected wing mass only; does not claim floor plans, room arrangement, facade openings, parapets or roof profile."
    names.append(name)

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(json.dumps({"saved": ASSET, "objects_added": names,
                  "collection_object_count": len(collection.objects),
                  "sha256_before": before}, indent=2))
