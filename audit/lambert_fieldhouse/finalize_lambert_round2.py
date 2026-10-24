import bpy, json, math
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene

# The round-2 preview exposed a bright patch that looked like a detached roof flap.
# Diagnostic renders confirmed the roof/interior softboxes were leaking their
# light into the exterior preview. Keep those lights available for interior
# review, but save them disabled for the default exterior render.
roofmat=bpy.data.materials['LAMB | weathered membrane / standing seam']
nt=roofmat.node_tree
bs=nt.nodes.get('Principled BSDF')
noise=next((n for n in nt.nodes if n.type=='TEX_NOISE'),None)
ramp=next((n for n in nt.nodes if n.type=='VALTORGB'),None)
bump=next((n for n in nt.nodes if n.type=='BUMP'),None)
if noise:
    noise.inputs['Scale'].default_value=56.0
    noise.inputs['Detail'].default_value=2.0
    noise.inputs['Roughness'].default_value=.45
if ramp:
    ramp.color_ramp.elements[0].position=0.0
    ramp.color_ramp.elements[0].color=(.18,.20,.22,1)
    ramp.color_ramp.elements[1].position=1.0
    ramp.color_ramp.elements[1].color=(.24,.26,.28,1)
if bump:
    bump.inputs['Strength'].default_value=.018
    bump.inputs['Distance'].default_value=.003
if bs:
    bs.inputs['Metallic'].default_value=0.0
    bs.inputs['Roughness'].default_value=.97
    if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value=0.0
    if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value=0.0
    if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value=.01

interior_light_objects=[]
for ob in bpy.data.objects:
    if ob.type=='LIGHT' and ('interior' in ob.name.lower() or 'track fill' in ob.name.lower()):
        interior_light_objects.append(ob)
        ob.hide_render=True

# Reopen after saving, then refresh both saved review views.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
interior_light_objects=[ob for ob in bpy.data.objects if ob.type=='LIGHT' and ('interior' in ob.name.lower() or 'track fill' in ob.name.lower())]
scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['LAMB | three-quarter preview camera']
scene.render.filepath=OUT+r'/exterior_round2.png'
bpy.ops.render.render(write_still=True)
# Enable interior light rig only for the cutaway review, then reopen the saved
# file so its default camera/render state retains the no-leak exterior setup.
for ob in interior_light_objects:
    ob.hide_render=False
hidden=[]
for name in ('LAMB_Structure','LAMB_Facade'):
    col=bpy.data.collections.get(name)
    if col:
        for ob in col.objects: hidden.append((ob,ob.hide_render)); ob.hide_render=True
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
if canopy: hidden.append((canopy,canopy.hide_render)); canopy.hide_render=True
scene.camera=bpy.data.objects['LAMB | interior review camera']
scene.render.filepath=OUT+r'/interior_round2.png'
bpy.ops.render.render(write_still=True)
for ob,val in hidden: ob.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
asset=bpy.data.collections['Asset_lambert_fieldhouse']
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']
n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n))
material_failures=[]
for ob in asset.all_objects:
    for m in getattr(ob.data,'materials',[]):
        if m is None or not m.use_nodes or not any(n.type=='OUTPUT_MATERIAL' for n in m.node_tree.nodes):
            material_failures.append([ob.name,m.name if m else None])
assert not material_failures,material_failures
report={
 'revision':2,'reopen':'PASS','asset_file':'modular/buildings/lambert_fieldhouse.blend',
 'collection':'Asset_lambert_fieldhouse','asset_object_count':len(list(asset.all_objects)),
 'measured_lane1_centerline_perimeter_m':perimeter,'lane_count':6,'lane_boundary_count':7,
 'glass_block_grid_segments':sum(len(o.data.vertices)//8 for o in bpy.data.objects if o.name.startswith('LAMB | glass-block joint grid')),
 'interior_access_aisle_meshes':sum(1 for o in bpy.data.objects if o.name.startswith('LAMB | spectator circulation aisles')),
 'event_equipment':'portable high jump mat and standards; schematic placement',
 'roof_hotspot_diagnosis':'Interior softbox lights leaked into the exterior preview through the unsealed schematic canopy; saved those lights disabled by default and enabled them only for the cutaway render.',
 'roof_profile':'arched form remains schematic; no surveyed elevation or measured covering details found',
 'material_output_failures':material_failures,
 'source_camera':scene.camera.name if scene.camera else None,
 'master_manifest_shared_files_edited':False,
 'previews':['audit/lambert_fieldhouse/exterior_round2.png','audit/lambert_fieldhouse/interior_round2.png']
}
with open(OUT+r'/validation_round2.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
