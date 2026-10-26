import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[2]
coll=bpy.data.collections.get('Asset_massing_faith_west_community_center_84aa829')
scene=bpy.data.scenes.get('Building_massing_faith_west_community_center_84aa829')
rows=[]
for o in coll.all_objects:
    coords=[o.matrix_world@Vector(c) for c in o.bound_box]
    bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
    row={'name':o.name,'type':o.type,'bounds':bounds,'verts':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None,'materials':[m.name for m in o.data.materials]}
    if o.name == 'FaithWest_Public_Podium_Walls_With_Window_Openings':
        row['vertices_world']=[list(o.matrix_world@v.co) for v in o.data.vertices]
    rows.append(row)
report={'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'scene':scene.name,'collection':coll.name,'objects':len(rows),'rows':rows,'materials':sorted({m.name for o in coll.all_objects for m in o.data.materials})}
out=root/'audit/faith_west_community_center_independent_grade/candidate_probe.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('FAITH_WEST_GRADE_PROBE',len(rows),json.dumps([r['name'] for r in rows]))
