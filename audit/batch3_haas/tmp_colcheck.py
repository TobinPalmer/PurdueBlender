import bpy
for n in ['Reference_Incompatible_Geometry_felix_haas_hall','Asset_felix_haas_hall']:
 c=bpy.data.collections[n];print(n,'hide_render',c.hide_render,'hide_viewport',c.hide_viewport)
