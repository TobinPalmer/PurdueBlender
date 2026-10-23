import bpy, os, json
from mathutils import Vector
blend=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=blend);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
# Search for a genuine clear sightline from any pane to one of the source-plan 1086 desks.
glasses=[o for o in bpy.data.objects if o.type=='MESH' and 'Glass' in o.name and 'RAWL_' in o.name]
desks=[o for o in bpy.data.objects if o.type=='MESH' and '1086_Desk' in o.name]
candidates=[]
for go in glasses:
 for face in go.data.polygons:
  pts=[go.matrix_world@go.data.vertices[i].co for i in face.vertices]
  pc=sum(pts,Vector())/len(pts)
  normal=(go.matrix_world.to_3x3()@face.normal).normalized()
  for desk in desks:
   # Aim at the modeled desktop surface, not above it.
   target=desk.matrix_world.translation+Vector((0,0,.045))
   delta=target-pc;dist=delta.length
   if dist>26 or dist<.5:continue
   d=delta.normalized();origin=pc-d*3.0;remaining=dist+3.2;hits=[]
   for _ in range(12):
    hit,loc,n,fi,obj,ma=s.ray_cast(dg,origin,d,distance=remaining)
    if not hit:break
    hits.append(obj.name);step=(loc-origin).length+.012;remaining-=step
    if remaining<=0:break
    origin=loc+d*.012
   if hits and hits[0]==go.name and desk.name in hits:
    candidates.append({'glass':go.name,'pane_center':[round(q,3) for q in pc],'desk':desk.name,'desk_center':[round(q,3) for q in target],'distance':round(dist,3),'hits':hits})
print('SIGHTLINE_CANDIDATES',json.dumps(candidates[:12],indent=2))
with open('audit/batch4_rawls/round6_1086_sightline_candidates.json','w') as f:json.dump(candidates,f,indent=2)
# Overlay the precise 2024 first-floor plan image with the saved plan-derived geometry.
for o in s.objects:o.hide_render=not (o.name.startswith('RAWL_2026_Plan') or 'RAWL_2026_1086_' in o.name)
wallmat=bpy.data.materials.new('R6_Overlay_PlanWall_Contrast');wallmat.use_nodes=True;wallmat.diffuse_color=(.08,.11,.14,1)
wb=next(n for n in wallmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');wb.inputs['Base Color'].default_value=(.055,.08,.105,1);wb.inputs['Roughness'].default_value=.8
for o in s.objects:
 if not o.hide_render and o.name.startswith('RAWL_2026_Plan') and o.type=='MESH':o.data.materials.clear();o.data.materials.append(wallmat)
img=bpy.data.images.load(os.path.abspath('audit/batch4_rawls/plan.png'),check_existing=True)
verts=[(75.342,25.622,-.06),(75.342,-32.938,-.06),(-47.538,-32.938,-.06),(-47.538,25.622,-.06)]
mesh=bpy.data.meshes.new('R6_2024_Plan_Reference_Image_Mesh');mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
for loop,coord in zip(mesh.polygons[0].loop_indices,[(0,1),(1,1),(1,0),(0,0)]):uv.data[loop].uv=coord
plane=bpy.data.objects.new('R6_2024_FirstFloor_Plan_Overlay_RenderOnly',mesh);s.collection.objects.link(plane)
mat=bpy.data.materials.new('R6_2024_Plan_Reference_Image_Material');mat.use_nodes=True;mat.node_tree.nodes.clear();out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');em=mat.node_tree.nodes.new('ShaderNodeEmission');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;mat.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs['Emission'],out.inputs['Surface']);mesh.materials.append(mat)
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
w=bpy.data.worlds.new('R6_Plan_Overlay_World');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.82,.84,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.7;s.world=w
cd=bpy.data.cameras.new('R6_Plan_Overlay_Camera');cam=bpy.data.objects.new('R6_Plan_Overlay_Camera',cd);s.collection.objects.link(cam);s.camera=cam;cam.location=(10,-2,85);cam.rotation_euler=(0,0,0);cd.type='ORTHO';cd.ortho_scale=88
ld=bpy.data.lights.new('R6_Plan_Overlay_Key','AREA');ld.energy=4000;ld.size=45;lo=bpy.data.objects.new('R6_Plan_Overlay_Key',ld);s.collection.objects.link(lo);lo.location=(10,-2,50);lo.rotation_euler=(0,0,0)
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.abspath('audit/batch4_rawls/2024_plan_geometry_overlay_round6.png');bpy.ops.render.render(write_still=True)
