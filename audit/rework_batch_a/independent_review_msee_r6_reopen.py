import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/materials_science_and_electrical_engineering_msee.blend'
OUT=ROOT/'audit/rework_batch_a/materials_science_and_electrical_engineering_msee_R6_independent_reopen.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections.get('Asset_materials_science_and_electrical_engineering_msee')
scene=bpy.context.scene
assert scene and asset
shell=next(o for o in asset.all_objects if o.name=='materials_science_and_electrical_engineering_msee_official_GIS_shell')
entry=[o for o in asset.all_objects if 'MSEE' in o.name and ('entry' in o.name.lower() or 'fanlight' in o.name.lower() or 'door' in o.name.lower())]
atrium=[o for o in asset.all_objects if 'atrium' in o.name.lower()]
meshes=[o for o in asset.all_objects if o.type=='MESH']
unpacked=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
no_material=[o.name for o in meshes if len(o.data.materials)==0]
shell_bounds=[[min((shell.matrix_world@v.co)[i] for v in shell.data.vertices),max((shell.matrix_world@v.co)[i] for v in shell.data.vertices)] for i in range(3)]
out={
 'asset_reopened':True,'blender_version':bpy.app.version_string,'scene':scene.name,
 'scene_names':[s.name for s in bpy.data.scenes],
 'asset_collection':asset.name,'direct_objects':len(asset.objects),'all_asset_objects':len(asset.all_objects),
 'mesh_objects':len(meshes),'shell':shell.name,'shell_world_bounds_m':shell_bounds,
 'entry_related_objects':len(entry),'atrium_related_objects':len(atrium),
 'unpacked_external_images':unpacked,'meshes_without_materials':no_material,
 'result':'PASS' if not unpacked and not no_material else 'CHECK'
}
OUT.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
