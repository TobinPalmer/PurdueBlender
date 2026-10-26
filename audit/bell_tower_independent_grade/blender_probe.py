import bpy, json, math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/bell_tower.blend'
MANIFEST=ROOT/'modular/manifest.json'
EXPECTED='Asset_bell_tower'
SCENE='Building_bell_tower'

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
entry=next(x for x in manifest['assets'] if x['id']=='bell_tower')
collection=bpy.data.collections.get(EXPECTED)
assert collection is not None
assert collection.name==entry['collection']
assert bpy.context.scene.name==SCENE
assert len(collection.objects)==entry['object_count']
objects=sorted(o.name for o in collection.objects)
assert objects==sorted(entry['objects'])
depsgraph=bpy.context.evaluated_depsgraph_get()
allpts=[]; names_bounds={}; ground_foot_bottom_xy=[]; mesh_count=0; cameras_lights=[]; external_images=[]; packed_images=[]; linked=[]
for obj in collection.objects:
    if obj.type in {'CAMERA','LIGHT'}: cameras_lights.append((obj.name,obj.type))
    if obj.library: linked.append(obj.library.filepath)
    if obj.type=='MESH':
        mesh_count+=1
        ev=obj.evaluated_get(depsgraph); mesh=ev.to_mesh()
        pts=[ev.matrix_world @ v.co for v in mesh.vertices]
        ev.to_mesh_clear()
        if pts:
            names_bounds[obj.name]=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
            if obj.name.startswith('Ground_Limestone_Foot_'):
                ground_foot_bottom_xy.extend([[float(p.x),float(p.y)] for p in pts if abs(p.z)<1e-5])
            allpts.extend(pts)
    for slot in obj.material_slots:
        mat=slot.material
        if mat and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image:
                    if node.image.filepath and not node.image.packed_file:
                        external_images.append(node.image.filepath)
                    if node.image.packed_file: packed_images.append(node.image.name)
bounds=[[min(p[i] for p in allpts),max(p[i] for p in allpts)] for i in range(3)]
# Structural ground piers and shaft are separate useful envelope definitions for an open tower.
def merge_bounds(names):
    pts=[]
    for n in names:
        b=names_bounds.get(n)
        if b:
            for i in range(3):
                pass
            pts.append(b)
    return [[min(b[i][0] for b in pts),max(b[i][1] for b in pts)] for i in range(3)] if pts else None
pier_names=[n for n in names_bounds if n.startswith('Ground_Limestone_Pier_') or n.startswith('Ground_Limestone_Foot_')]
shaft_names=[n for n in names_bounds if n=='Shaft_Structural_Envelope']
roof_names=[n for n in names_bounds if n.startswith('Pyramidal_Metal_Roof') or n.startswith('Finial_')]
# collection-only export/reopen probe
probe=HERE/'collection_export_probe.blend'
bpy.data.libraries.write(str(probe),{collection},path_remap='RELATIVE_ALL',fake_user=True)
export_bpy=HERE/'verify_export_reopen.py'
export_bpy.write_text('''import bpy, json\nfrom pathlib import Path\nexpected="Asset_bell_tower"\np=Path(__file__).with_name("collection_export_probe.blend")\nbpy.ops.wm.open_mainfile(filepath=str(p))\nc=bpy.data.collections.get(expected)\nassert c is not None\nassert len(c.objects)==578\nassert all(o.type not in {"CAMERA","LIGHT"} for o in c.objects)\nprint(json.dumps({"reopened_collection":c.name,"object_count":len(c.objects),"camera_light_objects":[(o.name,o.type) for o in c.objects if o.type in {"CAMERA","LIGHT"}],"object_names":sorted(o.name for o in c.objects)}))\n''',encoding='utf-8')
# Save report; the second Blender invocation reopens collection-only probe.
report={
 'asset':str(ASSET),'scene':bpy.context.scene.name,'collection':collection.name,
 'manifest_id':entry['id'],'manifest_collection_matches':collection.name==entry['collection'],
 'object_count':len(collection.objects),'manifest_object_count':entry['object_count'],'object_names':objects,
 'object_names_match_manifest':objects==sorted(entry['objects']),'mesh_count':mesh_count,
 'evaluated_geometry_bounds_local_m':bounds,'structural_ground_pier_bounds_local_m':merge_bounds(pier_names),
 'ground_foot_bottom_xy':ground_foot_bottom_xy,'ground_pier_names':pier_names,'ground_feature_bounds':{n:names_bounds[n] for n in pier_names},'ground_foot_centers_xy':{n:[(names_bounds[n][0][0]+names_bounds[n][0][1])/2,(names_bounds[n][1][0]+names_bounds[n][1][1])/2] for n in pier_names if n.startswith('Ground_Limestone_Foot_')},'shaft_bounds_local_m':merge_bounds(shaft_names),
 'shaft_names':shaft_names,'roof_finial_bounds_local_m':merge_bounds(roof_names),
 'asset_camera_or_light_objects':cameras_lights,'external_unpacked_images':sorted(set(external_images)),
 'packed_images':sorted(set(packed_images)),'linked_library_paths':sorted(set(linked)),
 'export_probe':str(probe),'blender_version':bpy.app.version_string,
 'manifest_origin':entry.get('placement_origin_xy_m'),'manifest_world_bounds':entry.get('bounds_world_m'),
 'manifest_local_bounds':entry.get('local_bounds_m')
}
(HERE/'blender_probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

