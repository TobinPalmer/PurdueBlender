import bpy
for o in bpy.data.objects:
 if o.type=='MESH' and any(k in o.name.lower() for k in ['path','walk','pav','site','courtyard','plaza','ground','curb','step','drive']):
  print(o.name,'loc',tuple(round(x,2) for x in o.location),'dim',tuple(round(x,2) for x in o.dimensions),'mats',[m.name if m else None for m in o.data.materials])
