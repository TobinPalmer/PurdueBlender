import bpy, json
ASSET=r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_1089875810_8c9b95d.blend"
bpy.ops.wm.open_mainfile(filepath=ASSET)
out=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    mats=[]
    for m in o.data.materials:
        n=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
        mats.append({'name':m.name,'diffuse':list(m.diffuse_color),'base':list(n.inputs['Base Color'].default_value) if n else None})
    out.append({'object':o.name,'materials':mats,'face_materials':{str(i):sum(1 for p in o.data.polygons if p.material_index==i) for i in range(len(mats))}})
print(json.dumps(out,indent=2))
