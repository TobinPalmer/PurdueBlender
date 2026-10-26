import bpy,json,os
from pathlib import Path
obj=bpy.data.objects['Hawkins Hall']
pts=[list(obj.matrix_world @ v.co) for v in obj.data.vertices]
bottom=[p[:2] for p in pts if abs(p[2])<1e-4]
# Use native mesh vertex order: lower shell is first ring in current library.
path=Path('audit/massing_hawkins_hall_282335f/current_asset_geometry.json')
with path.open('w',encoding='utf-8') as f: json.dump({'building_id':'massing_hawkins_hall_282335f','asset':'modular/buildings/massing_hawkins_hall_282335f.blend','collection':'Asset_massing_hawkins_hall_282335f','object':'Hawkins Hall','mesh_vertex_count':len(obj.data.vertices),'mesh_face_count':len(obj.data.polygons),'materials':[m.name if m else None for m in obj.data.materials],'bottom_ring_local_campus_m':bottom,'all_world_bounds_m':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]},f,indent=2)
print(path,len(bottom))
