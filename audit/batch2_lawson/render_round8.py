import bpy, os, sys
from mathutils import Vector
ASSET=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend';OUT=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson'
mode='cutaway'
if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+1:mode=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=ASSET);scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.55
scene.render.film_transparent=False
world=scene.world
if not world:world=bpy.data.worlds.new('Lawson R4 temporary render world');scene.world=world
world.use_nodes=True;bg=world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.17,.19,.22,1);bg.inputs['Strength'].default_value=.34
hide_names={'LWSN_Exterior_Brick','LWSN_Limestone_Bands','LWSN_Window_Glazing','LWSN_Window_Frames','LWSN_Rotunda_Curtain_Glass','LWSN_Rotunda_Spandrel_Panels','LWSN_Rotunda_Mullions','LWSN_Rotunda_Parapet_Coping','LWSN_Roof_Surface','LWSN_Mechanical_Penthouse','LWSN_Rooftop_Mechanical_Units','LWSN_R8_North_GIS_Footprint_Closure'}
hidden=[]
for ob in list(bpy.data.objects):
    if ob and ((mode!='exterior' and ob.name in hide_names) or ob.type=='LIGHT'):
        hidden.append((ob,ob.hide_render));ob.hide_render=True
floor=bpy.data.objects.get('LWSN_First_Floor_Surface')
mat=bpy.data.materials.new('LWSN_R8_TEMP_Cutaway_Floor');mat.diffuse_color=(.30,.34,.36,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.30,.34,.36,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.85
if floor and mode!='exterior':floor.data.materials.clear();floor.data.materials.append(mat)
def area(name,loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='LWSN_R8_TEMP_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def render_cam(name,loc,target,scale,path,res):
    bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.name='LWSN_R8_TEMP_'+name;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;scene.camera=c
    scene.render.resolution_x=res[0];scene.render.resolution_y=res[1];scene.render.filepath=path;bpy.ops.render.render(write_still=True)
if mode=='exterior':
    scene.view_settings.exposure=.35;scene.render.resolution_x=1400;scene.render.resolution_y=950
    area('Exterior_Key',(15,-50,46),8500,35,(0,0,5));area('Exterior_Fill',(-42,-32,22),3500,28,(0,-5,6))
    bpy.ops.object.light_add(type='SUN',location=(0,0,30));sun=bpy.context.object;sun.name='LWSN_R8_TEMP_Exterior_Sun';sun.data.energy=1.25;sun.rotation_euler=(.42,-.35,-.55)
    render_cam('Exterior_Camera',(44,-78,32),(0,-1,6),106,OUT+r'/exterior_round8.png',(1400,950))
elif mode=='cutaway':
    scene.view_settings.exposure=.85;scene.render.resolution_x=1600;scene.render.resolution_y=1200;area('Cutaway_Key',(22,-38,50),6500,30,(0,-2,0));area('Cutaway_Fill',(-35,-8,28),3800,22,(0,-3,0));render_cam('FirstFloor_Cutaway',(36,-43,65),(0,-1,1),94,OUT+r'/interior_cutaway_round8.png',(1600,1200))
elif mode=='entry':
    # Isolate the GIS-matched vestibule with the structural wall behind it;
    # omit interior partitions so the outside entrance reads as one feature.
    keep_prefix=('LWSN_R8_', 'LWSN_Rotunda_')
    keep_exact={'LWSN_First_Floor_Surface','LWSN_Foundation_Base','LWSN_Exterior_Brick','LWSN_Limestone_Bands','LWSN_Window_Glazing','LWSN_Window_Frames'}
    for ob in list(bpy.data.objects):
        if not ob or ob.name in keep_exact or ob.name.startswith(keep_prefix):continue
        ob.hide_render=True
    scene.view_settings.exposure=.15;scene.render.resolution_x=1400;scene.render.resolution_y=1000;area('Entry_Key',(18,-31,8),2600,10,(11.55,-39.24,2));area('Entry_Fill',(4,-45,5),950,8,(11.55,-39.24,2));render_cam('EntryLobby_Detail',(14,-49,5.5),(11.55,-39.24,2),13.5,OUT+r'/entry_lobby_round8.png',(1400,1000))
elif mode=='commons':
    scene.view_settings.exposure=.0;scene.render.resolution_x=1400;scene.render.resolution_y=1000;area('Commons_Key',(20,-14,9),1800,10,(12.77,-8.45,2));area('Commons_Fill',(18,-2,7),900,8,(12.77,-8.45,2));render_cam('Commons_VideoWall_FaceOn',(25,-8.45,2.7),(12.77,-8.45,2.0),7.4,OUT+r'/commons_wall_round8.png',(1400,1000))
else:raise ValueError('mode must be cutaway, entry, or commons')
print('Rendered',mode,'from saved/reopened source')
