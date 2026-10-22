import bpy,json,math,shutil,bmesh
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=P/'audit/finishing_south'
m=json.loads((P/'modular/manifest.json').read_text());refs=json.loads((P/'audit/official_building_references.json').read_text());out=[]
def mat(n,c):
 a=bpy.data.materials.new(n);a.diffuse_color=(*c,1);a.use_nodes=True;a.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);return a
for ident,code,h in [('class_of_1950','CL50',16),('felix_haas_hall','HAAS',11.5),('math_sciences','MATH',33.2)]:
 a=next(x for x in m['assets'] if x['id']==ident);fp=P/'modular'/a['file'];backup=D/(ident+'_before.blend')
 if not backup.exists():shutil.copy2(fp,backup)
 bpy.ops.wm.open_mainfile(filepath=str(fp));col=bpy.data.collections[a['collection']];before=len(col.all_objects)
 ref=next(x for x in refs['buildings'] if x['code']==code);ox,oy=a['placement_origin_xy_m'];ring=[(x-ox,y-oy) for x,y in ref['rings_xy_m'][0]]
 if math.dist(ring[0],ring[-1])<.001:ring.pop()
 if sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(ring,ring[1:]+ring[:1]))<0:ring.reverse()
 archived=[];rc=bpy.data.collections.get('Reference_Incompatible_Geometry_'+ident)
 for ob in list(col.all_objects):
  n=ob.name
  legacy=any(t in n for t in ['Wall_North','Wall_South','Wall_East','Wall_West','Brick_Wall_','Beltcourse_','Base_North','Base_South','Base_East','Base_West']) and 'Corrected_GIS' not in n
  if legacy and rc and ob.type=='MESH':
   for c in list(ob.users_collection):c.objects.unlink(ob)
   rc.objects.link(ob);archived.append(n)
 brick=mat(code+'_Finish_Brick',(.33,.12,.065));stone=mat(code+'_Finish_Limestone',(.66,.59,.43));glass=mat(code+'_Finish_Reflective_Glass',(.055,.22,.29));dark=mat(code+'_Finish_Bronze',(.075,.055,.036))
 materials=[brick,stone,glass,dark];wall=bpy.data.objects[code+'_Corrected_GIS_Wall_Envelope'];old=wall.data
 vs=[];fs=[];mi=[]
 def quad(p,q,z1,z2,offset,material):
  dx=q[0]-p[0];dy=q[1]-p[1];le=math.hypot(dx,dy);nx=-dy/le;ny=dx/le;k=len(vs)
  vs.extend([(p[0]+nx*offset,p[1]+ny*offset,z1),(q[0]+nx*offset,q[1]+ny*offset,z1),(q[0]+nx*offset,q[1]+ny*offset,z2),(p[0]+nx*offset,p[1]+ny*offset,z2)]);fs.append((k,k+1,k+2,k+3));mi.append(material)
 bands=[(0,.65,1),(.65,h-.5,0),(h-.5,h-.25,1),(h-.25,h,0)]
 for p,q in zip(ring,ring[1:]+ring[:1]):
  curved=ident=='class_of_1950' and p[1]<-13 and q[1]<-13
  these=[(0,.65,1),(.65,5.8,0),(5.8,6.25,3),(6.25,10.9,2),(10.9,11.3,1),(11.3,15.5,0),(15.5,16,1)] if curved else bands
  for lo,hi,ma in these:quad(p,q,lo,hi,0,ma);quad(q,p,lo,hi,-.18,0)
  # Close top and bottom of the 18cm wall, preserving the GIS outer face.
  dx=q[0]-p[0];dy=q[1]-p[1];le=math.hypot(dx,dy);nx=-dy/le*.18;ny=dx/le*.18
  for z in [0,h]:
   k=len(vs);vs.extend([(p[0],p[1],z),(q[0],q[1],z),(q[0]+nx,q[1]+ny,z),(p[0]+nx,p[1]+ny,z)]);fs.append((k,k+1,k+2,k+3));mi.append(0)
  if curved:
   # Photo supports continuous reflective upper glazing, bronze mullions and stone cap.
   # Thin strips sit just outside wall plane so no opaque backing hides the glass.
   quad(p,q,8.45,8.51,-.012,3)
   dx=q[0]-p[0];dy=q[1]-p[1];le=math.hypot(dx,dy)
   for t in [.0,.5]:
    u=(p[0]+t*dx,p[1]+t*dy);v=(u[0]+dx/le*.055,u[1]+dy/le*.055);quad(u,v,6.25,10.9,-.018,3)
 me=bpy.data.meshes.new(code+'_Finished_GIS_Envelope');me.from_pydata(vs,[],fs);me.update();wall.data=me
 for ma in materials:me.materials.append(ma)
 for poly,ma in zip(me.polygons,mi):poly.material_index=ma
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 wall['finish_evidence']='CL50 curved glazing/brick/stone from Purdue Libraries photo. Other trim is inherited design estimate; vertical dimensions unverified.'
 bpy.ops.wm.save_as_mainfile(filepath=str(fp));bpy.ops.wm.open_mainfile(filepath=str(fp));col=bpy.data.collections[a['collection']]
 # Render only the exported asset; preserved incompatible reference objects stay hidden.
 scene=bpy.context.scene;camd=bpy.data.cameras.new('FinishReview');cam=bpy.data.objects.new('FinishReview',camd);scene.collection.objects.link(cam);cx=(min(x for x,y in ring)+max(x for x,y in ring))/2;cy=(min(y for x,y in ring)+max(y for x,y in ring))/2
 cam.location=(cx+65,cy-95,65);cam.rotation_euler=(Vector((cx,cy,h*.4))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=90;scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.view_settings.view_transform='Standard';scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.filepath=str(D/(ident+'_after.png'));bpy.ops.render.render(write_still=True)
 out.append({'id':ident,'before_objects':before,'after_objects':len(col.all_objects),'reopened':True,'placement_change_m':[0,0],'footprint_change_m':0,'height_retained_estimated_m':h,'action':'Rebuilt thin envelope with explicit brick/stone material bands; CL50 south curved upper glazing and bronze mullions from primary photo. Heights and trim dimensions remain estimates. No added HVAC or invented roof machinery.','source_feature':ref['fid'],'source_CRS':'EPSG:4326 converted by existing project linear formula','source_snapshot':'audit/official_building_references.json','retrieved':'2026-10-22','architectural_source':'https://collections.lib.purdue.edu/campus/images/buildings/195-class-of-1950-lecture-hall.jpeg' if ident=='class_of_1950' else 'Inherited material and trim organization; no adequate measured elevation source found.','source_date':'unknown','uncertainty':'Facade band heights estimated; Haas/Math facade arrangement and heights remain unverified.'})
 (D/'changes.json').write_text(json.dumps(out,indent=2))
 print('FINISHED',ident,len(col.all_objects),flush=True)
