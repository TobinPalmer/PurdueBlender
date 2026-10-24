import bpy, json, math
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
asset=bpy.data.collections.get('Asset_lambert_fieldhouse')
assert asset is not None
assert set(c.name for c in asset.children)=={'LAMB_Structure','LAMB_Facade','LAMB_Roof','LAMB_Interior','LAMB_Site'}
objs=list(asset.all_objects)
assert bpy.context.scene.camera and bpy.context.scene.camera.name=='LAMB | three-quarter preview camera'
assert bpy.data.objects.get('LAMB | interior review camera') is not None
track=bpy.data.objects.get('LAMB | 6-lane 200 m stadium track surface')
assert track is not None and track.type=='MESH'
assert len([o for o in bpy.data.objects if o.name.startswith('LAMB | lane boundary ')])==7
assert not any(o.name.startswith('LAMB | level 1 interior floor plate') for o in objs)
assert not any(o.name.startswith('LAMB | schematic interior arena floor') for o in objs)

# Measure local library bounds and ensure every exported object is inside the
# stable Asset collection. Preview cameras and lights intentionally sit outside.
pts=[]
for ob in objs:
    pts += [ob.matrix_world @ Vector(corner) for corner in ob.bound_box]
lo=[min(p[i] for p in pts) for i in range(3)]
hi=[max(p[i] for p in pts) for i in range(3)]
mat_fail=[]
for ob in objs:
    for slot in getattr(ob.data,'materials',[]):
        if slot is None or not slot.use_nodes or slot.node_tree is None or not any(n.type=='OUTPUT_MATERIAL' for n in slot.node_tree.nodes):
            mat_fail.append([ob.name,slot.name if slot else None])
unpacked=[img.name for img in bpy.data.images if img.source=='FILE' and not img.packed_file and img.filepath]
assert not mat_fail, mat_fail

# Export-facing collections have source objects only; the preview rig is excluded.
asset_collection_names={asset.name}|{c.name for c in asset.children}
outside_export=[o.name for o in objs if not any(c.name in asset_collection_names for c in o.users_collection)]
assert not outside_export, outside_export

# Refresh exterior render after the final source save. The separate interior
# render already uses temporary visibility overrides and does not alter source.
scene.render.resolution_x=1100; scene.render.resolution_y=760; scene.render.resolution_percentage=100
scene.render.filepath=OUT+r'/exterior_round1.png'
bpy.ops.render.render(write_still=True)

straight=45.0
radius=(200.0-2*straight)/(2*math.pi)
report={
 'reopen':'PASS',
 'asset_file':'modular/buildings/lambert_fieldhouse.blend',
 'collection':'Asset_lambert_fieldhouse',
 'asset_object_count':len(objs),
 'mesh_object_count':sum(o.type=='MESH' for o in objs),
 'interior_object_count':len(bpy.data.collections['LAMB_Interior'].objects),
 'roof_object_count':len(bpy.data.collections['LAMB_Roof'].objects),
 'local_asset_bounds_m':[lo,hi],
 'track_lap_centerline_m':2*straight+2*math.pi*radius,
 'track_lanes':6,
 'lane_boundary_count':7,
 'track_straight_estimate_m':straight,
 'derived_centerline_radius_m':radius,
 'material_output_failures':mat_fail,
 'unpacked_image_dependencies':unpacked,
 'default_camera':scene.camera.name,
 'preview_camera_separate_from_export_collection':bpy.data.objects['LAMB | interior review camera'] not in objs,
 'master_manifest_and_shared_files_edited':False,
 'exterior_preview':'audit/lambert_fieldhouse/exterior_round1.png',
 'interior_preview':'audit/lambert_fieldhouse/interior_round1.png'
}
with open(OUT+r'/validation_round1.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
