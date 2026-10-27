import bpy,json,hashlib
from pathlib import Path
P=Path(bpy.data.filepath);D=Path('audit/batch3_haas');C=bpy.data.collections['Asset_felix_haas_hall']
def bounds(o):
 if o.type!='MESH':return None
 q=[o.matrix_world@v.co for v in o.data.vertices]
 if not q:return None
 return [[min(v[i] for v in q) for i in range(3)],[max(v[i] for v in q) for i in range(3)]]
objs=[o for o in C.all_objects if o];mesh=[o for o in objs if o.type=='MESH']
roof_names=['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof'];roof_bounds={n:bounds(bpy.data.objects[n]) for n in roof_names}
shell=json.loads((D/'reopen_check_round10.json').read_text())['gis_envelope_bounds_m'];(sminx,sminy,_),(smaxx,smaxy,_)=shell
allv=[o.matrix_world@v.co for o in mesh for v in o.data.vertices];allb=[[min(v[i] for v in allv) for i in range(3)],[max(v[i] for v in allv) for i in range(3)]]
combined=[[min(b[0][i] for b in roof_bounds.values()) for i in range(3)],[max(b[1][i] for b in roof_bounds.values()) for i in range(3)]]
pad=.25;eps=.003
checks={'main_roof_eaves_at_11_7m':abs(roof_bounds[roof_names[0]][0][2]-11.7)<.003,'main_roof_peak_at_14m':abs(roof_bounds[roof_names[0]][1][2]-14)<.003,'entry_roof_eaves_at_11_7m':abs(roof_bounds[roof_names[1]][0][2]-11.7)<.003,'entry_roof_peak_at_13_2m':abs(roof_bounds[roof_names[1]][1][2]-13.2)<.003,'roof_plan_bounds_shell_plus_0_25m':abs(combined[0][0]-(sminx-pad))<eps and abs(combined[1][0]-(smaxx+pad))<eps and abs(combined[0][1]-(sminy-pad))<eps and abs(combined[1][1]-(smaxy+pad))<eps}
far_x=[]
for o in mesh:
 b=bounds(o)
 if b and b[1][0]>18.5:far_x.append({'name':o.name,'bounds':b})
external=[{'name':i.name,'path':i.filepath,'packed':i.packed_file is not None} for i in bpy.data.images if i.source=='FILE'];images=[]
for m in bpy.data.materials:
 if m.node_tree:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image:images.append({'material':m.name,'image':n.image.name,'path':n.image.filepath})
sha=hashlib.sha256(P.read_bytes()).hexdigest();r={'reopened':True,'blender_version':bpy.app.version_string,'asset_path':str(P.resolve()),'asset_sha256':sha,'export_collection':C.name,'object_count':len(objs),'mesh_count':len(mesh),'local_mesh_bounds_m':allb,'roof_mesh_bounds_m':roof_bounds,'combined_roof_bounds_m':combined,'gis_shell_bounds_m':shell,'eave_projection_m':{'x_minus':sminx-combined[0][0],'x_plus':combined[1][0]-smaxx,'y_minus':sminy-combined[0][1],'y_plus':combined[1][1]-smaxy},'objects_at_far_x_extent':far_x,'external_images':external,'material_image_nodes':images,'gis_shell_and_placement_edited':False,'checks':checks,'status':'PASS' if all(checks.values()) and not images else 'FAIL','renders':['audit/batch3_haas/exterior_round12.png','audit/batch3_haas/entrance_round12.png']}
(D/'round12_validation.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2))
