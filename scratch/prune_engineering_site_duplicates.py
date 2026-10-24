import bpy
from pathlib import Path
p = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
remove_names = {
    'Engineering_Fountain_Grand_Plaza_Arena',
    'Engineering_Mall_Central_Concourse',
    'Engineering_Mall_EastWest_Promenade',
    'Engineering_Mall_Fountain_Plaza',
    'Engineering_Mall_NorthSouth_Promenade',
    *(f'Engineering_Mall_Lawn_Curb_{i}' for i in range(1,5)),
    *(f'Engineering_Mall_Lawn_Turf_{i}' for i in range(1,5)),
}
missing = remove_names - set(bpy.data.objects.keys())
if missing: raise RuntimeError(f'Expected legacy ground objects missing: {sorted(missing)}')
for name in sorted(remove_names):
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
# Keep the water feature, fountain sculpture, benches, lighting and unrelated site assets.
bpy.ops.wm.save_as_mainfile(filepath=str(p))
print('PRUNED',len(remove_names),'objects; fountain props remain',sum(1 for o in bpy.data.objects if 'Fountain' in o.name))
