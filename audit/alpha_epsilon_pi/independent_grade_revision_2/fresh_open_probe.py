import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
asset_path=root/'modular'/'buildings'/'alpha_epsilon_pi.blend'
evidence_dir=Path(__file__).resolve().parent.parent
geo=json.loads((evidence_dir/'purdue_gis_features_fid754_821.json').read_text(encoding='utf-8-sig'))
feature=next(f for f in geo['features'] if int(f['properties']['FID'])==754)
source=feature['geometry']['coordinates'][0][:-1]
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
scene=bpy.data.scenes.get('Building_alpha_epsilon_pi')
col=bpy.data.collections.get('Asset_alpha_epsilon_pi')
root_obj=bpy.data.objects.get('AssetRoot_alpha_epsilon_pi')
assert scene and col and root_obj
assert scene.get('building_id')=='alpha_epsilon_pi'
assert col.get('local_coordinates') is True
origin=tuple(float(x) for x in col['placement_origin_xy_m'])
foundation=bpy.data.objects.get('AEPi_Foundation_GIS_754')
assert foundation and foundation.type=='MESH'
# Rebuild source local coordinates using the documented project transform.
lat0,lon0=40.4274,-86.9137
sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
source_local=[((lon-lon0)*sx-origin[0],(lat-lat0)*sy-origin[1]) for lon,lat in source]
asset_local=[(float(v.co.x),float(v.co.y)) for v in list(foundation.data.vertices)[:len(source_local)]]
errors=[math.hypot(a[0]-s[0],a[1]-s[1]) for a,s in zip(asset_local,source_local)]
objects=list(col.all_objects); meshes=[o for o in objects if o.type=='MESH']
missing=[o.name for o in meshes if not o.data.materials]
parent_errors=[o.name for o in meshes if o.parent!=root_obj]
unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
materials=sorted({m.name for o in meshes for m in o.data.materials if m})
brick_material=bpy.data.materials.get('AEPi | variegated warm red brick')
brick_links=[]
if brick_material and brick_material.node_tree:
    brick_links=[{
      'from_type':link.from_node.type,'from_node':link.from_node.name,'from_socket':link.from_socket.name,
      'to_type':link.to_node.type,'to_node':link.to_node.name,'to_socket':link.to_socket.name
    } for link in brick_material.node_tree.links]
brick_shader={
  'material_present':brick_material is not None,
  'uv_to_brick_vector':any(x['from_type']=='TEX_COORD' and x['from_socket']=='UV' and x['to_type']=='TEX_BRICK' and x['to_socket']=='Vector' for x in brick_links),
  'brick_color_to_principled_base_color':any(x['from_type']=='TEX_BRICK' and x['from_socket']=='Color' and x['to_type']=='BSDF_PRINCIPLED' and x['to_socket']=='Base Color' for x in brick_links),
  'brick_factor_to_bump_height':any(x['from_type']=='TEX_BRICK' and x['from_socket']=='Factor' and x['to_type']=='BUMP' and x['to_socket']=='Height' for x in brick_links),
  'bump_to_principled_normal':any(x['from_type']=='BUMP' and x['from_socket']=='Normal' and x['to_type']=='BSDF_PRINCIPLED' and x['to_socket']=='Normal' for x in brick_links),
  'links':brick_links
}
# Count distinguishing modeled parts, plus named surface/material info for factual checks.
counts={
 'windows':sum(1 for o in objects if 'Facade_' in o.name and 'FrontGlass' in o.name),
 'window_acs':sum(1 for o in objects if 'WindowAC' in o.name),
 'dormers':sum(1 for o in objects if 'Dormer_Glass' in o.name),
 'entry_objects':sum(1 for o in objects if 'Entry_' in o.name),
 'interior_objects':sum(1 for o in objects if any(o.name.startswith(p) for p in ('AEPi_Interior_','AEPi_Ground_Partition_','AEPi_Level2_','AEPi_Level3_','AEPi_Lounge_','AEPi_Dining_','AEPi_Kitchen_'))),
}
heights=[]
for name in ('AEPi_Ground_Floor_GIS_754','AEPi_Continuous_Exterior_And_Interior_Walls','AEPi_Mansard_Lower_Slope','AEPi_Mansard_Upper_Slope','AEPi_Mansard_Flat_Cap','AEPi_Rear_Roof_Chimney','AEPi_Chimney_Cap'):
 o=bpy.data.objects.get(name)
 if o:
  z=[(o.matrix_world@Vector(v)).z for v in o.bound_box]
  heights.append({'name':name,'z_min':min(z),'z_max':max(z)})
out={
 'asset':str(asset_path),'asset_sha256':hashlib.sha256(asset_path.read_bytes()).hexdigest(),
 'scene':scene.name,'building_id':scene.get('building_id'),'collection':col.name,'local_coordinates':col.get('local_coordinates'),
 'placement_origin_xy_m':list(origin),'objects':len(objects),'mesh_objects':len(meshes),'material_count':len(materials),'materials':materials,
 'foundation_vertex_count':len(source_local),'max_corresponding_vertex_error_m':max(errors) if errors else None,
 'missing_material_meshes':missing,'mesh_parent_errors':parent_errors,'unpacked_external_images':unpacked,
 'bounds_local_m':{'min':[min((o.matrix_world@Vector(v))[i] for o in meshes for v in o.bound_box) for i in range(3)],'max':[max((o.matrix_world@Vector(v))[i] for o in meshes for v in o.bound_box) for i in range(3)]},
 'feature_counts':counts,'vertical_components':heights,'brick_shader':brick_shader
}
path=Path(__file__).resolve().parent/'fresh_open_probe.json'
path.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
