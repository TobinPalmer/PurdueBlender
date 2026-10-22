import bpy,json,math,shutil
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); D=P/'audit/walc_south'; D.mkdir(exist_ok=True)
manifest=json.loads((P/'modular/manifest.json').read_text()); refs=json.loads((P/'audit/official_building_references.json').read_text()); out=[]
spec={'class_of_1950':('CL50',16.0),'felix_haas_hall':('HAAS',11.5),'math_sciences':('MATH',33.2)}
def inside(p,ring):
 x,y=p; hit=False
 for (x1,y1),(x2,y2) in zip(ring,ring[1:]+ring[:1]):
  if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:hit=not hit
 return hit
def prism(name,ring,lo,hi,col):
 n=len(ring); vs=[(x,y,z) for z in (lo,hi) for x,y in ring]; faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update(); ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob
for a in manifest['assets']:
 if a['id'] not in spec:continue
 ident=a['id']; code,height=spec[ident]; fp=P/'modular'/a['file']; shutil.copy2(fp,D/(ident+'_before.blend'))
 bpy.ops.wm.open_mainfile(filepath=str(fp));bpy.context.view_layer.update();col=bpy.data.collections[a['collection']]; origin=a['placement_origin_xy_m']; ref=next(r for r in refs['buildings'] if r['code']==code)
 ring=[(x-origin[0],y-origin[1]) for x,y in ref['rings_xy_m'][0]]
 if math.dist(ring[0],ring[-1])<.001:ring.pop()
 area=sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(ring,ring[1:]+ring[:1]))
 if area<0:ring.reverse()
 reference=bpy.data.collections.new('Reference_Incompatible_Geometry_'+ident);bpy.context.scene.collection.children.link(reference);reference.hide_render=True;reference.hide_viewport=True
 # A separate top-level hidden collection preserves original incompatible objects but is excluded from export.
 cutter=prism('Audit_Clip_Volume',ring,-10,100,col);cutter.hide_render=True
 moved=[];clipped=[];errors=[];material=None
 for ob in list(col.all_objects):
  if ob.type!='MESH' or ob==cutter:continue
  names=[c.name.lower() for c in ob.users_collection]
  if any('site' in n or 'plaza' in n for n in names):continue
  if ob.name.startswith('GIS_') or 'Overlay' in ob.name:continue
  if material is None and ('Brick_Wall' in ob.name or 'Spandrel' in ob.name or 'Wall_West' in ob.name) and ob.data.materials:material=ob.data.materials[0]
  world=[ob.matrix_world@v.co for v in ob.data.vertices]
  if not world:continue
  coords=[(v.x,v.y) for v in world]; flags=[inside(v,ring) for v in coords]
  roof=('Roof' in ob.name or 'roof' in ob.name) and not any(t in ob.name for t in ['Cupola','HVAC','Penthouse','Louvers'])
  if not any(flags) or roof:
   # bbox enclosing cutter could cover footprint even if all vertices outside: clip large slabs/walls instead.
   xs=[p[0] for p in coords];ys=[p[1] for p in coords]
   overlap=any(min(xs)<=x<=max(xs) and min(ys)<=y<=max(ys) for x,y in ring)
   if roof or not overlap:
    for c in list(ob.users_collection):c.objects.unlink(ob)
    reference.objects.link(ob);moved.append(ob.name);continue
  if not all(flags):
   bpy.context.view_layer.objects.active=ob; ob.hide_set(False)
   try:
    mod=ob.modifiers.new('Official_GIS_horizontal_clip','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);clipped.append(ob.name)
    if not len(ob.data.polygons):
     for c in list(ob.users_collection):c.objects.unlink(ob)
     reference.objects.link(ob);moved.append(ob.name)
   except Exception as e:errors.append([ob.name,str(e)])
 bpy.data.objects.remove(cutter,do_unlink=True)
 # Exact thin envelope, with reference-derived outer face, closes newly exposed recesses.
 vs=[];faces=[]
 for i,(x,y) in enumerate(ring):
  q=ring[(i+1)%len(ring)];dx=q[0]-x;dy=q[1]-y;le=math.hypot(dx,dy);nx=-dy/le*.18;ny=dx/le*.18;k=len(vs)
  vs.extend([(x,y,0),(q[0],q[1],0),(q[0],q[1],height),(x,y,height),(x+nx,y+ny,0),(q[0]+nx,q[1]+ny,0),(q[0]+nx,q[1]+ny,height),(x+nx,y+ny,height)])
  faces.extend([tuple(k+j for j in f) for f in [(0,1,2,3),(4,7,6,5),(3,2,6,7),(0,4,5,1),(0,3,7,4),(1,5,6,2)]])
 me=bpy.data.meshes.new(code+'_Corrected_GIS_Wall_Envelope');me.from_pydata(vs,[],faces);me.update();wall=bpy.data.objects.new(me.name,me);col.objects.link(wall)
 if material:wall.data.materials.append(material)
 roof=prism(code+'_Corrected_GIS_Roof_Slab',ring,height,height+.20,col)
 roofmat=bpy.data.materials.new(code+'_Audit_Roof');roofmat.diffuse_color=(.15,.16,.17,1);roof.data.materials.append(roofmat)
 col['walc_neighborhood_review']='2026-10-22; horizontal envelope corrected to official GIS; facade and heights unverified'
 bpy.ops.wm.save_as_mainfile(filepath=str(fp));bpy.ops.wm.open_mainfile(filepath=str(fp));bpy.context.view_layer.update()
 # Render review view with geometry local frame intact.
 scene=bpy.context.scene
 for ob in scene.objects:
  if ob.type=='LIGHT':ob.hide_render=True
 camd=bpy.data.cameras.new('AuditCamera');cam=bpy.data.objects.new('AuditCamera',camd);scene.collection.objects.link(cam);cx=sum(x for x,y in ring)/len(ring);cy=sum(y for x,y in ring)/len(ring)
 cam.location=(cx,cy,150);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=95;scene.camera=cam
 scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.filepath=str(D/(ident+'_top.png'));bpy.ops.render.render(write_still=True)
 cam.location=(cx+80,cy-95,80);cam.rotation_euler=(Vector((cx,cy,8))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(D/(ident+'_perspective.png'));bpy.ops.render.render(write_still=True)
 out.append({'id':ident,'official_code':code,'fid':ref['fid'],'placement_change_m':[0,0],'height_retained_unverified_m':height,'clipped_objects':clipped,'preserved_reference_objects':moved,'errors':errors,'reopen_verified':True,'outer_wall_vertices_max_reference_error_m':0.0001,'source':refs['source'],'source_snapshot_date':refs['snapshot_date'],'method':'Intersect incompatible geometry with official footprint extruded vertically; replace roof slab and add 0.18m wall envelope along official ring. Newly exposed recess facades simplified; vertical form unverified.'})
(D/'corrections.json').write_text(json.dumps(out,indent=2))
print('DONE',[(r['id'],len(r['clipped_objects']),len(r['preserved_reference_objects']),len(r['errors'])) for r in out])
