import bpy,json
from pathlib import Path
m=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_estimated')
if m:
 m.diffuse_color=(0.07,0.012,0.004,1)
 for n in m.node_tree.nodes:
  if n.type=='TEX_BRICK':
   n.inputs['Color1'].default_value=(0.065,0.010,0.0035,1)
   n.inputs['Color2'].default_value=(0.038,0.0055,0.0018,1)
   n.inputs['Mortar'].default_value=(0.025,0.0035,0.0012,1)
  if n.type=='BUMP':n.inputs['Strength'].default_value=0.06
  if n.type=='BSDF_PRINCIPLED':n.inputs['Roughness'].default_value=0.91
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
Path('audit/batch3_haas/round8_changes.json').write_text(json.dumps({'roof_material_tuned':'Moderated the overly salmon result from first round-eight lighting; roof tile scale and silhouette remain estimates.'},indent=2),encoding='utf-8')
print('R8_ROOF_TUNED')
