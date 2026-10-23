import bpy,os,json
from mathutils import Vector
P=os.path.abspath('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_hicks')
s=bpy.context.scene;c=bpy.data.collections['Asset_hicks_library'];sub=bpy.data.collections['HIKS_2013_Study_Furnishing_Interpretation']
m=bpy.data.materials.new('HIKS_Study_Ceiling_Light');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.8,.78,.72,1);b.inputs['Emission Color'].default_value=(1,.94,.8,1);b.inputs['Emission Strength'].default_value=3
for x in [-8.5,8.5]:
 for y in [-4,0,4]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,-2.15));o=bpy.context.object;o.name='HIKS_Study_Linear_Luminaire';o.dimensions=(1.2,.22,.07);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for cc in list(o.users_collection):cc.objects.unlink(o)
  sub.objects.link(o);o.data.materials.append(m);o['evidence']='Suspended linear ceiling lighting supported by2013 interior photo; estimated placement'
# Leave evidence lights/camera outside export; master appearance must be lit by scene environment.
cam=s.camera;cam.location=(-9,-6,-3.65);cam.rotation_euler=(Vector((-8,5,-4.35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22
s.render.filepath=P+'/interior.png';bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
# exterior sunlight proof
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
ld=bpy.data.lights.new('ReviewSun','SUN');ld.energy=3;o=bpy.data.objects.new('ReviewSun',ld);s.collection.objects.link(o);o.rotation_euler=(.3,-.4,-.5)
cam.location=(36,38,27);cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48
s.render.filepath=P+'/exterior.png';bpy.ops.render.render(write_still=True)
open(P+'/technical.json','w').write(json.dumps({'export_objects':len(c.all_objects),'missing_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))],'frame':'unchanged local geometry, ground0/subterranean-5.304 and-9.449','materials':len(bpy.data.materials)},indent=2))
