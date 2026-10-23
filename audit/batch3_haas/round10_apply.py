import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('modular/buildings/felix_haas_hall.blend')
# Keep a recoverable round-nine baseline before round-ten edits.
bpy.ops.wm.save_as_mainfile(filepath='audit/batch3_haas/felix_haas_hall_round9_backup.blend')
C=bpy.data.collections['Asset_felix_haas_hall']; removed=[]
# The north/west second beltcourse is a pale unsupported projection on the end view.
A=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
if not A:A=bpy.data.collections.new('Reference_Incompatible_Geometry_felix_haas_hall');bpy.context.scene.collection.children.link(A)
for name in ['HAAS_Beltcourse2_North','HAAS_Beltcourse2_West']:
 o=bpy.data.objects.get(name)
 if o:
  removed.append(name)
  for col in list(o.users_collection):col.objects.unlink(o)
  A.objects.link(o);o.hide_render=True
A.hide_render=True;A.hide_viewport=True
# Increase only the narrow in-plane dimension of each independent masonry bar.
# Preserve shell extents and clamp inlay tips to the GIS footprint. Each group of 8
# vertices is the front/back pair of one quad converted to an individual solid prism.
expanded={}
for name,factor in [('HAAS_R7_EastFacade_Inlaid_Brickwork',1.35),('HAAS_R8_EastWing_Brick_Inlays_EST',1.55)]:
 o=bpy.data.objects[name];me=o.data;verts=me.vertices;groups=0
 for start in range(0,len(verts),8):
  block=verts[start:start+8]
  ys=[v.co.y for v in block];zs=[v.co.z for v in block]
  yc=(min(ys)+max(ys))/2;zc=(min(zs)+max(zs))/2
  dy=max(ys)-min(ys);dz=max(zs)-min(zs)
  if dy<=dz:
   for v in block:v.co.y=max(-25.9795,min(26.7597,yc+(v.co.y-yc)*factor))
  else:
   for v in block:v.co.z=zc+(v.co.z-zc)*factor
  groups+=1
 me.update();expanded[name]={'prism_groups':groups,'narrow_axis_factor':factor}
 o['round10_masonry']='Widened only the narrow face dimension of sourced-photo-derived red masonry surround bars; geometry remains estimated and within GIS plan envelope.'
# Make roof lighting less directional while keeping the red tile color signal; preserve tile texture.
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
for n in m.node_tree.nodes:
 if n.type=='BSDF_PRINCIPLED':
  n.inputs['Emission Color'].default_value=(0.07,0.012,0.004,1)
  n.inputs['Emission Strength'].default_value=0.65
  n.inputs['Roughness'].default_value=0.98
C['round10_changes']='Widened east brick surround bars modestly, archived unsupported north/west beltcourse trim, and added stronger low-red emission to reduce directional roof facet contrast. GIS shell unchanged; roof height/profile remain estimated.'
Path('audit/batch3_haas/round10_changes.json').write_text(json.dumps({'archived_north_west_beltcourse_projection':removed,'brick_bar_expansion':expanded,'roof_emission_strength':0.65,'roof_roughness':0.98,'gis_shell_vertices_moved':False},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(P))
print('ROUND10',removed,expanded)
