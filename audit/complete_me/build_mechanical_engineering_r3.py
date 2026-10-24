"""R3 source-registered 2023 roof-surface map for Mechanical Engineering.

The 2023 Indiana orthophoto is projected to the asset's approximate campus
local XY frame using the saved R2 request bounds and project conversion. It is
applied only to upward faces of the FID857 roof mesh. No roof elevations,
wall heights, facade schedule, or interior circulation are inferred here.
Run: blender -b modular/buildings/mechanical_engineering.blend --python audit/complete_me/build_mechanical_engineering_r3.py
"""
from __future__ import annotations
import bpy, json, math, shutil
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit' / 'complete_me'
ASSET_PATH = ROOT / 'modular' / 'buildings' / 'mechanical_engineering.blend'
ORTHO = AUDIT / 'indiana_current_orthophoto_me_r2.jpg'
REG = json.loads((AUDIT / 'mechanical_engineering_ortho_registration_r2.json').read_text(encoding='utf-8'))
BACKUP = AUDIT / 'mechanical_engineering_before_r3.blend'
if not BACKUP.exists():
    shutil.copy2(ASSET_PATH, BACKUP)

asset = bpy.data.collections['Asset_mechanical_engineering']
roof = bpy.data.objects['ME_Official_857_Roof']
root = bpy.data.objects['AssetRoot_mechanical_engineering']
if roof.type != 'MESH' or 'ME_Official_857_Structural_Envelope' not in asset.objects:
    raise RuntimeError('Expected FID857 roof and structural envelope in asset export collection')
if len(REG['request_bbox_3857']) != 4 or not ORTHO.exists():
    raise RuntimeError('Missing registered orthophoto or saved request extent')

# R2's source crop extent is EPSG:3857 in [xmin,ymin,xmax,ymax] order.
xmin, ymin, xmax, ymax = [float(x) for x in REG['request_bbox_3857']]
origin_x, origin_y = 66.30000114440918, 86.5
lat0 = math.radians(40.4274)
meters_lon = 111412.84 * math.cos(lat0)

image = bpy.data.images.load(str(ORTHO), check_existing=True)
IMAGE_NAME = 'ME_R3_Indiana_2023_Orthophoto_FID857_Roof'
image.name = IMAGE_NAME
image.colorspace_settings.name = 'sRGB'
image.pack()

mat = bpy.data.materials.get('ME_R3_FID857_2023_Orthophoto_Roof')
if mat is None:
    mat = bpy.data.materials.new('ME_R3_FID857_2023_Orthophoto_Roof')
mat.use_nodes = True
mat.diffuse_color = (0.32, 0.25, 0.18, 1.0)
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
out = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Roughness'].default_value = 0.78
tex = nodes.new('ShaderNodeTexImage')
tex.image = image
tex.interpolation = 'Linear'
tex.extension = 'EXTEND'
uvn = nodes.new('ShaderNodeUVMap')
uvn.uv_map = 'ME_R3_Ortho_UV'
links.new(uvn.outputs['UV'], tex.inputs['Vector'])
links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

# Preserve the existing membrane on vertical edges. Only top-facing polygons
# receive the image material; UV projection follows registered campus XY.
mesh = roof.data
uv_layer = mesh.uv_layers.get('ME_R3_Ortho_UV') or mesh.uv_layers.new(name='ME_R3_Ortho_UV')
if len(mesh.materials) == 0:
    raise RuntimeError('Expected original roof membrane material for sides')
if mat.name not in [m.name for m in mesh.materials]:
    mesh.materials.append(mat)
image_index = next(i for i,m in enumerate(mesh.materials) if m == mat)
top_polys = []
uv_values = []
for poly in mesh.polygons:
    is_top = poly.normal.z > 0.999
    if is_top:
        poly.material_index = image_index
        top_polys.append(poly.index)
    for loop_index in poly.loop_indices:
        vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
        # Asset coordinates are FID857 GIS local XY minus its declared marker.
        gx, gy = float(vertex.x) + origin_x, float(vertex.y) + origin_y
        lon = -86.9137 + gx / meters_lon
        lat = 40.4274 + gy / 111040.0
        mx = 6378137.0 * math.radians(lon)
        my = 6378137.0 * math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0))
        u = (mx - xmin) / (xmax - xmin)
        v = (my - ymin) / (ymax - ymin)
        uv_layer.data[loop_index].uv = (u, v)
        if is_top:
            uv_values.append([u,v])
mesh.update()
if not top_polys:
    raise RuntimeError('Could not locate upward-facing roof polygons')

roof['r3_roof_surface_source'] = '2023 Indiana Current Imagery, catalog item in2023_30001885_06; source is a registered 6-inch orthophoto crop, not measured roof geometry.'
roof['r3_roof_surface_method'] = 'Projected source-crop EPSG:3857 bounds to local mesh XY; applied as packed image texture only to upward-facing FID857 roof mesh polygons.'
roof['r3_height_and_silhouette_status'] = 'Unchanged and unverified. DSM returns were not assigned to individual wings because roof/equipment/canopy returns remain unresolved.'
roof['r3_top_material_polygons'] = len(top_polys)
asset['r3_revision'] = 'R3 applies the registered 2023 orthophoto to the FID857 top roof surface. No FID857 or FID108 geometry elevations, facade schedule, or interior layouts changed.'
asset['r3_height_status'] = 'FID857 height and wing-specific roof silhouette remain unverified; 2018 DSM/2016-2020 DTM data cannot separate structural roof from equipment/canopy per wing.'

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))

# Reopen validation records actual saved image/material assignments and geometry.
asset = bpy.data.collections['Asset_mechanical_engineering']
roof = bpy.data.objects['ME_Official_857_Roof']
mesh = roof.data
image_mat = bpy.data.materials['ME_R3_FID857_2023_Orthophoto_Roof']
image = bpy.data.images[IMAGE_NAME]
packed_images = [im.name for im in bpy.data.images if im.packed_file is not None]
tops = [p for p in mesh.polygons if p.normal.z > 0.999]
assigned = [p for p in tops if mesh.materials[p.material_index] == image_mat]
assigned_loops = [li for p in assigned for li in p.loop_indices]
uvs = [mesh.uv_layers['ME_R3_Ortho_UV'].data[li].uv for li in assigned_loops]
root = bpy.data.objects['AssetRoot_mechanical_engineering']
shell = bpy.data.objects['ME_Official_857_Structural_Envelope']
def z_bounds(ob):
    return [min(float(v.co.z) for v in ob.data.vertices),max(float(v.co.z) for v in ob.data.vertices)]
def xy_bounds(ob):
    return [[min(float(v.co[i]) for v in ob.data.vertices),max(float(v.co[i]) for v in ob.data.vertices)] for i in (0,1)]
validation = {
    'revision': 3, 'saved_file_reopened': True, 'asset_path': str(ASSET_PATH),
    'blender_version': bpy.app.version_string, 'export_collection': asset.name,
    'root_location': [round(float(v),6) for v in root.location],
    'root_scale': [round(float(v),6) for v in root.scale],
    'fid857_shell_xy_local_m': xy_bounds(shell), 'fid857_shell_z_m': z_bounds(shell),
    'fid857_roof_z_m': z_bounds(roof), 'fid857_top_face_count': len(tops),
    'fid857_top_face_count_textured': len(assigned),
    'fid857_top_uv_min_max': [[min(float(uv[i]) for uv in uvs),max(float(uv[i]) for uv in uvs)] for i in (0,1)],
    'orthophoto_image': IMAGE_NAME, 'orthophoto_source': 'audit/complete_me/indiana_current_orthophoto_me_r2.jpg',
    'orthophoto_packed': IMAGE_NAME in packed_images, 'no_external_texture_dependency': IMAGE_NAME in packed_images,
    'source_extent_3857': [xmin,ymin,xmax,ymax],
    'fid857_shell_height_unchanged_from_r2': abs(max(v.co.z for v in shell.data.vertices)-18.5)<1e-5,
    'fid857_roof_height_unchanged_from_r2': abs(max(v.co.z for v in roof.data.vertices)-18.75)<1e-5,
    'fid108_geometry_changed': False, 'master_or_shared_files_changed': False,
    'limitations': ['Orthophoto is a 2023 overhead appearance source and does not define wall/roof heights or roof slope.', 'FID857 GIS registration uses approximate campus-local conversion, not survey control.', 'Roof silhouette, structural heights, facade registration, and current interior circulation remain uncertain.']
}
validation['passed'] = bool(validation['saved_file_reopened'] and validation['export_collection']=='Asset_mechanical_engineering' and validation['root_location']==[0.0,0.0,0.0] and validation['root_scale']==[1.0,1.0,1.0] and validation['fid857_top_face_count']>0 and validation['fid857_top_face_count']==validation['fid857_top_face_count_textured'] and validation['orthophoto_packed'] and validation['fid857_shell_height_unchanged_from_r2'] and validation['fid857_roof_height_unchanged_from_r2'] and validation['fid108_geometry_changed'] is False)
(AUDIT/'mechanical_engineering_r3_validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
if not validation['passed']:
    raise RuntimeError('R3 save/reopen validation failed: '+json.dumps(validation))

# A temporary overhead render checks that the registered surface reads as the
# expected roof mosaic. Camera/lights are removed after preview, before exit.
scene = bpy.context.scene
old_camera = scene.camera
cam_data = bpy.data.cameras.new('ME_R3_Temp_Ortho_Camera')
cam = bpy.data.objects.new('ME_R3_Temp_Ortho_Camera',cam_data)
scene.collection.objects.link(cam)
cam.location = (origin_x-66.30000114440918,origin_y-86.5,130.0)
cam.location.x = 4.0
cam.location.y = 10.0
cam.rotation_euler = (0.0,0.0,0.0)
cam_data.type = 'ORTHO'; cam_data.ortho_scale = 145.0
scene.camera = cam
old_engine = scene.render.engine
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    pass
scene.render.resolution_x = 1200; scene.render.resolution_y = 1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath = str(AUDIT/'mechanical_engineering_r3_registered_roof_top.png')
scene.render.film_transparent = True
scene.render.image_settings.color_mode='RGBA'
scene.render.resolution_percentage=75
bpy.ops.render.render(write_still=True)
scene.camera = old_camera
bpy.data.objects.remove(cam,do_unlink=True)
bpy.data.cameras.remove(cam_data)
print(json.dumps(validation,indent=2))
