import bpy,json
c=bpy.data.collections['Asset_rawls_hall']
for pat in ['1086_Desk','1086_Chair','DeskSupport','ChairLeg','ChairBack','Door_','RAWL_2026_Core','RAWL_2026_1098','RAWL_2026_1011']:
 os=[o for o in c.all_objects if pat in o.name]
 print('PATTERN',pat,len(os))
 for o in os[:4]:print(' ',o.name,'loc',tuple(round(x,2) for x in o.location),'dim',tuple(round(x,2) for x in o.dimensions),'rot',round(o.rotation_euler.z,2))
