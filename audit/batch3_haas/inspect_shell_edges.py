import bpy,json
from pathlib import Path
o=bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope']
pts=[tuple(round(float(x),4) for x in v.co) for v in o.data.vertices]
unique={tuple((p[0],p[1])) for p in pts}
Path('audit/batch3_haas/shell_xy_vertices.json').write_text(json.dumps(sorted(unique),indent=2))
print(json.dumps(sorted(unique),indent=2))
