import bpy,math
from mathutils import Vector
from pathlib import Path
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_R10']
# Rebuild a compact, source-colored clay tile material with per-face 2D UVs.
nt=m.node_tree;nt.nodes.clear();uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map='R10_Roof_UV';brick=nt.nodes.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1.0;brick.inputs['Color1'].default_value=(0.09,0.012,0.004,1);brick.inputs['Color2'].default_value=(0.055,0.006,0.0018,1);brick.inputs['Mortar'].default_value=(0.028,0.0035,0.001,1);brick.inputs['Brick Width'].default_value=.62;brick.inputs['Row Height'].default_value=.25;brick.inputs['Mortar Size'].default_value=.006
em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=3.5;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(uvn.outputs['UV'],brick.inputs['Vector']);nt.links.new(brick.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs['Emission'],out.inputs['Surface'])
for name in ['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 o=bpy.data.objects[name];mesh=o.data
 uv=mesh.uv_layers.get('R10_Roof_UV') or mesh.uv_layers.new(name='R10_Roof_UV')
 for poly in mesh.polygons:
  verts=[mesh.vertices[i].co.copy() for i in poly.vertices]
  edges=[]
  for i in range(len(verts)):
   d=verts[(i+1)%len(verts)]-verts[i];edges.append(d)
  axis_u=max(edges,key=lambda d:d.length).normalized();normal=poly.normal.normalized();axis_v=normal.cross(axis_u).normalized();origin=sum(verts,Vector())/len(verts)
  for li in poly.loop_indices:
   vi=mesh.loops[li].vertex_index;delta=mesh.vertices[vi].co-origin
   uv.data[li].uv=(delta.dot(axis_u),delta.dot(axis_v))
 mesh.update();o.data.materials.clear();o.data.materials.append(m);o['round10_roof']='Tile pattern mapped in each hipped-roof plane using metric local UVs; red-clay emissive balance chosen for even face color. Tile dimensions/profile remain estimates.'
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=8;S.cycles.use_denoising=True;S.render.resolution_x=1200;S.render.resolution_y=960;S.render.resolution_percentage=100;S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-3.0
for n in ['HAAS_R9_Key','HAAS_R9_Fill','HAAS Round9 QA Camera','HAAS Round10 preview']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
for name,loc,energy,size in [('HAAS_R9_Key',(60,-50,65),300,72),('HAAS_R9_Fill',(0,0,80),5000,100)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('HAAS Round10 preview');cam=bpy.data.objects.new('HAAS Round10 preview',camd);S.collection.objects.link(cam);S.camera=cam;camd.type='ORTHO';cam.location=(55,-55,38);cam.rotation_euler=(Vector((-6,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=82
for o in bpy.data.objects:
 if any(col.name=='Asset_felix_haas_hall' for col in o.users_collection):o.hide_render=o.name.startswith('HAAS_Plan_')
S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/roof_uniform_preview.png';bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
