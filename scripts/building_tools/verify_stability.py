import bpy,json,os
s=bpy.context.scene
original=s.camera
s.render.resolution_percentage=25
s.render.image_settings.file_format='PNG'
r=[]
names=[original.name,'Cam_97_HAAS_East_MemorialSteps_Hero','Cam_98_HAAS_1903_Memorial_Rotunda_Interior']
for i,name in enumerate(names):
 c=bpy.data.objects.get(name)
 if c is None: continue
 s.camera=c
 s.render.filepath=bpy.path.abspath('//stability_render_%d.png'%i)
 bpy.ops.render.render(write_still=True)
 r.append({'camera':name,'render':'PASS'})
open(bpy.path.abspath('//stability_verification.json'),'w').write(json.dumps(r,indent=2))
print('STABILITY_RENDER_PASS',json.dumps(r))
