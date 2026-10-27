import bpy, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
asset=bpy.data.collections.get('Asset_heine_pharmacy')
assert asset
shell=bpy.data.objects.get('RHPH structural shell | GIS outline')
assert shell
bounds=[]
for axis in range(3):
    vals=[(shell.matrix_world@v.co)[axis] for v in shell.data.vertices]
    bounds.append([min(vals),max(vals)])
front=bpy.data.objects.get('Heine evidence facade | seven vertical window stacks')
stone=bpy.data.objects.get('Heine evidence facade | limestone window surrounds and spandrels')
mullions=bpy.data.objects.get('Heine evidence facade | vertical sash mullions')
assert front and stone and mullions
assert len(front.data.polygons)==35
assert len(stone.data.polygons)==63
assert len(mullions.data.polygons)==35
assert not any(o.name.startswith('RHPH vertical corridor glazing |') or o.name.startswith('RHPH vertical limestone piers | pier ') for o in bpy.data.objects)
mat=bpy.data.materials['HEINE_PHARMACY | evidence palette textured masonry']
brick_node=next(n for n in mat.node_tree.nodes if n.type=='TEX_BRICK')
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bump=next(n for n in mat.node_tree.nodes if n.type=='BUMP')
links=mat.node_tree.links
assert any(l.from_node==brick_node and l.from_socket.name=='Color' and l.to_node==bsdf and l.to_socket.name=='Base Color' for l in links)
assert any(l.from_node==bump and l.to_node==bsdf and l.to_socket.name=='Normal' for l in links)
missing=[]
for img in bpy.data.images:
    if img.source=='FILE' and img.filepath and not img.packed_file:
        path=bpy.path.abspath(img.filepath, library=img.library)
        if not Path(path).exists(): missing.append(path)
assert not missing, missing
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
preview=root/'audit'/'heine_pharmacy'/'heine_pharmacy_fresh_open.png'
scene.render.filepath=str(preview); scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True)
report={
 'status':'PASS','blender_version':bpy.app.version_string,
 'reopened_file':bpy.data.filepath,'stable_collection':asset.name,
 'asset_object_count':len(asset.all_objects),'footprint_bounds_local_m':bounds,
 'front_window_panes':len(front.data.polygons),'stone_surround_and_spandrel_faces':len(stone.data.polygons),
 'mullion_faces':len(mullions.data.polygons),'stale_overglazing_objects':False,
 'procedural_brick_color_and_bump_links':True,'missing_texture_paths':missing,
 'preview_path':str(preview),'uncertainty':'Facade bay rhythm follows one dated exterior photograph; hidden elevations, exact opening dimensions, height and interior plan remain estimated/schematic.'}
(root/'audit'/'heine_pharmacy'/'fresh_open_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
