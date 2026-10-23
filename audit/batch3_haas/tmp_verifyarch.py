import bpy
for n in ['HAAS_Beltcourse2_North','HAAS_Beltcourse2_West']:
 o=bpy.data.objects.get(n);print(n,o, o.hide_render if o else None,[c.name for c in o.users_collection] if o else None)
A=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall');print('archive',A.hide_render,A.hide_viewport)
