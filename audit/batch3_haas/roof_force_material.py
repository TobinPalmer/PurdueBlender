import bpy
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
for l in list(p.inputs['Base Color'].links):nt.links.remove(l)
p.inputs['Base Color'].default_value=(.14,.018,.008,1);p.inputs['Roughness'].default_value=.84;m.diffuse_color=(.14,.018,.008,1)
# Keep shallow bump for tile relief only.
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
