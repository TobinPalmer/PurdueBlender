import bpy
for o in bpy.data.objects:
 if o.type=='LIGHT':print(o.name,o.data.type,o.data.energy,tuple(o.location),o.hide_render)
for m in bpy.data.materials:
 if 'Roof' in m.name or 'RedClay' in m.name:print('MAT',m.name,tuple(m.diffuse_color))
