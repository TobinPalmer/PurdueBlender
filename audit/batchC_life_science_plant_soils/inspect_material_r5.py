import bpy
f=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\life_science_plant_and_soils_laboratory.blend'; bpy.ops.wm.open_mainfile(filepath=f)
for n in ['LSPS | schematic clear facade glazing','LSPS | greenhouse clear glazing','LSPS | charcoal anodized metal']:
 m=bpy.data.materials[n]; print('\n',n, 'blend',getattr(m,'blend_method','n/a'),'surface',getattr(m,'surface_render_method','n/a'))
 for node in m.node_tree.nodes:
  if node.type in ('BSDF_PRINCIPLED','MIX_SHADER','BSDF_TRANSPARENT','OUTPUT_MATERIAL'):
   vals=[]
   for i in node.inputs:
    if hasattr(i,'default_value') and not i.is_linked:
     v=i.default_value
     try:v=tuple(round(float(x),3) for x in v)
     except TypeError: pass
     vals.append((i.name,v))
   print(node.type,vals[:15])
