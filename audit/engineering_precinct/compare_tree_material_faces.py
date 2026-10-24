import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\foliage_library\source\tree_small_02\tree_small_02.blend'
with bpy.data.libraries.load(p,link=False) as (src,dst): dst.objects=['tree_small_02_LOD1']
o=dst.objects[0]; counts={}
for poly in o.data.polygons:
 name=o.data.materials[poly.material_index].name if poly.material_index<len(o.data.materials) and o.data.materials[poly.material_index] else 'none'
 counts[name]=counts.get(name,0)+1
print('SOURCE',counts)
p2=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\foliage_library\engineering_foliage_library.blend'
with bpy.data.libraries.load(p2,link=False) as (src,dst): dst.collections=['PH_Tree_Small_02_LOD2']
o=dst.collections[0].all_objects[0]; counts={}
for poly in o.data.polygons:
 name=o.data.materials[poly.material_index].name if poly.material_index<len(o.data.materials) and o.data.materials[poly.material_index] else 'none'
 counts[name]=counts.get(name,0)+1
print('LOD',counts)
