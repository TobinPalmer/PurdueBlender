import bpy, json
m=bpy.data.materials.get('HAAS_Photo_Limestone')
if m:
    m.diffuse_color=(0.87,0.78,0.63,1)
    for n in m.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value=(0.87,0.78,0.63,1)
            n.inputs['Roughness'].default_value=0.82
b=bpy.data.materials.get('HAAS_R6_Red_Brick_Inlay')
if b:
    b.diffuse_color=(0.34,0.07,0.028,1)
    for n in b.node_tree.nodes:
        if n.type=='TEX_BRICK':
            n.inputs['Color1'].default_value=(0.40,0.085,0.032,1)
            n.inputs['Color2'].default_value=(0.27,0.045,0.016,1)
            n.inputs['Mortar'].default_value=(0.16,0.045,0.02,1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('R6_MATERIALS_TUNED',len(bpy.data.collections['Asset_felix_haas_hall'].objects))
