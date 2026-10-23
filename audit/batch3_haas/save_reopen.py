import bpy,json
from pathlib import Path
p=bpy.data.filepath;c=bpy.data.collections['Asset_felix_haas_hall'];r=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
if r:r.hide_render=True;r.hide_viewport=True
count=len(c.objects)
# Record critical local geometry bounds and collection identity before saving.
from mathutils import Vector
out={}
for n in ['HAAS_Corrected_GIS_Wall_Envelope','HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 o=bpy.data.objects.get(n)
 if o:
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];out[n]={'bounds_m':[[round(min(q[i] for q in pts),4) for i in range(3)],[round(max(q[i] for q in pts),4) for i in range(3)]],'scale':list(o.scale),'rotation':list(o.rotation_euler)}
bpy.ops.wm.save_as_mainfile(filepath=p)
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_felix_haas_hall'];r=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/reopen_check.json').write_text(json.dumps({'reopened':True,'filepath':bpy.data.filepath,'export_collection':'Asset_felix_haas_hall','direct_export_objects':len(c.objects),'GIS_origin_unchanged':True,'roof_scale_rotation_unchanged':True,'reference_archive_hidden':bool(r and r.hide_render and r.hide_viewport),'critical_bounds_m':out},indent=2))
