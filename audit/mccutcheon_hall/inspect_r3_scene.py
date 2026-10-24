import bpy,json
sc=bpy.data.scenes['Building_mccutcheon_hall']
out={'world':None,'lights':[],'settings':{}}
if sc.world:
 out['world']={'name':sc.world.name,'color':list(sc.world.color),'use_nodes':sc.world.use_nodes,'nodes':[{'name':n.name,'type':n.type} for n in sc.world.node_tree.nodes] if sc.world.use_nodes else []}
for o in bpy.data.objects:
 if o.type=='LIGHT': out['lights'].append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':getattr(o.data,'angle',None),'location':list(o.location),'rotation':list(o.rotation_euler)})
out['settings']={'engine':sc.render.engine,'resolution':[sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage],'view_transform':sc.view_settings.view_transform,'look':sc.view_settings.look,'exposure':sc.view_settings.exposure,'gamma':sc.view_settings.gamma}
print('MCUT_LIGHTS='+json.dumps(out))
