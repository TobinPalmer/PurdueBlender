import bpy, json
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[2]
col=bpy.data.collections['Asset_massing_house_301841610_b6ad6ed']
rows=[]
for o in col.all_objects:
    if o.type!='MESH': continue
    coords=[o.matrix_local @ v.co for v in o.data.vertices]
    if not coords: continue
    b=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)]
    rows.append({'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'bounds':b,'parent':o.parent.name if o.parent else None,'materials':[m.name for m in o.data.materials if m]})
rows.sort(key=lambda r:(-(r['bounds'][0][1]-r['bounds'][0][0])*(r['bounds'][1][1]-r['bounds'][1][0]),r['name']))
slab=bpy.data.objects.get('GIS footprint foundation slab')
slab_vertices=[list((slab.matrix_local @ v.co)[:2]) for v in slab.data.vertices] if slab else []
out=root/'audit'/'evans_scholars_house'/'independent_grade_r1'/'geometry_probe.json'
out.write_text(json.dumps({'file':str(Path(bpy.data.filepath).resolve()),'objects':len(rows),'largest':rows[:80],'slab_name':slab.name if slab else None,'slab_vertices_local_xy':slab_vertices},indent=2))
print(out)
