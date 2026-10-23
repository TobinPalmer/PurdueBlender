import bpy
p=bpy.types.ColorManagedViewSettings.bl_rna.properties['look']
print([i.identifier for i in p.enum_items])
