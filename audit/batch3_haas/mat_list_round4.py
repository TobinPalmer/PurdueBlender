import bpy
for m in bpy.data.materials:
 if any(s in m.name.lower() for s in ['stone','limestone','bedford','brick']):print(m.name,tuple(m.diffuse_color))
for o in bpy.data.objects:
 if o.name in ['HAAS_Corrected_GIS_Wall_Envelope','HAAS_Photo_Main_Hipped_Roof']:
  print(o.name,[m.name for m in o.data.materials])
