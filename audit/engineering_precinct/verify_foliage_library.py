import bpy
from pathlib import Path

collections=[c for c in bpy.data.collections if c.asset_data]
materials=[m for m in bpy.data.materials if m.asset_data]
assert len(collections)>=17, f'Expected foliage/prop collection assets, got {len(collections)}'
assert len(materials)>=9, f'Expected campus/PBR material assets, got {len(materials)}'
assert all(image.packed_file for image in bpy.data.images if image.source=='FILE'), 'Library has an unpacked image dependency'
assert all(c.get('license') for c in collections), 'Collection asset missing provenance/license'
for name in ('PH_Tree_Small_02_LOD2','PH_Fir_Sapling_A_LOD2','PH_Fir_Sapling_B_LOD2','PH_Fir_Sapling_C_LOD2',
             'PH_Shrub_02_A_LOD2','PH_Fern_02_Variants','PH_Grass_Medium_01_Selective_LOD2'):
    assert bpy.data.collections.get(name), f'Missing expected collection {name}'
catalog_file=Path(bpy.data.filepath).parent/'blender_assets.cats.txt'
assert catalog_file.exists() and 'VERSION 1' in catalog_file.read_text(encoding='utf-8')
print('FOLIAGE_LIBRARY_REOPEN_QA',{'collections':len(collections),'materials':len(materials),
      'packed_images':sum(bool(image.packed_file) for image in bpy.data.images),'total_images':len(bpy.data.images),
      'collection_asset_names':[c.name for c in collections],
      'mesh_faces':{c.name:sum(len(o.data.polygons) for o in c.all_objects if o.type=='MESH') for c in collections}})
