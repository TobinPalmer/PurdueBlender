import bpy,json,os,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
AUDIT=ROOT/'audit'
PRE= AUDIT/'batchC_boilermaker_aquatic_r1'
PRE.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
wall=bpy.data.objects['AQUA R1 | continuous brick and concrete high-bay envelope']
assert wall.data.materials[0].name=='AQUA | mottled Purdue red-brown brick'
wall_corners=[wall.matrix_world@Vector(c) for c in wall.bound_box]
wall_xy=[[min(p[i] for p in wall_corners),max(p[i] for p in wall_corners)] for i in (0,1)]
assert abs(wall_xy[0][0]+30.098)<.02 and abs(wall_xy[0][1]-30.098)<.02
assert abs(wall_xy[1][0]+51.252)<.02 and abs(wall_xy[1][1]-51.252)<.02
windows=[o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | facade bay') and o.name.endswith('glazing')]
assert len(windows)==57,len(windows)
def world_z_bounds(obj):
 p=[obj.matrix_world@Vector(c) for c in obj.bound_box]
 return min(x.z for x in p),max(x.z for x in p)
assert all(1.7 < (world_z_bounds(o)[1]-world_z_bounds(o)[0]) < 1.9 for o in windows)
assert all(o.data.materials[0].name=='AQUA R1 | blue-gray reflective ribbon glazing' for o in windows)
competition=bpy.data.objects['Aquatic | interior pool basin']; compwater=bpy.data.objects['Aquatic | water surface']
dive=bpy.data.objects['AQUA R1 | dive pool basin 17ft deep']; divewater=bpy.data.objects['AQUA R1 | dive pool water']
assert abs(compwater.location.z-.19)<.01
assert abs(dive.dimensions.z-17*.3048)<.01
assert abs(divewater.location.z-.18)<.01
platforms=[o for o in asset.all_objects if o.type=='MESH' and 'm diving platform' in o.name]
assert len(platforms)==5,len(platforms)
assert {round(o.location.z,1) for o in platforms}=={1.,3.,5.,7.5,10.}
assert bpy.data.objects.get('AQUA R1 | 12-person spa shell')
assert bpy.data.objects.get('AQUA R1 | north facade building name')
assert all(o.data.materials for o in asset.all_objects if o.type=='MESH')
assert not any(i.source=='FILE' and i.filepath and not bpy.path.abspath(i.filepath) for i in bpy.data.images)
scene=bpy.context.scene
scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.render.resolution_percentage=80
scene.camera=bpy.data.objects['AQUA R1 | North Street View Camera']
scene.render.filepath=str(PRE/'aquatic_r1_north_exterior.png')
bpy.ops.render.render(write_still=True,scene=scene.name)
# Cutaway presentation: hide the wall, full roof skin and gable glazing for this render only.
toggles=[]
for o in asset.all_objects:
 if o.type=='MESH' and (o==wall or 'pitched roof planes' in o.name or 'standing seam roof ribs' in o.name or 'gable end infill' in o.name or 'schematic clear-span roof truss' in o.name):
  toggles.append((o,o.hide_render)); o.hide_render=True
scene.render.resolution_x=1100; scene.render.resolution_y=1350; scene.render.resolution_percentage=80
scene.camera=bpy.data.objects['AQUA R1 | Interior Cutaway Camera']; scene.camera.data.type='ORTHO'; scene.camera.data.ortho_scale=133
scene.render.filepath=str(PRE/'aquatic_r1_interior_cutaway.png')
bpy.ops.render.render(write_still=True,scene=scene.name)
for o,v in toggles: o.hide_render=v
# A closer cutaway render checks competition and dive pool equipment at human scale.
for o,v in toggles: o.hide_render=True
scene.render.resolution_x=1300; scene.render.resolution_y=900; scene.render.resolution_percentage=80
scene.camera=bpy.data.objects['AQUA R1 | Interior Detail Camera']; scene.camera.data.type='PERSP'; scene.camera.data.lens=43
scene.render.filepath=str(PRE/'aquatic_r1_interior_detail.png')
bpy.ops.render.render(write_still=True,scene=scene.name)
for o,v in toggles: o.hide_render=v
# Validation uses fully reopened asset; the cutaway hides are temporary and are not saved.
allz=[]
for o in asset.all_objects:
 if o.type=='MESH': allz.extend((o.matrix_world@Vector(c)).z for c in o.bound_box)
result={
 'revision':1,'passed':True,'reopened_saved_asset':True,'blender_version':bpy.app.version_string,
 'asset_file':'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend',
 'collection':asset.name,'child_inclusive_objects':len(asset.all_objects),
 'gis_feature_id':896,'project_local_gis_bbox_center_xy_m':[-808.683,80.337],
 'local_xy_frame_and_official_gis_footprint_unchanged':True,'perimeter_wall_bounds_local_m':[[round(v,3) for v in pair] for pair in wall_xy],'perimeter_wall_object':wall.name,
 'north_facade_evidence':'Google Street View, Jul 2023 panorama y0c6EFsDkT7g2ak3hsZh5A at 40.4289496,-86.9232244 facing ~180 degrees; exterior brick, lower ribbon windows, centered entry and name sign.',
 'ribbon_glazing_panels':len(windows),'ribbon_glazing_height_range_m':[round(min(world_z_bounds(o)[1]-world_z_bounds(o)[0] for o in windows),3),round(max(world_z_bounds(o)[1]-world_z_bounds(o)[0] for o in windows),3)],
 'competition_pool_water_surface_z_m':round(compwater.location.z,3),'competition_pool_basin_depth_m':round(competition.dimensions.z,3),
 'dive_pool_depth_m':round(dive.dimensions.z,4),'dive_pool_official_target_depth_m':round(17*.3048,4),
 'diving_platform_levels_m':[round(o.location.z,1) for o in platforms],
 'spa_present':True,'exterior_building_name_present':True,
 'all_meshes_have_material':all(o.data.materials for o in asset.all_objects if o.type=='MESH'),
 'mesh_z_bounds_m':[round(min(allz),3),round(max(allz),3)],
 'external_image_dependencies':sum(i.source=='FILE' and bool(i.filepath) for i in bpy.data.images),
 'master_or_manifest_edited':False,
 'renders':['audit/batchC_boilermaker_aquatic_r1/aquatic_r1_north_exterior.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r1_interior_cutaway.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r1_interior_detail.png']}
(PRE/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
