import bpy,os
p=os.path.abspath(r'modular/buildings/felix_haas_hall.blend')
bpy.ops.wm.open_mainfile(filepath=p)
m=bpy.data.materials['HAAS_Slate_Roof']
b=next(n for n in m.node_tree.nodes if n.get('codex_surface_detail'))
b.inputs['Strength'].default_value=0.025
b.inputs['Distance'].default_value=0.00025
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=p)
sc=bpy.context.scene
sc.render.resolution_percentage=75
if sc.render.engine=='CYCLES': sc.cycles.samples=24
sc.render.filepath=os.path.abspath('audit/material_review/felix_haas_final.png')
bpy.ops.render.render(write_still=True)
