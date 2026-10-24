import bpy, json
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
site=bpy.data.collections['LAMB_Site']
scene=bpy.context.scene

# The first paver preview used the facade's small-object brick coordinates and
# rendered almost black. Replace it with a dedicated warm red paver material and
# actual staggered units. The GCP record supports a brick inlay at this entrance;
# no surveyed paving dimensions are claimed.
for ob in list(site.objects):
    if ob.name.startswith('LAMB | Stadium entry brick inlay round3'):
        bpy.data.objects.remove(ob,do_unlink=True)

mat=bpy.data.materials.get('LAMB | Stadium entry paver red-brown') or bpy.data.materials.new('LAMB | Stadium entry paver red-brown')
mat.diffuse_color=(.48,.17,.09,1); mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.48,.17,.09,1); bs.inputs['Roughness'].default_value=.82; bs.inputs['Metallic'].default_value=0

verts=[]; faces=[]
def append_box(center,size):
    x,y,z=center; sx,sy,sz=(q*.5 for q in size); n=len(verts)
    verts.extend([(x-sx,y-sy,z-sz),(x+sx,y-sy,z-sz),(x+sx,y+sy,z-sz),(x-sx,y+sy,z-sz),
                  (x-sx,y-sy,z+sz),(x+sx,y-sy,z+sz),(x+sx,y+sy,z+sz),(x-sx,y+sy,z+sz)])
    faces.extend([tuple(n+i for i in face) for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
cols,rows=14,6
width,depth=3.30,.75
for row in range(rows):
    for col in range(cols):
        pitch_x=width/cols; pitch_y=depth/rows
        x=-width/2+(col+.5)*pitch_x + (pitch_x*.5 if row%2 else 0)
        y=-50.20-depth/2+(row+.5)*pitch_y
        # Keep the staggered half-bricks within the same inlay border.
        if x > width/2-pitch_x*.40: continue
        append_box((x,y,.1325),(pitch_x-.012,pitch_y-.012,.025))
me=bpy.data.meshes.new('LAMB | entrance inlay staggered pavers mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
ob=bpy.data.objects.new('LAMB | Stadium entry brick inlay round3',me); site.objects.link(ob)

# Save/reopen and refresh the exterior render; keep the track geometry as saved.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['LAMB | three-quarter preview camera']
scene.render.filepath=OUT+r'/exterior_round3.png'; bpy.ops.render.render(write_still=True)
# Refresh the interior cutaway too; re-enable interior lights only for this view.
lights=[o for o in bpy.data.objects if o.type=='LIGHT' and ('interior' in o.name.lower() or 'track fill' in o.name.lower())]
for o in lights:o.hide_render=False
hidden=[]
for cname in ('LAMB_Structure','LAMB_Facade'):
    c=bpy.data.collections.get(cname)
    if c:
        for o in c.objects:hidden.append((o,o.hide_render));o.hide_render=True
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
if canopy:hidden.append((canopy,canopy.hide_render));canopy.hide_render=True
scene.camera=bpy.data.objects['LAMB | interior review camera']
scene.render.filepath=OUT+r'/interior_round3.png';bpy.ops.render.render(write_still=True)
for o,val in hidden:o.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections['Asset_lambert_fieldhouse']
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']; n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n))
report={'reopen':'PASS','asset_file':'modular/buildings/lambert_fieldhouse.blend',
        'asset_object_count':len(list(asset.all_objects)),'paver_unit_count':len(faces)//6,
        'track_mesh_measured_lane1_centerline_perimeter_m':perimeter,
        'exterior_preview':'audit/lambert_fieldhouse/exterior_round3.png',
        'master_manifest_shared_files_edited':False}
with open(OUT+r'/validation_round3.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
