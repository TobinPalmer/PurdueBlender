import bpy, os, json
R=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=R+'/loeb.blend')
s=bpy.context.scene; dom=bpy.data.objects['Loeb_Mantaflow_Liquid_Domain']; bpy.context.view_layer.objects.active=dom
bpy.ops.fluid.free_all()
d=dom.modifiers[0].domain_settings; d.cache_directory='//cache_attempt3'; d.cache_frame_start=1; d.cache_frame_end=48; d.cache_type='ALL'; d.resolution_max=80
for o in s.objects:
    if o.name.startswith('Loeb_Liquid_Inflow'):
        o.hide_render=False; o.modifiers[0].show_render=True; o.modifiers[0].show_viewport=True
        o.modifiers[0].flow_settings.surface_distance=2
s.frame_set(1); bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend'); bpy.ops.fluid.bake_all()
stats=[]
for f in [12,24,48]:
    s.frame_set(f); ev=dom.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); stats.append({'frame':f,'vertices':len(me.vertices),'polygons':len(me.polygons)}); ev.to_mesh_clear()
    s.render.filepath=R+'/attempt3_frame_%03d.png'%f; bpy.ops.render.render(write_still=True)
json.dump(stats,open(R+'/attempt3_verification.json','w'),indent=2); bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend')
