import bpy
from pathlib import Path
from mathutils import Vector
D=Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas')
C=bpy.data.collections['Asset_felix_haas_hall'];S=bpy.context.scene
S.render.engine='CYCLES';S.cycles.samples=18;S.cycles.use_denoising=True
S.render.resolution_percentage=100;S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-2.6;S.view_settings.gamma=1.0
for name,loc,energy,size,color in [('HAAS_R8_Key',(60,-50,65),1300,72,(1.0,.96,.9)),('HAAS_R8_Fill',(45,38,42),1700,70,(1.0,.97,.92))]:
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('HAAS Round8 QA Camera');cam=bpy.data.objects.new('HAAS Round8 QA Camera',camd);S.collection.objects.link(cam);S.camera=cam;camd.type='ORTHO'
def visibility(only_plan=False):
    for o in bpy.data.objects:
        in_asset=any(col.name=='Asset_felix_haas_hall' for col in o.users_collection)
        if not in_asset:continue
        plan=o.name.startswith('HAAS_Plan_')
        o.hide_render=(not plan if only_plan else plan)
def render(name,loc,target,scale,res=(1600,1280),only_plan=False):
    visibility(only_plan);S.render.resolution_x,S.render.resolution_y=res
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale
    S.render.filepath=str(D/name);bpy.ops.render.render(write_still=True);print('R8_RENDER',name)
render('exterior_final.png',(55,-55,38),(-6,0,6),82)
render('entrance_final.png',(70,-10,18),(9,0,4),40)
render('interior_plan_final.png',(-6,0,90),(-6,0,0),70,only_plan=True)
for name,loc,target,scale in [('elevation_east.png',(70,0,19),(-5,0,5),76),('elevation_west.png',(-72,0,19),(-5,0,5),76),('elevation_south.png',(-6,-72,19),(-6,0,5),68),('elevation_north.png',(-6,72,19),(-6,0,5),68)]:
    render(name,loc,target,scale,res=(1500,1050))


