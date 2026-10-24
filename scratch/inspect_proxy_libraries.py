import bpy,json
from pathlib import Path
root=Path.cwd(); m=json.load(open(root/'modular/manifest.json',encoding='utf-8'))
ids=['massing_materials_science_and_electrical_engineering_msee_003a4e2','massing_forney_hall_of_chemical_engineering_frny_d94ba3a','massing_hampton_hall_of_civil_engineering_hamp_9715f0e','massing_max_w_maileen_brown_family_hall_of_electrical_engineering_bhee_078fbfb','massing_potter_engineering_center_potr_89c4c33']
for i in ids:
 a=next(x for x in m['assets'] if x['id']==i); p=root/'modular'/a['file']
 with bpy.data.libraries.load(str(p),link=True) as (src,dst): dst.collections=[a['collection']]
 c=dst.collections[0]; print(i,[(o.name,tuple(round(float(v),1) for v in o.location),tuple(round(float(v),1) for v in o.dimensions)) for o in c.all_objects if o.type=='MESH'][:4])
