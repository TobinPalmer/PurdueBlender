import bpy, json
asset=r'modular/buildings/massing_house_301841248_fe939c7.blend'
bpy.ops.wm.open_mainfile(filepath=asset)
scene=bpy.context.scene
root=bpy.data.objects.get('House_301841248')
coll=bpy.data.collections.get('Asset_massing_house_301841248_fe939c7')
assert scene.name=='Building_massing_house_301841248_fe939c7'
assert root and coll and list(coll.objects)==[root] and list(scene.objects)==[root]
assert root.get('interior_representation','').startswith('Schematic only')
assert root.get('roof_transition','').startswith('Continuous roof cover')
print('FRESH_OPEN_PASS',bpy.app.version_string,'objects',len(coll.objects),'root_vertices',len(root.data.vertices),'cutaway_preview_is_audit_render=true')
