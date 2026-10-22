import bpy,sys,os,math,json
from mathutils import Vector
ROOT=os.path.abspath('.')
OUT=os.path.join(ROOT,'materials/buildings/beering_hall')
c=bpy.data.collections['Asset_beering_hall']
orig={o.name:[list(row) for row in o.matrix_world] for o in c.all_objects}
# Add fine-scale tactile variation without changing geometry or authored base colors.
def finish(m,scale,strength,distance,rough):
 n=m.node_tree.nodes; l=m.node_tree.links
 p=next(x for x in n if x.type=='BSDF_PRINCIPLED')
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=3
 tc=n.new('ShaderNodeTexCoord');l.new(tc.outputs['Object'],tex.inputs['Vector'])
 b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=distance;l.new(tex.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal'])
 ramp=n.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=max(0.05,rough-.09);ramp.inputs['To Max'].default_value=min(1,rough+.09);l.new(tex.outputs['Fac'],ramp.inputs['Value']);l.new(ramp.outputs['Result'],p.inputs['Roughness'])
for m in bpy.data.materials:
 name=m.name
 if 'Limestone' in name: finish(m,95,.22,.001,.66)
 elif 'Woodwork' in name or 'Oak' in name: finish(m,35,.13,.0007,.39)
 elif 'Leather' in name:finish(m,190,.19,.0005,.4)
 elif 'Carpet' in name:finish(m,230,.4,.001,.93)
 elif 'Terrazzo' in name:finish(m,55,.16,.0005,.27)
 elif 'Copper' in name:finish(m,12,.23,.001,.48)
 elif 'Bronze' in name:finish(m,150,.09,.00025,.31)
 elif 'Glass' in name:
  p=next(x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.07,.115,.15,1);p.inputs['Roughness'].default_value=.13;p.inputs['IOR'].default_value=1.48;p.inputs['Transmission Weight'].default_value=.32
# Helper invoked below, once available.
exec(open(os.path.join(OUT,'brick_call.py')).read())
# Studio collection: intentionally separate from export.
st=bpy.data.collections.get('MaterialReview_Beering') or bpy.data.collections.new('MaterialReview_Beering')
if st.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(st)
def add_obj(name,data):
 o=bpy.data.objects.new(name,data);st.objects.link(o);return o
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=add_obj('Beering_Review_Camera',bpy.data.cameras.new('Beering_Review_Camera'));bpy.context.scene.camera=cam
cam.location=(108,-122,62);aim(cam,(0,0,12));cam.data.lens=46
sun=add_obj('Beering_Review_Sun',bpy.data.lights.new('Beering_Review_Sun','SUN'));sun.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-35));sun.data.energy=2.4;sun.data.angle=.08
world=bpy.data.worlds.new('Beering_Review_Daylight');world.use_nodes=True
n=world.node_tree.nodes; l=world.node_tree.links;n.clear();sky=n.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_elevation=.6;sky.sun_rotation=2.1;bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.3;l.new(sky.outputs[0],bg.inputs['Color']);output=n.new('ShaderNodeOutputWorld');l.new(bg.outputs[0],output.inputs[0]);bpy.context.scene.world=world
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
pbr.pack_textures();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'modular/buildings/beering_hall.blend'))
assert all(orig[o.name]==[list(row) for row in o.matrix_world] for o in c.all_objects)
s.render.filepath=os.path.join(OUT,'hero.png');bpy.ops.render.render(write_still=True)
cam.location=(51,-52,13);aim(cam,(27,-20,10));cam.data.lens=48;s.render.filepath=os.path.join(OUT,'closeup.png');bpy.ops.render.render(write_still=True)
print('SUCCESS',len(c.all_objects))


