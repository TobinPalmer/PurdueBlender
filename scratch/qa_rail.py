import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_american_railway_building_rail_fc0f9a2.blend')
print('all objects',len(bpy.data.objects),'materials')
for name in ('RAIL | warm red running-bond brick','RAIL | sealed warm concrete','RAIL | oak work surfaces','RAIL | dark charcoal membrane and metal'):
 m=bpy.data.materials.get(name);print(name,m.diffuse_color[:],[(n.type,[(i.name,getattr(i,'default_value',None)) for i in n.inputs if i.name in ('Base Color','Roughness','Metallic')]) for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'])
print('surface settings',bpy.context.scene.view_settings.exposure,bpy.context.scene.view_settings.gamma,bpy.context.scene.view_settings.look,bpy.context.scene.render.engine)
col=bpy.data.collections.get('Asset_massing_american_railway_building_rail_fc0f9a2');print('collection',len(col.objects));print('massing',bpy.data.objects.get('American Railway Building (RAIL)'))
