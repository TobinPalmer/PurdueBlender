import bpy, json
out=[]
for sc in bpy.data.scenes:
 out.append({'scene':sc.name,'cam':sc.camera.name if sc.camera else None,'engine':sc.render.engine,'res':[sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage], 'filepath':sc.render.filepath})
print(json.dumps(out))
