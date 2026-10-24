import bpy, json, os, math
from mathutils import Vector
asset_path=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
out_path=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/validation_round3.json'
bpy.ops.wm.open_mainfile(filepath=asset_path)
root=bpy.data.objects.get('AssetRoot_lawson_hall')
coll=bpy.data.collections.get('Asset_lawson_hall')
assert root and coll
objs=list(coll.all_objects)
mesh_objs=[o for o in objs if o.type=='MESH']
missing_mats=[o.name for o in mesh_objs if len(o.data.materials)==0]
missing_images=[]
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file and im.filepath and not os.path.exists(bpy.path.abspath(im.filepath)):
        missing_images.append({'name':im.name,'filepath':im.filepath})
# World-space bounds from all export meshes, after the saved library is reopened.
coords=[]
for o in mesh_objs:
    coords.extend(o.matrix_world @ Vector(c) for c in o.bound_box)
bounds={axis:[min(getattr(v,axis) for v in coords),max(getattr(v,axis) for v in coords)] for axis in ('x','y','z')} if coords else {}
brick=bpy.data.materials.get('LWSN_Purdue_Red_Brick')
brick_color_link=False
if brick and brick.use_nodes:
    bs=brick.node_tree.nodes.get('Principled BSDF')
    if bs:
        brick_color_link=any(l.to_node==bs and l.to_socket==bs.inputs['Base Color'] and l.from_node.name=='Brick Texture' for l in brick.node_tree.links)
result={
 'source':'modular/buildings/lawson_hall.blend','opened_from_saved_file':os.path.normcase(os.path.abspath(bpy.path.abspath(bpy.data.filepath)))==os.path.normcase(os.path.abspath(asset_path)),
 'root_name':root.name,'root_location':list(root.location),'root_rotation_euler':list(root.rotation_euler),'root_scale':list(root.scale),'root_matrix_world':[list(row) for row in root.matrix_world],
 'export_collection':'Asset_lawson_hall','export_object_count':len(objs),'mesh_object_count':len(mesh_objs),'world_bounds_m':bounds,
 'unmaterialed_meshes':missing_mats,'missing_external_images':missing_images,'brick_texture_drives_base_color':brick_color_link,
 'round3_entry_door_leaves':sum(o.name.startswith('LWSN_R3_Entry_Double_Door_Leaf') for o in objs),
 'first_floor_partition_door_leaves':sum(o.name.startswith('LWSN_R3_Plan_Door_Leaf_') for o in objs),
 'stair_flight_meshes':sum(o.name.startswith('LWSN_Stair_Flight') for o in objs),
 'round3_stair_landings':sum(o.name.startswith('LWSN_R3_Stair_Landing_') for o in objs),
 'temporary_preview_camera_saved':any(o.name.startswith('LWSN_R3_TEMP_') for o in bpy.data.objects),
 'notes':'Independent geometry detail remains illustrative; first-floor plan is north-up and approximately registered. No upper-floor plan, measured elevations, survey, or verified current roof/penthouse geometry.'
}
with open(out_path,'w',encoding='utf8') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))

