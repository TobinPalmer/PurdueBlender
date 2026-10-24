import bpy
from pathlib import Path

PROJECT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = PROJECT / "modular/buildings/hovde_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

COLLECTION = bpy.data.collections["Asset_hovde_hall"]
ROOT = bpy.data.objects["HOVD_Root"]

# The 2016 geotagged front photograph clearly shows six Corinthian supports.
# Round 8 removed the two middle supports, so restore them from the surviving
# column assemblies and lay out all six at an even cadence across the portico.
# Image-proportion measurement: the stone front spans about 0.25 of the
# 70 m facade in the near-frontal 2016 photo. The six shafts fill most of it.
centers = [-8.355, -5.115, -1.875, 1.365, 4.605, 7.845]
parts = (
    "HOVD_Classical_Column_",
    "HOVD_Column_Base_",
    "HOVD_Column_Capital_",
    "HOVD_Column_FluteCollar_Base_",
    "HOVD_Column_FluteCollar_Capital_",
)
for prefix in parts:
    # Restore missing positions 3 and 4 before applying the final six-column rhythm.
    for new_index, source_index in ((3, 2), (4, 5)):
        new_name = prefix + str(new_index)
        if bpy.data.objects.get(new_name):
            continue
        src = bpy.data.objects[prefix + str(source_index)]
        obj = src.copy()
        obj.data = src.data
        obj.name = new_name
        obj.parent = ROOT
        for col in src.users_collection:
            col.objects.link(obj)
    for i, y in enumerate(centers, 1):
        obj = bpy.data.objects.get(prefix + str(i))
        if obj:
            obj.location.y = y
            # The surviving round-8 shafts are smaller than the photo's column
            # rhythm; restore a plausible limestone column diameter.
            xy = max(obj.dimensions.x, obj.dimensions.y)
            threshold = {
                "HOVD_Classical_Column_": 0.9,
                "HOVD_Column_Base_": 1.4,
                "HOVD_Column_Capital_": 1.4,
                "HOVD_Column_FluteCollar_Base_": 1.05,
                "HOVD_Column_FluteCollar_Capital_": 1.05,
            }[prefix]
            if xy < threshold:
                obj.scale.x *= 1.25
                obj.scale.y *= 1.25

# Distinguish the stone layers subtly while retaining shared, portable materials.
limestone = bpy.data.materials["Bedford_Indiana_Limestone"]
trim = bpy.data.materials.get("Hovde_Limestone_Trim")
if trim is None:
    trim = limestone.copy()
    trim.name = "Hovde_Limestone_Trim"
    trim.diffuse_color = (0.69, 0.655, 0.59, 1)
    if trim.use_nodes:
        bsdf = next((n for n in trim.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.69, 0.655, 0.59, 1)
            bsdf.inputs["Roughness"].default_value = 0.68

# The original front photograph documents warm terracotta roof tile and red brick.
# Soften the brick contrast without changing its measured-looking physical course size.
brick = bpy.data.materials["Purdue_Red_Brick"]
if brick.use_nodes:
    for node in brick.node_tree.nodes:
        if node.type == "TEX_BRICK":
            node.inputs["Color1"].default_value = (0.29, 0.070, 0.035, 1)
            node.inputs["Color2"].default_value = (0.245, 0.055, 0.028, 1)
            node.inputs["Mortar"].default_value = (0.115, 0.085, 0.067, 1)

# Lift window tone toward the blue-gray reflections seen in the source photo.
for mat_name in ("Hovde_Bankers_Green_Glass", "Solar_Ribbon_Glass"):
    mat = bpy.data.materials.get(mat_name)
    if mat and mat.use_nodes:
        bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.15, 0.235, 0.27, 1)
            bsdf.inputs["Roughness"].default_value = 0.15

# Keep the center entry legible in the oblique view: the tympanum gains modest
# depth so its edge reads as stone construction rather than a paper-thin overlay.
pediment = bpy.data.objects["HOVD_Portico_Pediment_Base"]
pediment.scale.y = 0.2904

# Match the photo-derived portico-to-façade proportion while retaining its center.
# These four parts are authored with their long axis on local X and rotated 90°.
portico_width_scales = {
    "HOVD_Portico_Cornice": 0.9366,
    "HOVD_Portico_Entablature": 0.9597,
    "HOVD_Portico_Pediment_Base": 1.3146,
    "HOVD_Portico_Pediment_Crown": 1.1088,
}
for name, scale_x in portico_width_scales.items():
    bpy.data.objects[name].scale.x = scale_x

# Use the slightly lighter stone on the cornice and crown to show member joints.
for name in ("HOVD_Portico_Cornice", "HOVD_Portico_Pediment_Crown"):
    obj = bpy.data.objects[name]
    if obj.data.materials:
        obj.data.materials[0] = trim

bpy.context.view_layer.update()
assert len([1 for i in range(1, 7) if bpy.data.objects.get("HOVD_Classical_Column_" + str(i))]) == 6
assert all(bpy.data.objects.get(prefix + str(i)) for prefix in parts for i in range(1, 7))
assert tuple(round(v, 3) for v in ROOT.location) == (-62.85, 93.0, 0.0)
assert round(ROOT.rotation_euler.z, 6) == 0.689754

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print("ROUND9_SAVED", ASSET)
print("Six source-backed columns at", centers)
print("Root transform preserved", tuple(ROOT.location), tuple(ROOT.rotation_euler), tuple(ROOT.scale))
