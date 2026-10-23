import bpy,json
from pathlib import Path
p=bpy.data.filepath;c=bpy.data.collections['Asset_felix_haas_hall'];archive=bpy.data.collections['Reference_Incompatible_Geometry_felix_haas_hall'];moved=[]
for n in ['HAAS_East_Door_Leaves','HAAS_East_Door_Transom','HAAS_East_Door_Pull_-0.6','HAAS_East_Door_Pull_0.6','HAAS_Win_Floor1_East_-8.0','HAAS_Win_Floor1_East_8.0']:
 o=bpy.data.objects.get(n)
 if o and any(col==c for col in o.users_collection):
  c.objects.unlink(o);archive.objects.link(o);o['archive_reason']='Superseded by 2026 photo-aligned entrance door/window meshes; original preserved for recovery.';moved.append(n)
archive.hide_render=True;archive.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=p)
Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/duplicate_cleanup.json').write_text(json.dumps({'archived_superseded_assets':moved,'archive_collection':archive.name,'reason':'Prevent overlap between older floor-1 door/window assemblies and revised photo-aligned entrance detail'},indent=2))
