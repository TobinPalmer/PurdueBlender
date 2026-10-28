"""Render saved Haas revisions consistently; creates no changes in the source library."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector

D=Path(__file__).resolve().parent
input_asset_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
tag=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'baseline'
daylight='--daylight' in sys.argv
only=sys.argv[sys.argv.index('--only')+1].split(',') if '--only' in sys.argv else None
exposure=.7 if daylight else 0
world_strength=.8 if daylight else .4
out=D/tag/'renders';out.mkdir(parents=True,exist_ok=True)
S=bpy.context.scene;C=bpy.data.collections['Asset_felix_haas_hall']
for o in bpy.data.objects:
    if o.type in ('LIGHT','CAMERA'):
        o.hide_render=True
for o in C.all_objects:
    if o is None:continue
    if o.name.startswith(('HAAS_Plan_','HAAS_Plan_Label_')):o.hide_render=True
S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True
S.render.resolution_x=1000;S.render.resolution_y=800;S.render.resolution_percentage=100
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=0;S.view_settings.gamma=1
S.view_settings.exposure=exposure
world=bpy.data.worlds.new('Haas_SecondPass_NeutralWorld');world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.7,.75,.8,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.4;S.world=world
if daylight:world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.8,.8,.8,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=world_strength
def light(name,loc,power,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector((-10,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
light('SecondPass_Key',(20,-35,55),15000,50)
light('SecondPass_Fill',(-40,30,40),11000,40)
camdata=bpy.data.cameras.new('SecondPass_Camera');cam=bpy.data.objects.new('SecondPass_Camera',camdata)
S.collection.objects.link(cam);S.camera=cam;camdata.type='ORTHO'
views=[
('east',(85,0,7),(-6,0,7),66),('west',(-100,0,7),(-10,0,7),66),
('north',(-10,100,7),(-10,0,7),55),('south',(-10,-100,7),(-10,0,7),55),
('southeast',(65,-65,38),(-6,0,6),83),('northwest',(-75,65,38),(-10,0,6),83),
('roof',(-6,0,100),(-6,0,0),70),('west_windows',(-55,0,10),(-26,0,8.5),28),
('entrance',(55,-20,15),(11,0,5),36),
('front_detail',(60,0,6.5),(12,0,6.5),28),
('rear_entry',(-60,12,7),(-26,12,3.5),20)]
settings=[]
for name,position,target,scale in views:
    if only and name not in only:continue
    cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale
    S.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True)
    settings.append({'view':name,'camera_position_m':position,'target_m':target,'ortho_scale_m':scale,'path':f'{tag}/renders/{name}.png'})
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==input_asset_sha256,'Source changed while rendering; discard this render set.'
record={'asset_sha256':input_asset_sha256,'render_engine':S.render.engine,'samples':12,'exposure':exposure,'world_strength':world_strength,'daylight_variant':daylight,'resolution':[1000,800],'views':settings,'library_saved_by_renderer':False}
(out.parent/'render_settings.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('REVIEW_RENDER_COMPLETE',tag)
