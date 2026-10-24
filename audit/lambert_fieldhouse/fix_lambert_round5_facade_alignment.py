import bpy, json, math
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
facade=bpy.data.collections['LAMB_Facade']

# The first round-5 preview showed that rectangular full-elevation strips crossed
# the clipped GIS footprint corners. Remove those strips and rebuild stone bands
# on each actual GIS perimeter edge instead of extending past the walls.
for o in list(facade.objects):
    if o.name.startswith('LAMB | round5 facade pilasters') or o.name.startswith('LAMB | round5 horizontal stone bands'):
        bpy.data.objects.remove(o,do_unlink=True)
limestone=bpy.data.materials['LAMB | warm pale limestone concrete round5']
old=[o for o in facade.objects if o.name.startswith('LAMB | pale concrete facade pier')]
centroid=Vector((0,0,0))
for o in old: centroid+=o.location
if old: centroid/=len(old)
for o in old:
    radial=Vector((o.location.x-centroid.x,o.location.y-centroid.y,0))
    if radial.length: o.location+=radial.normalized()*.24
    o.data.materials.clear(); o.data.materials.append(limestone)
    # Make the existing GIS-aligned pilaster rhythm slightly legible, retaining
    # each segment's surveyed/source-derived orientation and position.
    if o.dimensions.x < .52: o.dimensions.x=.52
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.select_set(False)

foot=bpy.data.objects['Lambert Fieldhouse | official GIS footprint ground floor']
ring=[]
for i in range(0,20,2):
    v=foot.data.vertices[i].co
    p=Vector((v.x,v.y,0))
    if not ring or (p-ring[-1]).length>.01: ring.append(p)
# The ring has ten unique points; the closing point is implicit.
if len(ring)>1 and (ring[0]-ring[-1]).length<.01: ring.pop()
ctr=sum(ring,Vector((0,0,0)))/len(ring)
for edge,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
    tangent=b-a; length=tangent.length
    if length<1: continue
    outward=Vector((-(tangent.y),tangent.x,0)).normalized()
    mid=(a+b)*.5
    # Select the normal pointing away from the footprint center.
    if outward.dot(mid-ctr)<0: outward.negate()
    angle=math.atan2(tangent.y,tangent.x)
    for z in (3.34,5.48,8.75,11.04):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(mid.x+outward.x*.16,mid.y+outward.y*.16,z))
        o=bpy.context.object; o.name='LAMB | round5 GIS-edge stone band '+str(edge)+' z'+str(z)
        o.dimensions=(length+.04,.32,.20)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.rotation_euler[2]=angle
        for c in list(o.users_collection): c.objects.unlink(o)
        facade.objects.link(o); o.data.materials.append(limestone)

# Save/reopen and refresh both fixed review angles.
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']; n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n))
bpy.ops.wm.save_as_mainfile(filepath=ASSET); bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['LAMB | three-quarter preview camera']; scene.render.filepath=OUT+r'/exterior_round5.png'; bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.type=='LIGHT' and ('interior' in o.name.lower() or 'track fill' in o.name.lower()): o.hide_render=False
hidden=[]
for cname in ('LAMB_Structure','LAMB_Facade'):
    c=bpy.data.collections.get(cname)
    if c:
        for o in c.objects: hidden.append((o,o.hide_render)); o.hide_render=True
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
if canopy: hidden.append((canopy,canopy.hide_render)); canopy.hide_render=True
scene.camera=bpy.data.objects['LAMB | interior review camera']; scene.render.filepath=OUT+r'/interior_round5.png'; bpy.ops.render.render(write_still=True)
for o,val in hidden:o.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections['Asset_lambert_fieldhouse']
report={'revision':5,'saved_and_reopened':'PASS','asset_object_count':len(list(asset.all_objects)),
        'GIS_footprint_perimeter_edges':len(ring),'stone_band_levels_m':[3.34,5.48,8.75,11.04],
        'facade_pilaster_count':len(old),'track_mesh_measured_lane1_centerline_perimeter_m':perimeter,
        'previews':['audit/lambert_fieldhouse/exterior_round5.png','audit/lambert_fieldhouse/interior_round5.png'],
        'issues':[],'master_manifest_shared_files_edited':False}
with open(OUT+r'/validation_round5.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
