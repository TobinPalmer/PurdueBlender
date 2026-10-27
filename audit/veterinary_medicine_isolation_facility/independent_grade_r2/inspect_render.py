import bpy,json
s=bpy.context.scene
print(json.dumps({'render_engine':s.render.engine,'camera':s.camera.name if s.camera else None,'resolution':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps,'objects':len(s.objects),'world':s.world.name if s.world else None,'views':s.view_settings.view_transform},indent=2))
for m in bpy.data.materials:
 if m.use_nodes:
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs:
   print(m.name,tuple(round(float(x),3) for x in bs.inputs['Base Color'].default_value),round(float(bs.inputs['Roughness'].default_value),2),len(m.node_tree.nodes))
