import bpy,re,json
from pathlib import Path
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall'];P=bpy.data.filepath
# Remove the earlier six-pier run; round-four run replaces it on both long sides.
for o in list(C.objects):
 if o.name.startswith('HAAS_Estimated_Long_Facade_'):
  bpy.data.objects.remove(o,do_unlink=True)
# Shift five side-window sets to evenly spaced centers wholly within GIS envelope.
old=[-22.0,-16.0,-10.0,-4.0,1.0];new=[-22.8,-17.1,-11.4,-5.7,0.0]
for o in C.objects:
 if o.name.startswith('HAAS_Estimated_Side_'):
  mm=re.search(r'_S_(\d+)(?:_|$)',o.name)
  if mm and int(mm.group(1))<5:o.location.x+=new[int(mm.group(1))]-old[int(mm.group(1))]
# Keep far-side clones in sync with the adjusted source bays.
for o in C.objects:
 if '_N_' in o.name and '_R4' in o.name and o.name.startswith('HAAS_Estimated_Side_'):
  mm=re.search(r'_S_(\d+)(?:_|$)',o.name)
  if mm and int(mm.group(1))<5:o.location.x+=new[int(mm.group(1))]-old[int(mm.group(1))]
# Match visible masonry to the dark red-brown brick and pale cream limestone of the Purdue image.
for m in bpy.data.materials:
 if 'brick' in m.name.lower():
  m.diffuse_color=(.26,.065,.028,1)
  if m.use_nodes:
   p=m.node_tree.nodes.get('Principled BSDF')
   if p and not any(l.to_node==p and l.to_socket==p.inputs['Base Color'] for l in m.node_tree.links):p.inputs['Base Color'].default_value=(.26,.065,.028,1)
   for n in m.node_tree.nodes:
    if n.type=='TEX_BRICK':
     n.inputs['Color1'].default_value=(.29,.07,.03,1);n.inputs['Color2'].default_value=(.18,.038,.016,1);n.inputs['Mortar'].default_value=(.18,.115,.075,1)
 if any(t in m.name.lower() for t in ['limestone','bedford']):
  m.diffuse_color=(.90,.79,.59,1)
  if m.use_nodes:
   p=m.node_tree.nodes.get('Principled BSDF')
   if p and not any(l.to_node==p and l.to_socket==p.inputs['Base Color'] for l in m.node_tree.links):p.inputs['Base Color'].default_value=(.90,.79,.59,1)
# Roof courses need to be larger and darker; reduce fine bump so the broad roof reads as terracotta tile.
r=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];r.diffuse_color=(.07,.014,.006,1)
for n in r.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.065,.013,.006,1);n.inputs['Color2'].default_value=(.038,.007,.003,1);n.inputs['Mortar'].default_value=(.020,.004,.002,1);n.inputs['Brick Width'].default_value=.62;n.inputs['Row Height'].default_value=.25;n.inputs['Mortar Size'].default_value=.006
 if n.type=='BUMP':n.inputs['Strength'].default_value=.14;n.inputs['Distance'].default_value=.003
# Correct tiny end-face offsets so overlays intersect the GIS wall instead of hovering beside it.
for o in C.objects:
 if o.name.startswith('HAAS_R4_West_'):o.location.x+=.04
bpy.ops.wm.save_as_mainfile(filepath=P)
Path('audit/batch3_haas/round4_material_geometry_fix.json').write_text(json.dumps({'old_long_facade_pi ers_removed':True,'window_bay_centers_m':new,'far_side_bays_updated':True,'brick_tone':'dark red-brown; per node and material', 'limestone_tone':'warm pale cream', 'roof_tile_pattern':'larger 0.62m x 0.25m procedural courses with reduced bump contrast', 'west_overlays':'shifted 0.04m inward to intersect GIS shell'},indent=2))
