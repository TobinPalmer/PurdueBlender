import bpy, json, hashlib
from pathlib import Path
asset = Path(r'modular/buildings/massing_beta_theta_pi_fid826.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(asset))
collection = bpy.data.collections['Asset_massing_beta_theta_pi_fid826']
roof = bpy.data.objects['GIS_FID826_Continuous_Closed_RoofShell']
bm_mesh = roof.data
bad_faces=[]
for obj in collection.objects:
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            if poly.area < 1e-8:
                bad_faces.append((obj.name, poly.index, poly.area))
roof_up=sum(poly.normal.z > 0.05 for poly in bm_mesh.polygons)
report={
  'fresh_open':'passed', 'scene':bpy.context.scene.name, 'collection':collection.name,
  'collection_objects':len(collection.objects), 'mesh_objects':sum(o.type=='MESH' for o in collection.objects),
  'materials':len({m.name for o in collection.objects if o.type=='MESH' for m in o.data.materials if m}),
  'external_image_dependencies':sum(1 for im in bpy.data.images if im.source=='FILE' and im.packed_file is None),
  'roof_vertices':len(bm_mesh.vertices), 'roof_faces':len(bm_mesh.polygons),
  'roof_upward_faces':roof_up, 'roof_upward_fraction':roof_up/len(bm_mesh.polygons),
  'roof_zero_area_faces':sum(poly.area<1e-8 for poly in bm_mesh.polygons),
  'all_mesh_zero_area_faces':len(bad_faces), 'all_mesh_zero_area_examples':bad_faces[:10],
  'sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper()
}
print('FRESH_OPEN_REPORT',json.dumps(report,sort_keys=True))
