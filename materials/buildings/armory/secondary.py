import bpy,math
from mathutils import Vector

def secondary():
 for name,scale,rough,dist in [('Bedford_Indiana_Limestone',17,.74,.001),('Armory_Barre_Granite',65,.65,.0008),('Armory_Roof_Copper',1.4,.58,.0003),('Armory_Dark_Bronze',26,.36,.00012),('Armory_Dark_Oak',16,.43,.0004),('Campus_Teak_Wood_Bench',18,.5,.0004)]:
  m=bpy.data.materials.get(name)
  if not m:continue
  n=m.node_tree.nodes;l=m.node_tree.links;p=next(x for x in n if x.type=='BSDF_PRINCIPLED');base=p.inputs['Base Color'].default_value[:]
  tex=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=4
  l.new(tex.outputs['Object'],noise.inputs['Vector'])
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(c*.72 for c in base[:3])+(1,);ramp.color_ramp.elements[1].color=tuple(min(c*1.06,1) for c in base[:3])+(1,)
  if name=='Armory_Roof_Copper':
   ramp.color_ramp.elements[0].color=(.09,.14,.105,1);ramp.color_ramp.elements[1].color=(.27,.37,.28,1);p.inputs['Metallic'].default_value=.65
  l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.25;bump.inputs['Distance'].default_value=dist;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);p.inputs['Roughness'].default_value=rough
 m=bpy.data.materials['Solar_Ribbon_Glass'];p=next(x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.60,.68,.71,1);p.inputs['Transmission Weight'].default_value=.85;p.inputs['Roughness'].default_value=.12;p.inputs['IOR'].default_value=1.5;p.inputs['Alpha'].default_value=1

def setup():
 s=bpy.context.scene
 c=bpy.data.collections.new('Armory_Material_Preview');s.collection.children.link(c)
 def ob(name,data):
  o=bpy.data.objects.new(name,data);c.objects.link(o);return o
 cam=ob('Armory_Preview_Camera',bpy.data.cameras.new('Armory_Preview_Camera'));s.camera=cam
 sun=ob('Armory_Preview_Sun',bpy.data.lights.new('Armory_Preview_Sun','SUN'));sun.rotation_euler=(math.radians(30),math.radians(-25),math.radians(-30));sun.data.energy=2.5;sun.data.angle=.12
 s.world=bpy.data.worlds.new('Armory_Preview_Daylight');s.world.use_nodes=True;n=s.world.node_tree.nodes;n.clear();sky=n.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_elevation=.6;sky.sun_rotation=2.1;sky.sun_disc=False;bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.35;out=n.new('ShaderNodeOutputWorld');s.world.node_tree.links.new(sky.outputs[0],bg.inputs[0]);s.world.node_tree.links.new(bg.outputs[0],out.inputs[0])
 s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
 return cam

def aim(cam,loc,target,lens):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens

