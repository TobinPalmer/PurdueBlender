import bpy, json
from pathlib import Path
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\phi_kappa_psi_fid856\candidate_inspection.json')
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 rows.append({'object':o.name,'vertex_count':len(pts),'location':list(o.location),'dimensions':list(o.dimensions),'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'vertices':[list(p) for p in pts]})
out.write_text(json.dumps({'file':bpy.data.filepath,'scene':bpy.context.scene.name,'objects':rows},indent=2))
print(out, len(rows))
