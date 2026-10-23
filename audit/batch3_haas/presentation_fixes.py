import bpy, math, json
from pathlib import Path
C=bpy.data.collections['Asset_felix_haas_hall']; p=bpy.data.filepath
def box(name,loc,dims,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.data.materials.append(material);return o
stone=bpy.data.materials['HAAS_Photo_Limestone'];glass=bpy.data.materials['HAAS_Photo_BlueGlass']
stone.diffuse_color=(.69,.61,.47,1);stone.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.69,.61,.47,1)
brick=bpy.data.materials.get('Purdue_Red_Brick.001')
if brick:
 brick.diffuse_color=(.52,.205,.105,1)
 for n in brick.node_tree.nodes:
  if n.type=='TEX_BRICK':
   n.inputs['Color1'].default_value=(.52,.205,.105,1);n.inputs['Color2'].default_value=(.38,.125,.065,1);n.inputs['Mortar'].default_value=(.28,.16,.11,1)
  if n.type=='BUMP':n.inputs['Strength'].default_value=.1;n.inputs['Distance'].default_value=.0008
roof=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_estimated')
if roof:
 roof.diffuse_color=(.065,.008,.003,1)
 for n in roof.node_tree.nodes:
  if n.type=='TEX_BRICK':
   n.inputs['Color1'].default_value=(.085,.012,.004,1);n.inputs['Color2'].default_value=(.048,.006,.002,1);n.inputs['Mortar'].default_value=(.035,.007,.003,1)
for o in list(C.objects):
 if o.name.startswith(('HAAS_Photo_Visible_Arch_','HAAS_Photo_Visible_Arched_Glass')):
  bpy.data.objects.remove(o,do_unlink=True)
for i,y in enumerate((-7.65,7.65)):
 box('HAAS_Photo_Visible_Arched_Glass_%02d'%i,(13.32,y,3.0),(.055,2.65,2.65),glass)
 for dy in (-1.42,1.42):box('HAAS_Photo_Visible_Arch_Jamb_%02d_%s'%(i,str(dy)),(13.38,y+dy,3.0),(.16,.14,2.9),stone)
 box('HAAS_Photo_Visible_Arch_Sill_%02d'%i,(13.38,y,1.55),(.16,2.98,.16),stone)
 cu=bpy.data.curves.new('HAAS Front Arched Head','CURVE');cu.dimensions='3D';cu.bevel_depth=.09;cu.bevel_resolution=3
 sp=cu.splines.new('POLY');sp.points.add(24)
 for k,pnt in enumerate(sp.points):
  t=math.pi*k/24;pnt.co=(13.4,y+1.32*math.cos(t),4.1+.52*math.sin(t),1)
 ob=bpy.data.objects.new('HAAS_Photo_Visible_Arch_Head_%02d'%i,cu);C.objects.link(ob);cu.materials.append(stone)
for o in C.objects:
 if o.name.startswith('HAAS_Plan_Label_'):
  o.data.size=.92;o.location.z=3.45
  m=o.data.materials[0];m.diffuse_color=(.96,.91,.74,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.96,.91,.74,1)
bpy.ops.wm.save_as_mainfile(filepath=p)
Path('audit/batch3_haas/presentation_fixes.json').write_text(json.dumps({'saved':True,'notes':'Front arched glazing placed on outer face so GIS shell does not obscure it; brick simplified and lightened; roof darkened and warmed; plan labels brightened for readability.'},indent=2))
