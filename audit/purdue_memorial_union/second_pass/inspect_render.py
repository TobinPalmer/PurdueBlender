"""Read-only fresh-open inspection and neutral PMU review renders. Never saves the asset."""
import bpy, sys, json, hashlib, argparse, math
from pathlib import Path
from mathutils import Vector

p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--views',default='south,southwest,roof,entry');p.add_argument('--samples',type=int,default=12);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
col=bpy.data.collections['Asset_purdue_memorial_union']
rows=[]
for o in col.all_objects:
    pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    rows.append(dict(name=o.name,type=o.type,bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],matrix=[list(r) for r in o.matrix_world],materials=[m.name if m else None for m in getattr(o.data,'materials',[])]))
record=dict(asset=bpy.data.filepath,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),collection=col.name,objects=rows,external_images=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file],materialless=[o.name for o in col.all_objects if o.type=='MESH' and not o.data.materials])
(out/'inspection.json').write_text(json.dumps(record,indent=2))
scene=bpy.context.scene
for o in scene.objects:
    if o.type in {'LIGHT','CAMERA'}:o.hide_render=True
scene.render.engine='CYCLES';scene.cycles.samples=a.samples
scene.cycles.use_denoising=True
scene.render.resolution_x=1120;scene.render.resolution_y=840;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('PMU_Review_Neutral');scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.65,.68,.72,1);bg.inputs['Strength'].default_value=.55
sun_data=bpy.data.lights.new('PMU_Review_Sun','SUN');sun_data.energy=2;sun_data.angle=.15
sun=bpy.data.objects.new('PMU_Review_Sun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(30),math.radians(-25),math.radians(-25))
scene.view_settings.view_transform='AgX'
camera_data=bpy.data.cameras.new('PMU_Review_Camera');camera=bpy.data.objects.new('PMU_Review_Camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO'
views={'south':((0,-230,19),(0,0,16),140),'north':((0,230,24),(0,0,15),140),'east':((230,0,24),(0,0,15),145),'west':((-230,0,24),(0,0,15),145),'southwest':((-155,-200,100),(0,0,12),165),'southeast':((160,-200,100),(0,0,12),165),'roof':((0,0,230),(0,0,0),145),'entry':((10.25,-150,16),(10.25,-44,15),34)}
settings={}
for name in a.views.split(','):
    pos,target,scale=views[name];camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=scale
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    settings[name]=dict(position=pos,target=target,ortho_scale=scale)
(out/'render_settings.json').write_text(json.dumps(dict(views=settings,samples=a.samples,engine=scene.render.engine,resolution=[1120,840]),indent=2))
print('PMU_INSPECTION_COMPLETE',record['sha256'],len(rows))
