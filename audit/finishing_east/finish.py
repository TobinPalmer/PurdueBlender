import bpy,bmesh,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/finishing_east';M=json.loads((R/'modular/manifest.json').read_text());report={}
def render(c,path):
 s=bpy.context.scene; pts=[o.matrix_world@Vector(v) for o in c.all_objects if o.type=='MESH' for v in o.bound_box];lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)));center=(lo+hi)/2
 cd=bpy.data.cameras.new('Evidence');cam=bpy.data.objects.new('Evidence',cd);s.collection.objects.link(cam);cam.location=center+Vector((110,-140,115));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=max(hi.x-lo.x,hi.y-lo.y)*1.45;s.camera=cam;s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.filepath=str(path);bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)
for id in ['potter_engineering','mechanical_engineering','electrical_engineering','walc']:
 a=next(x for x in M['assets'] if x['id']==id);p=R/'modular'/a['file'];shutil.copy2(p,D/(id+'_before.blend'));bpy.ops.wm.open_mainfile(filepath=str(p));c=bpy.data.collections[a['collection']];before=len(c.all_objects);render(c,D/(id+'_before.png'));changes=[]
 for o in [q for q in c.all_objects if q.type=='MESH' and 'Structural_Envelope' in q.name]:
  if o.type!='MESH' or 'Structural_Envelope' not in o.name:continue
  fid=o['source_fid'];prefix=o.name.split('Structural_Envelope')[0];bands=[b for b in c.all_objects if b.name.startswith(prefix+'Limestone_Band_')];z0=min(v.co.z for v in o.data.vertices);z1=max(v.co.z for v in o.data.vertices);pts=[v.co.copy() for v in o.data.vertices if abs(v.co.z-z0)<1e-5];n=len(pts);brick=o.data.materials[0];stone=bands[0].data.materials[0];intervals=[(min(v.co.z for v in b.data.vertices),max(v.co.z for v in b.data.vertices)) for b in bands];zs=sorted(set([z0,z1]+[max(z0,min(z1,z)) for pair in intervals for z in pair]));verts=[(v.x,v.y,z) for z in zs for v in pts];faces=[];mi=[]
  for k,(low,high) in enumerate(zip(zs,zs[1:])):
   material=int(any(l<=(low+high)/2<=h for l,h in intervals))
   for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j));mi.append(material)
  # Retain exact existing triangulation of caps.
  for face in o.data.polygons:
   if all(abs(o.data.vertices[i].co.z-z0)<1e-5 for i in face.vertices):faces.append(tuple(i for i in face.vertices));mi.append(0)
   elif all(abs(o.data.vertices[i].co.z-z1)<1e-5 for i in face.vertices):faces.append(tuple((len(zs)-1)*n+(i%n) for i in face.vertices));mi.append(0)
  mesh=bpy.data.meshes.new(o.name+'_Continuous');mesh.from_pydata(verts,[],faces);mesh.materials.append(brick);mesh.materials.append(stone)
  for face,mat in zip(mesh.polygons,mi):face.material_index=mat
  o.data=mesh
  for b in bands:bpy.data.objects.remove(b,do_unlink=True)
  changes.append({'envelope':o.name,'removed_overlapping_bands':len(bands),'material_intervals':intervals})
 # Correct generated winding, including WALC source facade strips.
 fixed=[]
 for o in c.all_objects:
  if o.type=='MESH' and ('Official_' in o.name or 'WALC_Source906_' in o.name):
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();fixed.append(o.name)
 for mat in {m for o in c.all_objects if o.type=='MESH' for m in o.data.materials if m and ('Reference_' in m.name or id in m.name)}:
  if not mat.use_nodes:
   color=tuple(mat.diffuse_color);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.28 if 'Glass' in mat.name else .75
 bpy.ops.wm.save_as_mainfile(filepath=str(p));bpy.ops.wm.open_mainfile(filepath=str(p));c=bpy.data.collections[a['collection']];render(c,D/(id+'_after.png'));checks=[]
 for o in c.all_objects:
  if o.type=='MESH' and 'Structural_Envelope' in o.name:
   bm=bmesh.new();bm.from_mesh(o.data);checks.append({'object':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True)});bm.free()
 report[id]={'before_objects':before,'after_objects':len(c.all_objects),'changes':changes,'normal_mesh_count':len(fixed),'checks':checks,'placement_unchanged':a['placement_origin_xy_m'],'reopened':True,'heights_and_facade_patterns':'still estimates'};(D/'verification.json').write_text(json.dumps(report,indent=2))

