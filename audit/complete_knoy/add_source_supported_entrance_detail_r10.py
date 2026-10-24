import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/knoy_hall.blend'
OUT=ROOT/'audit/complete_knoy/entrance_detail_validation_r10.json'
PHOTO='https://hist152purdue.wordpress.com/2018/08/09/knoy-hall/'
IMAGE='audit/complete_knoy/ref_knoy_main_entrance_hist152_2018.jpg'

def digest_meshes(coll, exclude=()):
 h=hashlib.sha256(); n=0
 for o in sorted(coll.objects,key=lambda x:x.name):
  if o.type!='MESH' or o.name in exclude: continue
  n+=1; h.update(o.name.encode())
  for row in o.matrix_world: h.update(','.join(f'{v:.8f}' for v in row).encode())
  for v in o.data.vertices: h.update(','.join(f'{c:.8f}' for c in v.co).encode())
  for p in o.data.polygons: h.update(','.join(str(i) for i in p.vertices).encode())
 return h.hexdigest(),n
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections.get('Asset_knoy_hall'); assert asset
root=bpy.data.objects.get('AssetRoot_knoy_hall'); assert root
brick=bpy.data.materials['KNOY_Purdue_Red_Brick']
wall=bpy.data.objects['KNOY_Exterior_Masonry_Walls']
# Remove a prior generated sign so this source pass can be rerun safely.
existing_sign=bpy.data.objects.get('KNOY_Entrance_Sign_Lettering')
if existing_sign:
 data=existing_sign.data
 bpy.data.objects.remove(existing_sign,do_unlink=True)
 if data and data.users==0:
  (bpy.data.meshes if data.__class__.__name__=='Mesh' else bpy.data.curves).remove(data)
before,old_count=digest_meshes(asset)
# Source photo shows the south entry sign wall as brick. Select the two
# existing inner/outer faces of segment V25-V26 and the existing L1 lintel band.
selected=[]
for p in wall.data.polygons:
 c=wall.matrix_world@p.center
 if 3.10 < c.z < 4.48 and abs(c.x-0.75)<0.08 and abs(c.y+46.09)<0.25:
  selected.append(p)
assert len(selected)==2, f'Expected the paired inner/outer south portal sign-wall faces; found {len(selected)}'
for p in selected: p.material_index=1

# Silver entrance lettering visible above the south doorway in the 2018 photo.
mat=bpy.data.materials.get('KNOY_Entrance_Sign_Metal') or bpy.data.materials.new('KNOY_Entrance_Sign_Metal')
mat.use_nodes=True
nodes=mat.node_tree.nodes
bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
bsdf.inputs['Base Color'].default_value=(0.68,0.70,0.72,1.0)
bsdf.inputs['Metallic'].default_value=0.35
bsdf.inputs['Roughness'].default_value=0.34
mat['evidence_source']=PHOTO
mat['evidence_status']='Light/silver entrance lettering visible in the 2018 Purdue History Project photo; metal appearance is estimated.'
mat['measurement_limit']='Exact sign substrate, finish, reflectance and color are not specified.'
curve=bpy.data.curves.new('KNOY_Entrance_Sign_Lettering','FONT')
curve.body='KNOY HALL OF TECHNOLOGY'
curve.align_x='CENTER'
curve.size=0.24
curve.extrude=0.010
curve.bevel_depth=0.002
curve.bevel_resolution=2
obj=bpy.data.objects.new('KNOY_Entrance_Sign_Lettering',curve)
asset.objects.link(obj)
obj.parent=root
obj.matrix_parent_inverse=wall.matrix_parent_inverse.copy()  # Match shell GIS-to-local placement.
# Segment V25-V26 is the modeled south entrance edge. The sign is located at
# the existing canopy/entry zone; size and exact mounting position are estimates.
edge=Vector((202.973-235.317,-2.461+1.878)).normalized()
outward=Vector((-edge.y,edge.x))
center=Vector(((235.317+202.973)/2,(-1.878-2.461)/2))+outward*0.05
obj.location=(center.x,center.y,3.92)
normal=Vector((outward.x,outward.y,0.0)).normalized()
obj.rotation_euler=Vector((0,0,1)).rotation_difference(normal).to_euler()
obj.data.materials.append(mat)
obj['evidence_source']=PHOTO
obj['source_image']=IMAGE
obj['source_feature']='Visible KNOY HALL OF TECHNOLOGY lettering above the south entrance doors.'
obj['geometry_status']='Text and south entrance zone are photo-supported; scale and precise mounting position are estimates.'
obj['estimated_text_height_m']=0.24
obj['measurement_limit']='The perspective image is uncalibrated; exact letter size, mounting depth, elevation and surveyed position are unknown.'
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active=obj
bpy.ops.object.convert(target='MESH')
obj=bpy.context.view_layer.objects.active
obj.name='KNOY_Entrance_Sign_Lettering'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections.get('Asset_knoy_hall'); wall=bpy.data.objects['KNOY_Exterior_Masonry_Walls']; obj=bpy.data.objects.get('KNOY_Entrance_Sign_Lettering')
assert obj and obj.type=='MESH' and obj.get('source_feature')
assert obj.parent and obj.parent.name=='AssetRoot_knoy_hall'
# Re-identify band after reopen and confirm paired face assignment.
faces=[]
for p in wall.data.polygons:
 c=wall.matrix_world@p.center
 if 3.10<c.z<4.48 and abs(c.x-0.75)<0.08 and abs(c.y+46.09)<0.25: faces.append(p)
assert len(faces)==2 and all(p.material_index==1 for p in faces)
after,count=digest_meshes(asset,exclude=('KNOY_Entrance_Sign_Lettering',))
assert before==after and old_count==count
points=[obj.matrix_world@v.co for v in obj.data.vertices]
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
report={'revision':10,'saved_asset_reopened':'PASS','asset':'modular/buildings/knoy_hall.blend','source_photo':'https://hist152purdue.wordpress.com/2018/08/09/knoy-hall/','local_photo':IMAGE,'sign_object':'KNOY_Entrance_Sign_Lettering','sign_geometry_type':obj.type,'sign_bounds_local_m':bounds,'sign_text':obj.get('source_feature'),'sign_size_status':obj.get('geometry_status'),'south_sign_wall_face_materials_changed':len(faces),'south_wall_finish':'KNOY_Purdue_Red_Brick','geometry_hash_of_preexisting_meshes_before':before,'geometry_hash_of_preexisting_meshes_after':after,'preexisting_mesh_count':count,'new_mesh_count_in_asset':sum(o.type=='MESH' for o in asset.objects),'existing_geometry_changed':False,'no_roof_l5_pv_or_registration_changes':True,'uncertainty':'Photo and plan identify the south entrance area, but image is uncalibrated. Sign size and exact mounting position are estimates. The remaining facade rhythm and full elevations remain schematic.'}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,indent=2))

