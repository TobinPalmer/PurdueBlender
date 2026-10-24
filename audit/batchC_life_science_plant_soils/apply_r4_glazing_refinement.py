import bpy
ASSET=r"C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap\\modular\\buildings\\life_science_plant_and_soils_laboratory.blend"
bpy.ops.wm.open_mainfile(filepath=ASSET)
for name,color,metal,rough,opacity in [("LSPS | schematic clear facade glazing",(.055,.085,.095),.32,.21,.92),("LSPS | greenhouse clear glazing",(.14,.21,.20),.28,.25,.82)]:
 m=bpy.data.materials[name]; b=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value=(*color,1); b.inputs["Metallic"].default_value=metal; b.inputs["Roughness"].default_value=rough; mix=next(n for n in m.node_tree.nodes if n.type=="MIX_SHADER"); mix.inputs["Factor"].default_value=opacity; m["r4_source_basis"]="Qualitative Purdue/GIS and August 2019 Google Street View glazing cue: darker reflective glazing; exact color/reflectance is estimated."
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("Saved R4 glazing contrast",ASSET)
