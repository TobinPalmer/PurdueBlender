import bpy, json, math, random, xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit' / 'engineering_precinct'
OSM = AUDIT / 'osm_snapshot.xml'
PLANTS = AUDIT / 'arboretum_plants_snapshot.json'
OUT = ROOT / 'modular' / 'site' / 'engineering_mall_groundwork_patch.blend'
FOLIAGE_LIB = ROOT / 'modular' / 'site' / 'foliage_library' / 'engineering_foliage_library.blend'
COLLECTION_NAME = 'Engineering_Mall_Groundwork_Patch'
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
M_PER_LON = 84810.60416539927
M_PER_LAT = 111040.0
FOCUS = (-105.0, 110.0, 90.0, 300.0)

# Work in campus coordinates, matching modular/AGENTS.md.
def xy(lon, lat):
    return ((lon + 86.9137) * M_PER_LON, (lat - 40.4274) * M_PER_LAT)

def mat(name, color, roughness=0.82, scale=1.0, detail=2.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    tex = m.node_tree.nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = scale
    tex.inputs['Detail'].default_value = detail
    tex.inputs['Roughness'].default_value = 0.72
    ramp = m.node_tree.nodes.new('ShaderNodeValToRGB')
    low = tuple(max(0.0, c*0.88) for c in color)+(1,)
    high = tuple(min(1.0, c*1.12+0.015) for c in color)+(1,)
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = low
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = high
    m.node_tree.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
    m.node_tree.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    return m

def link_obj(obj, col):
    col.objects.link(obj)

def world_xy_uv(mesh, repeats_per_meter):
    """Use the project XY coordinates for tiled asphalt/grass PBRs on meshes without source UVs."""
    layer=mesh.uv_layers.new(name='CampusXY_PBR_UV')
    for loop in mesh.loops:
        co=mesh.vertices[loop.vertex_index].co
        layer.data[loop.index].uv=(co.x*repeats_per_meter,co.y*repeats_per_meter)

def clean_previous():
    old = bpy.data.collections.get(COLLECTION_NAME)
    if old:
        for parent in list(old.users_scene):
            parent.collection.children.unlink(old)
        for parent in bpy.data.collections:
            if old in parent.children.values(): parent.children.unlink(old)
        bpy.data.collections.remove(old)

# Start a fresh scene so the exported library contains only this module.
bpy.ops.wm.read_factory_settings(use_empty=True)
library_collections=['PH_Tree_Small_02_LOD2'] + [f'PH_Shrub_02_{v}_LOD2' for v in 'ABCD'] + [f'PH_Shrub_04_{v}_LOD2' for v in 'ABCD'] + [f'PH_Fir_Sapling_{v}_LOD2' for v in 'ABC'] + ['PH_Fern_02_Variants','PH_Grass_Medium_01_Selective_LOD2']
reuse_material_names=['Campus_Walkway_Concrete','Manicured_Campus_Lawn','Purdue_Landscape_Green','Plaza_Architectural_Concrete','Plaza_Purdue_Red_Brick_Pavers','Street_Asphalt_Dark','Street_Curb_Concrete','grass_ground','asphalt_01']
with bpy.data.libraries.load(str(FOLIAGE_LIB),link=True) as (src,dst):
    missing=[n for n in library_collections if n not in src.collections]
    if missing: raise RuntimeError(f'Foliage library collections missing: {missing}')
    dst.collections=library_collections
    missing=[n for n in reuse_material_names if n not in src.materials]
    if missing: raise RuntimeError(f'Reused site materials missing: {missing}')
    dst.materials=reuse_material_names
asset_collections={c.name:c for c in dst.collections}
site_mats={m.name:m for m in dst.materials}
col = bpy.data.collections.new(COLLECTION_NAME)
bpy.context.scene.collection.children.link(col)

def surface_material(name, base, noise_scale, variation, bump_distance, bump_strength):
    """Project-local, meter-scaled procedural surface; avoids mutating linked source materials."""
    m=bpy.data.materials.new(name); m.diffuse_color=(*base,1); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.88
    tc=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=noise_scale; noise.inputs['Detail'].default_value=3.0
    noise.inputs['Roughness'].default_value=.72
    l.new(tc.outputs['Object'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    lo=tuple(max(0,c*(1-variation)) for c in base)+(1,)
    hi=tuple(min(1,c*(1+variation)) for c in base)+(1,)
    ramp.color_ramp.elements[0].position=.2; ramp.color_ramp.elements[0].color=lo
    ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=hi
    l.new(noise.outputs['Fac'],ramp.inputs['Fac']); l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump'); bump.inputs['Distance'].default_value=bump_distance
    bump.inputs['Strength'].default_value=bump_strength
    l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m

# The surfaces in this module use object-space coordinates in campus meters. A low-frequency
# field gives broad natural variation; a separate finer field adds material grain without making
# the site read as speckled noise. Grass colors vary at roughly 0.5–1 m, with fine turf relief.
def layered_surface(name, base, macro_scale, macro_variation, fine_scale, bump_distance, bump_strength, roughness=.88):
    m=bpy.data.materials.new(name); m.diffuse_color=(*base,1); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=roughness
    tc=n.new('ShaderNodeTexCoord'); macro=n.new('ShaderNodeTexNoise')
    macro.inputs['Scale'].default_value=macro_scale; macro.inputs['Detail'].default_value=2.0
    macro.inputs['Roughness'].default_value=.68; l.new(tc.outputs['Object'],macro.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    lo=tuple(max(0,c*(1-macro_variation)) for c in base)+(1,)
    hi=tuple(min(1,c*(1+macro_variation)) for c in base)+(1,)
    ramp.color_ramp.elements[0].position=.22; ramp.color_ramp.elements[0].color=lo
    ramp.color_ramp.elements[1].position=.78; ramp.color_ramp.elements[1].color=hi
    l.new(macro.outputs['Fac'],ramp.inputs['Fac']); l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    fine=n.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value=fine_scale
    fine.inputs['Detail'].default_value=2.0; fine.inputs['Roughness'].default_value=.7
    l.new(tc.outputs['Object'],fine.inputs['Vector'])
    bump=n.new('ShaderNodeBump'); bump.inputs['Distance'].default_value=bump_distance
    bump.inputs['Strength'].default_value=bump_strength
    l.new(fine.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    m['coordinate_units']='Object-space campus meters'; m['macro_variation_scale_per_m']=macro_scale
    m['fine_detail_scale_per_m']=fine_scale
    return m

grass=layered_surface('Engineering_Mall_Mown_Grass_Textured',(.105,.225,.052),1.25,.22,32,.012,.35)
grass['source']='Procedural close-mown turf with broad color variation and fine surface relief'
grass['texture_scale_note']='Object-space coordinates are campus meters; macro variation spans about 0.8 m and fine relief about 3 cm'
# Neutral concrete aggregate reads as pale warm gray under both daylight and shade.
walkway=layered_surface('Engineering_Mall_Walkway_Concrete_Textured',(.47,.455,.415),2.0,.11,28,.004,.26)
walkway['source']='Procedural meter-scaled campus concrete: restrained slab-scale variation and fine aggregate'
asphalt=layered_surface('Engineering_Mall_Asphalt_Textured',(.105,.112,.108),1.0,.30,42,.003,.32,roughness=.94)
asphalt['source']='Procedural neutral charcoal asphalt with meter-scaled aggregate; replaces broken external image material on this patch'
patch_pavers=bpy.data.materials.new('Engineering_Mall_Plaza_Pavers_Textured'); patch_pavers.use_nodes=True
bs=patch_pavers.node_tree.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.84
n=patch_pavers.node_tree.nodes; l=patch_pavers.node_tree.links; tc=n.new('ShaderNodeTexCoord')
brick=n.new('ShaderNodeTexBrick'); brick.inputs['Scale'].default_value=1.0
brick.inputs['Mortar Size'].default_value=.012; brick.inputs['Mortar Smooth'].default_value=.004
brick.inputs['Brick Width'].default_value=.58; brick.inputs['Row Height'].default_value=.38
brick.inputs['Color1'].default_value=(.48,.46,.41,1); brick.inputs['Color2'].default_value=(.57,.55,.50,1)
brick.inputs['Mortar'].default_value=(.32,.31,.28,1); l.new(tc.outputs['Object'],brick.inputs['Vector'])
l.new(brick.outputs['Color'],bs.inputs['Base Color'])
paver_bump=n.new('ShaderNodeBump'); paver_bump.inputs['Distance'].default_value=.004; paver_bump.inputs['Strength'].default_value=.24
l.new(brick.outputs['Fac'],paver_bump.inputs['Height']); l.new(paver_bump.outputs['Normal'],bs.inputs['Normal'])
patch_pavers['source']='Meter-scaled warm-gray procedural concrete pavers with consistent narrow joints'
materials={'concrete':walkway,'paved':walkway,'pavers':patch_pavers,
           'asphalt':asphalt,'grass':grass}

# OSM landuse outlines omit the continuous subgrade beneath the paths, leaving the preview sky
# visible as blue-gray bands between mapped lawn islands. Add a local turf underlay beneath all
# OSM path and plaza surfaces. It is deliberately below the mapped turf polygons and hardscape.
gx0,gx1,gy0,gy1=FOCUS
margin=25.0
gx0-=margin; gx1+=margin; gy0-=margin; gy1+=margin
ground_mesh=bpy.data.meshes.new('Engineering_Mall_Continuous_Subgrade_Mesh')
ground_mesh.from_pydata([(gx0,gy0,.002),(gx1,gy0,.002),(gx1,gy1,.002),(gx0,gy1,.002)],[],[(0,1,2,3)])
ground_mesh.materials.append(grass); ground_mesh.update()
ground_obj=bpy.data.objects.new('Engineering_Mall_Continuous_Turf_Subgrade',ground_mesh); link_obj(ground_obj,col)
ground_obj['surface']='continuous campus turf underlay beneath OSM-mapped paths and lawn parcels'
ground_obj['source']='Project-local fill for unmapped subgrade gaps; not a surveyed landuse boundary'
ground_obj['geometry_status']='flat local underlay clipped to the documented patch focus extent and placed below mapped surfaces'

# Parse official OSM geometry snapshot, clipped by a documented focus extent.
root = ET.parse(OSM).getroot()
node_geo = {n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in root.findall('node')}
node_xy = {k:xy(*v) for k,v in node_geo.items()}
def inside(p): return FOCUS[0] <= p[0] <= FOCUS[1] and FOCUS[2] <= p[1] <= FOCUS[3]

# The mapped radial walk centerlines terminate exactly on the fountain plaza outline. Their
# square end caps leave small triangular turf slivers where the surveyed walk widths meet the
# separately mapped paving polygon. Extend only those terminal centerlines into the existing
# plaza so the same walk material overlaps the pavers. The outline and the walk's surveyed
# alignment and width remain unchanged.
plaza_way = next((w for w in root.findall('way') if w.attrib['id']=='283274215'), None)
if plaza_way is None: raise RuntimeError('OSM fountain plaza outer way 283274215 is missing')
plaza_ring = [node_xy[n.attrib['ref']] for n in plaza_way.findall('nd') if n.attrib['ref'] in node_xy]
if len(plaza_ring)>1 and math.dist(plaza_ring[0],plaza_ring[-1])<0.02: plaza_ring=plaza_ring[:-1]

def plaza_contains(p):
    x,y=p; result=False
    for a,b in zip(plaza_ring,plaza_ring[1:]+plaza_ring[:1]):
        if (a[1]>y)!=(b[1]>y):
            xi=(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]
            if x<xi: result=not result
    return result

def plaza_edge_distance(p):
    best=float('inf')
    for a,b in zip(plaza_ring,plaza_ring[1:]+plaza_ring[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1]; denom=dx*dx+dy*dy
        t=0.0 if denom<1e-12 else max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/denom))
        best=min(best,math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy)))
    return best

def extend_plaza_terminal(points,width):
    """Let a mapped walk overlap the plaza only where its endpoint lies on the OSM rim."""
    pts=list(points)
    if len(pts)<2: return pts
    extension=min(2.0,max(1.25,width*0.55))
    for endpoint_index,neighbor_index in ((0,1),(-1,-2)):
        endpoint=pts[endpoint_index]; neighbor=pts[neighbor_index]
        if plaza_edge_distance(endpoint)>0.06: continue
        dx,dy=endpoint[0]-neighbor[0],endpoint[1]-neighbor[1]
        length=math.hypot(dx,dy)
        if length<0.08: continue
        ux,uy=dx/length,dy/length
        # Choose the collinear direction that enters the plaza; this works for either end of a
        # way without assuming OSM point order. Short samples avoid crossing to another edge.
        candidates=[(ux,uy),(-ux,-uy)]
        inward=next(((vx,vy) for vx,vy in candidates if plaza_contains((endpoint[0]+vx*.15,endpoint[1]+vy*.15))),None)
        if inward is None: continue
        moved=(endpoint[0]+inward[0]*extension,endpoint[1]+inward[1]*extension)
        if endpoint_index==0: pts[0]=moved
        else: pts[-1]=moved
    return pts

def clip_segment(a, b):
    """Liang-Barsky clip for one centerline segment against the documented focus."""
    x0,y0=a; x1,y1=b; dx=x1-x0; dy=y1-y0
    p=(-dx,dx,-dy,dy); q=(x0-FOCUS[0],FOCUS[1]-x0,y0-FOCUS[2],FOCUS[3]-y0)
    u0,u1=0.0,1.0
    for pi,qi in zip(p,q):
        if abs(pi)<1e-12:
            if qi<0: return None
            continue
        t=qi/pi
        if pi<0: u0=max(u0,t)
        else: u1=min(u1,t)
        if u0>u1: return None
    return ((x0+u0*dx,y0+u0*dy),(x0+u1*dx,y0+u1*dy))

def clipped_runs(points):
    runs=[]; current=[]
    for a,b in zip(points,points[1:]):
        clipped=clip_segment(a,b)
        if clipped is None:
            if len(current)>1: runs.append(current)
            current=[]; continue
        ca,cb=clipped
        if not current or math.dist(current[-1],ca)>0.02:
            if len(current)>1: runs.append(current)
            current=[ca]
        current.append(cb)
    if len(current)>1: runs.append(current)
    return runs

def clip_polygon(poly):
    """Sutherland-Hodgman clip for simple grass parcels."""
    out=list(poly)
    bounds=[(0,FOCUS[0],True),(0,FOCUS[1],False),(1,FOCUS[2],True),(1,FOCUS[3],False)]
    for axis,bound,greater in bounds:
        src=out; out=[]
        if not src: break
        def valid(p): return p[axis]>=bound if greater else p[axis]<=bound
        prev=src[-1]; prev_ok=valid(prev)
        for cur in src:
            cur_ok=valid(cur)
            if cur_ok != prev_ok:
                den=cur[axis]-prev[axis]
                t=0.0 if abs(den)<1e-12 else (bound-prev[axis])/den
                out.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
            if cur_ok: out.append(cur)
            prev,prev_ok=cur,cur_ok
    return out

def create_ribbon(way_id, pts, width, material, label, surface):
    verts, faces = [], []
    for a,b in zip(pts, pts[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        d=math.hypot(dx,dy)
        if d < 0.08: continue
        nx,ny=-dy/d*width/2,dx/d*width/2
        i=len(verts)
        verts.extend([(a[0]+nx,a[1]+ny,.045),(a[0]-nx,a[1]-ny,.045),(b[0]-nx,b[1]-ny,.045),(b[0]+nx,b[1]+ny,.045)])
        faces.append((i,i+1,i+2,i+3))
    if not faces: return
    me=bpy.data.meshes.new(f'OSM_{way_id}_surface_mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(f'OSM_Way_{way_id}_{label}',me); link_obj(ob,col)
    ob['source']='OpenStreetMap'; ob['source_feature_id']=str(way_id); ob['surface']=surface; ob['width_m']=width; ob['width_status']='estimated from path type unless explicitly tagged'; ob['geometry_status']='OSM line geometry, locally projected to project XY'

# Create paths in explicit OSM-tagged surface families; avoid inventing lane markings.
path_count=0; grass_count=0
for w in root.findall('way'):
    tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
    refs=[nd.attrib['ref'] for nd in w.findall('nd')]
    pts=[node_xy[r] for r in refs if r in node_xy]
    if len(pts)<2 or not any(inside(p) for p in pts): continue
    highway=tags.get('highway')
    if highway in {'footway','pedestrian','path','cycleway','steps','service','primary'}:
        # Retain sequences whose segment intersects the engineering mall focus.
        runs=clipped_runs(pts)
        if not runs: continue
        surface=tags.get('surface','paved')
        if surface=='asphalt' or highway=='primary': key='asphalt'
        elif surface=='paving_stones': key='pavers'
        elif surface=='concrete': key='concrete'
        else: key='paved'
        width_tag=tags.get('width')
        try: width=float(width_tag.split()[0]) if width_tag else None
        except: width=None
        if width is None:
            width={'primary':7.0,'service':3.4,'cycleway':3.2,'pedestrian':4.5,'steps':2.0,'footway':2.6,'path':2.0}.get(highway,2.5)
            if tags.get('name') in {'Stadium Mall','Stadium Mall Drive'}: width=4.2
        label=tags.get('name',highway).replace(' ','_')
        # Way 283274215 is a closed outer paving polygon, not a centerline path. Treating its
        # 22 perimeter edges as independent square-ended ribbons created triangular gaps at each
        # vertex. Its concave-safe filled polygon below already represents the complete plaza.
        is_plaza_outline=(w.attrib['id']=='283274215' and len(pts)>=4 and pts[0]==pts[-1])
        if not is_plaza_outline:
            for run_i,run in enumerate(runs):
                run=extend_plaza_terminal(run,width)
                create_ribbon(w.attrib['id'] if len(runs)==1 else f"{w.attrib['id']}_{run_i}",run,width,materials[key],label,surface)
        # This surveyed OSM ring is the Engineering Fountain's outer paving boundary; fill its area.
        if w.attrib['id']=='283274215' and len(pts)>=4 and pts[0]==pts[-1]:
            from mathutils.geometry import tessellate_polygon
            from mathutils import Vector
            ring=clip_polygon(pts[:-1])
            tris=tessellate_polygon([[Vector((p[0],p[1],.028)) for p in ring]])
            verts=[(p[0],p[1],.028) for p in ring]
            faces=[tuple(int(j) for j in tri) for tri in tris]
            me=bpy.data.meshes.new('OSM_283274215_Engineering_Fountain_Plaza_mesh'); me.from_pydata(verts,[],faces); me.materials.append(materials['pavers']); me.update()
            ob=bpy.data.objects.new('Engineering_Fountain_Plaza_Paving_OSM_283274215',me); link_obj(ob,col)
            ob['source']='OpenStreetMap way 283274215'; ob['surface']='paving_stones'; ob['geometry_status']='closed outer plaza polygon filled with concave-safe triangulation'
            ob['area_note']='OSM-tagged fountain plaza paving; polygon interpretation confirmed by project coordinate auditor'
        # Preserve the OSM feature count: the plaza is represented by its filled surface mesh.
        path_count+=1
    if tags.get('landuse')=='grass' or tags.get('natural')=='grass':
        if len(pts)>=4 and pts[0]==pts[-1]:
            ring=clip_polygon(pts[:-1])
            if len(ring)<3: continue
            from mathutils.geometry import tessellate_polygon
            from mathutils import Vector
            tris=tessellate_polygon([[Vector((p[0],p[1],.012)) for p in ring]])
            verts=[(p[0],p[1],.012) for p in ring]
            faces=[tuple(int(j) for j in tri) for tri in tris]
            me=bpy.data.meshes.new(f'OSM_{w.attrib["id"]}_turf_mesh'); me.from_pydata(verts,[],faces); me.materials.append(materials['grass']); me.update()
            ob=bpy.data.objects.new(f'OSM_Grass_{w.attrib["id"]}',me); link_obj(ob,col)
            ob['source']='OpenStreetMap'; ob['source_feature_id']=w.attrib['id']; ob['surface']='campus turf'; grass_count+=1

# Exact plant points from Purdue Arboretum open data; actual species and XY, estimated crown shape.
data=json.loads(PLANTS.read_text(encoding='utf-8'))
features=[]
for f in data['features']:
    a=f['attributes']; g=f.get('geometry') or {}
    if not g.get('x') or not g.get('y'): continue
    px=xy(g['x'],g['y'])
    if not inside(px): continue
    habit=(a.get('habit') or '').lower()
    if not any(k in habit for k in ('tree','shrub')): continue
    features.append((a,px))
# A temporary camera projects inventory trees into the fixed comparison frame. This lets us
# vary only crowns that screen the mall center, while leaving the foreground drive open.
from bpy_extras.object_utils import world_to_camera_view
scene=bpy.context.scene
view_cam_data=bpy.data.cameras.new('Temporary_Reference_Camera')
view_cam=bpy.data.objects.new('Temporary_Reference_Camera',view_cam_data); scene.collection.objects.link(view_cam)
view_cam.location=(55.0,185.0,13.0)
view_target=Vector((-11.9,110.7,-3.8)); view_cam.rotation_euler=(view_target-view_cam.location).to_track_quat('-Z','Y').to_euler()
view_cam_data.lens=24; view_cam_data.clip_end=1200; scene.camera=view_cam
scene.render.resolution_x=1280; scene.render.resolution_y=960; bpy.context.view_layer.update()
# Low polygon silhouettes share a mesh; individual objects encode inventoried canopy spread/height.
# Unit interpretation: DBH/spread are represented conservatively in meters after source field conversion;
# heights are data-driven when present and otherwise inferred from canopy spread/species.
tree_asset=asset_collections['PH_Tree_Small_02_LOD2']
shrub_assets=[asset_collections[f'PH_Shrub_02_{v}_LOD2'] for v in 'ABCD']
fir_assets=[asset_collections[f'PH_Fir_Sapling_{v}_LOD2'] for v in 'ABC']
tree_count=0
for a,(x,y) in features:
    common=(a.get('commonname') or '').strip()
    habit=(a.get('habit') or '').lower()
    inventory_spread=a.get('spread') or 0
    dbh=a.get('diameter') or 0
    height=a.get('height') or 0
    # Database canopy spread appears in feet; crown radius scaled conservatively to avoid false bulk.
    is_shrub='shrub' in habit and 'tree' not in habit
    if inventory_spread:
        canopy_d=max(0.9,min(3.0,float(inventory_spread)*0.3048)) if is_shrub else max(2.0,min(14.0,float(inventory_spread)*0.3048))
        canopy_status='inventory spread converted from feet; visual crown scale applied'
    else:
        inferred_spread_m=1.5 if is_shrub else max(1.8,min(8.0,1.4+float(dbh)*0.18))
        canopy_d=inferred_spread_m
        canopy_status='estimated from habit and DBH; not measured'
    # Height values are sparse and align with feet-sized inventory fields; use a conservative species/habit estimate if absent.
    if height:
        h=max(2.5,min(18.0,float(height)*0.3048))
        height_status='inventory value converted from feet; field unit inferred from range'
    else:
        h=max(0.9,min(2.3,canopy_d*0.82)) if is_shrub else max(3.2,min(13.0,4.0+float(dbh)*0.18))
        height_status='estimated by habit and DBH; not measured'
    if any(k in common.lower() for k in ('arborvitae','juniper','pine','spruce','fir','hemlock','yew')): kind='conifer'
    elif any(k in common.lower() for k in ('crabapple','hawthorn','redbud','pear')): kind='ornamental'
    else: kind='deciduous'
    asset_col=shrub_assets[int(a['OBJECTID'])%len(shrub_assets)] if is_shrub else (fir_assets[int(a['OBJECTID'])%len(fir_assets)] if kind=='conifer' else tree_asset)
    plant_name=f'Plant_{a.get("OBJECTID")}_{common.replace(" ","_")}'
    ob=bpy.data.objects.new(plant_name,None); link_obj(ob,col)
    if asset_col:
        ob.instance_type='COLLECTION'; ob.instance_collection=asset_col
        ob['visual_asset_source']='Poly Haven CC0 linked collection instance'
        ob['visual_asset_collection']=asset_col.name
        ob['visual_asset_lod']=asset_col.get('lod','LOD2')
    else:
        raise RuntimeError(f'No reusable foliage asset selected for inventory plant {a.get("OBJECTID")} ({common})')
    ob.location=(x,y,.02)
    variability=int(a['OBJECTID'])
    fx=0.82+((variability*17)%37)/100.0
    fy=0.82+((variability*29)%37)/100.0
    view_distance=math.hypot(x-55.0,y-185.0)
    reference_xy=world_to_camera_view(scene,view_cam,Vector((x,y,0.0)))
    reference_crown=world_to_camera_view(scene,view_cam,Vector((x,y,h*0.80)))
    # Keep mapped mature midground canopy broad while leaving the near curb and walk legible.
    is_mature_tree=not is_shrub and float(dbh or 0)>=18 and float(inventory_spread or 0)>=45
    if is_shrub:
        visual_scale=0.44
    elif is_mature_tree:
        visual_scale=0.92
        height_status += '; mature-tree dimensions follow inventoried spread and DBH'
    else:
        visual_scale=0.58 if view_distance<30 else (0.90 if view_distance<75 else 0.82)
    # A few surveyed small ornamental trees directly in the reference-frame fountain sightline
    # receive restrained view-only adjustments. They are not a blanket canopy scaling rule.
    if int(a['OBJECTID']) in {1679, 6995, 2295, 7728}:
        visual_scale *= 0.72
        h *= 1.12
        height_status += '; selected center sightline crown narrowed and slightly raised to separate nearby canopy while screening sculpture; image-fit estimate'
    if is_mature_tree and 0.18<=reference_crown.x<=0.38 and 0.27<=reference_crown.y<=0.45 and view_distance<48:
        visual_scale*=0.50
        height_status += '; near left oak crown reduced to preserve foreground drive and tower sightline in ECN framing'
    if int(a['OBJECTID']) == 7473:
        # Retain survey point and source dimensions; undo an earlier over-reduction in the comparison view.
        visual_scale *= 0.98
        height_status += '; Shumard Oak view crown restored to 0.40 XY scale after earlier over-reduction; inventory XY, DBH 25 in and spread 62 ft retained'
    source_bounds=json.loads(asset_col['asset_bounds_xyz_m'])
    target_x=canopy_d*(0.88 if is_shrub else visual_scale)*fx
    target_y=canopy_d*(0.88 if is_shrub else visual_scale)*fy
    ob.scale=(target_x/max(source_bounds[0],.001),target_y/max(source_bounds[1],.001),h/max(source_bounds[2],.001))
    ob.rotation_euler[2]=((int(a['OBJECTID'])*137)%360)*math.pi/180
    ob['source']='Purdue Arboretum Open Data'; ob['source_objectid']=int(a['OBJECTID']); ob['common_name']=common; ob['scientific_name']=f"{a.get('genus') or ''} {a.get('species') or ''}".strip(); ob['inventory_habit']=a.get('habit') or ''; ob['inventory_dbh_in']=dbh or None; ob['inventory_spread_ft']=inventory_spread or None; ob['inventory_height_ft']=height or None; ob['height_m']=round(h,2); ob['height_status']=height_status; ob['canopy_diameter_m']=round(canopy_d,2); ob['canopy_status']=canopy_status; ob['visual_crown_scale_xy']=visual_scale; ob['preview_view_distance_m']=round(view_distance,1); ob['reference_frame_x']=round(reference_xy.x,3); ob['reference_frame_y']=round(reference_xy.y,3); ob['reference_crown_x']=round(reference_crown.x,3); ob['reference_crown_y']=round(reference_crown.y,3); ob['placement']='georeferenced inventory point'; ob['crown_adjustment_reason']=('OBJECTID 7473: previous comparison crown was over-reduced; restored to 0.40 view scale while preserving inventoried point, Shumard Oak species, DBH 25 in, and 62 ft spread' if int(a['OBJECTID'])==7473 else ('Selected 2023-frame sightline crown narrowed to avoid a merged foreground blob; mapped inventory point and source dimensions retained' if int(a['OBJECTID']) in {1679,6995,2295,7728} else 'Inventory XY, species and source dimensions retained; silhouette scale is an explicitly estimated modeling choice')); tree_count+=1

# Camera-calibrated photo inference for the broad forecourt drive and left diagonal walk.
# Keep these tagged separately; they supplement, and do not replace, OSM path topology.
ECN_REFERENCE='https://engineering.purdue.edu/ECN/WebCam/cam05/2023_06_19_14_40.jpg'
def image_ground_point(u,v,z=0.06):
    sensor_x=36.0
    sensor_y=sensor_x*scene.render.resolution_y/scene.render.resolution_x
    local=Vector(((2.0*u-1.0)*sensor_x/(2.0*view_cam_data.lens),
                  (2.0*v-1.0)*sensor_y/(2.0*view_cam_data.lens),-1.0))
    ray=view_cam.rotation_euler.to_quaternion() @ local
    if ray.z >= -1e-5: raise ValueError(f'image ray misses ground at {(u,v)}')
    t=(z-view_cam.location.z)/ray.z
    return view_cam.location + ray*t

# The mapped crowns leave gaps across the fountain silhouette in the fixed archive frame.
# Add three separately identified, image-inferred trees on projected ground rays. Their species and
# dimensions are estimates, not inventory; staggered locations and crown variants avoid a single wall.
inferred_canopies=[
    (0.46,0.35,'Northern Red Oak','Quercus rubra',4.8,7.5),
    (0.55,0.325,'Black Gum','Nyssa sylvatica',5.3,7.8),
    (0.615,0.37,'Northern Red Oak','Quercus rubra',5.7,8.2),
    (0.72,0.405,'Northern Red Oak','Quercus rubra',4.5,7.5),
    (0.78,0.36,'Black Gum','Nyssa sylvatica',5.0,7.6),
]
for i,(u,v,common_name,scientific_name,spread_m,height_m) in enumerate(inferred_canopies,1):
    base=image_ground_point(u,v,0.04)
    ob=bpy.data.objects.new(f'ECN_Inferred_Tree_{i}_{common_name.replace(" ","_")}_est',None); link_obj(ob,col)
    ob.instance_type='COLLECTION'; ob.instance_collection=tree_asset
    bounds=json.loads(tree_asset['asset_bounds_xyz_m'])
    ob.location=(base.x,base.y,0.04)
    ob.scale=(spread_m*.80/max(bounds[0],.001),spread_m*.76/max(bounds[1],.001),height_m/max(bounds[2],.001))
    ob.rotation_euler.z=(i*51)*math.pi/180
    ob['source']='Image-derived planting estimate; Purdue ECN Cam05 2023-06-19 frame'
    ob['source_url']='https://engineering.purdue.edu/ECN/WebCam/cam05/2023_06_19_14_40.jpg'
    ob['source_objectid']=None; ob['common_name']=common_name+' (regional species estimate)'
    ob['scientific_name']=scientific_name+' (species estimate; not individually identified in image)'
    ob['inventory_habit']='tree (image-inferred)'; ob['inventory_dbh_in']=None
    ob['inventory_spread_ft']=None; ob['inventory_height_ft']=None
    ob['height_m']=height_m; ob['height_status']='Image-fit height estimate; no individual field measurement'
    ob['canopy_diameter_m']=spread_m; ob['canopy_status']='Image-fit crown spread estimate; no inventory record'
    ob['placement']='ground-plane ray from normalized ECN image frame; inferred planting point'
    ob['reference_frame_x']=round(u,3); ob['reference_frame_y']=round(v,3)
    ob['uncertainty']='Species and planting coordinates cannot be identified from the photograph alone; regional species estimates follow the Arboretum StoryMap, dimensions are visual-fit assumptions.'
    ob['crown_adjustment_reason']='Discrete staggered inferred crown in fountain sightline; mapped inventory points and provenance remain separate.'
    ob['visual_asset_source']='Poly Haven tree_small_02 CC0 LOD1 composite; linked reusable collection instance'
    ob['visual_asset_collection']=tree_asset.name
    ob['visual_asset_lod']='LOD2 decimated composite'
    ob['crown_geometry_status']='Source asset silhouette scaled to image-fit crown dimensions; individual species form is not verified.'
def image_strip(name,pairs,material,z,note):
    verts=[]; faces=[]
    for i,(a,b) in enumerate(pairs):
        verts.extend([tuple(image_ground_point(*a,z)),tuple(image_ground_point(*b,z))])
        if i:
            j=2*i
            faces.append((j-2,j-1,j+1,j))
    me=bpy.data.meshes.new(name+'_mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); link_obj(ob,col)
    ob['source']='Image-derived from Purdue ECN Cam05 archive; not an OSM survey feature'
    ob['source_url']=ECN_REFERENCE
    ob['projection']='Normalized image rays intersect z=0 with an inferred Mall-facing MSEE third-floor viewpoint XY=(55,185)m, Z=13m, 222-degree azimuth, 9.5-degree downward pitch, and 24mm lens; all pose values are estimates.'
    ob['geometry_status']='Approximate image-derived footprint; authoritative OSM way geometry remains separate.'
    ob['uncertainty']='Exact camera window, lens calibration and ground elevation are unverified.'
    ob['feature_note']=note
    return ob

drive_pairs=[]
for i in range(33):
    u=i/32
    upper=0.012+0.032*math.sin(math.pi*u)
    drive_pairs.append(((u,0.005),(u,upper)))
image_strip('ECN_Inferred_Curved_Forecourt_Drive',drive_pairs,materials['concrete'],0.065,
              'Narrow pale curved drive traced along the bottom 0–4.4 percent of the dated webcam frame.')

walk_pairs=[]
for i in range(21):
    t=i/20
    u=0.01+0.29*t; v=0.12+0.20*t+0.018*math.sin(math.pi*t)
    du,dv=0.20,-0.29; norm=math.hypot(du,dv); du/=norm; dv/=norm; half=0.021
    walk_pairs.append(((u-du*half,v-dv*half),(u+du*half,v+dv*half)))
image_strip('ECN_Inferred_Left_Diagonal_Walk',walk_pairs,materials['paved'],0.075,
            'Diagonal approach traced from the lower-left edge toward x=0.30, y=0.65 in the reference image; image-space width is estimated.')

scene.camera=None; bpy.data.objects.remove(view_cam,do_unlink=True); bpy.data.cameras.remove(view_cam_data)

# Point ownership, sources, and coarse accuracy are embedded for downstream reviewers.
col['coordinate_system']='Project local campus XY meters; X east, Y north, Z up; origin 40.4274,-86.9137'
col['source_osm']='https://www.openstreetmap.org/; way geometries from audit snapshot dated 2026-10-23'
col['source_plants']='https://www.arboretum.purdue.edu/open-data/; Purdue Arboretum feature inventory snapshot, retrieved 2026-10-23'
col['footprint']='Engineering Mall / Engineering Fountain immediate pathways and planting, approximate bbox X[-105,110] Y[90,300]'
col['fountain_anchor_osm_way']=283274213
col['fountain_anchor_xy_m']=(-7.8042,137.9294)
col['fountain_plaza_outer_way']=283274215
col['geometry_caveat']='OSM centerlines and plant inventory positions are mapped data, not a new ground survey. Path widths, heights, crowns, and species silhouette geometry are estimated.'

# Save a clean linked asset.
bpy.context.scene['foliage_library']='//foliage_library/engineering_foliage_library.blend'
for library in bpy.data.libraries:
    if Path(bpy.path.abspath(library.filepath)).resolve()==FOLIAGE_LIB.resolve():
        library.filepath='//foliage_library/engineering_foliage_library.blend'
col['foliage_asset_library']='//foliage_library/engineering_foliage_library.blend'
col['foliage_asset_source']='Poly Haven CC0; campus hardscape materials/props reused from campus_site.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print('SAVED',OUT)
print('PATHS',path_count,'GRASS',grass_count,'PLANTS',tree_count,'OBJECTS',len(col.objects))
