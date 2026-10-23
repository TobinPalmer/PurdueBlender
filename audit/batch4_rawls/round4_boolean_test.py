import bpy,os,math
from mathutils import Vector
p=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene
wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];glass=bpy.data.objects['RAWL_North_Windows_Glass'];mw=glass.matrix_world
verts=[];faces=[]
for poly in glass.data.polygons:
 pts=[mw@glass.data.vertices[i].co for i in poly.vertices]
 if len(pts)!=4:continue
 cx=sum(v.x for v in pts)/4;cz=sum(v.z for v in pts)/4
 # expand the opening by about 7cm each side; preserve the measured facade slope
 front=[]
 for v in pts:
  side=-1 if v.x<cx else 1
  top=-1 if v.z<cz else 1
  x=v.x+side*.07;z=v.z+top*.06;y=v.y+(x-v.x)*(.597/54.727)
  front.append(Vector((x,y+.06,z)))
 back=[v+Vector((0,-1.2,0)) for v in front]
 base=len(verts);verts += [tuple(v) for v in front+back]
 faces += [tuple(base+i for i in [0,1,2,3]),tuple(base+i for i in [7,6,5,4])]
 for i in range(4):faces.append((base+i,base+(i+4),base+((i+1)%4+4),base+(i+1)%4))
mesh=bpy.data.meshes.new('R4_North_Window_Cutters_Mesh');mesh.from_pydata(verts,[],faces);mesh.update();cut=bpy.data.objects.new('R4_North_Window_Cutters_TEST',mesh);s.collection.objects.link(cut)
# Apply boolean to a temporary duplicate, keep original for this diagnostic render.
dup=wall.copy();dup.data=wall.data.copy();dup.name='R4_Masonry_Boolean_Test';s.collection.objects.link(dup);dup.hide_render=False;wall.hide_render=True
mod=dup.modifiers.new('R4_Window_Openings_TEST','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
bpy.context.view_layer.objects.active=dup;dup.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);cut.hide_render=True
print('wall faces before/after',len(wall.data.polygons),len(dup.data.polygons))
# use neutral facade daylight close view
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=750
w=bpy.data.worlds.new('R4_Boolean_Test_World');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.72,.8,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.7;s.world=w
ld=bpy.data.lights.new('R4_Boolean_Sun','SUN');ld.energy=2.0;l=bpy.data.objects.new('R4_Boolean_Sun',ld);s.collection.objects.link(l);l.rotation_euler=(math.radians(20),math.radians(-30),math.radians(-35))
camd=bpy.data.cameras.new('R4_Boolean_Camera');cam=bpy.data.objects.new('R4_Boolean_Camera',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(8,68,17);cam.rotation_euler=(Vector((8,10,11))-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=50
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_window_boolean_test_round4.png');bpy.ops.render.render(write_still=True)
