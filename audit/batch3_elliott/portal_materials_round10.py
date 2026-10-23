import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');o=bpy.data.objects['ELLT_R8_Upper_Portal_DoorLeaf_L_Estimated'];print('materials',[(m.name, tuple(m.diffuse_color),m.use_nodes) for m in o.data.materials]);print('material polygon counts', {i:sum(p.material_index==i for p in o.data.polygons) for i in range(len(o.data.materials))});print('dimensions',tuple(o.dimensions));
for m in o.data.materials:
 print(m.name, [(n.name,n.type,tuple(n.inputs['Base Color'].default_value) if n.type=='BSDF_PRINCIPLED' else '') for n in m.node_tree.nodes] if m.use_nodes else '')
