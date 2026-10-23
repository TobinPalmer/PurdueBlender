import bpy,math,os,json
from mathutils import Vector
OUT=os.path.dirname(__file__);col=bpy.data.collections['Asset_rawls_hall'];nt=bpy.data.materials['RAWL_Purdue_Red_Brick'].node_tree
tex=next(n for n in nt.nodes if n.type=='TEX_BRICK');tc=next(n for n in nt.nodes if n.type=='TEX_COORD');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tc.outputs['Object'],sep.inputs[0]);geom=nt.nodes.new('ShaderNodeNewGeometry');ns=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Normal'],ns.inputs[0]);ab=nt.nodes.new('ShaderNodeMath');ab.operation='ABSOLUTE';nt.links.new(ns.outputs['X'],ab.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(ab.outputs[0],mix.inputs[0]);cx=nt.nodes.new('ShaderNodeCombineXYZ');cy=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(sep.outputs['X'],cx.inputs['X']);nt.links.new(sep.outputs['Y'],cy.inputs['X']);nt.links.new(sep.outputs['Z'],cx.inputs['Y']);nt.links.new(sep.outputs['Z'],cy.inputs['Y']);nt.links.new(cx.outputs[0],mix.inputs[1]);nt.links.new(cy.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],tex.inputs['Vector'])
# Desk support legs and chair backs; illustrative fixtures remain tagged.
def cube(n,p,d,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(m)
for o in list(col.all_objects):
 if '2026_1086_Desk' in o.name:
  p=o.location
  for dx in [-.48,.48]:cube('RAWL_2026_DeskSupport',(p.x+dx,p.y,.37),(.045,.40,.72),bpy.data.materials['RAWL_Dark_Bronze_Metal'])
 if '2026_1086_Chair' in o.name:
  p=o.location;cube('RAWL_2026_ChairBack',(p.x-.18,p.y,.68),(.06,.43,.43),bpy.data.materials['RAWL_Interior_CharcoalCarpet'])
for o in list(bpy.data.objects):
 if o.type=='CAMERA':
  # Legacy cameras still in campus coordinates: correct only camera transform.
  if o.location.x>200:o.location.x-=323.6582336425781;o.location.y+=409.62242126464844
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
# Render-only inspection settings, not saved.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.new('ReviewWorld');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.8,1,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
ld=bpy.data.lights.new('ReviewSun','SUN');ld.energy=2.5;lo=bpy.data.objects.new('ReviewSun',ld);s.collection.objects.link(lo);lo.rotation_euler=(.35,-.45,-.4)
cam=bpy.data.objects.new('ReviewCam',bpy.data.cameras.new('ReviewCam'));s.collection.objects.link(cam);s.camera=cam
def render(n,p,t,ortho=None):
 cam.location=p;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.ortho_scale=ortho or 50;cam.data.lens=25;s.render.filepath=os.path.join(OUT,n+'.png');bpy.ops.render.render(write_still=True)
render('exterior',(75,70,55),(7,0,10))
for o in list(bpy.data.objects):
 if o and not o.name.startswith('RAWL_2026_') and o.type=='MESH':o.hide_render=True
render('interior_plan',(6,0,85),(6,0,0),95)
render('classroom',(30,4,3.4),(32,-6,1))
json.dump({'export_collection':col.name,'objects':len(col.all_objects),'added_objects':len([o for o in col.all_objects if o.name.startswith('RAWL_2026_')]),'missing_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]},open(os.path.join(OUT,'checks.json'),'w'),indent=2)
