import bpy,json
P=bpy.data.filepath;C=bpy.data.collections['Asset_felix_haas_hall']
locations={
 'HAAS_Plan_Label_00':('STAIR 1',-15.0,22.0),
 'HAAS_Plan_Label_01':('STAIR 2',-23.5,-16.5),
 'HAAS_Plan_Label_02':('STAIR 3',3.3,7.6),
 'HAAS_Plan_Label_03':('LIFT',-14.9,-14.0),
 'HAAS_Plan_Label_04':('RR 117',-14.0,-16.8),
 'HAAS_Plan_Label_05':('RR 119',-14.2,-21.4),
 'HAAS_Plan_Label_06':('CONF 111',-8.7,.8),
 'HAAS_Plan_Label_07':('CONF 101',6.8,6.6),
 'HAAS_Plan_Label_08':('STUDENT ORG',-19.3,-7.1),
 'HAAS_Plan_Label_09':('TA 151/145',-19.3,10.6)}
for name,(text,x,y) in locations.items():
 o=bpy.data.objects.get(name)
 if o:
  o.data.body=text;o.location=(x,y,4.3);o.data.size=.72
for o in list(C.objects):
 if ('Estimated_Side_' in o.name and o.name.endswith('_N')) or '_N_' in o.name and 'Estimated_Side' in o.name:
  bpy.data.objects.remove(o,do_unlink=True)
lm=bpy.data.materials.get('HAAS_Plan_Label_Charcoal')
if lm:
 lm.diffuse_color=(.008,.01,.012,1);lm.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.008,.01,.012,1)
bpy.ops.wm.save_as_mainfile(filepath=P)
with open('audit/batch3_haas/plan_label_layout.json','w') as f:json.dump({'labels':locations,'unverified_far_side_windows_removed':True},f,indent=2)
