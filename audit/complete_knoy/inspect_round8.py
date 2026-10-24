import bpy, json
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for n in ['KNOY_FloorSlab_L1','KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5','KNOY_Roof','KNOY_Penthouse','KNOY_Root','KNOY_Main_Building']:
 o=bpy.data.objects.get(n)
 if o:
  vs=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else []
  print(n, 'loc', list(o.location), 'dims', list(o.dimensions), 'z', (min(v.z for v in vs), max(v.z for v in vs)) if vs else None, 'status',o.get('story_status'))
print('scene',bpy.context.scene.camera.name if bpy.context.scene.camera else None, bpy.context.scene.render.filepath)
