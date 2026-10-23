import bpy
p=bpy.data.filepath;m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];nt=m.node_tree
brick=next(n for n in nt.nodes if n.type=='TEX_BRICK');brick.inputs['Color1'].default_value=(.16,.025,.012,1);brick.inputs['Color2'].default_value=(.095,.012,.006,1);brick.inputs['Mortar'].default_value=(.065,.015,.007,1);brick.inputs['Brick Width'].default_value=.55;brick.inputs['Row Height'].default_value=.20;brick.inputs['Mortar Size'].default_value=.003
bump=next(n for n in nt.nodes if n.type=='BUMP');bump.inputs['Distance'].default_value=.002;bump.inputs['Strength'].default_value=.15
m.diffuse_color=(.16,.025,.012,1);bpy.ops.wm.save_as_mainfile(filepath=p)
