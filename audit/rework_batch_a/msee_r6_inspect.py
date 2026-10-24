import bpy, json, os
from mathutils import Vector
path=os.path.abspath('modular/buildings/materials_science_and_electrical_engineering_msee.blend')
bpy.ops.wm.open_mainfile(filepath=path)
prefixes=('MSEE_window_','MSEE_sill_','MSEE_mullion_','MSEE_Max_W_Brown_two_story_glazed_atrium','R5_MSEE_entry_')
res=[]
for o in bpy.data.objects:
    if not o.name.startswith(prefixes): continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    center=sum(pts,Vector())/8
    dims=[round(max(p[i] for p in pts)-min(p[i] for p in pts),3) for i in range(3)]
    mats=[m.name for m in o.data.materials] if hasattr(o.data,'materials') else []
    res.append({'name':o.name,'type':o.type,'center':[round(v,3) for v in center],'dims':dims,
                'local_dimensions':[round(v,3) for v in o.dimensions],
                'rotation':[round(v,4) for v in o.rotation_euler],
                'materials':mats})
out=os.path.abspath('audit/rework_batch_a/materials_science_and_electrical_engineering_msee_R6_object_inspection.json')
with open(out,'w') as f:json.dump(res,f,indent=2)
print('wrote',out,'rows',len(res))
