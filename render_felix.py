import bpy, os
p=os.path.abspath(r'modular/buildings/felix_haas_hall.blend')
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
sc.render.resolution_percentage=75
if sc.render.engine=='CYCLES': sc.cycles.samples=24
os.makedirs('audit/material_review',exist_ok=True)
sc.render.filepath=os.path.abspath('audit/material_review/felix_haas_before.png')
bpy.ops.render.render(write_still=True)
