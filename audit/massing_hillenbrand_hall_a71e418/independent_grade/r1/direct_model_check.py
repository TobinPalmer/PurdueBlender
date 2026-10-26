import bpy, json
from mathutils import Vector
from pathlib import Path
root=Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
asset=root/'modular/buildings/massing_hillenbrand_hall_a71e418.blend'
out=root/'audit/massing_hillenbrand_hall_a71e418/independent_grade/r1/direct_model_check.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.data.scenes.get('Building_massing_hillenbrand_hall_a71e418')
coll=bpy.data.collections.get('Asset_massing_hillenbrand_hall_a71e418')
meshes=[o for o in bpy.data.objects if o.type=='MESH']
objects=[]
for o in meshes:
    verts=[o.matrix_world @ Vector(v) for v in o.bound_box]
    objects.append({'name':o.name,'vertex_count':len(o.data.vertices),'face_count':len(o.data.polygons),'world_bounds':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)],'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'modifiers':[m.name for m in o.modifiers],'material_slots':[m.name if m else None for m in o.data.materials]})
checks={'scene':scene is not None,'export_collection':coll is not None,'single_mesh':len(meshes)==1,'mesh_in_export_collection':len(meshes)==1 and coll is not None and meshes[0].name in coll.objects,'no_modifiers':len(meshes)==1 and not meshes[0].modifiers,'no_file_images':all(not im.filepath for im in bpy.data.images if im.source=='FILE')}
result={'blender_version':bpy.app.version_string,'asset_path':str(asset),'scene_name':scene.name if scene else None,'collection_name':coll.name if coll else None,'objects':objects,'checks':checks,'all_checks_pass':all(checks.values())}
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
