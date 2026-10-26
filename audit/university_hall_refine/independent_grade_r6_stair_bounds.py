"""Measure saved gallery and stair meshes from the exact R6 file."""
import hashlib, json
from pathlib import Path
import bpy

root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/university_hall.blend'
expected='5fb431e4a8c6d5f47e50fc7085de981f64a2f4982b73af57830cdac162bd9da2'
actual=hashlib.sha256(asset.read_bytes()).hexdigest()
if actual!=expected: raise RuntimeError(f'R6 hash mismatch: {actual}')
if Path(bpy.data.filepath).resolve()!=asset.resolve(): raise RuntimeError('Open exact saved asset before measurement')
col=bpy.data.collections['Asset_university_hall']
deps=bpy.context.evaluated_depsgraph_get()
rows=[]
for obj in col.all_objects:
    if obj.type!='MESH' or not any(token in obj.name for token in ('StairFlight','StairLanding','GalleryFloor','FirstGallery','AcademyOverlook')):
        continue
    ev=obj.evaluated_get(deps); me=ev.to_mesh()
    try:
        points=[ev.matrix_world@v.co for v in me.vertices]
        if not points: continue
        bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
    finally: ev.to_mesh_clear()
    rows.append({'name':obj.name,'bounds_m':bounds,'object_dimensions_m':list(obj.dimensions),'parent':obj.parent.name if obj.parent else None})
out={'asset':str(asset),'sha256':actual,'blender_version':bpy.app.version_string,'objects':rows}
(root/'audit/university_hall_refine/independent_grade_r6_stair_bounds.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
