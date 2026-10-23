import bpy
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');brick=next(n for n in nt.nodes if n.type=='TEX_BRICK')
if not any(l.from_node==brick and l.to_node==p and l.to_socket==p.inputs['Base Color'] for l in nt.links):nt.links.new(brick.outputs['Color'],p.inputs['Base Color'])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
