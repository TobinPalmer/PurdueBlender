import bpy
s=bpy.data.scenes['Building_walc'].display.shading
print('settings',[(p.identifier,getattr(s,p.identifier,None)) for p in s.bl_rna.properties if p.identifier in ('light','studio_light','studiolight_rotate_z','show_shadows','show_cavity','background_type','color_type','show_specular_highlight','single_color')])
print('studio',[(x.name,x.type) for x in bpy.context.preferences.studio_lights])
