import bpy,importlib.util
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent.parent;spec=importlib.util.spec_from_file_location('sunset_cloud_world',p/'lighting'/'sunset_cloud_world.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);s=bpy.context.scene;mod.build_world(s);s['campus_time']=18
camdata=bpy.data.cameras.new('GradientTestCamera');cam=bpy.data.objects.new('GradientTestCamera',camdata);s.collection.objects.link(cam);cam.location=(70,-112,38);cam.rotation_euler=(Vector((-7,17,70))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=39;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=4;s.render.resolution_x=640;s.render.resolution_y=400;s.render.resolution_percentage=100;s.render.filepath=str(p/'lighting'/'renders'/'world_gradient_test.png');bpy.ops.render.render(write_still=True)
