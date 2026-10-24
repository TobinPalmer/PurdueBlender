import bpy, json
p=r'modular/buildings/materials_science_and_electrical_engineering_msee.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections.get('Asset_materials_science_and_electrical_engineering_msee')
print('COLL',len(c.all_objects))
for m in bpy.data.materials:
    if 'msee' in m.name.lower():
        bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes and m.node_tree else None
        print('MAT',m.name, tuple(round(x,3) for x in bs.inputs['Base Color'].default_value) if bs else None, round(bs.inputs['Roughness'].default_value,2) if bs else None)
for o in c.all_objects:
    nm=o.name.lower()
    if any(x in nm for x in ['shell','facade','atrium','entry','roof','glass','window']) and o.type=='MESH':
        b=o.bound_box
        w=[o.matrix_world @ __import__('mathutils').Vector(v) for v in b]
        coords=[[round(min(v[i] for v in w),2),round(max(v[i] for v in w),2)] for i in range(3)]
        mats=[m.name for m in o.data.materials if m]
        print('OBJ',o.name,'bounds',coords,'mats',mats[:3])
