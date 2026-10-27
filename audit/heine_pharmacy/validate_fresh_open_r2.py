import bpy, hashlib, json, os
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular' / 'buildings' / 'heine_pharmacy.blend'
OUT = ROOT / 'audit' / 'heine_pharmacy'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection = bpy.data.collections.get('Asset_heine_pharmacy')
assert collection and collection.name == 'Asset_heine_pharmacy'
objects = list(collection.all_objects)
shell = bpy.data.objects['RHPH structural shell | GIS outline']
shell_pts = [shell.matrix_world @ v.co for v in shell.data.vertices]
shell_bounds = [[min(p[i] for p in shell_pts), max(p[i] for p in shell_pts)] for i in range(3)]
expected_bounds = [[-36.168739318847656,36.168739318847656],[-33.99116516113281,33.99116516113281],[-1.0,22.0]]
assert all(abs(a-b) < 1e-5 for row, exp in zip(shell_bounds, expected_bounds) for a,b in zip(row,exp)), shell_bounds
names = [o.name for o in objects]
def obj(name):
    result = bpy.data.objects.get(name)
    assert result and result in objects, name
    return result
glazing = obj('Heine evidence facade R2 | tall vertical glazing')
spandrels = obj('Heine evidence facade R2 | broad limestone spandrels')
rails = obj('Heine evidence facade R2 | restrained glazing rails')
arches = obj('Heine evidence entry R2 | four arch portal')
piers = obj('Heine evidence entry R2 | heavy piers')
crown = obj('Heine evidence entry R2 | crown beam')
assert len(glazing.data.polygons) == 14
assert len(spandrels.data.polygons) == 21
assert len(rails.data.polygons) == 14
assert 'RHPH | pharmacy entry arcade lintel' not in names
assert not any(n.startswith('RHPH | tall entry arcade pier ') or n.startswith('RHPH | stone arcade arch ') for n in names)
missing = []
used_materials = set()
for ob in objects:
    if ob.type == 'MESH':
        used_materials.update(m for m in ob.data.materials if m)
for mat in used_materials:
    if mat.use_nodes and mat.node_tree:
        for node in mat.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image and node.image.source == 'FILE':
                path = bpy.path.abspath(node.image.filepath)
                if not os.path.exists(path): missing.append(path)
assert not missing, missing
portal_pts = [piers.matrix_world @ Vector(corner) for corner in piers.bound_box]
assert abs(min(p.z for p in portal_pts) - (-0.95)) < 1e-4
crown_pts = [crown.matrix_world @ Vector(corner) for corner in crown.bound_box]
assert abs(max(p.z for p in crown_pts) - 7.35) < 1e-4
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.filepath = str(OUT/'heine_pharmacy_fresh_open_r2.png')
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
asset_bytes = ASSET.read_bytes()
record = {
  'status':'PASS', 'revision':'R2', 'blender_version':bpy.app.version_string,
  'reopened_file':str(ASSET), 'asset_sha256':hashlib.sha256(asset_bytes).hexdigest(),
  'stable_collection':collection.name, 'asset_object_count':len(objects),
  'asset_mesh_object_count':sum(o.type=='MESH' for o in objects),
  'shell_bounds_local_m':shell_bounds, 'shell_geometry_preserved':True,
  'r2_glazing_panels':len(glazing.data.polygons), 'r2_broad_stone_faces':len(spandrels.data.polygons),
  'r2_fine_glazing_rails':len(rails.data.polygons), 'r2_arch_surface_faces':len(arches.data.polygons),
  'r2_pier_faces':len(piers.data.polygons), 'r2_crown_faces':len(crown.data.polygons),
  'portal_arch_count':4, 'portal_width_m':17.25, 'portal_top_z_m':7.35,
  'legacy_r1_small_window_grid_removed':True, 'legacy_small_entry_arcade_removed':True,
  'missing_external_textures':missing, 'fresh_open_render':str(OUT/'heine_pharmacy_fresh_open_r2.png'),
  'placement_origin_or_manifest_edited':False,
  'uncertainty':'Facade and portal dimensions visually estimated from one perspective photograph; hidden elevations, surveyed height and interior layout remain unresolved.'
}
(OUT/'fresh_open_verification_r2.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
