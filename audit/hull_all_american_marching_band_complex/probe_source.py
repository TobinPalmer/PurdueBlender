import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/massing_hull_all_american_marching_band_complex_665bcb7.blend'
report=root/'audit/hull_all_american_marching_band_complex/source_probe.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
coll=bpy.data.collections['Asset_massing_hull_all_american_marching_band_complex_665bcb7']
rows=[]
for obj in coll.objects:
 if obj.type!='MESH': continue
 verts=[list(obj.matrix_world@v.co) for v in obj.data.vertices]
 rows.append({'name':obj.name,'type':obj.type,'world_vertices':verts,'vertex_count':len(obj.data.vertices),'face_count':len(obj.data.polygons),'materials':[m.name if m else None for m in obj.data.materials]})
probe={'blend':str(asset.relative_to(root)),'scene':'Building_massing_hull_all_american_marching_band_complex_665bcb7','collection':coll.name,'objects':rows}
report.write_text(json.dumps(probe,indent=2)+'\n',encoding='utf-8')
print(report)
