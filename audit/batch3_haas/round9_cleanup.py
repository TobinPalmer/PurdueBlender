import bpy,json
from pathlib import Path
from mathutils import Vector
path=Path('modular/buildings/felix_haas_hall.blend')
bpy.ops.wm.save_as_mainfile(filepath='audit/batch3_haas/felix_haas_hall_round9_before_cleanup.blend')
C=bpy.data.collections['Asset_felix_haas_hall']; removed=[]; fonts=[]
# Side window schedules are inferred only, and these strips/arches overshoot the GIS shell.
for o in list(C.objects):
 if o.name.startswith(('HAAS_Estimated_Side_Arch_','HAAS_Estimated_Side_Upper_Jamb_')) or o.name.startswith('HAAS_R4_West_Upper'):
  removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)
# Remove identified unsupported floating formula labels from visible/renderable collections.
A=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
if not A:
 A=bpy.data.collections.new('Reference_Incompatible_Geometry_felix_haas_hall'); bpy.context.scene.collection.children.link(A)
for n in ['HAAS_Algorithm_1','HAAS_Algorithm_2','HAAS_Algorithm_3']:
 o=bpy.data.objects.get(n)
 if o:
  fonts.append(n)
  for col in list(o.users_collection): col.objects.unlink(o)
  A.objects.link(o);o.hide_render=True
A.hide_render=True;A.hide_viewport=True
# Soften the roof texture's bump response, which was exaggerating tile-to-tile contrast.
m=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_estimated')
if m and m.use_nodes:
 for n in m.node_tree.nodes:
  if n.type=='BUMP': n.inputs['Strength'].default_value=0.004; n.inputs['Distance'].default_value=0.00035
  elif n.type=='BSDF_PRINCIPLED':
   if 'Emission Color' in n.inputs: n.inputs['Emission Color'].default_value=(0.07,0.012,0.004,1)
   if 'Emission Strength' in n.inputs: n.inputs['Emission Strength'].default_value=0.12
C['round9_cleanup']='Removed unsupported estimated side arch and upper-jamb overlays extending beyond GIS shell; archived and render-hidden floating algorithm labels; reduced roof bump and added low warm emission for more even roof-plane color. GIS wall shell untouched.'
Path('audit/batch3_haas/round9_cleanup.json').write_text(json.dumps({'removed_estimated_side_overlays':removed,'archived_formula_labels':fonts,'gis_shell_vertices_moved':False,'roof_bump_strength':0.004,'roof_bump_distance':0.00035,'roof_emission_strength':0.12},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(path))
print('CLEANUP',len(removed),removed,len(C.objects),len(fonts))
