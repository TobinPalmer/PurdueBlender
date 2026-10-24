import bpy, json
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
asset=bpy.data.collections['Asset_lambert_fieldhouse']
site=bpy.data.collections['LAMB_Site']
facade=bpy.data.collections['LAMB_Facade']
rig=bpy.data.collections['Preview_Rig']

def material(name,color,rough=.7,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=color; m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    return m

def cube_in_collection(name,loc,dims,mat,col):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object; ob.name=name; ob.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    col.objects.link(ob); ob.data.materials.append(mat); return ob

# Existing block-glass panels are true openings in the facade. Make the historic
# glass-block reading stronger and less hole-like while retaining translucency.
glass=bpy.data.materials.get('LAMB | glass-block facade with interior light transmission')
if glass and glass.use_nodes:
    nt=glass.node_tree
    bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
    mix=next((n for n in nt.nodes if n.type=='MIX_SHADER'),None)
    if bs:
        bs.inputs['Base Color'].default_value=(.55,.64,.66,1)
        bs.inputs['Roughness'].default_value=.36
        if 'Emission Color' in bs.inputs:
            bs.inputs['Emission Color'].default_value=(.28,.34,.34,1)
            bs.inputs['Emission Strength'].default_value=.12
    if mix:
        # The original mix weight left 76% transparent. Set it to 43% transparent.
        mix.inputs[0].default_value=.43

# Reduce facade darkness through a neutral, camera-side softbox and modestly
# stronger preview fill. All lights are preview-rig only and export with no assets.
key=bpy.data.objects.get('LAMB Preview key')
fill=bpy.data.objects.get('LAMB Preview fill')
rim=bpy.data.objects.get('LAMB Preview rim')
top=bpy.data.objects.get('LAMB Preview top softbox')
for ob,factor in ((key,1.45),(fill,1.45),(rim,1.25),(top,.8)):
    if ob and ob.type=='LIGHT': ob.data.energy*=factor
fillname='LAMB | Stadium facade daylight fill round3'
old=bpy.data.objects.get(fillname)
if old:
    bpy.data.objects.remove(old,do_unlink=True)
light_data=bpy.data.lights.new(fillname,'AREA'); light_data.energy=42000; light_data.shape='DISK'; light_data.size=58; light_data.color=(.88,.91,1.0)
light=bpy.data.objects.new(fillname,light_data); rig.objects.link(light); light.location=(0,-92,38)
light.rotation_euler=(Vector((0,-16,5))-Vector(light.location)).to_track_quat('-Z','Y').to_euler()

# Purdue GCP notes identify the sidewalk on the north side of Stadium Ave and a
# brick inlay in the sidewalk at Lambert's main entrance. In this project-local
# orientation the main entrance is the existing south/negative-Y threshold.
# These context pieces are intentionally minimal; road geometry stays in master.
for ob in list(site.objects):
    if ob.name.startswith('LAMB | Stadium sidewalk round3') or ob.name.startswith('LAMB | Stadium curb round3') or ob.name.startswith('LAMB | Stadium entry brick inlay round3') or ob.name.startswith('LAMB | inlay border round3'):
        bpy.data.objects.remove(ob,do_unlink=True)
walk=material('LAMB | Stadium sidewalk concrete',(.48,.49,.47,1),.86)
curbmat=material('LAMB | Stadium curb concrete',(.39,.40,.39,1),.84)
brick=bpy.data.materials.get('LAMB | mottled Purdue red-brown brick')
cube_in_collection('LAMB | Stadium sidewalk round3',(0,-50.45,.04),(98.0,2.2,.08),walk,site)
cube_in_collection('LAMB | Stadium curb round3',(0,-51.62,.14),(98.0,.20,.28),curbmat,site)
cube_in_collection('LAMB | inlay border round3',(0,-50.20,.092),(3.9,1.1,.035),curbmat,site)
cube_in_collection('LAMB | Stadium entry brick inlay round3',(0,-50.20,.115),(3.45,.78,.035),brick,site)

# Keep the six-lane track and its confirmed measured geometry unchanged.
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']
n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n))

# Preserve the saved exterior-render lighting state: interior lights remain
# disabled by default. Save and reopen before rendering both views.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['LAMB | three-quarter preview camera']
scene.render.filepath=OUT+r'/exterior_round3.png'
bpy.ops.render.render(write_still=True)

# Interior cutaway: turn on the interior light rig only for this render.
lights=[ob for ob in bpy.data.objects if ob.type=='LIGHT' and ('interior' in ob.name.lower() or 'track fill' in ob.name.lower())]
for ob in lights: ob.hide_render=False
hidden=[]
for name in ('LAMB_Structure','LAMB_Facade'):
    col=bpy.data.collections.get(name)
    if col:
        for ob in col.objects: hidden.append((ob,ob.hide_render)); ob.hide_render=True
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
if canopy: hidden.append((canopy,canopy.hide_render)); canopy.hide_render=True
scene.camera=bpy.data.objects['LAMB | interior review camera']
scene.render.filepath=OUT+r'/interior_round3.png'
bpy.ops.render.render(write_still=True)
for ob,val in hidden: ob.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)

# Re-measure after reopen; this value comes from the saved mesh, not its design formula.
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']
n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
measured=sum((center[(i+1)%n]-center[i]).length for i in range(n))
asset=bpy.data.collections['Asset_lambert_fieldhouse']
glassmat=bpy.data.materials['LAMB | glass-block facade with interior light transmission']
mix=next((n for n in glassmat.node_tree.nodes if n.type=='MIX_SHADER'),None)
report={
 'revision':3,'reopen':'PASS','asset_file':'modular/buildings/lambert_fieldhouse.blend',
 'collection':'Asset_lambert_fieldhouse','asset_object_count':len(list(asset.all_objects)),
 'track_mesh_measured_lane1_centerline_perimeter_m':measured,'track_lanes':6,'track_boundary_lines':7,
 'Stadium_context':'minimal concrete walk, curb, and brick inlay outside the existing entry threshold; supported by Purdue GCP notes',
 'block_glass_transparency_mix_factor':mix.inputs[0].default_value if mix else None,
 'preview_exterior_fill_energy_w':bpy.data.objects[fillname].data.energy,
 'interior_equipment_and_seating':'retained from round 2; placement and event configuration remain schematic',
 'preview_files':['audit/lambert_fieldhouse/exterior_round3.png','audit/lambert_fieldhouse/interior_round3.png'],
 'shared_master_manifest_edited':False
}
with open(OUT+r'/validation_round3.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
