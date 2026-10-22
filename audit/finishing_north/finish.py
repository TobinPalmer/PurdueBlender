import bpy,json,pathlib,shutil,math
from mathutils import Vector
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');d=p/'audit/finishing_north';results={}
for id in ['elliott_hall_of_music','knoy_hall','bell_tower']:
 path=p/'modular/buildings'/(id+'.blend');shutil.copy2(path,d/(id+'_before.blend'));bpy.ops.wm.open_mainfile(filepath=str(path));c=bpy.data.collections['Asset_'+id];changes=[]
 if id=='elliott_hall_of_music':
  wall=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls'];wall.data.materials.clear();wall.data.materials.append(bpy.data.materials['Elliott_Purdue_Red_Brick']);changes.append('Reassigned exterior walls from limestone to existing Purdue red brick shader, supported by Purdue Convocations 2015 article.')
  # Orient each vertical face outward using signed XY perimeter area.
  vv=wall.data.vertices; n=len(vv)//2;area=sum(vv[i].co.x*vv[(i+1)%n].co.y-vv[(i+1)%n].co.x*vv[i].co.y for i in range(n))
  if area<0:
   for f in wall.data.polygons:f.flip()
  mod=wall.modifiers.new('Estimated inward masonry thickness 0.30m','SOLIDIFY');mod.thickness=.3;mod.offset=-1;mod.use_even_offset=True
  roof=bpy.data.objects['ELLT_Official_Footprint_Roof_Estimated_22_5m'];roof.data.update()
  for f in roof.data.polygons:
   if f.normal.z<0:f.flip()
  mod=roof.modifiers.new('Estimated roof thickness downward 0.20m','SOLIDIFY');mod.thickness=.2;mod.offset=-1
  wall['thickness_status']='Estimated 0.30m inward; exterior mapped perimeter unchanged';roof['thickness_status']='Estimated .20m downward, top retained22.5m';changes.append('Added inward .30m wall and downward .20m roof thickness with outward normals; estimated construction thicknesses, no height/footprint adjustment.')
 # Make material-colored solid viewport agree with material render; original diffuse defaults were grey.
 changed=0
 for mat in {m for o in c.all_objects if o.type=='MESH' for m in o.data.materials if m}:
  if mat.use_nodes:
   bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   if bs and not bs.inputs['Base Color'].is_linked:
    rgba=bs.inputs['Base Color'].default_value
    if max(abs(mat.diffuse_color[i]-rgba[i]) for i in range(4))>.001:mat.diffuse_color=rgba;changed+=1
 if changed:changes.append('Synchronized '+str(changed)+' viewport material colors with existing rendered shader colors.')
 bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));c=bpy.data.collections['Asset_'+id];assert c.library is None
 # Only temporary inspection camera, never saved.
 visible=[o for o in c.all_objects if o.type=='MESH' and not o.hide_render];pts=[o.matrix_world@Vector(v)for o in visible for v in o.bound_box];lo=Vector(tuple(min(v[i]for v in pts)for i in range(3)));hi=Vector(tuple(max(v[i]for v in pts)for i in range(3)));ctr=(lo+hi)/2;span=max(hi-lo)
 camdata=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camdata);bpy.context.scene.collection.objects.link(cam);cam.location=ctr+Vector((span*.9,-span*1.1,span*.9));cam.rotation_euler=(ctr-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=span*1.6
 s=bpy.context.scene;s.camera=cam;s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(d/(id+'_after.png'));bpy.ops.render.render(write_still=True)
 results[id]={'changes':changes,'export_count':len(c.all_objects),'save_reopen':True,'bounds':[list(lo),list(hi)],'limitations':'Architectural subordinate dimensions remain estimated; interiors unverified. Bell and Knoy geometry retained.'}
(d/'results.json').write_text(json.dumps(results,indent=2))
