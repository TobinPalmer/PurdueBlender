import bpy,os
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
names=['armory','beering_hall','american_railway_building','brown_laboratory_of_chemistry','peirce_hall']
for name in names:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'modular','buildings',name+'.blend'))
 with open(os.path.join(ROOT,'audit','texture_batch_1',name+'_objects.txt'),'w',encoding='utf8') as f:
  for o in bpy.data.objects:
   if o.type!='MESH': continue
   mats=[m.name for m in o.data.materials if m]
   if mats:
    f.write(f'{o.name} | {mats} | dims={tuple(round(v,2) for v in o.dimensions)}\n')
