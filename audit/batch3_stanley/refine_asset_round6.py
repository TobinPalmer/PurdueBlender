"""Stanley Coulter Hall R6: source-led east glazing, entry cleanup, circulation."""
import bpy, hashlib, json, re
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend'
AUDIT=ROOT/'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_stanley_coulter_hall']
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
scene=bpy.context.scene
if list(root.location)!=[0.0,0.0,0.0] or any(abs(v-1.0)>1e-6 for v in root.scale):
    raise RuntimeError('R6 must preserve the identity asset root')

def world_bounds(o):
    pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]

def transform_mesh_world(obj, transform):
    if obj.data.users>1: obj.data=obj.data.copy()
    inv=obj.matrix_world.inverted()
    for v in obj.data.vertices:
        p=obj.matrix_world@v.co
        transform(p)
        v.co=inv@p
    obj.data.update()

def ensure_hidden_archive(name,purpose):
    col=bpy.data.collections.get(name)
    if col is None:
        col=bpy.data.collections.new(name)
        scene.collection.children.link(col)
    col.hide_render=True
    col.hide_viewport=True
    col['purpose']=purpose
    return col

def archive_object(obj,archive,note):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    archive.objects.link(obj)
    obj.hide_render=True
    obj.hide_viewport=True
    obj.hide_set(True)
    obj['R6_status']=note

# 1) Replace the regular upper east window boxes with source-supported continuous
# glazed groups. The current Purdue CLA photo shows a broad upper glass band with
# slender vertical mullions; the lower rows and all wall openings are unchanged.
facade_archive=ensure_hidden_archive(
    'SC_Archived_Facade_Windows_R6',
    'Superseded individual upper-east window modules retained for audit; R6 renders the photograph-supported grouped glazing band.'
)
row_re=re.compile(r'^SC_Win_East_Level3_ThirdFloor_(\d+)_(LimestoneTrim|BronzeFrame|GlassPane)$')
old_windows=[]
centers=[]
for idx in range(8):
    pane=bpy.data.objects.get(f'SC_Win_East_Level3_ThirdFloor_{idx}_GlassPane')
    if not pane: raise RuntimeError(f'Missing upper east pane index {idx}')
    b=world_bounds(pane)
    centers.append({'index':idx,'y':(b[0][1]+b[1][1])/2,'x':b[1][0]})
for obj in list(asset.all_objects):
    m=row_re.match(obj.name)
    if m:
        old_windows.append(obj.name)
        archive_object(obj,facade_archive,'Replaced by continuous photo-supported east upper glazing in R6; retained recoverably.')
if len(old_windows)!=24:
    raise RuntimeError(f'Expected 24 upper-east window modules to archive, found {len(old_windows)}')

centers.sort(key=lambda p:p['y'])
n=len(centers)
ys=[p['y'] for p in centers]; xs=[p['x']+0.018 for p in centers]
mean_y=sum(ys)/n; mean_x=sum(xs)/n
slope=sum((y-mean_y)*(x-mean_x) for y,x in zip(ys,xs))/sum((y-mean_y)**2 for y in ys)
intercept=mean_x-slope*mean_y
def facade_x(y): return intercept+slope*y

# Each side group corresponds to the observed 4-module window grouping around
# the south-facing portal. The gap around the entrance remains unobstructed.
groups=[(-22.05,-7.95),(0.05,14.95)]
zbot,ztop=10.04,11.96
glass=bpy.data.materials.get('Architectural_Glazing')
bronze=bpy.data.materials.get('Dark_Bronze_Framing')
limestone=bpy.data.materials.get('Bedford_Indiana_Limestone')
if not all((glass,bronze,limestone)):
    raise RuntimeError('Expected existing R5 glazing, bronze, and limestone materials')

# Opaque reflective glazing reads as sky/window reflections against the modeled
# solid wall; avoid transmission through the uncut brick wall mesh.
if glass.use_nodes:
    bs=next((node for node in glass.node_tree.nodes if node.type=='BSDF_PRINCIPLED'),None)
    if bs:
        bs.inputs['Base Color'].default_value=(0.025,0.055,0.075,1)
        bs.inputs['Metallic'].default_value=0.24
        bs.inputs['Roughness'].default_value=0.20
glass.diffuse_color=(0.04,0.10,0.14,1)

def mesh_prism(name,verts,faces,material):
    mesh=bpy.data.meshes.new(name+'_Mesh')
    mesh.from_pydata(verts,[],faces);mesh.materials.append(material);mesh.update()
    obj=bpy.data.objects.new(name,mesh);asset.objects.link(obj)
    obj['R6_evidence']='Grouped upper glazing follows the visible east/courtyard facade in Purdue CLA photograph; dimensions remain estimated.'
    return obj

def band_panel(name,y0,y1,z0,z1,depth,material):
    # front and rear vertices follow the slight east-wall angle measured from
    # the existing upper window pane centers.
    xf0,xf1=facade_x(y0),facade_x(y1)
    xr0,xr1=xf0-depth,xf1-depth
    verts=[(xf0,y0,z0),(xf1,y1,z0),(xf1,y1,z1),(xf0,y0,z1),
           (xr0,y0,z0),(xr1,y1,z0),(xr1,y1,z1),(xr0,y0,z1)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh_prism(name,verts,faces,material)

new_glazing=[]
for gi,(y0,y1) in enumerate(groups):
    new_glazing.append(band_panel(f'SC_R6_East_Glazing_Band_{gi}',y0,y1,zbot,ztop,0.035,glass))
    # Slim limestone head and sill tie the former window openings together.
    new_glazing.append(band_panel(f'SC_R6_East_Glazing_Head_{gi}',y0,y1,11.98,12.12,0.20,limestone))
    new_glazing.append(band_panel(f'SC_R6_East_Glazing_Sill_{gi}',y0,y1,9.88,10.02,0.20,limestone))
    # Thin bronze mullions remain aligned to the old opening centers and read
    # as divisions in one ribbon rather than a grid of thick picture frames.
    group_centers=[p['y'] for p in centers if y0+0.2<p['y']<y1-0.2]
    for mi,yc in enumerate(group_centers):
        yf0,yf1=yc-0.035,yc+0.035
        xf=facade_x(yc)+0.015
        verts=[(xf,yf0,zbot),(xf,yf1,zbot),(xf,yf1,ztop),(xf,yf0,ztop),
               (xf-0.07,yf0,zbot),(xf-0.07,yf1,zbot),(xf-0.07,yf1,ztop),(xf-0.07,yf0,ztop)]
        faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
        new_glazing.append(mesh_prism(f'SC_R6_East_Glazing_Mullion_{gi}_{mi}',verts,faces,bronze))

# 2) Remove the unsupported oversized wall lanterns. Keep a reversible copy in
# a hidden archive rather than silently deleting source geometry.
entry_archive=ensure_hidden_archive(
    'SC_Archived_Entry_Fixtures_R6',
    'R5 entry lantern blocks are hidden pending a current source confirming their design.'
)
archived_lanterns=[]
for name in ('SC_Lantern_Bracket_0','SC_Lantern_Glow_0','SC_Lantern_Bracket_1','SC_Lantern_Glow_1'):
    obj=bpy.data.objects.get(name)
    if obj and obj.name in asset.all_objects:
        archived_lanterns.append(name)
        archive_object(obj,entry_archive,'R5 wall fixture was conspicuous and unsupported by the inspected current facade photograph.')

# Slim the heavy entrance entablature and pull it back toward the photographed
# stone surround. Keep the photo-supported paired round shafts and recessed door.
ent=bpy.data.objects.get('SC_Portico_Entablature')
entry_before=world_bounds(ent) if ent else None
if ent:
    transform_mesh_world(ent,lambda p:setattr(p,'x',28.10+(p.x-28.10)*0.62))
    transform_mesh_world(ent,lambda p:setattr(p,'z',6.62-(6.62-p.z)*0.66))
    ent['R6_entry_note']='Reduced cap projection and visual height to make the recessed arch/transom and paired supports legible; exact dimensions remain photographic estimates.'
entry_after=world_bounds(ent) if ent else None

# 3) Keep roof construction explicitly unverified but add fine, restrained
# shingle-like surface breakup consistent with the undated archive photograph.
roofmat=bpy.data.materials.get('Historic_Slate_Roof_Procedural')
roof_nodes=0
roof=bpy.data.objects.get('SC_Historic_Slate_Roof')
if roofmat and roofmat.use_nodes:
    nodes=roofmat.node_tree.nodes; links=roofmat.node_tree.links
    principled=next((node for node in nodes if node.type=='BSDF_PRINCIPLED'),None)
    texcoord=next((node for node in nodes if node.type=='TEX_COORD'),None)
    if principled and texcoord:
        wave=nodes.new('ShaderNodeTexWave');wave.name='R6_Subtle_Slate_Courses';wave.label='R6 estimated shallow roof courses'
        wave.wave_type='BANDS';wave.bands_direction='X';wave.inputs['Scale'].default_value=74.0
        wave.inputs['Distortion'].default_value=0.35;wave.inputs['Detail'].default_value=1.0
        bump=nodes.new('ShaderNodeBump');bump.name='R6_Slate_Course_Bump';bump.inputs['Strength'].default_value=0.12;bump.inputs['Distance'].default_value=0.004
        links.new(texcoord.outputs['Generated'],wave.inputs['Vector'])
        links.new(wave.outputs['Color'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],principled.inputs['Normal'])
        roof_nodes=2
if roof: roof['R6_roof_note']='Shallow course breakup is a restrained visualization based on undated historic roof image; current roof material/profile/height remain unverified.'

# 4) Model a connected, explicitly schematic circulation spine linking the
# public entry, lobby stair and graduate hub. The source documents uses and
# a nearby elevator but do not provide current room-by-room as-built routing.
interior_col=bpy.data.collections.new('SC_R6_Interior_Circulation_Schematic')
asset.children.link(interior_col)
interior_col['status']='Diagrammatic connected route only; exact current interior partitions and door positions are not verified.'
mat_floor=bpy.data.materials.get('Polished_Terrazzo')
mat_wall=bpy.data.materials.get('Unverified_Interior_Shell') or bpy.data.materials.get('SC_Interior_Paint_Warm_Offwhite')
if not mat_floor or not mat_wall: raise RuntimeError('Missing existing interior materials')

def box(name,x0,x1,y0,y1,z0,z1,material):
    verts=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
           (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(material);mesh.update()
    obj=bpy.data.objects.new(name,mesh);interior_col.objects.link(obj)
    return obj

# Route extends 7.1m from the center of the east entry to the modeled lobby
# stair, stays north of the existing study-table groups, and remains open at
# its inner end to the graduate hub. Height is one normal floor storey.
box('SC_R6_Circulation_Spine_Floor',20.15,27.82,-3.72,-2.02,1.812,1.86,mat_floor)
box('SC_R6_Circulation_Wall_South',20.15,27.52,-3.91,-3.80,1.86,4.75,mat_wall)
box('SC_R6_Circulation_Wall_North',20.15,27.52,-1.94,-1.83,1.86,4.75,mat_wall)
# A short open landing connects the corridor to the staircase shell.
box('SC_R6_Stair_Landing_Floor',19.60,20.30,-3.80,-1.94,1.812,1.86,mat_floor)
for obj in interior_col.objects:
    obj['R6_status']='Schematic circulation evidence; not a verified current as-built plan.'

# Save the modified standalone library. Do not edit the campus master or its marker.
before={'active_object_count':len(asset.all_objects),'asset_file':str(ASSET)}
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
digest=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={
    'round':6,'building':'Stanley Coulter Hall','asset':str(ASSET),'sha256':digest,
    'changes':{
        'upper_east_glazing':'Replaced 8 regular upper-floor window modules with two grouped glazed bands and thin mullions matching the current Purdue CLA image composition; opening/footprint and lower rows unchanged.',
        'archived_upper_windows':old_windows,'archived_fixture_objects':archived_lanterns,
        'entry_entablature_bounds_before_m':entry_before,'entry_entablature_bounds_after_m':entry_after,
        'roof_course_nodes_added':roof_nodes,'interior_circulation_objects':[o.name for o in interior_col.objects],
        'identity_root_preserved':True
    },
    'sources':[{
        'provider':'Purdue College of Liberal Arts','url':'https://www.cla.purdue.edu/academic/english/images/stanleycoulterhall.jpg',
        'retrieved':'2026-10-25','photo_date':'not exposed','supports':'Upper grouped glazing, paired entrance supports, stone surround, recessed doors, and stair/rail composition; not exact dimensions.'
    },{
        'provider':'Purdue e-Archives','url':'https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1310/',
        'record':'PPBUC01117','date':'undated; digitized 2006-12-01','supports':'Historic low roof surface/color context only.'
    },{
        'provider':'Purdue Board of Trustees','url':'https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/University%20Hall%20Related%20Renovations.pdf',
        'pages':'11-13','date':'2022-09-28','supports':'Renovation area and historical plans; not current as-built interior routing.'
    }],
    'limits':['Upper glazing group dimensions are estimated from an undimensioned photo.','Roof courses are a restrained procedural visualization from an undated archive image and do not establish current construction or height.','The circulation spine is schematic and connected but not verified as-built; do not treat room partitions or exact door routing as surveyed.','Master placement marker and campus neighborhood alignment were not edited or checked in this asset-only revision.']
}
(AUDIT/'build_r6.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
