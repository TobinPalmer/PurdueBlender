import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
for name in ['LSPS | schematic clear facade glazing','LSPS | greenhouse clear glazing']:
 m=bpy.data.materials[name];n=next(n for n in m.node_tree.nodes if n.type=='MIX_SHADER');print(name,[(i.name,getattr(i,'default_value',None)) for i in n.inputs])

