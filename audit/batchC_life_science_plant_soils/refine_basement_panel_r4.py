import bpy
ASSET=r"C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap\\modular\\buildings\\life_science_plant_and_soils_laboratory.blend"
bpy.ops.wm.open_mainfile(filepath=ASSET)
m=bpy.data.materials["LSPS | R3 insulated cold-room panels"]; m.diffuse_color=(.44,.49,.50,1); m.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value=(.44,.49,.50,1)
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("Saved basement panel contrast")
