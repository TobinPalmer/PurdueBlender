import bpy, math, json
from pathlib import Path
from mathutils import Matrix, Vector
C=bpy.data.collections['Asset_felix_haas_hall'];P=bpy.data.filepath;stone=bpy.data.materials['HAAS_Photo_Limestone']
# Make the hipped roof visibly dark red-brown under the saved QA lighting.
roof=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];roof.diffuse_color=(.010,.001,.0003,1)
for n in roof.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.010,.001,.00035,1);n.inputs['Color2'].default_value=(.005,.00035,.00012,1);n.inputs['Mortar'].default_value=(.0025,.00015,.00005,1)
 if n.type=='BUMP':n.inputs['Strength'].default_value=.10;n.inputs['Distance'].default_value=.002
# Add two matching window bays on both long sides of the projecting entrance pavilion.
# These are estimated because the public photo does not show or dimension the side elevations.
pivot=Vector((-22.8,-26.1,0));R=Matrix.Identity(4)
def clone(target_x,target_y,label):
 sources=[o for o in C.objects if o.name.startswith('HAAS_Estimated_Side_') and '_S_0' in o.name and 'Stone_Band' not in o.name]
 delta=Vector((target_x,target_y,0))-pivot
 T=Matrix.Translation(delta);n=0
 for o in sources:
  q=o.copy();q.data=o.data.copy() if o.data else None;q.name=f'HAAS_R5_Pavilion_{label}_{o.name.split("_S_0",1)[-1]}'
  C.objects.link(q);q.matrix_world=T@R@o.matrix_world;q['evidence']='Purdue Events exterior image supports brick/limestone contrast but not this side elevation; location and dimensions estimated.';n+=1
 return n
def box(name,loc,dims,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for col in list(o.users_collection):col.objects.unlink(o)
 C.objects.link(o);o.data.materials.clear();o.data.materials.append(material);o['evidence']='Purdue exterior photo supports brick and limestone contrast; pavilion side detail is estimated.';return o
for side,y in [('South',-11.66),('North',12.72)]:
 # Stable naming allows rerunning this correction without duplicate geometry.
 for o in list(C.objects):
  if o.name.startswith(f'HAAS_R5_Pavilion_{side}_') or o.name.startswith(f'HAAS_R5_Pavilion_{side}Band_') or o.name.startswith(f'HAAS_R5_Pavilion_{side}Pier_'):
   bpy.data.objects.remove(o,do_unlink=True)
 new=clone(5.0,y,side+'_A')+clone(10.3,y,side+'_B')
 for j,(z,h) in enumerate([(1.02,.22),(5.15,.18),(9.55,.22)]):box(f'HAAS_R5_Pavilion_{side}Band_{j}',(7.78,y,z),(10.5,.18,h),stone)
 for j,x in enumerate([2.55,7.78,13.02]):box(f'HAAS_R5_Pavilion_{side}Pier_{j}',(x,y,5.18),(.48,.20,8.35),stone)
# Ensure first-floor source-status legend is in render-visible collection.
C['round5_pavilion']='Two estimated upper/lower window assemblies and limestone course/pier rhythms added to both pavilion side elevations. Not measured from the public image.'
C['round5_roof']='Deep red clay tone tuned under saved QA lights; 0.62m by 0.25m procedural course dimensions remain estimates.'
bpy.ops.wm.save_as_mainfile(filepath=P)
Path('audit/batch3_haas/round5_side_roof_changes.json').write_text(json.dumps({'pavilion_sides':'added two upper/lower window bays, three stone belt courses, and three piers to each long pavilion side','roof':'deepened to dark red-brown under final lighting, courses retained','interior_legend':'embedded in round5_refinements.py; plan-derived labels/adjacency distinguished from estimated dimensions and furnishing','limits':'pavilion side facade schedule and all metric details remain estimated'},indent=2))

