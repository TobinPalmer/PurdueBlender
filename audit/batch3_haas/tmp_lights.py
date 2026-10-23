import bpy
for o in bpy.context.scene.objects:
 if o.type=='LIGHT': print(o.name,o.data.type,o.data.energy,tuple(round(x,2) for x in o.location),o.hide_render)
