import bpy, json, os
src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
shell=bpy.data.objects['KRCH structural shell | GIS outline']
assert shell.type=='MESH'
# The official project description identifies transparent public/social space on level one.
# Cut the facade plane behind the documented multi-level curtainwall so the lobby and stair are visible.
bpy.ops.mesh.primitive_cube_add(size=1, location=(16.15,-14.0,7.1))
cutter=bpy.context.object; cutter.name='TEMP | lobby glazing opening cutter'
cutter.dimensions=(19.7,2.6,15.3)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.view_layer.objects.active=shell
shell.select_set(True); cutter.select_set(False)
mod=shell.modifiers.new('Evidence-backed transparent lobby facade opening','BOOLEAN')
mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)
shell['facade_opening_note']='Central street-facing facade cut open behind the documented four-level curtainwall; preserves the GIS footprint and wall envelope. Source: Sasaki project description, first-floor Main Street transparent public/social space. Exact opening width is interpreted from facade imagery.'
shell['facade_opening_source']='https://www.sasaki.com/projects/purdue-university-krach-leadership-center/'
# Save only this Krach modular library.
bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'shell_vertices':len(shell.data.vertices),'shell_faces':len(shell.data.polygons),'opening':[6.3,26.0,-15.3,-12.7,-0.55,14.75]},indent=2))
