import bpy, json
from pathlib import Path

marker = bpy.data.objects.get('Placement_wiley_hall')
collection = bpy.data.collections.get('Asset_wiley_hall')
payload = {
    'master': str(Path(bpy.data.filepath).resolve()),
    'marker_exists': marker is not None,
    'collection_exists': collection is not None,
    'collection_library': bpy.path.abspath(collection.library.filepath) if collection and collection.library else None,
    'marker_location': list(marker.location) if marker else None,
    'marker_rotation': list(marker.rotation_euler) if marker else None,
    'marker_scale': list(marker.scale) if marker else None,
    'instance_collection': marker.instance_collection.name if marker and marker.instance_collection else None,
    'instance_matrix_world': [list(row) for row in marker.matrix_world] if marker else None,
    'top_level_children_named_asset': [c.name for c in bpy.context.scene.collection.children if c.name == 'Asset_wiley_hall'],
}
Path(__file__).with_name('master_placement_r2.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf8')
print(json.dumps(payload, indent=2))
