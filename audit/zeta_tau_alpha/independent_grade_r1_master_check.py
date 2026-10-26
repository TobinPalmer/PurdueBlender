import bpy,json,os,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'purdue_campus_master.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
marker_name='Placement_massing_zeta_tau_alpha_af8a443'
objs=[o for o in bpy.data.objects if o.name==marker_name]
instances=[]
for o in bpy.data.objects:
 if o.instance_type=='COLLECTION' and o.instance_collection and 'zeta_tau_alpha' in o.name.lower():
  instances.append({'name':o.name,'collection':o.instance_collection.name,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale)})
for o in objs:
 instances.append({'name':o.name,'type':o.type,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'instance_type':o.instance_type,'collection':o.instance_collection.name if o.instance_collection else None})
out={'master_path':str(path),'master_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scene':bpy.context.scene.name,'matches':instances,'object_names_containing_zta':[o.name for o in bpy.data.objects if 'zeta' in o.name.lower() or 'zta' in o.name.lower()]}
Path(__file__).with_name('independent_grade_r1_master_check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
