import bpy,os
files=['south_hall','stewart_center','tarkington_hall','university_hall','walc']
for f in files:
 p=os.path.abspath(f'modular/buildings/{f}.blend'); bpy.ops.wm.open_mainfile(filepath=p); sc=bpy.context.scene
 print('\nFILE',f,'objs',len(bpy.data.objects),'camera',sc.camera.name if sc.camera else None,'engine',sc.render.engine)
 for m in bpy.data.materials:
  if m.users and m.node_tree:
   pr=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   if not pr: continue
   base=pr.inputs['Base Color']
   c=tuple(round(x,2) for x in base.default_value) if not base.is_linked else 'linked'
   print(' ',m.name,'base',c,'rough',round(pr.inputs['Roughness'].default_value,2),'nodes',len(m.node_tree.nodes))
