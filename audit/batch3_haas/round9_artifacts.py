import bpy,json
from pathlib import Path
C=bpy.data.collections['Asset_felix_haas_hall'];archive=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
if not archive:
 archive=bpy.data.collections.new('Reference_Incompatible_Geometry_felix_haas_hall');bpy.context.scene.collection.children.link(archive)
removed=[]
for name in ['HAAS_R4_Long_South_Band_1','HAAS_R4_Long_North_Band_1']:
 o=bpy.data.objects.get(name)
 if o:removed.append(name);bpy.data.objects.remove(o,do_unlink=True)
archived=[]
for name in ['HAAS_Algorithm_1','HAAS_Algorithm_2','HAAS_Algorithm_3']:
 o=bpy.data.objects.get(name)
 if o:
  archived.append(name)
  for col in list(o.users_collection):col.objects.unlink(o)
  archive.objects.link(o)
archive.hide_render=True;archive.hide_viewport=True
C['round9_removed_artifacts']='Removed two unsupported raised mid-level side bands and archived three floating algorithm-text objects that appeared as a blue elevation streak. GIS shell unchanged.'
Path('audit/batch3_haas/round9_artifact_changes.json').write_text(json.dumps({'removed_side_projection_bands':removed,'archived_blue_artifact_objects':archived,'GIS_shell_vertices_moved':False},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('ROUND9_ARTIFACTS',removed,archived,len(C.objects))
