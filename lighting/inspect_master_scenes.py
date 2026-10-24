import bpy,json
for s in bpy.data.scenes:
 print('SCENEINFO',json.dumps({'name':s.name,'objects':len(s.objects),'cameras':sum(o.type=='CAMERA' for o in s.objects),'placements':sum(o.name.startswith('Placement_') for o in s.objects),'world':s.world.name if s.world else None,'camera':s.camera.name if s.camera else None}))
