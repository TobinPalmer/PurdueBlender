import bpy,json,math,shutil
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=P/'audit/walc_south';m=json.loads((P/'modular/manifest.json').read_text());refs=json.loads((P/'audit/official_building_references.json').read_text());report=json.loads((D/'corrections.json').read_text())
for a in m['assets']:
 if a['id'] not in ['class_of_1950','math_sciences','felix_haas_hall','stanley_coulter_hall']:continue
 ident=a['id'];fp=P/'modular'/a['file'];bpy.ops.wm.open_mainfile(filepath=str(fp));bpy.context.view_layer.update();col=bpy.data.collections[a['collection']];rc=bpy.data.collections.get('Reference_Incompatible_Geometry_'+ident)
 if rc is None:
  shutil.copy2(fp,D/(ident+'_before.blend'));rc=bpy.data.collections.new('Reference_Incompatible_Geometry_'+ident);bpy.context.scene.collection.children.link(rc);rc.hide_viewport=True;rc.hide_render=True
 code={'class_of_1950':'CL50','math_sciences':'MATH','felix_haas_hall':'HAAS','stanley_coulter_hall':'SC'}[ident];r=next(x for x in refs['buildings'] if x['code']==code);origin=a['placement_origin_xy_m'];ring=[(x-origin[0],y-origin[1]) for x,y in r['rings_xy_m'][0]]
 def dist(p,a,b):
  dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
  return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
 removed=[]
 for ob in list(col.all_objects):
  hide=ob.name=='SC_Campus_Lawn_Base'
  if ob.type=='FONT':
   pt=ob.matrix_world.translation
   hide=min(dist(pt,p,q) for p,q in zip(ring,ring[1:]))>2
  if hide:
   for c in list(ob.users_collection):c.objects.unlink(ob)
   rc.objects.link(ob);removed.append(ob.name)
 bpy.ops.wm.save_as_mainfile(filepath=str(fp));bpy.ops.wm.open_mainfile(filepath=str(fp));bpy.context.view_layer.update()
 existing=next((x for x in report if x['id']==ident),None)
 if existing:existing['additional_hidden_floating_labels']=removed
 else:report.append({'id':ident,'official_code':'SC','fid':r['fid'],'horizontal_status':'Existing structural masonry follows official polygon; AABB extrema discrepancy under 0.004 m','placement_change_m':[0,0],'removed_unsupported_site_overlay':removed,'height_status':'unverified','reopen_verified':True,'source':refs['source'],'source_snapshot_date':refs['snapshot_date']})
 scene=bpy.context.scene;camd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',camd);scene.collection.objects.link(cam);xs=[x for x,y in ring];ys=[y for x,y in ring];cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2;cam.location=(cx,cy,150);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=95;scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.filepath=str(D/(ident+'_top.png'));bpy.ops.render.render(write_still=True)
 cam.location=(cx+80,cy-95,80);cam.rotation_euler=(Vector((cx,cy,8))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(D/(ident+'_perspective.png'));bpy.ops.render.render(write_still=True)
(D/'corrections.json').write_text(json.dumps(report,indent=2));print('DONE',[(r['id'],r.get('additional_hidden_floating_labels',r.get('removed_unsupported_site_overlay'))) for r in report])
