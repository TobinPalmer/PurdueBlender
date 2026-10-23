import bpy
from pathlib import Path
P=bpy.data.filepath;C=bpy.data.collections['Asset_felix_haas_hall']
roof=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];roof.diffuse_color=(.03,.005,.002,1)
for n in roof.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.030,.0045,.0018,1);n.inputs['Color2'].default_value=(.017,.0022,.0008,1);n.inputs['Mortar'].default_value=(.007,.001,.0004,1)
 if n.type=='BUMP':n.inputs['Strength'].default_value=.08;n.inputs['Distance'].default_value=.0018
 if n.type=='BSDF_PRINCIPLED':
  n.inputs['Roughness'].default_value=.94
  if 'Specular IOR Level' in n.inputs:n.inputs['Specular IOR Level'].default_value=.06
  if 'Metallic' in n.inputs:n.inputs['Metallic'].default_value=0.0
# Make the plan legend readable at the full 1600 px render size.
plate=bpy.data.objects['HAAS_Plan_Evidence_Legend_Plate'];plate.dimensions=(16.4,3.35,.08);bpy.ops.object.select_all(action='DESELECT');plate.select_set(True);bpy.context.view_layer.objects.active=plate;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);plate.location.y=-18.9
text=bpy.data.objects['HAAS_Plan_Evidence_Legend_Text'];text.data.body='PLAN SOURCE: room names and broad adjacency\nESTIMATED: room sizes and placement\nESTIMATED: doors, wall heights, circulation and furniture';text.data.size=.50;text.location=(2.35,-17.55,4.04)
ink=bpy.data.materials['HAAS_Plan_Label_Ink'];ink.diffuse_color=(.005,.005,.005,1)
if ink.use_nodes:ink.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.005,.005,.005,1)
bpy.ops.wm.save_as_mainfile(filepath=P)
