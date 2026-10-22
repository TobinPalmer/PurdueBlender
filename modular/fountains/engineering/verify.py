import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(D/'engineering.blend'))
s=bpy.context.scene;dom=bpy.data.objects['EF_Liquid_domain'];results=[]
for frame in [24,48,72,96]:
 s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();o=dom.evaluated_get(dg);me=o.to_mesh();coords=[o.matrix_world@v.co for v in me.vertices];row={'frame':frame,'vertices':len(me.vertices),'polygons':len(me.polygons)}
 if coords:row['min']=[min(v[i] for v in coords) for i in range(3)];row['max']=[max(v[i] for v in coords) for i in range(3)]
 o.to_mesh_clear();results.append(row)
 s.render.filepath=str(D/('render_%03d.png'%frame));bpy.ops.render.render(write_still=True)
(D/'verification.json').write_text(json.dumps({'frames':results,'cache':dom.modifiers[0].domain_settings.cache_directory},indent=2))
