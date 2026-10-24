import bpy,json
from pathlib import Path
root=Path.cwd(); m=json.load(open(root/'modular/manifest.json',encoding='utf-8'))
for a in m['assets']:
 if a['id'] in ['massing_materials_science_and_electrical_engineering_msee_003a4e2','massing_forney_hall_of_chemical_engineering_frny_d94ba3a','massing_hampton_hall_of_civil_engineering_hamp_9715f0e','massing_max_w_maileen_brown_family_hall_of_electrical_engineering_bhee_078fbfb','massing_potter_engineering_center_potr_89c4c33']:
  with bpy.data.libraries.load(str(root/'modular'/a['file']),link=True) as (s,d): d.collections=[a['collection']]
  c=d.collections[0]; o=next(x for x in c.all_objects if x.type=='MESH'); b=o.bound_box
  print(a['id'],[[round(min(v[i] for v in b),1),round(max(v[i] for v in b),1)] for i in range(3)])
