import bpy
import json
import sys

args = sys.argv[sys.argv.index('--') + 1:]
if not args:
    raise RuntimeError('Expected output JSON path after --')
out_path = args[0]
object_name = 'Shealy (Frances M.) Residence Hall'
collection_name = 'Asset_massing_shealy_frances_m_residence_hall_a210e50'
obj = bpy.data.objects.get(object_name)
collection = bpy.data.collections.get(collection_name)
if obj is None or collection is None or obj not in collection.objects[:]:
    raise RuntimeError('Expected Shealy mesh and exported collection were not found')
vertices = [list(obj.matrix_world @ vertex.co) for vertex in obj.data.vertices]
payload = {
    'filepath': bpy.data.filepath,
    'object_name': obj.name,
    'object_type': obj.type,
    'collection_name': collection.name,
    'collection_object_count': len(collection.objects),
    'vertex_count': len(obj.data.vertices),
    'face_count': len(obj.data.polygons),
    'location': list(obj.location),
    'rotation_euler': list(obj.rotation_euler),
    'scale': list(obj.scale),
    'materials': [material.name for material in obj.data.materials],
    'vertices_world': vertices,
}
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(payload, f)
