import bpy
from pathlib import Path
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
for k,f in [('ford_dining_court','ford_dining_court.blend'),('horticulture_building','horticulture_building.blend'),('hall_for_discovery_and_learning_research','hall_for_discovery_and_learning_research.blend'),('physics_building','physics_building_phys_3bf42f3.blend'),('ray_w_herrick_laboratories','ray_w_herrick_laboratories.blend'),('flex_lab','flex_lab.blend'),('brees_student_athletic_academic_center','brees_student_athletic_academic_center.blend'),('heine_pharmacy','heine_pharmacy.blend'),('krach_leadership_center','krach_leadership_center.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(root/'modular'/'buildings'/f)); a=next((c for c in bpy.data.collections if c.name=='Asset_'+k),None); print('\nASSET',k)
 for o in a.all_objects:
  if any(s in o.name.lower() for s in ['roof','bridge','entry','high-bay','glazed','mechanical','window','facade glazing','vestibule']): print(o.name, 'dim',tuple(round(x,2) for x in o.dimensions), 'loc',tuple(round(x,2) for x in o.location), 'batch',o.get('revision_batch','-'))
