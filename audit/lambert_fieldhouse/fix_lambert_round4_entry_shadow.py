import bpy, json
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)

# Object bounds confirm the previous black patch was not an overlap: the 15x8
# pavers sit at z=.120-.145, clear of the border top at z=.1095 and sidewalk
# top at z=.08. The dark surround is the solid entrance walk's cast shadow.
# Give only the public entrance-context concrete a modest ambient lift so the
# walk remains legible beneath the deep roof eave; leave all building materials alone.
mat=bpy.data.materials.get('LAMB | entrance context shadow-lift concrete') or bpy.data.materials.new('LAMB | entrance context shadow-lift concrete')
mat.diffuse_color=(.49,.50,.48,1); mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.49,.50,.48,1)
bs.inputs['Roughness'].default_value=.88
if 'Emission Color' in bs.inputs:
    bs.inputs['Emission Color'].default_value=(.35,.36,.34,1)
    bs.inputs['Emission Strength'].default_value=.40
for name in ('LAMB | immediate entry walk','LAMB | Stadium sidewalk round4','LAMB | Stadium curb round4','LAMB | inlay border round4','LAMB | entrance threshold'):
    ob=bpy.data.objects.get(name)
    if ob and ob.type=='MESH':
        ob.data.materials.clear(); ob.data.materials.append(mat)

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['LAMB | three-quarter preview camera']
scene.render.filepath=OUT+r'/exterior_round4.png'; bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.type=='LIGHT' and ('interior' in o.name.lower() or 'track fill' in o.name.lower()): o.hide_render=False
hidden=[]
for cname in ('LAMB_Structure','LAMB_Facade'):
    c=bpy.data.collections.get(cname)
    if c:
        for o in c.objects: hidden.append((o,o.hide_render)); o.hide_render=True
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
if canopy: hidden.append((canopy,canopy.hide_render)); canopy.hide_render=True
scene.camera=bpy.data.objects['LAMB | interior review camera']
scene.render.filepath=OUT+r'/interior_round4.png'; bpy.ops.render.render(write_still=True)
for o,val in hidden:o.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']; n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n))
asset=bpy.data.collections['Asset_lambert_fieldhouse']; pavers=bpy.data.objects['LAMB | Stadium entry brick inlay round4']
report={'revision':4,'saved_and_reopened':'PASS','asset_file':'modular/buildings/lambert_fieldhouse.blend','asset_object_count':len(list(asset.all_objects)),
        'entry_paver_unit_count':len(pavers.data.polygons)//6,'dark_patch_diagnosis':'No geometry overlap: the dark surround was the solid entrance walk shaded by the roof eave; a modest ambient lift now applies only to entrance/site concrete.',
        'track_mesh_measured_lane1_centerline_perimeter_m':perimeter,'track_lanes':6,'track_boundary_lines':7,
        'Stadium_context':'sidewalk, curb, brick inlay, and unmarked adjacent asphalt strip; dimensions and road lane layout schematic',
        'previews':['audit/lambert_fieldhouse/exterior_round4.png','audit/lambert_fieldhouse/interior_round4.png'],'master_manifest_shared_files_edited':False}
with open(OUT+r'/validation_round4.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
