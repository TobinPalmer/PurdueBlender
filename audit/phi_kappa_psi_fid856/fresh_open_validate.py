"""Fresh-open and render validation for the Phi Kappa Psi local library."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
asset_path=root/'modular'/'buildings'/'phi_kappa_psi_fid856.blend'
render_path=root/'audit'/'phi_kappa_psi_fid856'/'renders'/'fresh_open_front.png'
report_path=root/'audit'/'phi_kappa_psi_fid856'/'fresh_open_validation.json'
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
scene=bpy.context.scene
col=bpy.data.collections.get('Asset_phi_kappa_psi_fid856')
assert col is not None, 'Expected exported asset collection missing'
assert scene.name=='Building_phi_kappa_psi_fid856', scene.name
assert scene.camera is not None, 'Saved front camera missing'
external_images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath]
depgraph=bpy.context.evaluated_depsgraph_get()
points=[]
for obj in col.all_objects:
    ev=obj.evaluated_get(depgraph)
    if obj.type=='MESH':
        for v in ev.to_mesh().vertices:
            points.append(ev.matrix_world @ v.co)
        ev.to_mesh_clear()
    elif obj.type=='FONT':
        points.extend(ev.matrix_world @ Vector(corner) for corner in obj.bound_box)
assert points, 'Collection has no measurable geometry'
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
scene.render.resolution_x=1280; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(render_path)
bpy.ops.render.render(write_still=True)
assert render_path.exists() and render_path.stat().st_size>10000, 'Fresh-open render missing/empty'
report={
  'asset':str(asset_path),
  'sha256':hashlib.sha256(asset_path.read_bytes()).hexdigest(),
  'fresh_open_success':True,
  'fresh_open_render':str(render_path),
  'scene':scene.name,
  'collection':col.name,
  'collection_object_count':len(col.all_objects),
  'object_type_counts':{t:sum(o.type==t for o in col.all_objects) for t in sorted({o.type for o in col.all_objects})},
  'evaluated_bounds_local_m':bounds,
  'external_file_images':external_images,
  'procedural_materials_only':not external_images,
  'asset_dimensions_m':[bounds[i][1]-bounds[i][0] for i in range(3)],
  'known_uncertainty':'Height/story and all interior arrangement remain estimated/schematic.'
}
report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
