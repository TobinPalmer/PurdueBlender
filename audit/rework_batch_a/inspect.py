import bpy, os, json
from mathutils import Vector
files={
'MSEE':'modular/buildings/materials_science_and_electrical_engineering_msee.blend',
'BCHM':'modular/buildings/biochemistry_building.blend',
'ADDL':'modular/buildings/animal_disease_diagnostic_laboratory.blend',
'BRFM':'modular/buildings/david_and_bonnie_brunner_farm_animal_hospital.blend',
'AGAD':'modular/buildings/agricultural_administration_building.blend',
'ABE':'modular/buildings/agricultural_and_biological_engineering_abe.blend',
'BIDC':'modular/buildings/bechtel_innovation_design_center_bidc.blend',
'BIND':'modular/buildings/bindley_bioscience_center.blend',
'DAUC':'modular/buildings/dauch_alumni_center.blend',
'NWCP':'modular/buildings/northwest_chiller_plant.blend'}
out={}
for key,path in files.items():
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(path))
 col=next((c for c in bpy.data.collections if c.name.startswith('Asset_')),None)
 objs=[]
 for o in col.objects:
  if o.type=='MESH':
   pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
   lo=[round(min(p[i] for p in pts),2) for i in range(3)]; hi=[round(max(p[i] for p in pts),2) for i in range(3)]
   if (hi[2]-lo[2]>0.02) and (len(objs)<100): objs.append({'name':o.name,'mat':o.material_slots[0].material.name if o.material_slots and o.material_slots[0].material else '', 'b':[lo,hi]})
 out[key]={'file':path,'collection':col.name if col else '', 'objects':objs,'camera':bpy.context.scene.camera.name if bpy.context.scene.camera else None, 'resolution':[bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y]}
with open(os.path.abspath('audit/rework_batch_a/inspect.json'),'w') as f: json.dump(out,f,indent=2)
