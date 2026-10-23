import bpy,os,json
p=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=p)
# The north panes and mullions sit roughly 0.6 m behind the masonry's outer bounds.
# Move them toward +Y to the exterior reveal plane, based on the measured north wall/pane coordinates.
for n in ['RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions']:
 o=bpy.data.objects[n];o.location.y += .60
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.10,.20,.26,1);bs.inputs['Roughness'].default_value=.28;bs.inputs['Metallic'].default_value=.18;bs.inputs['Transmission Weight'].default_value=0;bs.inputs['Alpha'].default_value=1
# Slight lift keeps the glazing distinguishable in flat studio daylight without an emissive look.
if 'Emission Color' in bs.inputs:bs.inputs['Emission Color'].default_value=(.10,.18,.23,1);bs.inputs['Emission Strength'].default_value=.025
m.diffuse_color=(.10,.20,.26,1)
# Save to standalone asset only.
bpy.ops.wm.save_as_mainfile(filepath=p)
with open('audit/batch4_rawls/round3_model_changes.json','w') as f:json.dump({'asset':p,'north_pane_and_mullion_offset_world_m':[0,0.60,0],'basis':'North glass vertices span Y=20.16..20.72 while exterior masonry bbox reaches Y=20.79; offset clears the deep recess at the façade reveal.','glass_material':'Opaque blue-gray satin glazing with slight daylight lift; material palette is an estimate because available photo sources do not establish exact current glass appearance.','first_floor_plan_cutaway':'Render evidence only: isolated plan walls/furniture and hid overhead shell/slabs.','atrium_view':'Render evidence only: retained existing columns/guardrails and ground slab, hid upper overhead slabs to expose four-level section.','plan1086':'No new dimensioned GIS control points found; wall retained pending better evidence, 1–2m registration uncertainty.'},f,indent=2)
print('saved round3')
