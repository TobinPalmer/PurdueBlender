import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
blend=Path(bpy.data.filepath); audit=Path(__file__).resolve().parent
col=bpy.data.collections.get('Asset_winifred_parker_hall')
assert col is not None
root=bpy.data.objects.get('AssetRoot_winifred_parker_hall')
assert root is not None
assert bpy.data.objects.get('Parker_GIS_Continuous_Upper_Shell')
assert bpy.data.objects.get('Parker_GIS_Ground_Core_0')
assert bpy.data.objects.get('Parker_GIS_Roof_Outline')
def bounds(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
 pts=[ev.matrix_world@Vector(v) for v in ev.bound_box]
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
objs=list(col.all_objects); mesh=[o for o in objs if o.type=='MESH']
used={m for o in mesh for m in o.data.materials if m}
shell=bpy.data.objects['Parker_GIS_Continuous_Upper_Shell']
ground=bpy.data.objects['Parker_GIS_Ground_Core_0']
roof=bpy.data.objects['Parker_GIS_Roof_Outline']
report={'asset_path':str(blend),'sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'reopened_in_separate_blender_process':True,'collection':'Asset_winifred_parker_hall','scene':bpy.context.scene.name,'export_object_count':len(objs),'mesh_count':len(mesh),'material_count':len(used),'materialless_meshes':[o.name for o in mesh if not o.data.materials],'external_unpacked_image_files':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file],'asset_root':root.name,'asset_root_world_matrix':[[round(v,9) for v in row] for row in root.matrix_world],'main_shell_bounds_local':bounds(shell),'ground_core_bounds_local':bounds(ground),'roof_bounds_local':bounds(roof),'upper_shell_mesh':{'vertices':len(shell.data.vertices),'faces':len(shell.data.polygons),'material_names':[m.name for m in shell.data.materials if m]},'ground_mesh':{'vertices':len(ground.data.vertices),'faces':len(ground.data.polygons),'material_names':[m.name for m in ground.data.materials if m]},'roof_mesh':{'vertices':len(roof.data.vertices),'faces':len(roof.data.polygons),'material_names':[m.name for m in roof.data.materials if m]},'asset_origin_parent':shell.parent.name if shell.parent else None,'legacy_duplicate_mass_remaining':bpy.data.objects.get('Parker_EastWing_MainMass') is not None,'open_surface_detail':None}
assert report['export_object_count']>500
assert report['mesh_count']>500
assert not report['materialless_meshes']
assert report['main_shell_bounds_local'][2]==[4.199999809265137,20.200000762939453] or abs(report['main_shell_bounds_local'][2][0]-4.2)<.01
assert report['legacy_duplicate_mass_remaining'] is False
(audit/'gis_candidate_reopen_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
