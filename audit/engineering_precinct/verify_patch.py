import bpy
import json
from pathlib import Path

col = bpy.data.collections.get('Engineering_Mall_Groundwork_Patch')
assert col is not None, 'patch collection missing after reopening file'
objects = list(col.objects)
plants = [o for o in objects if o.name.startswith('Plant_')]
inferred_plants = [o for o in objects if o.name.startswith('ECN_Inferred_Tree_')]
paths = [o for o in objects if o.name.startswith('OSM_Way_')]
grass = [o for o in objects if o.name.startswith('OSM_Grass_')]
plaza = bpy.data.objects.get('Engineering_Fountain_Plaza_Paving_OSM_283274215')
assert len(plants) == 349, f'expected 349 inventory plant records, found {len(plants)}'
assert len(inferred_plants) == 5, f'expected 5 explicitly inferred trees, found {len(inferred_plants)}'
assert all(o.get('source_url') and o.get('uncertainty') for o in inferred_plants)
assert len(paths) == 92, f'expected 92 OSM path ribbons after excluding the closed plaza outline, found {len(paths)}'
assert len(grass) == 30, f'expected 30 grass parcels, found {len(grass)}'
assert plaza is not None, 'filled Engineering Fountain plaza is missing'
assert not any(o.name.startswith('OSM_Way_283274215') for o in objects), 'closed plaza boundary must not be modeled as separate segment ribbons'
assert all(max(v.co.z for v in o.data.vertices) <= .0121 for o in grass), 'mapped turf must remain below the plaza and path surfaces'
assert min(v.co.z for v in plaza.data.vertices) >= .0279, 'plaza mesh must remain above the turf underlay'
assert all(min(v.co.z for v in o.data.vertices) >= .0449 for o in paths), 'path ribbons must remain above turf surfaces'
assert all(o.get('source') == 'Purdue Arboretum Open Data' for o in plants)
assert all(o.get('height_status') and o.get('canopy_status') for o in plants)
snapshot=Path(__file__).resolve().with_name('arboretum_plants_snapshot.json')
source=json.loads(snapshot.read_text(encoding='utf-8'))
expected={int(f['attributes']['OBJECTID']):f['geometry'] for f in source['features'] if f.get('geometry') and f['geometry'].get('x') and f['geometry'].get('y')}
for plant in plants:
    geom=expected[int(plant['source_objectid'])]
    ex=(geom['x']+86.9137)*84810.60416539927
    ey=(geom['y']-40.4274)*111040.0
    assert abs(plant.location.x-ex)<0.001 and abs(plant.location.y-ey)<0.001, f'Plant XY changed: {plant.name}'
assert all(o.get('source') == 'OpenStreetMap' for o in paths)
assert all(o.type == 'EMPTY' and o.instance_type == 'COLLECTION' and o.instance_collection for o in plants)
assert all(o.type == 'MESH' and len(o.data.polygons) for o in paths + grass)
linked=[o for o in plants+inferred_plants if o.instance_type=='COLLECTION']
assert all(o.get('source_objectid') is not None for o in plants)
assert all(o.get('common_name') and o.get('inventory_habit') is not None for o in plants)
assert len(linked)==len(plants)+len(inferred_plants), f'every plant must be a reusable asset instance; found {len(linked)}'
assert all(o.instance_collection and o.instance_collection.get('license')=='CC0 1.0 Universal, Poly Haven asset' for o in linked)
assert len(plaza.data.polygons) > 0
print('PATCH_REOPEN_QA', {'objects': len(objects), 'plants': len(plants), 'linked_foliage_instances':len(linked), 'inferred_plants': len(inferred_plants), 'paths': len(paths), 'grass': len(grass), 'plaza_faces': len(plaza.data.polygons), 'library_paths':[l.filepath for l in bpy.data.libraries]})
