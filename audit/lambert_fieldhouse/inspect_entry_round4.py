import bpy, json
ASSET=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lambert_fieldhouse.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)
rows=[]
for ob in bpy.data.objects:
    if ob.type not in {'MESH','CURVE'}: continue
    bb=[ob.matrix_world @ __import__('mathutils').Vector(c) for c in ob.bound_box]
    lo=[min(v[i] for v in bb) for i in range(3)]; hi=[max(v[i] for v in bb) for i in range(3)]
    if lo[0] < 10 and hi[0] > -10 and lo[1] < -46 and hi[1] > -54 and lo[2] < 2.0:
        mats=[]
        for m in getattr(ob.data,'materials',[]):
            if not m: continue
            col=tuple(m.diffuse_color)
            if m.use_nodes:
                n=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
                if n: col=tuple(n.inputs['Base Color'].default_value)
            mats.append({'name':m.name,'color':col})
        if any(any(c < .22 for c in m['color'][:3]) for m in mats) or any(s in ob.name.lower() for s in ('entry','inlay','sidewalk','curb','road','apron','threshold','walk')):
            rows.append({'name':ob.name,'type':ob.type,'bounds':[lo,hi],'zloc':ob.location.z,'hide_render':ob.hide_render,'mats':mats})
print(json.dumps(sorted(rows,key=lambda x:x['name']),indent=2))
