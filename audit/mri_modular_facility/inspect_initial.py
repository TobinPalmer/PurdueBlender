"""Initial metrics for the original MRI1 massing before rebuild."""
import json,bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
obj=bpy.data.objects['MRI Modular Facility (MRI1)']
col=bpy.data.collections['Asset_massing_mri_modular_facility_mri1_a93e22b']
pts=[obj.matrix_world@v.co for v in obj.data.vertices]
lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
r={'original_asset_path':bpy.data.filepath,'object':obj.name,'collection':col.name,'object_type':obj.type,'collection_object_count':len(col.objects),'vertices':len(obj.data.vertices) if obj.type=='MESH' else None,'faces':len(obj.data.polygons) if obj.type=='MESH' else None,'bounds_xyz_m':{'min':lo,'max':hi},'materials':[m.name for m in obj.data.materials] if obj.type=='MESH' else [],'modifiers':[m.name for m in obj.modifiers],'identity_transform':list(obj.location)==[0.0,0.0,0.0] and list(obj.rotation_euler)==[0.0,0.0,0.0] and list(obj.scale)==[1.0,1.0,1.0]}
(ROOT/'audit'/'mri_modular_facility'/'initial_check.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print('MRI1_INITIAL='+json.dumps(r))
