import bpy,re,json,hashlib
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
rows=[]
for i in range(6):
 ds=sorted([o for o in bpy.data.objects if re.fullmatch(r'RAWL_2026_1086_Desk(?:\.\d{3})?',o.name)],key=lambda o:int(o.name.rsplit('.',1)[1]) if '.' in o.name else 0)[i*7:(i+1)*7]
 rows.append({'row':i,'desk_count':len(ds),'desk_center_z':round(sum(o.location.z for o in ds)/len(ds),3),'chair_center_z':round(sum(bpy.data.objects.get('RAWL_2026_1086_Chair'+o.name[len('RAWL_2026_1086_Desk'):]).location.z for o in ds)/len(ds),3)})
legs=[o for o in bpy.data.objects if o.name.startswith('RAWL_2026_DeskLeg')]
info={'fresh_reopen':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tier_rows':rows,'lifted_desk_legs':sum(bool(o.get('rawl_r10_lifted')) for o in legs),'desk_leg_total':len(legs),'tiers':[o.name for o in bpy.data.objects if o.name.startswith('RAWL_1086_R10_Schematic_Tier_')],'screen_objects':[o.name for o in bpy.data.objects if 'R10_Schematic_Projection_Surface' in o.name],'lectern_objects':[o.name for o in bpy.data.objects if 'R10_Schematic_Lectern' in o.name]}
Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch4_rawls\round10_classroom_validation.json').write_text(json.dumps(info,indent=2))
print(json.dumps(info,indent=2))
