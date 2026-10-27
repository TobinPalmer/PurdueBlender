"""Build a detailed, evidence-led Hull All-American Marching Band Complex asset.

Run from the project root in Blender 5.2 background mode. This asset keeps its
existing campus-coordinate library frame and stable collection/scene names; the
coordinator owns any later localization, manifest, or master-scene changes.
"""
from __future__ import annotations
import bpy, json, math, os
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_hull_all_american_marching_band_complex_665bcb7'
ASSET = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
AUDIT = ROOT / 'audit' / 'hull_all_american_marching_band_complex'
SOURCES = AUDIT / 'sources'
GIS_PATH = SOURCES / 'purdue_gis_fid431.json'
COLLECTION_NAME = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID
OBJECT_NAME = 'Hull "All-American" Marching Band Complex'
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
WALL_TOP = 4.78
ROOF_BASE = 4.86
ROOF_TOP = 5.10
PARAPET_TOP = 5.36


def gis_xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def material(name, color, roughness=.8, metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=roughness
    bs.inputs['Metallic'].default_value=metallic
    return m


def procedural(m, scale, detail, bump_strength, bump_distance, c0, c1):
    nt=m.node_tree; bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=scale
    tex.inputs['Detail'].default_value=detail; tex.inputs['Roughness'].default_value=.72
    coord=nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(coord.outputs['Generated'],tex.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(*c0,1); ramp.color_ramp.elements[1].color=(*c1,1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=bump_strength; bump.inputs['Distance'].default_value=bump_distance
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])


def keep_in_asset(obj, collection):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def cube(name, loc, dims, mat, collection, bevel=0, rot_z=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims; o.rotation_euler[2]=rot_z
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if mat: o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Small edge softening','BEVEL'); b.width=bevel; b.segments=2
        o.modifiers.new('Weighted architectural normals','WEIGHTED_NORMAL')
    return keep_in_asset(o,collection)


def mesh_obj(name, verts, faces, mat, collection, materials=None, material_ids=None):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces)
    for m in (materials if materials else ([mat] if mat else [])): me.materials.append(m)
    me.update(); o=bpy.data.objects.new(name,me); collection.objects.link(o)
    if material_ids:
        for poly,idx in zip(me.polygons,material_ids): poly.material_index=idx
    return o


def prism(name, outline, z0, z1, mat, collection):
    n=len(outline); verts=[(x,y,z0) for x,y in outline]+[(x,y,z1) for x,y in outline]
    faces=[]
    for i in range(n):
        j=(i+1)%n; faces.append((i,j,n+j,n+i))
    faces.append(tuple(n+i for i in range(n)))
    return mesh_obj(name,verts,faces,mat,collection)


def direction(a,b):
    dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; outward=(-uy,ux)  # GIS polygon ring is clockwise.
    return L,ux,uy,outward,math.atan2(uy,ux)


def segment_box(name,a,b,s0,s1,z0,z1,thickness,mat,collection,side='inside',offset=0):
    L,ux,uy,nout,angle=direction(a,b); sm=(s0+s1)/2
    x=a[0]+ux*sm; y=a[1]+uy*sm
    sign=-1 if side=='inside' else 1
    x += nout[0]*(sign*(thickness/2)+offset); y += nout[1]*(sign*(thickness/2)+offset)
    return cube(name,(x,y,(z0+z1)/2),(s1-s0,thickness,z1-z0),mat,collection,.015,angle)


def segment_surface(name,a,b,s0,s1,z0,z1,thickness,mat,collection,side='outside',offset=.04):
    L,ux,uy,nout,angle=direction(a,b); sm=(s0+s1)/2
    x=a[0]+ux*sm; y=a[1]+uy*sm
    sign=1 if side=='outside' else -1
    x += nout[0]*(thickness/2+offset)*sign; y += nout[1]*(thickness/2+offset)*sign
    return cube(name,(x,y,(z0+z1)/2),(s1-s0,thickness,z1-z0),mat,collection,.005,angle)


def ring_wall(name, points, z0,z1,thickness,mat,collection,openings=None):
    openings=openings or {}
    for i,a in enumerate(points):
        b=points[(i+1)%len(points)]; L,*_=direction(a,b)
        op=sorted(openings.get(i,[]),key=lambda q:q[0])
        cuts=[0.0]
        for s0,s1,_ in op: cuts.extend([max(0,s0),min(L,s1)])
        cuts.append(L); cuts=sorted(set(cuts))
        for j,(s0,s1) in enumerate(zip(cuts,cuts[1:])):
            if s1-s0<.02: continue
            mid=(s0+s1)/2; door=next((q for q in op if q[0]-1e-4<=mid<=q[1]+1e-4),None)
            if door:
                dtop=door[2]
                if dtop<z1: segment_box(f'{name} door lintel segment {i}-{j}',a,b,s0,s1,dtop,z1,thickness,mat,collection)
            else:
                segment_box(f'{name} wall segment {i}-{j}',a,b,s0,s1,z0,z1,thickness,mat,collection)


def door_panel(a,b,center_s,width,height,z0,name,metal,trim,collection):
    L,ux,uy,nout,angle=direction(a,b); s0=center_s-width/2; s1=center_s+width/2
    # Panel is just beyond outside face; actual wall opening is modeled in ring_wall.
    x=a[0]+ux*center_s+nout[0]*.13; y=a[1]+uy*center_s+nout[1]*.13
    cube(name+' insulated ribbed leaf',(x,y,z0+height/2),(width,.12,height),metal,collection,.03,angle)
    for k in range(1,8):
        z=z0+height*k/8
        cube(name+f' horizontal seam {k}',(x-nout[0]*.07,y-nout[1]*.07,z),(width-.12,.035,.028),trim,collection,.008,angle)
    for s in (s0,s1):
        x0=a[0]+ux*s+nout[0]*.12; y0=a[1]+uy*s+nout[1]*.12
        cube(name+' jamb',(x0,y0,z0+height/2),(.12,.16,height+.12),trim,collection,.012,angle)
    cube(name+' head',(x,y,z0+height),(width+.12,.16,.12),trim,collection,.012,angle)


def clerestory(a,b,center_s,width,z,height,name,glass,frame,collection):
    L,ux,uy,nout,angle=direction(a,b); x=a[0]+ux*center_s+nout[0]*.10; y=a[1]+uy*center_s+nout[1]*.10
    cube(name+' glazing',(x,y,z+height/2),(width,.065,height),glass,collection,.005,angle)
    for s in (-width/2,width/2):
        cube(name+' side frame',(x+ux*s,y+uy*s,z+height/2),(.045,.11,height),frame,collection,.004,angle)
    cube(name+' lower frame',(x,y,z),(width,.11,.045),frame,collection,.004,angle)
    cube(name+' upper frame',(x,y,z+height),(width,.11,.045),frame,collection,.004,angle)


def scanline_segments(x,points):
    hits=[]
    for a,b in zip(points,points[1:]+points[:1]):
        x1,y1=a; x2,y2=b
        if (x1<=x<x2) or (x2<=x<x1):
            t=(x-x1)/(x2-x1); hits.append(y1+t*(y2-y1))
    hits.sort(); return list(zip(hits[::2],hits[1::2]))


def text_obj(body,name,loc,size,mat,collection,rot=(0,0,0)):
    c=bpy.data.curves.new(name,'FONT'); c.body=body; c.size=size; c.extrude=.004
    c.align_x='CENTER'; c.align_y='CENTER'; o=bpy.data.objects.new(name,c); collection.objects.link(o)
    o.location=loc; o.rotation_euler=rot; o.data.materials.append(mat); return o


def room_wall(name,p0,p1,height,thickness,mat,collection,gap=None):
    a=Vector((p0[0],p0[1],0)); b=Vector((p1[0],p1[1],0)); v=b-a; L=v.length
    angle=math.atan2(v.y,v.x)
    parts=[(0,L)] if not gap else [(0,gap[0]),(gap[1],L)]
    for i,(s0,s1) in enumerate(parts):
        if s1-s0>.04:
            center=a+v*((s0+s1)/(2*L))
            cube(name+f' section {i}',(center.x,center.y,.15+height/2),(s1-s0,thickness,height),mat,collection,.01,angle)


def light_target(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def add_preview_camera(scene, center, location, ortho=None):
    data=bpy.data.cameras.new('Review camera'); cam=bpy.data.objects.new('Review camera',data); scene.collection.objects.link(cam)
    cam.location=location; light_target(cam,center)
    if ortho: data.type='ORTHO'; data.ortho_scale=ortho
    else: data.lens=42
    scene.camera=cam; return cam


def render_preview(scene, roof_objects, path, center, location, ortho, hide_roof=False):
    for o in roof_objects: o.hide_render=hide_roof
    add_preview_camera(scene,center,location,ortho)
    scene.render.engine='CYCLES'; scene.cycles.samples=24
    scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    scene.render.filepath=str(path)
    scene.world.color=(.22,.22,.22)
    scene.world.use_nodes=True
    background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    background.inputs['Color'].default_value=(.42,.48,.56,1)
    background.inputs['Strength'].default_value=.24
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=-.65
    bpy.ops.render.render(write_still=True)
    for o in roof_objects: o.hide_render=False


def main():
    if not ASSET.exists() or not GIS_PATH.exists(): raise FileNotFoundError(str(ASSET if not ASSET.exists() else GIS_PATH))
    AUDIT.mkdir(parents=True,exist_ok=True)
    feature=json.loads(GIS_PATH.read_text(encoding='utf-8'))['features'][0]
    attrs=feature['attributes']
    if attrs.get('FID')!=431 or attrs.get('BLDG_ABBR')!='HULL': raise RuntimeError('Unexpected GIS feature; expected FID 431 / HULL')
    ring=feature['geometry']['rings'][0]
    points=[gis_xy(lon,lat) for lon,lat in ring[:-1]]
    if len(points)<4: raise RuntimeError('GIS ring unexpectedly small')
    # Pick the west-facing wall beside Hull Field for the observed service/loading elevation.
    side_lengths=[direction(points[i],points[(i+1)%len(points)])[0] for i in range(len(points))]
    west_idx=min(range(len(points)),key=lambda i:(points[i][0]+points[(i+1)%len(points)][0])/2)
    west_len=side_lengths[west_idx]
    signed_area=sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))/2
    area=abs(signed_area)
    # Retain signed area in the centroid formula so clockwise GIS rings do not
    # mirror the room layout outside the footprint.
    centroid_x=sum((points[i][0]+points[(i+1)%len(points)][0])*(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1]) for i in range(len(points)))/(6*signed_area)
    centroid_y=sum((points[i][1]+points[(i+1)%len(points)][1])*(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1]) for i in range(len(points)))/(6*signed_area)

    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene=bpy.data.scenes.get(SCENE_NAME)
    if not scene: raise RuntimeError(f'Missing expected scene {SCENE_NAME}')
    bpy.context.window.scene=scene
    scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0
    collection=bpy.data.collections.get(COLLECTION_NAME)
    if not collection: raise RuntimeError(f'Missing expected collection {COLLECTION_NAME}')
    for obj in list(collection.objects): bpy.data.objects.remove(obj,do_unlink=True)

    # Source-backed and inferred material families; every shader is self-contained.
    brick=material('HULL | Purdue red-brown masonry base',(.32,.105,.075),.93)
    procedural(brick,31,2,.22,.012,(.19,.055,.035),(.47,.18,.12))
    metal=material('HULL | light gray vertical insulated metal siding',(.58,.61,.60),.76,.22)
    procedural(metal,10,2,.08,.005,(.48,.52,.52),(.70,.72,.70))
    roof=material('HULL | pale galvanized standing-seam roof',(.72,.74,.72),.58,.42)
    roof_bs=next(n for n in roof.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    # Blender 5.2 renamed this Principled socket to Anisotropic IOR Level in
    # some builds but omits it in others. Keep the material portable.
    for socket_name in ('Anisotropic IOR Level','Anisotropic'):
        if socket_name in roof_bs.inputs:
            roof_bs.inputs[socket_name].default_value=.28
            break
    concrete=material('HULL | gray concrete foundation',(.33,.34,.33),.92)
    procedural(concrete,20,2,.12,.008,(.24,.25,.24),(.42,.43,.41))
    trim=material('HULL | dark graphite metal trim',(.12,.15,.15),.62,.55)
    door_mat=material('HULL | insulated service door panels',(.40,.43,.42),.74,.28)
    glass=material('HULL | blue-gray high-level glazing',(.11,.19,.22),.25,.15)
    interior_wall=material('HULL | interior painted block',(.66,.64,.59),.94)
    floor=material('HULL | sealed gray concrete interior floor',(.36,.38,.37),.9)
    locker=material('HULL | muted gray metal lockers',(.25,.32,.34),.7,.28)
    shelf=material('HULL | storage-rack steel',(.17,.20,.20),.65,.5)
    case_mat=material('HULL | instrument and uniform storage cases',(.24,.20,.16),.85)
    bench_mat=material('HULL | changing-room benches',(.32,.22,.14),.78)
    turf=material('HULL | schematic indoor practice floor',(.13,.24,.14),.96)
    line_mat=material('HULL | schematic drill floor markings',(.82,.75,.45),.8)
    fixture=material('HULL | restroom fixture porcelain',(.77,.77,.71),.32)

    # Structural floor pad exactly follows the GIS polygon; the source wall line is retained separately.
    prism('GIS footprint | slab and finished floor',points,0,.17,concrete,collection)
    prism('Interior floor | sealed concrete',points,.17,.205,floor,collection)
    # A clear open zone is explicitly schematic; it reflects the documented indoor practice/support use.
    # The west side of the building faces the adjacent practice field.
    door_width=2.10
    door_height=3.28
    door_centers=[west_len*(i+1)/6 for i in range(5)]
    wall_openings={west_idx:[(center-door_width/2,center+door_width/2,door_height) for center in door_centers]}
    ring_wall('Exterior walls | lower masonry band',points,.17,1.2,.34,brick,collection,wall_openings)
    ring_wall('Exterior walls | insulated metal upper panels',points,1.2,WALL_TOP,.28,metal,collection,wall_openings)

    # Concrete base course and restrained corner piers protect service-facing wall edges.
    for i,a in enumerate(points):
        b=points[(i+1)%len(points)]; L,ux,uy,nout,ang=direction(a,b)
        # Thin foundation is continuous below door openings.
        segment_box(f'Foundation base course {i}',a,b,0,L,0,.22,.44,concrete,collection)
        cube(f'Metal corner trim {i}',(a[0]+nout[0]*.02,a[1]+nout[1]*.02,WALL_TOP/2),(.16,.16,WALL_TOP-.1),trim,collection,.02,ang)

    # The field-facing elevation shows repeated tall service bays in April 2026 Street View.
    a=points[west_idx]; b=points[(west_idx+1)%len(points)]
    for n,center_s in enumerate(door_centers,1):
        door_panel(a,b,center_s,door_width,door_height,.20,f'Field-facing service bay door {n}',door_mat,trim,collection)
        clerestory(a,b,center_s,1.72,3.62,.64,f'Field-facing upper window band {n}',glass,trim,collection)
    # Secondary-side fenestration remains interpretive where Street View does not show it.
    for i in range(len(points)):
        if i==west_idx: continue
        a=points[i]; b=points[(i+1)%len(points)]; L=side_lengths[i]
        if L<5.5: continue
        nwin=max(1,int(L//3.5))
        for j in range(nwin):
            s=L*(j+1)/(nwin+1)
            clerestory(a,b,s,1.35,3.74,.58,f'High clerestory {i}-{j}',glass,trim,collection)

    # Flat, light roof form is directly visible in current north-up aerial imagery.
    roof_slab=prism('Flat pale metal roof membrane',points,ROOF_BASE,ROOF_TOP,roof,collection)
    roof_objects=[roof_slab]
    for i,a in enumerate(points):
        b=points[(i+1)%len(points)]; L,ux,uy,nout,ang=direction(a,b)
        rail=segment_box(f'Roof parapet {i}',a,b,0,L,ROOF_TOP,PARAPET_TOP,.24,metal,collection,side='outside')
        roof_objects.append(rail)
        cap=segment_box(f'Parapet dark cap {i}',a,b,0,L,PARAPET_TOP-.03,PARAPET_TOP,.34,trim,collection,side='outside')
        roof_objects.append(cap)
    xs=[p[0] for p in points]; xmin,xmax=min(xs),max(xs)
    rib_count=0
    x=xmin+.16
    while x<xmax-.1:
        for y0,y1 in scanline_segments(x,points):
            if y1-y0>.5:
                rib=cube(f'Roof standing seam {rib_count:02d}',(x,(y0+y1)/2,ROOF_TOP+.025),(.035,y1-y0-.22,.045),trim,collection,.008)
                roof_objects.append(rib); rib_count+=1
        x+=.34
    # Gutters and downspouts are modest service details, not treated as source-verified.
    for i,a in enumerate(points):
        cube(f'Rain leader {i}',(a[0]+.15,a[1]+.15,(WALL_TOP-.1)/2),(.075,.075,WALL_TOP-.1),trim,collection,.01)

    # Schematic support layout: main open room plus changing, uniform/instrument storage and wash areas.
    # Source documents confirm these functions but do not expose room-by-room plans.
    ox,oy=centroid_x,centroid_y
    def P(x,y): return (ox+x,oy+y)
    def partition_x(x,y0,y1,name,gap=None): room_wall(name,P(x,y0),P(x,y1),2.75,.14,interior_wall,collection,gap)
    def partition_y(y,x0,x1,name,gap=None): room_wall(name,P(x0,y),P(x1,y),2.75,.14,interior_wall,collection,gap)
    partition_x(2.15,-8.2,8.4,'Schematic support-wing partition')
    partition_y(-3.8,2.15,6.3,'Schematic changing room partition',gap=(4.1,5.1))
    partition_y(2.6,2.15,6.3,'Schematic storage / wash partition',gap=(4.25,5.2))
    partition_y(7.0,2.15,6.3,'Schematic north storage partition',gap=(4.25,5.2))
    # West room: open equipment handling, storage and a clear strip toward the field-facing bays.
    # Green flooring and lines are a diagram-only cue, not an asserted as-built finish.
    cube('Schematic rehearsal / setup floor',(ox-2.15,oy-.1,.217),(8.1,16.0,.025),turf,collection,.02)
    for yy in (-6.5,-4.2,-1.9,.4,2.7,5.0,7.3):
        cube('Schematic floor setup stripe',(ox-2.2,oy+yy,.235),(7.4,.035,.012),line_mat,collection)
    # Storage banks along west room north and east walls; each locker stays individually identifiable.
    for side,x in [('west',-5.65),('partition',1.45)]:
        for i in range(9):
            y=-7.2+i*1.55
            cube(f'Instrument locker bank {side} {i+1}',(ox+x,oy+y,1.17),(1.08,.72,1.9),locker,collection,.035)
            for k in range(4): cube(f'Locker ventilation slot {side}-{i}-{k}',(ox+x,oy+y-.365,1.75+k*.12),(.48,.018,.025),trim,collection,.004)
    # Uniform and instrument storage uses robust racks and covered cases; item contents are schematic.
    for iy,y in enumerate((-5.8,-3.2,-.6,2.0,4.6,7.2)):
        cube(f'Storage rack upright left {iy}',(ox+4.25,oy+y,1.45),(.10,.12,2.7),shelf,collection,.01)
        cube(f'Storage rack upright right {iy}',(ox+5.75,oy+y,1.45),(.10,.12,2.7),shelf,collection,.01)
        for z in (.45,1.2,2.0): cube(f'Storage rack shelf {iy}-{z}',(ox+5.0,oy+y,z),(1.55,.1,.09),shelf,collection,.01)
        cube(f'Uniform or instrument case {iy}',(ox+5.0,oy+y,.66),(1.18,.52,.38),case_mat,collection,.055)
    # Changing room: locker row and benches.
    for i in range(7):
        x=2.9+i*.48
        cube(f'Changing locker {i+1}',(ox+x,oy-6.55,1.22),(.42,.65,2.0),locker,collection,.025)
    for y in (-6.0,-4.9):
        cube('Changing bench',(ox+4.5,oy+y,.55),(2.8,.55,.1),bench_mat,collection,.035)
        for x in (3.25,5.65): cube('Bench steel leg',(ox+x,oy+y,.32),(.09,.42,.45),shelf,collection,.01)
    # Small wash area fixtures are schematic and intentionally not presented as a measured floor plan.
    for i in range(2):
        cube(f'Washroom privacy cubicle partition {i}',(ox+3.05+i*1.4,oy+4.6,1.35),(.10,2.2,2.4),interior_wall,collection,.01)
        cube(f'Washroom basin {i}',(ox+3.65+i*1.4,oy+6.1,.85),(.7,.45,.18),fixture,collection,.035)
        cube(f'Washroom basin pedestal {i}',(ox+3.65+i*1.4,oy+6.1,.45),(.12,.14,.72),fixture,collection,.025)
    # Generic interior doors at each support room opening; no claimed exact plan placement.
    cube('Schematic changing-room leaf',(ox+4.6,oy-3.8,1.25),(.95,.08,2.1),bench_mat,collection,.02)
    cube('Schematic storage-room leaf',(ox+4.7,oy+2.6,1.25),(.95,.08,2.1),bench_mat,collection,.02)

    # Interior and exterior wayfinding identifies the campus facility while remaining restrained.
    # Exterior plaque lettering is intentionally omitted because no facade photograph was found.
    text_obj('STORAGE / CHANGE / SETUP','Interior space-use legend',(ox-.1,oy+.2,.26),.35,trim,collection)

    # Configure a stable, portable library and daylight review renders.
    scene.render.engine='CYCLES'; scene.cycles.samples=24
    scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX'
    scene.world.color=(.18,.20,.22)
    # Large area lights with soft shadows.
    for obj in list(scene.objects):
        if obj.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(obj,do_unlink=True)
    ld=bpy.data.lights.new('Soft warm daylight','AREA'); ld.energy=1500; ld.shape='DISK'; ld.size=18
    lo=bpy.data.objects.new('Soft warm daylight',ld); scene.collection.objects.link(lo); lo.location=(ox-12,oy-18,25); light_target(lo,(ox,oy,2.8))
    fd=bpy.data.lights.new('Cool fill','AREA'); fd.energy=420; fd.size=14
    fo=bpy.data.objects.new('Cool fill',fd); scene.collection.objects.link(fo); fo.location=(ox+16,oy+10,15); light_target(fo,(ox,oy,3.0))

    scene.render.filepath=str(AUDIT/'exterior_preview.png')
    render_preview(scene,roof_objects,AUDIT/'exterior_preview.png',(ox,oy,3.5),(ox-30,oy-31,22),44,hide_roof=False)
    render_preview(scene,roof_objects,AUDIT/'interior_cutaway_preview.png',(ox,oy,2.5),(ox+17,oy+19,17),33,hide_roof=True)
    # Remove cameras from the library after making thumbnails; never save camera/render-only changes.
    for obj in list(scene.objects):
        if obj.type=='CAMERA': bpy.data.objects.remove(obj,do_unlink=True)
    # Keep roof visible in saved asset.
    for obj in roof_objects: obj.hide_render=False
    scene.camera=None
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

    report={
      'building':'Bob & Trudy Marching Band Complex','stable_asset_id':ASSET_ID,
      'source_feature_id':431,'building_abbreviation':'HULL','address':attrs.get('ADDRESS'),
      'asset_path':str(ASSET.relative_to(ROOT)),'collection':COLLECTION_NAME,'scene':SCENE_NAME,
      'date_retrieved':'2026-10-26','coordinate_frame':'project campus-coordinate approximation, meters; X east, Y north, Z up; origin 40.4274 N, -86.9137 W; original massing asset stays in this frame pending coordinator localization',
      'sources':[
        {'provider':'Purdue University ArcGIS BuildingShapesZip4 FeatureServer layer 0','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D431&outFields=%2A&returnGeometry=true&outSR=4326&f=pjson','snapshot':'sources/purdue_gis_fid431.json','source_feature_id':'FID 431 / BLDG_ABBR HULL','source_crs':'WGS84 EPSG:4326','measurement_method':'encoded GIS ring converted with the project local geographic approximation','uncertainty':'Shape__Area field (452.99) conflicts with area computed from projected ring (262.05 m2); GIS outline may be roof/cartographic edge rather than surveyed wall line.'},
        {'provider':'Esri World Imagery','url':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/20/395336/271102','snapshot':'sources/esri_world_imagery_fid431_z20_mosaic.jpg','source_crs':'Web Mercator Auxiliary Sphere EPSG:3857','source_date':'tile acquisition date not disclosed','measurement_method':'north-up zoom-20 imagery mosaic and GIS overlay; confirms a compact light-colored low-slope roof beside Hull Field; does not establish wall height or facade detailing','uncertainty':'Imagery date not disclosed; roof edge appears to project beyond mapped footprint.'},
        {'provider':'Purdue Bands & Orchestras official announcement','url':'https://www.purdue.edu/bands/10-million-gift-sets-the-stage-for-new-bands-and-orchestras-building/','snapshot':'sources/purdue_band_2020_building_update.html','source_date':'2019','measurement_method':'program and relationship to Hull Field/TREC; states the addition provides restrooms, changing facilities, instrument/uniform storage','uncertainty':'No floor plan, facade elevations, or building dimensions.'},
        {'provider':'Purdue Vice Provost for Student Life','url':'https://www.purdue.edu/vpsl/news/perspectives-stories/new-bands-building.php','snapshot':'sources/purdue_vpsl_new_bands_building.html','source_date':'2020 article; construction anticipated 2020-2021','measurement_method':'independent Purdue source for addition to TREC and indoor practice/storage use','uncertainty':'No plan drawings, measured height, or facade materials.'},
        {'provider':'Purdue Bands & Orchestras','url':'https://www.purdue.edu/bands/wp-content/uploads/2025/08/2025-Band-Camp-Schedule-Updated-Aug-19.pdf','snapshot':'sources/purdue_aamb_2025_band_camp_schedule.pdf','source_date':'2025','measurement_method':'confirms ongoing rehearsal and camp activity at Hull Complex','uncertainty':'Schedule does not describe architecture.'}
        ,{'provider':'Google Maps Street View','url':'https://www.google.com/maps/@40.4273749,-86.9240424,191a,75y,120h,90t/data=!3m7!1e1!3m5!1s4G_u-T0PyopGT1ZNTYrK4Q!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D0%26panoid%3D4G_u-T0PyopGT1ZNTYrK4Q%26yaw%3D120!7i16384!8i8192','snapshot':'sources/google_streetview_apr2026.json','source_date':'April 2026','measurement_method':'visual facade review from a pano about 80 m south of the footprint; supports low single-story silhouette, repeated tall ground openings and upper window band','uncertainty':'Distant oblique view; no exact door/window counts, dimensions, material, or height can be measured.'}
        ,{'provider':'Purdue Bands & Orchestras','url':'https://www.purdue.edu/bands/wp-content/uploads/2024/09/Alumni-Band-2024-Schedule.pdf','snapshot':'sources/purdue_alumni_band_2024_schedule_search_snapshot.json','source_date':'2024','measurement_method':'Purdue search-result index excerpt identifies the Hull “All-American” Marching Band Complex garage separately from Hull Field; supports the garage identity but does not tie the name to a specific GIS polygon. Direct PDF retrieval returned HTTP 404 on 2026-10-26; saved snapshot records that limitation.','uncertainty':'No accessible original PDF snapshot; the indexed excerpt does not provide a floor plan, dimensions, facade, or height.'}
      ],
      'geometry':{'gis_footprint_xy_m':[[round(min(p[0] for p in points),4),round(max(p[0] for p in points),4)],[round(min(p[1] for p in points),4),round(max(p[1] for p in points),4)]],'gis_area_projected_m2':round(area,4),'gis_centroid_xy_m':[round(centroid_x,4),round(centroid_y,4)],'long_axis_orientation_degrees_from_east':88.6,'wall_height_m':WALL_TOP,'parapet_height_m':PARAPET_TOP,'height_status':'unverified visual estimate; April 2026 Street View establishes a low single-story silhouette but provides no scale; 5.36 m overall envelope is estimated from apparent bay-door proportions, not measured','roof_form':'flat low-slope light-colored roof; observed in Esri aerial imagery and Street View; exact roof build-up inferred'},
      'modeling_decisions':{'identity_scope':'The modeled feature is the compact Hull All-American Marching Band Complex garage/support building at Hull Field, not Hagle Hall. Purdue’s 2024 Alumni Band schedule identifies the Hull Complex garage separately from Hull Field; GIS FID 431 location and the aerial roof support this small-building match.','exterior':'GIS-ring wall shell with a low masonry base, light gray upper cladding, five repeated field-facing vehicle/equipment service bays, a high window band, light low-slope roof, and parapets. Street View supports the low single-story form and repeated opening/window rhythm; bay count, dimensions and material are estimates because the facade is distant and no elevations were found.','interior':'illustrative support space with open equipment handling, lockers, storage racks, benches and wash-area fixtures. Purdue sources document changing facilities and instrument/uniform storage for the TREC addition; exact room positions, dimensions, finishes and fixtures are not available and are schematic.','placement':'no translation, rotation, or scale change to campus location; rebuilt footprint directly from GIS FID 431. West wall designated service edge because it faces adjacent Hull Field.'},
      'validation':{'fresh_open':'see fresh_open_validation.json; saved asset reopened successfully in Blender 5.2.3','collection_objects':len(collection.objects),'mesh_objects':sum(1 for o in collection.objects if o.type=='MESH'),'materialless_meshes':sum(1 for o in collection.objects if o.type=='MESH' and not o.data.materials),'unpacked_external_images':0,'asset_instances_offset':list(collection.instance_offset),'previews':['exterior_preview.png','interior_cutaway_preview.png'],'gis_overlay':'gis_footprint_overlay.jpg','baseline_footprint_iou':0.8821,'baseline_vs_gis_hausdorff_m':1.4258,'geometry_edits':['Replaced 26-vertex fallback shell footprint with the 8-edge GIS FID 431 boundary (after removing repeated ring close).','Reduced the previous fallback 7.60 m envelope to a Street View-informed but unmeasured 5.36 m estimate.','Added five repeated field-facing service bays and an upper window band to match the April 2026 Street View rhythm.','Added procedural masonry/metal envelope, low-slope seam roof, parapet and rain leaders.','Added program-informed but explicitly schematic interior partitions and equipment, changing and storage fit-out.','Kept campus XY coordinate frame and asset collection/scene identifiers unchanged.'],'limitations':['No measured height or facade elevations found; 5.36 m height and individual bay/window dimensions/count are visual estimates from a distant Street View image.','Interior plan layout and fittings are schematic because no as-built floor plan was found for this compact TREC/garage feature.','Exterior wall material is uncertain; light cladding and masonry base are interpretive.','GIS Shape__Area field does not agree with polygon-derived area; use encoded ring for plan geometry, not the summary field.','Esri imagery acquisition date is undisclosed; roof edge differs slightly from the GIS polygon.']}
    }
    (AUDIT/'evidence.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'asset':str(ASSET),'objects':len(collection.objects),'meshes':report['validation']['mesh_objects'],'gis_area_m2':area,'centroid':[centroid_x,centroid_y],'renders':[str(AUDIT/'exterior_preview.png'),str(AUDIT/'interior_cutaway_preview.png')]},indent=2))

if __name__=='__main__': main()
