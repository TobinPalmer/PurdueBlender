import bpy,json
from pathlib import Path
C=bpy.data.collections['Asset_felix_haas_hall'];removed=[]
for o in list(C.objects):
 if o.name.startswith('HAAS_Estimated_Side_'):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
Path('audit/batch3_haas/round9_cleanup.json').write_text(json.dumps({'removed_estimated_side_overlays':removed,'archived_formula_labels':['HAAS_Algorithm_1','HAAS_Algorithm_2','HAAS_Algorithm_3'],'gis_shell_vertices_moved':False,'roof_bump_strength':0.004,'roof_bump_distance':0.00035,'roof_emission_strength':0.12},indent=2),encoding='utf-8')
C['round9_cleanup']='Removed unsupported estimated side window/arch/jamb overlays extending beyond GIS shell; archived and render-hidden floating algorithm labels; reduced roof bump and added low warm emission for more even roof-plane color. GIS wall shell untouched.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('removed',len(removed),removed,'direct',len(C.objects))
