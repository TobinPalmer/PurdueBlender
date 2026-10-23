import bpy
s=bpy.context.scene
print('EXPOSURE',s.view_settings.exposure,'OVERRIDES',[(v.name,str(v.material_override)) for v in s.view_layers]);print('LIGHTS',[(o.name,o.data.energy) for o in s.objects if o.type=='LIGHT']);print('WALL',[(o.name,[m.name for m in o.data.materials]) for o in s.objects if 'Corrected' in o.name])
