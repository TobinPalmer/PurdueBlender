import json,math,bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
snap=json.loads((ROOT/'audit/batchC_life_science_plant_soils_official_footprint.json').read_text()); ring=next(f for f in snap['features'] if f.get('attributes',{}).get('FID')==917)['geometry']['rings'][0][:-1]
ev=json.loads((ROOT/'audit/batchC_life_science_plant_soils_evidence.json').read_text()); ox,oy=ev['coordinate_method']['build_bbox_origin_xy_m']
exp=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274))-ox,(lat-40.4274)*111040-oy) for lon,lat in ring]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/life_science_plant_and_soils_laboratory.blend'))
ob=bpy.data.objects['Life Science Plant and Soils Laboratory | official GIS footprint ground floor']
act=sorted({(round(v.co.x,3),round(v.co.y,3)) for v in ob.data.vertices})
print('expected',[(round(x,3),round(y,3)) for x,y in exp]); print('actual',act)
