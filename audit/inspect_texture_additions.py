import bpy, sys, os
paths=sys.argv[sys.argv.index('--')+1:]
for p in paths:
    bpy.ops.wm.open_mainfile(filepath=p)
    print('FILE',os.path.basename(p))
    for m in bpy.data.materials:
        if m.use_nodes:
            out=[]
            for n in m.node_tree.nodes:
                if n.type=='TEX_NOISE':
                    out.append(('Noise',n.inputs['Scale'].default_value,n.inputs['Detail'].default_value,n.inputs['Roughness'].default_value))
                elif n.type=='TEX_IMAGE': out.append(('Image',n.image.name if n.image else None))
                elif n.type=='BSDF_PRINCIPLED': out.append(('BSDF',tuple(round(c,3) for c in n.inputs['Base Color'].default_value[:3]),round(n.inputs['Roughness'].default_value,3),round(n.inputs['Metallic'].default_value,3)))
            print('MAT',m.name, out)
    print('OBJECTS',len(bpy.data.objects))
