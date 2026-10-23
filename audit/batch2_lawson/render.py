import bpy,math,json
from mathutils import Vector
m=bpy.data.materials['LWSN_Purdue_Red_Brick'];nt=m.node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_BRICK');geo=next(n for n in nt.nodes if n.type=='NEW_GEOMETRY');pos=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],pos.inputs[0]);normal=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Normal'],normal.inputs[0]);ab=nt.nodes.new('ShaderNodeMath');ab.operation='ABSOLUTE';nt.links.new(normal.outputs['X'],ab.inputs[0]);cmp=nt.nodes.new('ShaderNodeMath');cmp.operation='GREATER_THAN';cmp.inputs[1].default_value=.5;nt.links.new(ab.outputs[0],cmp.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(cmp.outputs[0],mix.inputs[0]);nt.links.new(pos.outputs['X'],mix.inputs[1]);nt.links.new(pos.outputs['Y'],mix.inputs[2]);comb=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(mix.outputs[0],comb.inputs['X']);nt.links.new(pos.outputs['Z'],comb.inputs['Y']);nt.links.new(comb.outputs[0],tex.inputs['Vector'])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.world.color=(.25,.25,.25)
bpy.ops.object.light_add(type='AREA',location=(10,-10,45));bpy.context.object.data.energy=17000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=40
bpy.ops.object.light_add(type='SUN',location=(0,0,30));bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.5,-.3,-.6)
def view(name,p,target,ortho):
 bpy.ops.object.camera_add(location=p);c=bpy.context.object;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=ortho;s.camera=c;s.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/'+name+'.png';bpy.ops.render.render(write_still=True)
view('exterior',(67,-93,65),(0,0,5),115)
for o in bpy.data.collections['Asset_lawson_hall'].all_objects:
 if o and any(k in o.name for k in ['Roof','Penthouse','Mechanical','Exterior_Brick','Limestone_Bands','Window_','Rotunda_']):o.hide_render=True
view('interior_plan',(0,-5,100),(0,-5,0),91)
view('classroom',(30,-10,30),(5,9,1),35)
open('audit/batch2_lawson/technical.json','w').write(json.dumps({'objects':len(bpy.data.collections['Asset_lawson_hall'].all_objects),'missing_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file],'saved_reopened':True},indent=2))

