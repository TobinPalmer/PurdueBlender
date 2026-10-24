import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_knoy/knoy_hall_round6_candidate.blend')
p=bpy.data.objects.get('KNOY_Roof_PV_28Panel_Array_R6')
print(json.dumps({'hide_render':p.hide_render,'hide_viewport':p.hide_viewport,'display_type':p.display_type,'material':[m.name for m in p.data.materials],'first_vertices':[list(v.co) for v in p.data.vertices[:8]],'first_normal':list(p.data.polygons[0].normal),'bbox':[[min((p.matrix_world@Vector(v))[i] for v in p.bound_box) for i in range(3)],[max((p.matrix_world@Vector(v))[i] for v in p.bound_box) for i in range(3)]],'mat_color':list(p.data.materials[0].diffuse_color)},indent=2))
