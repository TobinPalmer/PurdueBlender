import bpy,os
files=['materials_science_and_electrical_engineering_msee','biochemistry_building','animal_disease_diagnostic_laboratory','david_and_bonnie_brunner_farm_animal_hospital','agricultural_administration_building','agricultural_and_biological_engineering_abe','bechtel_innovation_design_center_bidc','bindley_bioscience_center','dauch_alumni_center','northwest_chiller_plant']
for f in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/'+f+'.blend'))
 c=next(x for x in bpy.data.collections if x.name.startswith('Asset_'))
 print('\n##'+f)
 ms=sorted({m.name for o in c.all_objects if o.type=='MESH' for m in o.data.materials if m})
 print('\n'.join(ms))
