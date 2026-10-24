import bpy,os,json
from mathutils import Vector
files=['materials_science_and_electrical_engineering_msee','biochemistry_building','animal_disease_diagnostic_laboratory','david_and_bonnie_brunner_farm_animal_hospital','agricultural_administration_building','agricultural_and_biological_engineering_abe','bechtel_innovation_design_center_bidc','bindley_bioscience_center','dauch_alumni_center','northwest_chiller_plant']
for f in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/'+f+'.blend'));c=bpy.data.collections.get('Asset_'+f);code=f.split('_')[0].upper();shell=next((o for o in c.all_objects if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name)),None)
 def b(o):
  p=[o.matrix_world@Vector(v) for v in o.bound_box];return [[round(min(q[i] for q in p),2) for i in range(3)],[round(max(q[i] for q in p),2) for i in range(3)]]
 print('\n##',f,'shell',b(shell),'camera',list(bpy.context.scene.camera.location) if bpy.context.scene.camera else None)
 for o in c.all_objects:
  if o.type=='MESH' and any(s in o.name.lower() for s in ('main_entrance_glazed_door','primary_glazed_doors','revision_transparent','revision_research_lobby','two_story_glazed_atrium')):print(o.name,b(o))
 # sample windows at plane edges
 wins=[o for o in c.all_objects if o.type=='MESH' and 'window_' in o.name and not 'sill' in o.name and not 'mullion' in o.name]
 print('sample windows',[(o.name,b(o)) for o in wins[:2]])
