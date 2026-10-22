
import bpy
master = bpy.data.collections.get('Asset_hicks_library')
for c in master.children:
    print(f'Collection: {c.name}')
    for obj in c.objects:
        mats = [m.name for m in obj.data.materials if m] if obj.type == 'MESH' else 'None'
        print(f'  {obj.name} ({obj.type}) - mats: {mats}')
