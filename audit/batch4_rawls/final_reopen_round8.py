import bpy,os,json,hashlib
from mathutils import Vector
p=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene;bpy.context.view_layer.update()
def mtx(m):return [[round(float(m[r][c]),9) for c in range(4)] for r in range(4)]
def bounds(o):
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 return [[round(min(v[i] for v in pts),6),round(max(v[i] for v in pts),6)] for i in range(3)]
def mshash(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(('%0.9f,%0.9f,%0.9f;'%(v.co.x,v.co.y,v.co.z)).encode())
 for f in o.data.polygons:h.update((str(tuple(f.vertices))+';').encode())
 return h.hexdigest()
scene_data={'asset':p,'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'scene':s.name,
'objects':len(s.objects),'meshes':sum(o.type=='MESH' for o in s.objects),'collections':[],
'materialless_meshes':[o.name for o in s.objects if o.type=='MESH' and not o.data.materials],
'external_file_images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE'],
'linked_libraries':[lib.filepath for lib in bpy.data.libraries if lib.filepath],
'root':{'name':'AssetRoot_rawls_hall','world_matrix':mtx(bpy.data.objects['AssetRoot_rawls_hall'].matrix_world)},
'shell':{'name':'RAWL_Masonry_Exterior_Walls','world_matrix':mtx(bpy.data.objects['RAWL_Masonry_Exterior_Walls'].matrix_world),'bounds':bounds(bpy.data.objects['RAWL_Masonry_Exterior_Walls']),'mesh_sha256':mshash(bpy.data.objects['RAWL_Masonry_Exterior_Walls'])},
'fixed_objects':[],'mesh_local_bounds_outliers':[]}
for c in bpy.data.collections:
 if any(o in s.objects[:] for o in c.objects):scene_data['collections'].append({'name':c.name,'objects':len(c.objects),'instances':sum(o.type=='EMPTY' and o.instance_type=='COLLECTION' for o in c.objects)})
names=['Cam_RAWL_01_North_StateSt','Cam_RAWL_02_NW_Curved_Rotunda','Cam_RAWL_03_West_GrantSt_Skywalk','Cam_RAWL_04_SE_Diagonal_Facade','Cam_RAWL_05_Roof_Arched_Penthouse','Cam_RAWL_06_Ortho_Footprint_Top','RAWL_Site_Sidewalk_Apron','RAWL_South_Windows_South_BronzeMullions']
for n in names:
 o=bpy.data.objects[n];scene_data['fixed_objects'].append({'name':n,'type':o.type,'location':list(o.location),'parent':o.parent.name if o.parent else None,'parent_inverse':mtx(o.matrix_parent_inverse),'world_matrix':mtx(o.matrix_world),'world_bounds':bounds(o),'mesh_sha256':mshash(o) if o.type=='MESH' else None})
for o in s.objects:
 if o.type=='MESH':
  b=bounds(o)
  if max(abs(q) for ax in b[:2] for q in ax)>120:scene_data['mesh_local_bounds_outliers'].append({'name':o.name,'bounds':b})
with open('audit/batch4_rawls/round8_final_reopen_validation.json','w') as f:json.dump(scene_data,f,indent=2)
print(json.dumps(scene_data,indent=2))
