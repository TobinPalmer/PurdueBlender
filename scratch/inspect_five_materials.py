import bpy, os, json
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'
files=['math_sciences.blend','neil_armstrong_hall.blend','owen_hall.blend','purdue_memorial_union.blend','ross_ade.blend']
for fn in files:
    bpy.ops.wm.open_mainfile(filepath=os.path.join(root,fn))
    print('\n###',fn,'objects',len(bpy.data.objects))
    for o in bpy.data.objects:
        if o.type!='MESH' or not o.material_slots: continue
        for s in o.material_slots:
            m=s.material
            if not m: continue
            p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
            col=tuple(round(v,3) for v in p.inputs['Base Color'].default_value[:3]) if p else None
            print(o.name,'|',m.name,'| color',col,'| nodes',[(n.name,n.bl_idname) for n in m.node_tree.nodes] if m.use_nodes else [])
