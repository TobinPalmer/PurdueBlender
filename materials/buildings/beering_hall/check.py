import bpy
c=bpy.data.collections['Asset_beering_hall'];print('collections',[(x.name,x.hide_render) for x in bpy.data.collections]);print([(o.name,o.hide_render,list(o.matrix_world.translation)) for o in c.all_objects if 'Window' in o.name][:4]);print('exposure',bpy.context.scene.view_settings.exposure)
