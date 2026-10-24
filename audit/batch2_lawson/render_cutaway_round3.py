import bpy
from mathutils import Vector
asset=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
out=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/interior_cutaway_round3.png'
bpy.ops.wm.open_mainfile(filepath=asset)
coll=bpy.data.collections['Asset_lawson_hall']
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.55
scene.world.color=(.12,.12,.12)
exterior={'LWSN_Exterior_Brick','LWSN_Limestone_Bands','LWSN_Window_Glazing','LWSN_Window_Frames','LWSN_Rotunda_Curtain_Glass','LWSN_Rotunda_Spandrel_Panels','LWSN_Rotunda_Mullions','LWSN_Rotunda_Parapet_Coping','LWSN_Roof_Surface','LWSN_Mechanical_Penthouse','LWSN_Rooftop_Mechanical_Units'}
for o in coll.all_objects:
    if o and o.name in exterior:o.hide_render=True
for name,loc,power,size,target in [('Key',(15,-34,52),2400,30,(0,0,1)),('Fill',(-36,-12,30),900,24,(0,0,1))]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='LWSN_R3_TEMP_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(42,-48,54));c=bpy.context.object;c.name='LWSN_R3_TEMP_Interior_Cutaway';c.rotation_euler=(Vector((0,0,1))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=94;scene.camera=c
scene.render.filepath=out;bpy.ops.render.render(write_still=True)
print('Reopened source and rendered revised cutaway:',out)

