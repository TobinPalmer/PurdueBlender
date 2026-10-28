import bpy, json
from mathutils import Vector
asset='massing_schleman_hall_schm_ad4b05b'
obj=bpy.data.objects.get('Schleman Hall (SCHM)')
coll=bpy.data.collections.get('Asset_'+asset)
assert obj is not None and coll is not None and obj in coll.objects[:]
assert len(coll.objects)==1
assert obj.type=='MESH' and len(obj.data.vertices)>3000 and len(obj.data.polygons)>2000
assert len(obj.data.uv_layers)>0
materials=[m.name for m in obj.data.materials if m]
assert len(materials)>=5
assert all(0 <= p.material_index < len(obj.data.materials) for p in obj.data.polygons)
world=[obj.matrix_world @ Vector(v) for v in obj.bound_box]
lo=[min(v[i] for v in world) for i in range(3)]; hi=[max(v[i] for v in world) for i in range(3)]
print('FRESH_OPEN_VALIDATION='+json.dumps({'asset_id':asset,'file':bpy.data.filepath,'collection_objects':len(coll.objects),'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'uv_layers':[u.name for u in obj.data.uv_layers],'materials':materials,'bounds_world_m':{'min':lo,'max':hi},'packed_or_external_images':len([i for i in bpy.data.images if i.source=='FILE'])}))

