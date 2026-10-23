import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];glass=bpy.data.objects['RAWL_North_Windows_Glass'];mw=glass.matrix_world
verts=[];faces=[]
for poly in glass.data.polygons:
 pts=[mw@glass.data.vertices[i].co for i in poly.vertices]
 if len(pts)!=4:continue
 cx=sum(v.x for v in pts)/4;cz=sum(v.z for v in pts)/4;front=[]
 for v in pts:
  side=-1 if v.x<cx else 1;top=-1 if v.z<cz else 1;x=v.x+side*.08;z=v.z+top*.08;y=v.y+(x-v.x)*(.597/54.727)
  front.append(Vector((x,y+.04,z)))
 back=[v+Vector((0,-1.5,0)) for v in front];base=len(verts);verts += [tuple(v) for v in front+back]
 faces += [tuple(base+i for i in [0,1,2,3]),tuple(base+i for i in [7,6,5,4])]
 for i in range(4):faces.append((base+i,base+i+4,base+((i+1)%4+4),base+(i+1)%4))
mesh=bpy.data.meshes.new('R4_CUTTER_M');mesh.from_pydata(verts,[],faces);mesh.update();cut=bpy.data.objects.new('R4_CUTTER',mesh);s.collection.objects.link(cut)
dup=wall.copy();dup.data=wall.data.copy();dup.name='R4_Masonry_BoolDiag';s.collection.objects.link(dup);wall.hide_render=True
mod=dup.modifiers.new('R4_Openings','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=dup;dup.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);cut.hide_render=True
m=bpy.data.materials.new('R4_EMIT_DIAG');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.02,.4,1,1);e.inputs['Strength'].default_value=2;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);glass.data.materials.clear();glass.data.materials.append(m)
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
ld=bpy.data.lights.new('R4_DiagSun','SUN');ld.energy=2.2;l=bpy.data.objects.new('R4_DiagSun',ld);s.collection.objects.link(l);l.rotation_euler=(math.radians(24),math.radians(-30),math.radians(-35))
cd=bpy.data.cameras.new('R4_DiagCam');c=bpy.data.objects.new('R4_DiagCam',cd);s.collection.objects.link(c);c.location=(76,73,58);c.rotation_euler=(Vector((2,0,12))-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=102;s.camera=c
print('wall face counts',len(wall.data.polygons),len(dup.data.polygons));s.render.filepath=os.path.abspath('audit/batch4_rawls/north_window_boolean_emission_round4.png');bpy.ops.render.render(write_still=True)
