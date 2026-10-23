import bpy,os,json
p=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=p)
for n in ['RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions']:
 bpy.data.objects[n].location.y=.08
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.22,.36,.44,1);bs.inputs['Roughness'].default_value=.12;bs.inputs['Metallic'].default_value=.08;bs.inputs['Transmission Weight'].default_value=.16;bs.inputs['Alpha'].default_value=1;bs.inputs['IOR'].default_value=1.45
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.32;bs.inputs['Coat Roughness'].default_value=.13
if 'Emission Color' in bs.inputs:bs.inputs['Emission Color'].default_value=(.14,.23,.30,1);bs.inputs['Emission Strength'].default_value=.02
m.diffuse_color=(.22,.36,.44,1)
bpy.ops.wm.save_as_mainfile(filepath=p)
# update change record
with open('audit/batch4_rawls/round4_model_changes.json','w') as f:json.dump({'asset':p,'north_glass_and_mullions_world_Y':.08,'facade_measurement':'Masonry outer plane follows x=-21.394,y=20.193 to x=33.333,y=20.790; inner plane x=-21.040,y=19.847 to x=32.983,y=20.437. Glass vertices slope with the same façade. Offset +0.08 m puts panes close to the measured outer reveal: about 0.03m projection for north pane center, avoiding previous +0.60m protrusion.','glass_material':'Blue-gray, low-roughness glass with slight transmission and coat. Appearance remains approximate because no dimensioned current facade source was available.','plan1086':'No additional dimensioned control point found; wall stays provisional.'},f,indent=2)
print('saved corrected measured reveal')
