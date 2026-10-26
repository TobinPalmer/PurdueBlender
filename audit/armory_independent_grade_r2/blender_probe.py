from pathlib import Path
import json, math
import bpy

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/armory.blend'
OUT=HERE/'blender_probe.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
col=bpy.data.collections.get('Asset_armory')
assert scene.name=='Building_armory'
assert col and col.get('building_id')=='armory' and col.get('owner')=='Rosen' and col.get('source_feature_id')==207
assert not any(o.type in {'CAMERA','LIGHT'} for o in col.all_objects)

def bounds(objs):
    dg=bpy.context.evaluated_depsgraph_get(); pts=[]
    for obj in objs:
        if obj.type!='MESH': continue
        ev=obj.evaluated_get(dg); me=ev.to_mesh()
        pts.extend(ev.matrix_world @ v.co for v in me.vertices)
        ev.to_mesh_clear()
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
wall_names={'Armory_Wall_East','Armory_Wall_West','Armory_Wall_North_Low','Armory_Wall_South_Low'}
walls=[o for o in col.all_objects if o.name in wall_names]
assert len(walls)==4
wall_bounds=bounds(walls)
gable=bpy.data.objects.get('Armory_Rosen_Central_Stepped_Gable')
assert gable is not None and gable.name in col.all_objects.keys()
gable_bounds=bounds([gable])
assert not any(o.name.startswith('Armory_Tower_') or o.name.startswith('Armory_Truss_') for o in col.all_objects)
# Portable collection-only export; retain the relative foliage library path.
probe=HERE/'collection_export_probe.blend'
old=[]
for lib in bpy.data.libraries:
    old.append((lib,lib.filepath))
    abs_path=bpy.path.abspath(lib.filepath)
    rel=Path(abs_path)
    try: relpath=__import__('os').path.relpath(abs_path,str(HERE)).replace('\\','/')
    except Exception: relpath=lib.filepath
    lib.filepath='//'+relpath
bpy.data.libraries.write(str(probe),{col},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
for lib,path in old: lib.filepath=path
external=[img.filepath for img in bpy.data.images if img.filepath and img.source=='FILE' and not img.packed_file]
absolute_libs=[lib.filepath for lib in bpy.data.libraries if lib.filepath and not lib.filepath.startswith('//')]
assert not external and not absolute_libs
res={'asset':str(ASSET),'scene':scene.name,'collection':col.name,'building_id':col.get('building_id'),'owner':col.get('owner'),'source_feature_id':col.get('source_feature_id'),'collection_object_count':len(col.all_objects),'collection_objects':sorted(o.name for o in col.all_objects),'structural_wall_bounds_local_m':wall_bounds,'gable_bounds_local_m':gable_bounds,'gable_exists':True,'external_unpacked_images':external,'linked_libraries':[lib.filepath for lib in bpy.data.libraries],'absolute_library_paths':absolute_libs,'preview_camera_lights_in_export':False,'export_probe':str(probe)}
OUT.write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(res,indent=2,ensure_ascii=False))
