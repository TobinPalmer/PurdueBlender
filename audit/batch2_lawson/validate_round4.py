import bpy, json, os
from mathutils import Vector
ASSET=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
OUT=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/validation_round4.json'
bpy.ops.wm.open_mainfile(filepath=ASSET)
coll=bpy.data.collections.get('Asset_lawson_hall');root=bpy.data.objects.get('AssetRoot_lawson_hall')
assert coll and root
objs=[o for o in coll.all_objects if o];meshes=[o for o in objs if o.type=='MESH']
unmaterialed=[o.name for o in meshes if len(o.data.materials)==0]
missing_images=[]
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file and im.filepath and not os.path.exists(bpy.path.abspath(im.filepath)):
        missing_images.append({'name':im.name,'filepath':im.filepath})
coords=[]
for o in meshes:
    coords += [o.matrix_world @ Vector(v) for v in o.bound_box]
bounds={a:[min(getattr(v,a) for v in coords),max(getattr(v,a) for v in coords)] for a in ('x','y','z')}
brick=bpy.data.materials.get('LWSN_Purdue_Red_Brick');brick_connected=False
if brick:
    bs=brick.node_tree.nodes.get('Principled BSDF')
    brick_connected=bool(bs and any(l.to_node==bs and l.to_socket==bs.inputs['Base Color'] and l.from_node.name=='Brick Texture' for l in brick.node_tree.links))
wall=bpy.data.objects.get('LWSN_1130_Harris_Video_Wall')
round4=[o for o in objs if o.name.startswith('LWSN_R4_')]
roof_objs=[o for o in objs if o.get('evidence_status','').startswith('Schematic / unverified')]
stairs=[o for o in objs if o.name.startswith('LWSN_Stair_Flight')]
landings=[o for o in objs if o.name.startswith('LWSN_R3_Stair_Landing_')]
result={
 'source':'modular/buildings/lawson_hall.blend','reopened_saved_source':os.path.normcase(os.path.abspath(bpy.path.abspath(bpy.data.filepath)))==os.path.normcase(os.path.abspath(ASSET)),
 'export_collection':'Asset_lawson_hall','export_object_count':len(objs),'mesh_count':len(meshes),'root_name':root.name,'root_transform_identity':all(abs(root.matrix_world[i][j]-(1.0 if i==j else 0.0))<1e-7 for i in range(4) for j in range(4)),'root_matrix_world':[list(row) for row in root.matrix_world],
 'world_bounds_m':bounds,'unmaterialed_meshes':unmaterialed,'missing_external_images':missing_images,'brick_texture_drives_base_color':brick_connected,
 'round4_added_objects':len(round4),'video_wall_panel_count':sum(o.name.startswith('LWSN_R4_VideoWall_LCD_') for o in round4),'video_wall_reported_overall_dimensions_m':list(wall.dimensions) if wall else None,'video_wall_source_reported_dimensions_m':[4.8768,2.7432],
 'echo_spiral_height_m':round(max((o.matrix_world@Vector(v)).z for o in objs if o.name=='LWSN_R4_Echo_Spiral_Schematic' for v in o.bound_box)-min((o.matrix_world@Vector(v)).z for o in objs if o.name=='LWSN_R4_Echo_Spiral_Schematic' for v in o.bound_box),3) if any(o.name=='LWSN_R4_Echo_Spiral_Schematic' for o in objs) else None,
 'lobby_case_touchscreen_object_count':sum(('Kurz_Lobby' in o.name or 'Kurz_DisplayCase' in o.name) for o in round4),
 'roof_shell_objects_marked_unverified_schematic':len(roof_objs),'roof_height_verified':False,'model_max_z_m':bounds['z'][1],
 'first_floor_stair_flight_meshes':len(stairs),'first_floor_stair_flights_marked_vertical_continuity_unverified':all(o.get('evidence_status','').endswith('vertical continuity not verified') for o in stairs),'landing_meshes':len(landings),'continuous_floor_to_floor_stair_route_verified':False,
 'temporary_preview_cameras_saved':any(o.name.startswith('LWSN_R4_TEMP_') or o.name.startswith('LWSN_R3_TEMP_') for o in bpy.data.objects),
 'previews':['audit/batch2_lawson/exterior_round4.png','audit/batch2_lawson/interior_cutaway_round4.png','audit/batch2_lawson/entry_lobby_round4.png','audit/batch2_lawson/commons_wall_round4.png'],
 'limits':'The full shell/roof height reaches the reported model maximum but is unverified schematic geometry. First-floor source establishes stair locations; separate stair mesh pieces do not prove floor-to-floor continuity.'
}
with open(OUT,'w',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
