import bpy, os, json
R=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=R+'/loeb.blend')
s=bpy.context.scene
for o in s.objects:
    if o.name.startswith('Loeb_Liquid_Inflow'): o.hide_render=False
dom=bpy.data.objects['Loeb_Mantaflow_Liquid_Domain']; d=dom.modifiers[0].domain_settings
d.cache_directory='//cache_attempt2'; d.cache_frame_end=48
bpy.context.view_layer.objects.active=dom
bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend')
bpy.ops.fluid.bake_all()
stats=[]
for f in [12,24,48]:
    s.frame_set(f); ev=dom.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); stats.append({'frame':f,'vertices':len(me.vertices),'polygons':len(me.polygons)}); ev.to_mesh_clear()
    s.render.filepath=R+'/attempt2_frame_%03d.png'%f; bpy.ops.render.render(write_still=True)
json.dump(stats,open(R+'/attempt2_verification.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend')
