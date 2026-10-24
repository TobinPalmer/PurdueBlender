import bpy, hashlib, json, os
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/knoy_hall.blend'
OUT=ROOT/'audit/complete_knoy/facade_material_validation_r9.json'

def digest(asset):
 h=hashlib.sha256(); count=0
 for o in sorted(asset.objects,key=lambda x:x.name):
  if o.type!='MESH': continue
  count+=1; h.update(o.name.encode())
  for row in o.matrix_world: h.update(','.join(f'{v:.8f}' for v in row).encode())
  for v in o.data.vertices: h.update(','.join(f'{c:.8f}' for c in v.co).encode())
  for poly in o.data.polygons: h.update(','.join(str(i) for i in poly.vertices).encode())
 return h.hexdigest(),count

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections.get('Asset_knoy_hall'); assert asset
before,nmeshes=digest(asset)
source='https://polytechnic.purdue.edu/sites/default/files/styles/featured_image/public/article-images/Knoy-featured.jpg?itok=wcvG00BW'
notes={
 'KNOY_Purdue_Red_Brick':('Qualitative visual cue only: Purdue photo shows red/brown brick. Undated, single perspective, uncalibrated.','Exact brick color, dimensions, mortar color, and bond pattern have not been measured; procedural values are render estimates.'),
 'KNOY_Precast_Concrete':('Qualitative visual cue only: Purdue photo shows pale horizontal facade trim. Material identification is not confirmed.','Exact concrete/precast/stone specification, color, finish, and dimensions are unverified; shader is a neutral render estimate.'),
 'KNOY_Dark_Tinted_Glass':('Qualitative visual cue only: Purdue photo shows dark recessed glazing. Exact glazing tint and reflectance are unmeasured.','The single uncalibrated view does not establish glazing specification, color, or reflectance.')}
for name,(status,limit) in notes.items():
 m=bpy.data.materials.get(name); assert m and m.use_nodes, name
 m['evidence_source']=source
 m['evidence_status']=status
 m['measurement_limit']=limit
 if name=='KNOY_Purdue_Red_Brick':
  brick=next(n for n in m.node_tree.nodes if n.type=='TEX_BRICK')
  brick.inputs['Mortar'].default_value=(0.38,0.34,0.29,1.0)
  m['estimated_mortar_color'] = 'lighter warm mortar visual estimate; not measured'
  assert abs(brick.inputs['Brick Width'].default_value-.23)<1e-5
  assert abs(brick.inputs['Row Height'].default_value-.076)<1e-5
  assert abs(brick.inputs['Mortar Size'].default_value-.006)<1e-5
  m['estimated_brick_dimensions_m']='0.23 x 0.076; render scale only'
  m['estimated_mortar_width_m']=0.006
  bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  assert abs(bsdf.inputs['Roughness'].default_value-.60)<1e-5
 if name=='KNOY_Precast_Concrete':
  bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  assert abs(bsdf.inputs['Roughness'].default_value-.82)<1e-5
 if name=='KNOY_Dark_Tinted_Glass':
  bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  assert abs(bsdf.inputs['Roughness'].default_value-.08)<1e-5
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections.get('Asset_knoy_hall'); after,nmeshes_after=digest(asset)
assert before==after and nmeshes==nmeshes_after
mat_checks=[]
for name in notes:
 m=bpy.data.materials.get(name)
 assert m and m.get('evidence_source')==source and m.get('measurement_limit')
 mat_checks.append({'material':name,'evidence_status':m['evidence_status'],'source':m['evidence_source'],'measurement_limit':m['measurement_limit']})
brick_mat=bpy.data.materials['KNOY_Purdue_Red_Brick']
brick_node=next(n for n in brick_mat.node_tree.nodes if n.type=='TEX_BRICK')
mortar=tuple(round(v,3) for v in brick_node.inputs['Mortar'].default_value[:3])
assert mortar==(0.38,0.34,0.29)
report={'revision':9,'asset_reopened':'PASS','asset':'modular/buildings/knoy_hall.blend','materials':mat_checks,'brick_mortar_color_render_estimate':mortar,'asset_collection_mesh_count':nmeshes_after,'mesh_geometry_sha256_before':before,'mesh_geometry_sha256_after':after,'mesh_or_placement_geometry_changed':False,'scope':'Knoy shader and provenance metadata only; no geometry, placement, master, shared, or other building files changed.'}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,indent=2))


