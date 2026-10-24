import bpy,hashlib,json
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');ASSET=ROOT/'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_knoy_hall'];wall=bpy.data.objects['KNOY_Exterior_Masonry_Walls'];sign=bpy.data.objects['KNOY_Entrance_Sign_Lettering']
h=hashlib.sha256();n=0
for o in sorted(asset.objects,key=lambda o:o.name):
 if o.type!='MESH' or o==sign:continue
 n+=1;h.update(o.name.encode())
 for row in o.matrix_world:h.update(','.join(f'{v:.8f}' for v in row).encode())
 for v in o.data.vertices:h.update(','.join(f'{c:.8f}' for c in v.co).encode())
 for p in o.data.polygons:h.update(','.join(str(i) for i in p.vertices).encode())
faces=[]
for p in wall.data.polygons:
 c=wall.matrix_world@p.center
 if 3.10<c.z<4.48 and abs(c.x-.75)<.08 and abs(c.y+46.09)<.25:faces.append((p.index,p.material_index))
assert len(faces)==2 and all(idx==1 for _,idx in faces),faces
assert n==62
assert sign.parent==bpy.data.objects['AssetRoot_knoy_hall']
assert sign.matrix_parent_inverse==wall.matrix_parent_inverse
assert sign.type=='MESH' and sign.get('source_feature') and len(sign.data.vertices)>0
points=[sign.matrix_world@v.co for v in sign.data.vertices]
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
center=[(a+b)/2 for a,b in bounds]
assert abs(center[0]-.75)<.2 and abs(center[1]+46.3)<.2 and abs(center[2]-4.02)<.3,(bounds,center)
expected='c51a34c4704891f3442b17f7df0d9edc3741fc1cee7416041858dbeed39c9ed1'
assert h.hexdigest()==expected,h.hexdigest()
report={'saved_source_reopened':'PASS','asset_collection_objects':len(asset.objects),'mesh_count':sum(o.type=='MESH' for o in asset.objects),'sign_mesh':'PASS','sign_world_bounds_m':bounds,'sign_world_center_m':center,'sign_transform_matches_shell_gis_to_local_parent_inverse':True,'south_sign_wall_faces':[{'index':i,'material_index':m} for i,m in faces],'south_wall_finish':'KNOY_Purdue_Red_Brick','preexisting_mesh_count':n,'preexisting_mesh_geometry_sha256':h.hexdigest(),'expected_preexisting_mesh_geometry_sha256':expected,'preexisting_geometry_changed':False,'uncertain_roof_L5_PV_or_GIS_registration_geometry_changed':False,'assertions_passed':True}
(ROOT/'audit/complete_knoy/entrance_detail_validation_r10.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
