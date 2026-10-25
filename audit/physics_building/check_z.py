import bpy
for name in ['PHYS | limestone cornice','PHYS | limestone story belt','PHYS | estimated sloped red tile roof']:
 o=bpy.data.objects[name]; z=[v.co.z for v in o.data.vertices]; print(name,min(z),max(z))
