import bpy,json,hashlib
from pathlib import Path
p=Path(bpy.data.filepath);col=bpy.data.collections.get('Asset_massing_veterinary_medicine_isolation_facility_66d1305')
objects=list(col.all_objects) if col else []; meshes=[o for o in objects if o.type=='MESH']
vertices=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
materials=sorted({m.name for o in meshes for m in o.data.materials if m})
missing=[o.name for o in meshes if not o.data.materials]
images=[{'name':i.name,'filepath':i.filepath,'packed':i.packed_file is not None} for i in bpy.data.images if i.source=='FILE']
libraries=[{'name':l.name,'path':l.filepath} for l in bpy.data.libraries if l.filepath]
probe={'fresh_open':True,'blender_version':bpy.app.version_string,'asset_path':str(p),'asset_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scene':bpy.context.scene.name,'collection':col.name if col else None,'object_count':len(objects),'mesh_count':len(meshes),'vertex_count':sum(len(o.data.vertices) for o in meshes),'face_count':sum(len(o.data.polygons) for o in meshes),'bounds_local_m':{'min':[min(v[i] for v in vertices) for i in range(3)],'max':[max(v[i] for v in vertices) for i in range(3)]},'material_count':len(materials),'materials':materials,'mesh_objects_without_materials':missing,'file_image_dependencies':images,'linked_libraries':libraries,'opening_and_stall_object_counts':{'service_door':sum('service door' in o.name.lower() for o in objects),'stall_doors':sum('protocol stall door' in o.name.lower() for o in objects),'interior_view_windows':sum('viewing window' in o.name.lower() for o in objects),'door_vision_lites':sum('door vision lite' in o.name.lower() for o in objects)}}
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\veterinary_medicine_isolation_facility\independent_grade_r2\fresh_open_probe.json')
out.write_text(json.dumps(probe,indent=2),encoding='utf-8');print(json.dumps(probe,indent=2))
