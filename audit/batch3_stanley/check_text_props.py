import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
o=bpy.data.objects.get('SC_Portico_3D_Text');print('visible_shadow',hasattr(o,'visible_shadow'),'visible_diffuse',hasattr(o,'visible_diffuse'),'visible_glossy',hasattr(o,'visible_glossy'))
for p in o.bl_rna.properties: 
 if 'shadow' in p.identifier.lower():print(p.identifier)
print('materials',[(m.name,m.diffuse_color[:]) for m in bpy.data.materials if 'gold' in m.name.lower()])
