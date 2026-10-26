import bpy,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
manifest=json.loads((HERE/'sources/manifest_snapshot.json').read_text(encoding='utf-8-sig'))
e=next(a for a in manifest['assets'] if a.get('id')=='black_cultural_center')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'purdue_campus_master.blend'))
ms=[o for o in bpy.data.objects if o.name=='Placement_black_cultural_center']
r={'master_file':'purdue_campus_master.blend','marker_count':len(ms),'markers':[{'name':o.name,'location':[float(x) for x in o.location],'rotation_degrees':[math.degrees(float(x)) for x in o.rotation_euler],'scale':[float(x) for x in o.scale],'instance_collection':o.instance_collection.name if o.instance_collection else None,'library_path':o.instance_collection.library.filepath if o.instance_collection and o.instance_collection.library else None} for o in ms],'manifest_origin_xy_m':e['placement_origin_xy_m']}
(HERE/'master_placement_probe.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8'); print(json.dumps(r,indent=2))
