import bpy,os
for f in ['hovde_hall','hansen_life_sciences','knoy_hall']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(f'modular/buildings/{f}.blend')); print('\n'+f)
 for o in bpy.data.objects:
  if o.type=='MESH' and o.dimensions.length>10:
   mats=[s.material.name for s in o.material_slots if s.material]
   if any(k in o.name.lower() or any(any(t in m.lower() for t in ['roof','gravel','membrane','precast','limestone','concrete','brick','asphalt']) for m in mats) for k in ['roof','penthouse','slab']): print(o.name,tuple(round(x,1) for x in o.dimensions),mats)
