import bpy, json, pathlib, math
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');AUD=ROOT/'audit/batch3_elliott';SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene;COL=bpy.data.collections['Asset_elliott_hall_of_music']
# Fit the temporary integration warning to the landing instead of letting the
# label run beyond its edge.
direction=Vector((59.85-44.075,10.85-9.162)).normalized();side=Vector((-direction.y,direction.x,0));label_z=math.atan2(side.y,side.x)
for name in ('ELLT_R5_Hovde_Link_Deferred_Label','ELLT_R5_Hovde_Link_Deferred_Label_Back'):
 ob=bpy.data.objects.get(name)
 if ob and ob.type=='FONT':
  ob.data.body='HOVDE\nLINK\nPENDING';ob.data.size=.36;ob.data.align_x='CENTER';ob.data.align_y='CENTER';ob.rotation_euler.z=label_z;ob.location=(59.85-direction.x*.65,10.85-direction.y*.65,7.48)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC));bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene
scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True;scene.display.shading.background_type='WORLD'
def render(name,loc,target,scale,hide_prefixes=(),hidden_exact=()):
 changed=[]
 for ob in scene.objects:
  if any(ob.name.startswith(p) for p in hide_prefixes) or ob.name in hidden_exact:
   changed.append((ob,ob.hide_render));ob.hide_render=True
 cd=bpy.data.cameras.new('ELLT_R6_Final_'+name);cam=bpy.data.objects.new('ELLT_R6_Final_'+name,cd);scene.collection.objects.link(cam);cam.location=loc;cd.type='ORTHO';cd.ortho_scale=scale
 cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
 scene.render.filepath=str(AUD/(name+'.png'));bpy.ops.render.render(write_still=True)
 for ob,val in changed:ob.hide_render=val
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)
exterior_hide=('ELLT_R5_Hovde_Link_', 'ELLT_R4_Hovde_', 'ELLT_Access_')
interior_hide=('ELLT_R5_','ELLT_R6_','ELLT_R4_','ELLT_EXT_','ELLT_Access_','ELLT_Exterior_','ELLT_Estimated_')
interior_exact=('ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings','ELLT_Official_Footprint_Roof_Estimated_22_5m','ELLT_B3_ceiling')
render('interior_round6',(0,28,10),(0,-17,6),66,interior_hide,interior_exact)
render('interior_plan_round6',(0,0,92),(0,0,5),88,interior_hide,interior_exact)
render('hovde_gap_round6',(73,-8,27),(59.6,10.8,6.2),25,('ELLT_R4_Hovde_',))
result=json.loads((AUD/'result_round6.json').read_text());result['saved_and_reopened']=True;result['export_mesh_objects']=sum(o.type=='MESH' for o in bpy.data.collections['Asset_elliott_hall_of_music'].objects);result['interior_views']=['interior_round6.png','interior_plan_round6.png'];result['exterior_views']=['exterior_elevation_round6.png','hovde_gap_round6.png'];result['label']='HOVDE / LINK / PENDING, centered on landing top';(AUD/'result_round6.json').write_text(json.dumps(result,indent=2));print('Rendered true interior stage-to-auditorium view and plan; mesh count',result['export_mesh_objects'])
