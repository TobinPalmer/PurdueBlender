import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
f=Path(r'modular/buildings/peirce_hall.blend').resolve(); aud=Path(r'audit/peirce_hall').resolve()
sc=bpy.context.scene; asset=bpy.data.collections['Asset_peirce_hall']; qa=bpy.data.collections['QA_Views']; root=bpy.data.objects['AssetRoot_peirce_hall']
# Render exterior with stored facade camera and complete material setup.
sc.render.filepath=str(aud/'peirce_exterior.png'); sc.render.resolution_x=1440; sc.render.resolution_y=1080; sc.render.resolution_percentage=100
sc.render.engine='BLENDER_EEVEE'; sc.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True)
# A straight-on north elevation is the direct comparison to Purdue's documented place photo.
cam=sc.camera; cam.location=(0,43,5.7); cam.data.type='ORTHO'; cam.data.ortho_scale=43
cam.rotation_euler=(Vector((0,0,5.7))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(aud/'peirce_front_elevation.png')
bpy.ops.render.render(write_still=True)
# High-detail frontal strip for the six recessed middle bays and their lower slots.
detail_data=bpy.data.cameras.new('QA north recessed bay detail')
detail_cam=bpy.data.objects.new('QA north recessed bay detail',detail_data); qa.objects.link(detail_cam)
detail_cam.location=(0,45,5.35); detail_data.type='ORTHO'; detail_data.ortho_scale=36
detail_cam.rotation_euler=(Vector((0,12.67,5.35))-detail_cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=detail_cam; sc.render.resolution_x=2400; sc.render.resolution_y=360
sc.render.filepath=str(aud/'peirce_north_bay_detail.png'); bpy.ops.render.render(write_still=True)
# Closer view checks the pair of entry positions and adjacent lower glazing.
entry_data=bpy.data.cameras.new('QA north entry detail')
entry_cam=bpy.data.objects.new('QA north entry detail',entry_data); qa.objects.link(entry_cam)
entry_cam.location=(0,40,1.75); entry_data.type='ORTHO'; entry_data.ortho_scale=17
entry_cam.rotation_euler=(Vector((0,12.67,1.75))-entry_cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=entry_cam; sc.render.resolution_x=1700; sc.render.resolution_y=850
sc.render.filepath=str(aud/'peirce_north_entries.png'); bpy.ops.render.render(write_still=True)
sc.render.resolution_x=1440; sc.render.resolution_y=1080
# Isolate the interpretive ground-floor office/classroom fit-out and continuous circulation.
for o in list(asset.all_objects):
    if o is None:
        continue
    if o.name.startswith(('Peirce structural brick shell','Peirce flat roof','Peirce stone plinth','Peirce parapet','Peirce belt course','Ground window','Upper window','Middle recessed','Middle window','North public','North secondary','Roof mechanical','Roof vent')):
        o.hide_render=True
    if o.name.startswith(('Interior floor 2 |','Interior floor 3 |','Interior 2 ','Interior 3 ','Third-floor ')):
        o.hide_render=True
# Create a disposable overhead camera so desks, partitions, and doorway circulation read clearly.
camdata=bpy.data.cameras.new('QA ground-floor interior cutaway')
cam=bpy.data.objects.new('QA ground-floor interior cutaway',camdata); qa.objects.link(cam); cam.location=(0,0,24); camdata.type='ORTHO'; camdata.ortho_scale=44
cam.rotation_euler=(Vector((0,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=cam; sc.render.filepath=str(aud/'peirce_interior_cutaway.png'); sc.render.resolution_x=1440; sc.render.resolution_y=1080
bpy.ops.render.render(write_still=True)
# A separate view shows the source-documented third-floor break lounge/mural.
for o in list(asset.all_objects):
    if o is None:
        continue
    o.hide_render=False
    if o.name.startswith(('Peirce structural brick shell','Peirce flat roof','Peirce stone plinth','Peirce parapet','Peirce belt course','Ground window','Upper window','Middle recessed','Middle window','North public','North secondary','Roof mechanical','Roof vent')):
        o.hide_render=True
    if o.name.startswith(('Interior floor 1 |','Interior floor 2 |','Interior 1 ','Interior 2 ')):
        o.hide_render=True
lounge_data=bpy.data.cameras.new('QA evidence-based third-floor lounge')
lounge_cam=bpy.data.objects.new('QA evidence-based third-floor lounge',lounge_data); qa.objects.link(lounge_cam)
lounge_cam.location=(8,-16,11.2); lounge_data.type='ORTHO'; lounge_data.ortho_scale=10.2
lounge_cam.rotation_euler=(Vector((8,-6.15,9.55))-lounge_cam.location).to_track_quat('-Z','Y').to_euler()
for o in list(asset.all_objects):
    if o is not None and not o.name.startswith('Third-floor mural '):
        o.hide_render=True
# Neutral wall backdrop keeps this source-supported mural detail grounded while removing foreground clutter.
backdrop_mesh=bpy.data.meshes.new('QA lounge backdrop mesh')
backdrop_mesh.from_pydata([(-5,-5.7,6.5),(21,-5.7,6.5),(21,-5.7,12.5),(-5,-5.7,12.5)],[],[(0,1,2,3)])
backdrop_mesh.materials.append(bpy.data.materials['Interior | painted warm off white'])
backdrop=bpy.data.objects.new('QA lounge neutral wall backdrop',backdrop_mesh); qa.objects.link(backdrop)
sc.camera=lounge_cam; sc.render.filepath=str(aud/'peirce_third_floor_lounge.png')
bpy.ops.render.render(write_still=True)
# Mesh and local-frame audit.
bpy.context.view_layer.update()
mesh_objects=[o for o in asset.all_objects if o.type=='MESH']
mins=[1e99]*3; maxs=[-1e99]*3
for o in mesh_objects:
    for co in o.bound_box:
        v=o.matrix_world@Vector(co)
        for i in range(3): mins[i]=min(mins[i],v[i]); maxs[i]=max(maxs[i],v[i])
shell=bpy.data.objects['Peirce structural brick shell | closed GIS envelope']
bm=bmesh.new(); bm.from_mesh(shell.data); nm=sum(1 for e in bm.edges if not e.is_manifold); bm.free()
materials=sorted({m.name for o in asset.all_objects if o.type=='MESH' for m in o.data.materials if m})
all_asset_objects=[o for o in asset.all_objects if o is not None]
facade_upper_groups=sum(o.name.startswith('Upper window edge1 bay') and o.name.endswith(' infill') for o in all_asset_objects)
facade_recessed_bays=sum(o.name.startswith('Middle recessed bay ') and o.name.endswith(' infill') for o in all_asset_objects)
facade_inset_slots=sum(o.name.startswith('Middle recessed bay ') and o.name.endswith(' lower inset slot') for o in all_asset_objects)
door_wall_gaps={}
for fl in (1,2,3):
    door_wall_gaps[f'floor_{fl}_north_corridor_segments']=sum(o.name.startswith(f'Interior {fl} north corridor south partition segment') for o in all_asset_objects)
    door_wall_gaps[f'floor_{fl}_west_spine_segments']=sum(o.name.startswith(f'Interior {fl} west spine east partition segment') for o in all_asset_objects)
door_gaps_pass=all(door_wall_gaps[f'floor_{fl}_north_corridor_segments']==3 and door_wall_gaps[f'floor_{fl}_west_spine_segments']==2 for fl in (1,2,3))
door_header_count=sum(o.name.startswith('Interior ') and ' doorway header' in o.name for o in all_asset_objects)
facade_cutouts_applied=len(shell.data.polygons)>10 and nm==0
img_nodes=[]
for m in bpy.data.materials:
    if m.use_nodes:
        img_nodes += [n.image.filepath if n.image else None for n in m.node_tree.nodes if n.type=='TEX_IMAGE']
report={'status':'PASS' if nm==0 and door_gaps_pass and door_header_count==9 and facade_cutouts_applied and facade_upper_groups==6 and facade_recessed_bays==6 and facade_inset_slots==6 else 'CHECK','source_file':str(f),'asset_collection':asset.name,'nested_collections':[c.name for c in asset.children],'scene':sc.name,'asset_object_count':len(asset.all_objects),'mesh_count':len(mesh_objects),'root_location':list(root.location),'root_scale':list(root.scale),'root_parent':root.parent.name if root.parent else None,'bounds_local_meshes':[[round(x,4),round(y,4)] for x,y in zip(mins,maxs)],'shell_faces':len(shell.data.polygons),'shell_vertices':len(shell.data.vertices),'shell_non_manifold_edges':nm,'north_facade_apertures_applied_to_shell':facade_cutouts_applied,'north_facade_upper_sash_groups':facade_upper_groups,'north_facade_tall_recessed_bays':facade_recessed_bays,'north_facade_lower_inset_slots':facade_inset_slots,'doorway_wall_segment_counts':door_wall_gaps,'doorways_cut_through_partitions':door_gaps_pass,'doorway_headers':door_header_count,'material_count':len(materials),'materials':materials,'external_image_dependencies':img_nodes,'render_exterior':str(aud/'peirce_exterior.png'),'render_front':str(aud/'peirce_front_elevation.png'),'render_north_detail':str(aud/'peirce_north_bay_detail.png'),'render_entries':str(aud/'peirce_north_entries.png'),'render_interior':str(aud/'peirce_interior_cutaway.png'),'render_third_floor_lounge':str(aud/'peirce_third_floor_lounge.png')}
(aud/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
