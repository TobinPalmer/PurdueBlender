import bpy
from pathlib import Path
root = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
master = root / 'purdue_campus_master.blend'
patch = root / 'modular' / 'site' / 'engineering_mall_groundwork_patch.blend'
bpy.ops.wm.open_mainfile(filepath=str(master))
# Remove a prior instance if this integration script is rerun.
old = bpy.data.objects.get('Engineering_Mall_Groundwork_Patch_Instance')
if old: bpy.data.objects.remove(old, do_unlink=True)
with bpy.data.libraries.load(str(patch), link=True) as (src, dst):
    if 'Engineering_Mall_Groundwork_Patch' not in src.collections:
        raise RuntimeError('Patch collection not found in standalone patch')
    dst.collections = ['Engineering_Mall_Groundwork_Patch']
patch_collection = dst.collections[0]
if patch_collection is None: raise RuntimeError('Failed to link patch collection')
wrapper = bpy.data.collections.get('Linked_Engineering_Mall_Patch') or bpy.data.collections.new('Linked_Engineering_Mall_Patch')
if wrapper.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(wrapper)
inst = bpy.data.objects.new('Engineering_Mall_Groundwork_Patch_Instance', None)
inst.empty_display_type = 'PLAIN_AXES'
inst.instance_type = 'COLLECTION'
inst.instance_collection = patch_collection
inst.location = (0.0, 0.0, 0.0)
inst['module_role'] = 'Linked OSM Engineering Mall roads, turf, plaza and mapped plant instances'
inst['source_file'] = '//modular/site/engineering_mall_groundwork_patch.blend'
inst['placement_basis'] = 'Project XY campus coordinates; module origin at project origin'
wrapper.objects.link(inst)
# Store a project-relative dependency path.
for lib in bpy.data.libraries:
    if Path(bpy.path.abspath(lib.filepath)).resolve() == patch.resolve():
        lib.filepath = bpy.path.relpath(str(patch))
bpy.ops.wm.save_as_mainfile(filepath=str(master))
print('MASTER_SAVED',master,'PATCH_INSTANCE',inst.name,'LIBS',[(l.name,l.filepath) for l in bpy.data.libraries if 'engineering' in l.name.lower()])
