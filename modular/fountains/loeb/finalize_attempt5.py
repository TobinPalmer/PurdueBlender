import bpy, os, json, math
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__)); bpy.ops.wm.open_mainfile(filepath=R+'/loeb.blend'); s=bpy.context.scene
cx=(-86.915825+86.9137)*111412.84*math.cos(math.radians(40.4274)); cy=(40.425003-40.4274)*111040
delta=Vector((cx+50,cy+255,0)); original={o.name:[list(row) for row in o.matrix_world] for o in s.objects}; json.dump(original,open(R+'/attempt5_pretranslation_world_matrices.json','w'),indent=2)
dom=bpy.data.objects['Loeb_Mantaflow_Liquid_Domain']; s.frame_set(48)
def box():
    ev=dom.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); pts=[ev.matrix_world@v.co for v in me.vertices]; out={'vertices':len(pts),'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}; ev.to_mesh_clear(); return out
before=box()
for o in s.objects:
    if o.parent is None: o.location+=delta
bpy.context.view_layer.update(); after=box()
s['placement_evidence']='Provisional gross correction from Commons2010 OBJECT geotag40.425003,-86.915825. Unknown precision; no surveyed tolerance. Local project degree approximation.'
json.dump({'center_before':[-50,-255,0],'center_after':[cx,cy,0],'delta':list(delta),'precision':'unknown; no certified tolerance','reference':'https://commons.wikimedia.org/wiki/File:Purdue_University_Liberal_Arts_fountain.jpg','cache_bbox_before':before,'cache_bbox_after':after},open(R+'/attempt5_placement.json','w'),indent=2)
s.render.filepath=R+'/final_frame_048.png'; bpy.ops.render.render(write_still=True); bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend')
bpy.ops.wm.open_mainfile(filepath=R+'/loeb.blend'); s=bpy.context.scene; dom=bpy.data.objects['Loeb_Mantaflow_Liquid_Domain']; s.frame_set(24); reopened=box(); json.dump(reopened,open(R+'/reopen_verification.json','w'),indent=2)
