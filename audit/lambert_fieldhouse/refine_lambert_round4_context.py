import bpy, json
from mathutils import Vector

ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
site=bpy.data.collections['LAMB_Site']

def mat(name,color,rough=.8,emission=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=color; m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=color; bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=0
    if emission is not None and 'Emission Color' in bs.inputs:
        bs.inputs['Emission Color'].default_value=color
        bs.inputs['Emission Strength'].default_value=emission
    return m

def cube(name,center,dims,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    site.objects.link(o); o.data.materials.append(material); return o

# Remove only this building's prior preview context and replace the flat, nearly
# black-looking inlay/entry patch. Purdue GCP documents Stadium Avenue, the main
# entrance sidewalk, and its brick inlay; all extents here are explicitly schematic.
prefixes=('LAMB | Stadium sidewalk round3','LAMB | Stadium curb round3',
          'LAMB | Stadium entry brick inlay round3','LAMB | inlay border round3',
          'LAMB | Stadium Avenue roadway round4')
for ob in list(site.objects):
    if ob.name.startswith(prefixes): bpy.data.objects.remove(ob,do_unlink=True)

walk=mat('LAMB | Stadium sidewalk concrete',(.53,.54,.52,1),.88)
curbmat=mat('LAMB | Stadium curb concrete',(.50,.51,.49,1),.86)
asphalt=mat('LAMB | Stadium Avenue asphalt schematic',(.16,.18,.18,1),.94)
cube('LAMB | Stadium sidewalk round4',(0,-50.95,.04),(98.0,3.2,.08),walk)
cube('LAMB | Stadium curb round4',(0,-52.62,.13),(98.0,.22,.26),curbmat)
# Unmarked adjacent asphalt strip communicates the named avenue without asserting
# lane layout or surveyed street width. Road width and frontage extent are schematic.
cube('LAMB | Stadium Avenue roadway round4',(0,-56.45,-.005),(98.0,7.45,.05),asphalt)

border=cube('LAMB | inlay border round4',(0,-51.10,.092),(4.65,1.50,.035),curbmat)
palette=[mat('LAMB | entrance paver warm red',(.62,.22,.12,1),.82,.12),
         mat('LAMB | entrance paver brick red',(.49,.145,.075,1),.84,.10),
         mat('LAMB | entrance paver soft variation',(.70,.285,.15,1),.82,.12)]
verts=[]; faces=[]; face_mats=[]
def box(cx,cy,cz,sx,sy,sz,mi):
    n=len(verts); x0,x1=cx-sx/2,cx+sx/2; y0,y1=cy-sy/2,cy+sy/2; z0,z1=cz-sz/2,cz+sz/2
    verts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
    fs=((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))
    faces.extend([tuple(n+i for i in f) for f in fs]); face_mats.extend([mi,mi,mi,mi,mi,mi])

cols,rows=15,8; width,depth=4.25,1.20
px,py=width/cols,depth/rows
for row in range(rows):
    for col in range(cols):
        x=-width/2+(col+.5)*px + (px*.5 if row%2 else 0)
        if x>width/2-px*.4: continue
        y=-51.10-depth/2+(row+.5)*py
        mi=(row*3+col*5)%len(palette)
        box(x,y,.1325,px-.018,py-.018,.025,mi)
mesh=bpy.data.meshes.new('LAMB | round4 staggered entry brickwork mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
for m in palette: mesh.materials.append(m)
for p,mi in zip(mesh.polygons,face_mats): p.material_index=mi
pavers=bpy.data.objects.new('LAMB | Stadium entry brick inlay round4',mesh); site.objects.link(pavers)

# Preserve and record the direct saved-mesh track check.
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']
n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n))
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['LAMB | three-quarter preview camera']
scene.render.filepath=OUT+r'/exterior_round4.png'; bpy.ops.render.render(write_still=True)

# Render interior cutaway with lighting temporarily enabled, then reopen the
# actual saved file so exterior lights/visibility remain the stored state.
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

asset=bpy.data.collections['Asset_lambert_fieldhouse']
pavers=bpy.data.objects['LAMB | Stadium entry brick inlay round4']
report={'revision':4,'saved_and_reopened':'PASS','asset_file':'modular/buildings/lambert_fieldhouse.blend',
        'asset_object_count':len(list(asset.all_objects)),'entry_paver_unit_count':len(pavers.data.polygons)//6,
        'track_mesh_measured_lane1_centerline_perimeter_m':perimeter,'track_lanes':6,'track_boundary_lines':7,
        'context':'Stadium sidewalk, curb, brick entry inlay and an unmarked adjacent Avenue asphalt strip; frontage extent and dimensions schematic, no lane geometry asserted',
        'shared_master_manifest_edited':False,
        'previews':['audit/lambert_fieldhouse/exterior_round4.png','audit/lambert_fieldhouse/interior_round4.png']}
with open(OUT+r'/validation_round4.json','w') as f: json.dump(report,f,indent=2)
with open(OUT+r'/evidence_round4.json','w') as f:
    json.dump({'building_id':'massing_lambert_ward_l_fieldhouse_and_gymnasium_1656862','name':'Ward L. Lambert Fieldhouse and Gymnasium','asset_file':'modular/buildings/lambert_fieldhouse.blend','revision':4,'review_date':'2026-10-24',
      'changes':['Replaced the visually dark entrance patch with staggered warm red-brown paver units using a three-color brick palette.','Added a restrained unmarked asphalt strip adjacent to the Stadium Ave sidewalk and curb to communicate the named avenue.','Kept road lane layout and all paving dimensions/extent schematic; no unverified street markings or measurements were added.','Preserved the track geometry and rechecked its saved-mesh centerline perimeter.'],
      'source':{'provider':'Purdue University Engineering Computer Network, Ground Control Requirements','url':'https://engineering.purdue.edu/~bethel/pur_gcp.pdf','use':'Identifies Stadium Avenue, the sidewalk, and a brick inlay at the main entrance; supports contextual sidewalk/entry paving, while dimensions and roadway details remain unsurveyed here.'},
      'direct_mesh_measurement':{'track':'LAMB | 6-lane 200 m stadium track surface','method':'Average paired inner/outer boundary vertices at each station to recover lane-one centerline polygon; sum closed polygon edges in local meters.','perimeter_m':perimeter,'lane_count':6,'boundary_line_count':7},
      'uncertainties':['Road width, lane markings and precise sidewalk/curb/inlay dimensions are schematic.','Roof/facade geometry and interior event/seating layout retain documented schematic limitations.'],
      'validation':'audit/lambert_fieldhouse/validation_round4.json','previews':{'exterior':'audit/lambert_fieldhouse/exterior_round4.png','interior_cutaway':'audit/lambert_fieldhouse/interior_round4.png'},'master_manifest_shared_files_edited':False},f,indent=2)
print(json.dumps(report,indent=2))
