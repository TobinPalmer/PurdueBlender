import bpy, sys
for p in sys.argv[sys.argv.index('--')+1:]:
    bpy.ops.wm.open_mainfile(filepath=p)
    print('\nFILE',p)
    print('mats',len(bpy.data.materials))
    for m in bpy.data.materials:
        if m.users:
            print(m.name, 'nodes',m.use_nodes, 'users',m.users)
