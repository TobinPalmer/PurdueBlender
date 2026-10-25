import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
for name in ['PMU_Stained_Glass_Lancet','PMU_Lead_Gothic_Glass','PMU_Red_Brick_Gothic','PMU_Slate_Roof']:
 m=bpy.data.materials[name]; print(name,'diffuse',tuple(round(x,3) for x in m.diffuse_color))
 for n in m.node_tree.nodes:
  print(' ',n.name,n.type)
  if n.type=='BSDF_PRINCIPLED':
   for inp in ['Base Color','Metallic','Roughness','Alpha','Emission Color','Emission Strength']:
    try: print('   ',inp,n.inputs[inp].default_value)
    except: pass
  if n.type=='VALTORGB': print('   ramp',[(e.position,tuple(round(x,3) for x in e.color)) for e in n.color_ramp.elements])
