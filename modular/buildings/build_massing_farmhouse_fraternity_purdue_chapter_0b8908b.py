"""Build the FarmHouse Fraternity, Purdue Chapter modular asset.

All geometry is in the campus world coordinate frame (metres; X east, Y north).
The building's source outline is the named OSM way 301923755. The older Purdue
campus GIS feature 778 has a conflicting, much smaller rectangular shell and is
not used as the structural footprint.
"""
import bpy
import json
import math
import os
from mathutils import Vector, Matrix

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET_ID = 'massing_farmhouse_fraternity_purdue_chapter_0b8908b'
COLLECTION_NAME = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID
ASSET_PATH = os.path.join(os.path.dirname(__file__), ASSET_ID + '.blend')
EVIDENCE_DIR = os.path.join(ROOT, 'audit', 'farmhouse_fraternity_purdue_chapter')
OSM_PATH = os.path.join(EVIDENCE_DIR, 'sources', 'overpass_buildings_near_farmhouse_2026-10-26.json')
LAT0, LON0 = 40.4274, -86.9137

with open(OSM_PATH, 'r', encoding='utf-8') as f:
    osm = json.load(f)
outline_way = next(e for e in osm['elements'] if e.get('id') == 301923755)
outline = []
for p in outline_way['geometry'][:-1]:
    x = (p['lon'] - LON0) * 111412.84 * math.cos(math.radians(LAT0))
    y = (p['lat'] - LAT0) * 111040.0
    outline.append((x, y))

# Drop tiny tessellation kinks from the public building trace while preserving
# the salient corner cuts and stepped wings. Maximum movement is below 0.2 m.
def simplify_outline(points, max_deviation=0.18, max_turn_deg=9.0):
    pts=list(points)
    changed=True
    while changed and len(pts)>8:
        changed=False
        for i,p in enumerate(pts):
            a,b=pts[i-1],pts[(i+1)%len(pts)]
            ab=math.dist(a,b)
            if ab < 1e-6: continue
            dev=abs((b[0]-a[0])*(a[1]-p[1])-(a[0]-p[0])*(b[1]-a[1]))/ab
            v1=(p[0]-a[0],p[1]-a[1]); v2=(b[0]-p[0],b[1]-p[1])
            den=math.hypot(*v1)*math.hypot(*v2)
            dot=max(-1.0,min(1.0,(v1[0]*v2[0]+v1[1]*v2[1])/den)) if den else 1
            turn=math.degrees(math.acos(dot))
            if dev<=max_deviation and turn<=max_turn_deg:
                pts.pop(i); changed=True; break
    return pts

outline = simplify_outline(outline)

# A clean, deterministic build: the source library must contain no unrelated
# campus objects or materials from a previous generation.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = SCENE_NAME
collection = bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(collection)
review_collection = bpy.data.collections.new('Review_Setup_FarmHouse')
scene.collection.children.link(review_collection)

def material(name, color, roughness=0.72, noise_scale=22, bump_strength=0.14):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    tex = nt.nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = noise_scale
    tex.inputs['Detail'].default_value = 3.0
    tex.inputs['Roughness'].default_value = 0.72
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.23
    ramp.color_ramp.elements[0].color = (*(v * 0.79 for v in color), 1)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (*(min(1, v * 1.13) for v in color), 1)
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = bump_strength
    bump.inputs['Distance'].default_value = 0.035
    if 'brick' in name.lower():
        brick = nt.nodes.new('ShaderNodeTexBrick')
        brick.inputs['Color1'].default_value=(0.38,0.115,0.075,1)
        brick.inputs['Color2'].default_value=(0.23,0.060,0.041,1)
        brick.inputs['Mortar'].default_value=(0.42,0.34,0.27,1)
        brick.inputs['Scale'].default_value=2.0
        brick.inputs['Mortar Size'].default_value=0.035
        brick.inputs['Mortar Smooth'].default_value=0.02
        brick.inputs['Brick Width'].default_value=0.50
        brick.inputs['Row Height'].default_value=0.25
        texcoord=nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(texcoord.outputs['UV'],brick.inputs['Vector'])
        nt.links.new(brick.outputs['Color'],bsdf.inputs['Base Color'])
        nt.links.new(brick.outputs['Fac'],bump.inputs['Height'])
    else:
        nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m

BRICK = material('FarmHouse | red-brown running-bond brick', (0.30, 0.085, 0.055), 0.82, 76, 0.28)
BRICK_DARK = material('FarmHouse | brick variation', (0.22, 0.055, 0.035), 0.84, 90, 0.25)
MORTAR = material('FarmHouse | warm mortar', (0.52, 0.40, 0.32), 0.92, 120, 0.13)
STONE = material('FarmHouse | cream limestone', (0.72, 0.67, 0.56), 0.72, 14, 0.12)
STONE_LIGHT = material('FarmHouse | carved limestone trim', (0.84, 0.80, 0.71), 0.62, 28, 0.1)
ROOF = material('FarmHouse | charcoal dimensional shingle', (0.115, 0.125, 0.13), 0.9, 120, 0.2)
WHITE = material('FarmHouse | painted white wood', (0.88, 0.87, 0.82), 0.62, 30, 0.08)
GLASS = material('FarmHouse | blue-gray reflective glass', (0.08, 0.18, 0.23), 0.19, 4, 0.02)
WOOD = material('FarmHouse | stained oak entry', (0.20, 0.075, 0.035), 0.48, 28, 0.15)
METAL = material('FarmHouse | dark bronze metal', (0.07, 0.075, 0.073), 0.36, 12, 0.08)
FLOOR = material('FarmHouse | interior warm stone floor', (0.48, 0.42, 0.33), 0.73, 42, 0.13)
INT_WALL = material('FarmHouse | interior pale plaster', (0.72, 0.68, 0.59), 0.85, 20, 0.06)

parts = []
def mesh_obj(name, verts, faces, mat, indices=None):
    me = bpy.data.meshes.new(name + 'Mesh')
    me.from_pydata(verts, [], faces)
    me.materials.append(mat)
    if indices:
        for poly, idx in zip(me.polygons, indices):
            poly.material_index = idx
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    # Planar UVs in metres keep the brick courses horizontal and consistent on
    # north/south and east/west walls after the objects are joined into asset.
    uv_layer=me.uv_layers.new(name='Architectural UV')
    for poly in me.polygons:
        n=poly.normal
        for li in poly.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            if abs(n.z)>0.7: uv=(v.x,v.y)
            elif abs(n.x)>abs(n.y): uv=(v.y,v.z)
            else: uv=(v.x,v.z)
            uv_layer.data[li].uv=uv
    parts.append(ob)
    return ob

def box(name, center, size, mat, bevel=0, rotation_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler[2] = rotation_z
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('soft arris', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        mod = ob.modifiers.new('weighted corner normals', 'WEIGHTED_NORMAL')
    parts.append(ob)
    return ob

def prism(name, points, z0, z1, mat):
    n = len(points)
    verts = [(x, y, z) for z in (z0, z1) for x, y in points]
    faces = [tuple(range(n-1, -1, -1)), tuple(range(n, 2*n))]
    faces.extend((i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n))
    return mesh_obj(name, verts, faces, mat)

def face_poly(name, points, mat):
    return mesh_obj(name, points, [tuple(range(len(points)))], mat)

def signed_area(poly):
    return sum(poly[i][0]*poly[(i+1)%len(poly)][1] - poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly))) * 0.5

if signed_area(outline) < 0:
    outline.reverse()
xs, ys = [p[0] for p in outline], [p[1] for p in outline]
minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
cx, cy = (minx+maxx)/2, (miny+maxy)/2

# Four above-grade floors over a partial basement: height is estimated from
# the architect's four-story-over-basement description, not a survey.
BASEMENT = -1.35
FLOOR_Z = [0.0, 3.35, 6.55, 9.75, 12.95]
EAVE = 13.80
RIDGE = 19.20

# Stone foundation/base; brick walls to the eave. OSM outline is the measured
# plan polygon; the cladding/roof projection remains a small ornamental detail.
prism('FarmHouse | limestone base and basement', outline, BASEMENT, 0.72, STONE)
prism('FarmHouse | four-story brick exterior', outline, 0.55, EAVE, BRICK)

# Smooth stone string courses at floor transitions and top cornice.
for z in [0.72, 3.30, 6.50, 9.70, 12.90, 13.50]:
    prism('FarmHouse | continuous limestone story band', outline, z, z+0.18, STONE_LIGHT)
prism('FarmHouse | upper cornice', outline, 13.50, 13.84, WHITE)

# Main perimeter fenestration: repeated tall divided-light windows, framed in
# limestone. The source photos show vertical paired sash, pale surrounds, and
# projecting corner quoins. Each facade segment gets a rhythmic grid.
floors = [(0.98, 2.72), (3.58, 5.95), (6.78, 9.15), (9.98, 12.35)]
for ei, (a, b) in enumerate(zip(outline, outline[1:]+outline[:1])):
    ax, ay = a; bx, by = b
    dx, dy = bx-ax, by-ay
    L = math.hypot(dx, dy)
    if L < 1.35: continue
    tx, ty = dx/L, dy/L
    # CCW polygon: right-hand perpendicular points outwards.
    nx, ny = ty, -tx
    margin = 0.90
    nwin = max(1, int((L-2*margin)//3.55))
    pitch = (L-2*margin)/nwin
    centers = [margin + (j+0.5)*pitch for j in range(nwin)]
    for fi, (zlo, zhi) in enumerate(floors):
        for wi, s in enumerate(centers):
            # Ground level has larger paired openings; other storeys are tall sash.
            w = min(1.35 if fi == 0 else 1.08, pitch*0.52)
            h = zhi-zlo
            u, v = ax+tx*s, ay+ty*s
            def quad(u0,u1,z0,z1,off=0.035):
                return [(u0*tx+nx*off, u0*ty+ny*off, z0),
                        (u1*tx+nx*off, u1*ty+ny*off, z0),
                        (u1*tx+nx*off, u1*ty+ny*off, z1),
                        (u0*tx+nx*off, u0*ty+ny*off, z1)]
            # Coordinates above are based on world origin; adjust to edge start.
            def panel(name, du0, du1, zz0, zz1, mat, off=0.045):
                pts = [(ax+tx*(s+du)+nx*off, ay+ty*(s+du)+ny*off, zz)
                       for du,zz in [(du0,zz0),(du1,zz0),(du1,zz1),(du0,zz1)]]
                return face_poly(name, pts, mat)
            panel('FarmHouse | limestone window sill', -w/2-0.13, w/2+0.13, zlo-0.10, zlo+0.04, STONE_LIGHT)
            panel('FarmHouse | window header', -w/2-0.12, w/2+0.12, zhi-0.04, zhi+0.10, STONE_LIGHT)
            panel('FarmHouse | left limestone jamb', -w/2-0.11, -w/2+0.015, zlo, zhi, STONE_LIGHT)
            panel('FarmHouse | right limestone jamb', w/2-0.015, w/2+0.11, zlo, zhi, STONE_LIGHT)
            panel('FarmHouse | recessed sash glazing', -w/2+0.11, w/2-0.11, zlo+0.14, zhi-0.14, GLASS, 0.048)
            # Central meeting stile and two slim horizontal rails.
            panel('FarmHouse | vertical window mullion', -0.035, 0.035, zlo+0.12, zhi-0.12, WHITE, 0.058)
            for rz in (zlo + h*0.34, zlo + h*0.68):
                panel('FarmHouse | sash rail', -w/2+0.10, w/2-0.10, rz-0.025, rz+0.025, WHITE, 0.06)

# Limestone corner quoins: short projecting blocks interleaved with brick at
# each corner, closely following the current architect photographs.
for corner_i,(vx, vy) in enumerate(outline):
    prev=outline[corner_i-1]; nxt=outline[(corner_i+1)%len(outline)]
    v1=(vx-prev[0],vy-prev[1]); v2=(nxt[0]-vx,nxt[1]-vy)
    d=math.hypot(*v1)*math.hypot(*v2)
    if not d: continue
    turn=math.degrees(math.acos(max(-1,min(1,(v1[0]*v2[0]+v1[1]*v2[1])/d))))
    if turn < 35: continue
    for k, z in enumerate((0.86, 1.65, 2.43, 3.53, 5.25, 6.72, 8.45, 9.92, 11.65, 13.12)):
        box('FarmHouse | corner limestone quoin', (vx,vy,z), (0.48,0.48,0.36), STONE_LIGHT, 0.025)

# Roof: a coherent main north-south gable, white fascia and charcoal shingles.
# Published photographs show intersecting roof wings; the public outline alone
# cannot fix every ridge/valley, so this is a restrained design-level estimate.
roof_volumes=[]
def gable_roof(name, x0,x1,y0,y1,zbase,zridge, along_x=True):
    if along_x:
        v=[(x0,y0,zbase),(x1,y0,zbase),(x1,y1,zbase),(x0,y1,zbase),
           (x0,(y0+y1)/2,zridge),(x1,(y0+y1)/2,zridge)]
        f=[(0,3,2,1),(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5)]
    else:
        v=[(x0,y0,zbase),(x1,y0,zbase),(x1,y1,zbase),(x0,y1,zbase),
           ((x0+x1)/2,y0,zridge),((x0+x1)/2,y1,zridge)]
        f=[(0,3,2,1),(0,4,5,3),(4,1,2,5),(0,1,4),(3,5,2)]
    roof=mesh_obj(name+' | intersecting shingle roof volume',v,f,ROOF)
    roof_volumes.append(roof)
    # bright eaves emphasize the deep white roof trim in references
    if along_x:
        for y in (y0,y1): box(name+' | white eave fascia',((x0+x1)/2,y,zbase),(x1-x0+0.2,0.22,0.38),WHITE,0.03)
        box(name+' | ridge cap',((x0+x1)/2,(y0+y1)/2,zridge),(x1-x0,0.22,0.16),METAL,0.04)
    else:
        for x in (x0,x1): box(name+' | white eave fascia',(x,(y0+y1)/2,zbase),(0.22,y1-y0+0.2,0.38),WHITE,0.03)
        box(name+' | ridge cap',((x0+x1)/2,(y0+y1)/2,zridge),(0.22,y1-y0,0.16),METAL,0.04)

# The aerial and courtyard photographs show intersecting steep gable wings.
# The outline includes a U-shaped inner court; separate ridge/eave systems
# follow its south, west, east, and short northern connector wings. Heights and
# exact valleys are estimated from imagery rather than surveyed elevations.
gable_roof('FarmHouse | south entrance wing roof',minx+0.8,minx+23.0,miny+0.8,miny+17.0,EAVE,19.15,True)
gable_roof('FarmHouse | west court wing roof',minx+0.4,minx+10.5,miny+1.0,miny+16.5,EAVE,17.95,False)
gable_roof('FarmHouse | east long wing roof',maxx-11.8,maxx-0.45,miny+4.0,maxy-0.45,EAVE,18.30,False)
gable_roof('FarmHouse | north court connector roof',minx+10.1,minx+16.4,miny+16.0,maxy-0.35,EAVE,17.35,False)

# Union the watertight roof masses so the gable wings meet with real ridges and
# valleys instead of visibly overlapping slabs.
roof_root=roof_volumes[0]
for roof_part in roof_volumes[1:]:
    mod=roof_root.modifiers.new('merge intersecting gable roof volumes','BOOLEAN')
    mod.operation='UNION'; mod.solver='EXACT'; mod.object=roof_part
    bpy.context.view_layer.objects.active=roof_root
    roof_root.select_set(True); roof_part.select_set(False)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(roof_part,do_unlink=True)
    if roof_part in parts: parts.remove(roof_part)

# Main corner entrance: a chamfered projecting portico on the short southeast
# corner facade. The exact opening position follows the OSM corner bevel.
# OSM way turns the southeast corner with a diagonal on edge 6; the corner
# location and near-side photographs establish this as the main entry approach.
edges=[]
for i,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
    edges.append((math.dist(a,b),i,a,b))
entry_candidates=[e for e in edges if e[2][1] < miny+5.0 and e[3][0] > maxx-5.0 and abs(e[3][0]-e[2][0])>1.0 and abs(e[3][1]-e[2][1])>1.0]
entry_edge=max(entry_candidates or edges,key=lambda e:e[0])
L, ei, a, b = entry_edge
tx,ty=(b[0]-a[0])/L,(b[1]-a[1])/L
nx,ny=ty,-tx
entry_angle=math.atan2(ty,tx)
mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
def p_local(s, off, z): return (mid[0]+tx*s+nx*off,mid[1]+ty*s+ny*off,z)
doorw=1.95
doorh=2.55
face_poly('FarmHouse | recessed oak double entry', [p_local(-doorw/2,0.065,0.06),p_local(doorw/2,0.065,0.06),p_local(doorw/2,0.065,doorh),p_local(-doorw/2,0.065,doorh)], WOOD)
# Door leaves, raised panels, glass transom, hardware.
for side in (-1,1):
    box('FarmHouse | entry leaf raised panel',p_local(side*0.47,0.10,1.02),(0.80,0.045,1.35),WOOD,0.05,entry_angle)
    box('FarmHouse | entry leaf lower panel',p_local(side*0.47,0.11,0.40),(0.72,0.045,0.43),WOOD,0.04,entry_angle)
    box('FarmHouse | entry glass sidelights',p_local(side*1.04,0.075,1.72),(0.18,0.04,1.35),GLASS,0.01,entry_angle)
    box('FarmHouse | entry pilaster',p_local(side*1.25,0.15,1.62),(0.20,0.33,3.2),STONE_LIGHT,0.035,entry_angle)
    box('FarmHouse | portico column shaft',p_local(side*1.52,0.80,2.0),(0.38,0.38,4.0),WHITE,0.06,entry_angle)
    box('FarmHouse | portico column base',p_local(side*1.52,0.80,0.32),(0.55,0.55,0.60),STONE_LIGHT,0.07,entry_angle)
    box('FarmHouse | portico column capital',p_local(side*1.52,0.80,3.94),(0.54,0.54,0.35),WHITE,0.06,entry_angle)
box('FarmHouse | door transom glazing',p_local(0,0.08,2.80),(1.85,0.035,0.38),GLASS,0.01,entry_angle)
box('FarmHouse | entrance canopy soffit',p_local(0,1.15,4.30),(3.8,3.6,0.30),WHITE,0.06,entry_angle)
box('FarmHouse | entry pediment fascia',p_local(0,2.55,4.60),(4.2,0.24,0.44),WHITE,0.03,entry_angle)
face_poly('FarmHouse | white entry gable face', [p_local(-2.10,2.66,4.73),p_local(0,2.66,5.50),p_local(2.10,2.66,4.73)], WHITE)
face_poly('FarmHouse | white gable roof left', [p_local(-2.10,0.28,4.73),p_local(0,0.28,5.50),p_local(0,2.66,5.50),p_local(-2.10,2.66,4.73)], WHITE)
face_poly('FarmHouse | white gable roof right', [p_local(0,0.28,5.50),p_local(2.10,0.28,4.73),p_local(2.10,2.66,4.73),p_local(0,2.66,5.50)], WHITE)
box('FarmHouse | entrance step upper',p_local(0,2.0,0.08),(3.8,3.1,0.20),STONE_LIGHT,0.03,entry_angle)
box('FarmHouse | entrance step lower',p_local(0,2.4,-0.07),(4.6,3.8,0.18),STONE,0.03,entry_angle)
box('FarmHouse | porch address plaque backing',p_local(0,0.15,4.02),(0.60,0.08,0.34),STONE_LIGHT,0.02,entry_angle)
def text_mesh(name, body, size, location, rotation, mat):
    font=bpy.data.curves.new(name+' font','FONT')
    font.body=body; font.size=size; font.extrude=0.003; font.align_x='CENTER'; font.align_y='CENTER'
    ob=bpy.data.objects.new(name,font); collection.objects.link(ob)
    ob.location=location; ob.rotation_mode='QUATERNION'; ob.rotation_quaternion=rotation
    ob.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH')
    ob=bpy.context.object; ob.name=name; parts.append(ob)
    return ob
entry_text_rotation=Matrix(((tx,0,nx),(ty,0,ny),(0,1,0))).to_4x4().to_quaternion()
text_mesh('FarmHouse | entry address 1028','1028',0.24,p_local(0,0.205,4.02),entry_text_rotation,METAL)

# A long covered front porch is apparent in the project references. It runs
# along the south-facing hall rather than reading as a tiny freestanding hood.
porch_x0=minx+0.9
porch_x1=minx+22.0
porch_len=porch_x1-porch_x0
porch_cx=(porch_x0+porch_x1)/2
porch_y=miny-1.50
box('FarmHouse | covered porch stone walking surface',(porch_cx,porch_y,-0.06),(porch_len,3.10,0.16),STONE_LIGHT,0.025)
box('FarmHouse | long porch white soffit',(porch_cx,porch_y,3.72),(porch_len,3.10,0.24),WHITE,0.06)
box('FarmHouse | long porch shingle cap',(porch_cx,porch_y,3.90),(porch_len+0.25,3.30,0.16),ROOF,0.04)
box('FarmHouse | long porch outer fascia',(porch_cx,miny-3.10,3.71),(porch_len+0.20,0.20,0.44),WHITE,0.04)
box('FarmHouse | long porch end fascia west',(porch_x0,miny-1.50,3.71),(0.20,3.10,0.44),WHITE,0.04)
box('FarmHouse | long porch end fascia east',(porch_x1,miny-1.50,3.71),(0.20,3.10,0.44),WHITE,0.04)
post_count=7
for pi in range(post_count):
    px=porch_x0+1.2+pi*((porch_len-2.4)/(post_count-1))
    box('FarmHouse | porch brick column base',(px,miny-2.78,0.42),(0.72,0.72,0.84),BRICK,0.07)
    box('FarmHouse | porch limestone plinth',(px,miny-2.78,0.91),(0.76,0.76,0.18),STONE_LIGHT,0.035)
    box('FarmHouse | long porch white column',(px,miny-2.78,2.25),(0.42,0.42,2.58),WHITE,0.07)
    box('FarmHouse | long porch column capital',(px,miny-2.78,3.56),(0.65,0.65,0.28),WHITE,0.04)

# Readable house name on the clear upper south facade above the porch roof.
# The sign is intentionally modest and avoids the fourth-floor sash band.
sign_x=porch_cx
box('FarmHouse | facade name sign panel',(sign_x,miny-0.10,13.12),(4.5,0.16,0.58),STONE_LIGHT,0.04)
south_text_rotation=Matrix(((1,0,0),(0,0,-1),(0,1,0))).to_4x4().to_quaternion()
text_mesh('FarmHouse | readable name sign','FarmHouse',0.52,(sign_x,miny-0.20,13.20),south_text_rotation,METAL)
text_mesh('FarmHouse | sign chapter line','PURDUE CHAPTER',0.17,(sign_x,miny-0.205,12.98),south_text_rotation,METAL)

# Downspouts on prominent corners, roof valleys, vents, and a small roof hatch.
for vx,vy in (outline[0], outline[4], outline[9], outline[13]):
    box('FarmHouse | painted rain downspout',(vx,vy,(BASEMENT+EAVE)/2),(0.10,0.10,EAVE-BASEMENT),WHITE,0.025)
for x,y in ((cx-4,cy+7),(cx+5,cy+8),(cx+7,cy-4)):
    box('FarmHouse | roof vent cap',(x,y,16.65),(0.8,0.65,0.7),METAL,0.08)

# Interior floor plates and a restrained, exposed room-plan interpretation.
# The architect describes entrance foyer, chapter/formal rooms, dining and
# kitchen, library/studies, suites and dormitory. These plates/partitions are
# intentionally visible only when the roof is removed; not a furnished survey.
for z in (-0.2, 3.25, 6.45, 9.65, 12.85):
    prism('FarmHouse | interior floor plate',outline,z,z+0.12,FLOOR)
# Long interior corridor partitions and selected room dividers, set inside the
# envelope and away from major facades. No unsupported furniture is implied.
for level in (-1.12,0.35,3.55,6.75,9.95):
    z0=level; h=1.75 if level<0 else 2.62; z1=level+h
    # Central north-south corridor, west/east cross walls
    box('FarmHouse | corridor partition',(cx,cy,z0+h/2),(0.16,maxy-miny-5.0,h),INT_WALL,0.02)
    for yy in (cy-7.4, cy+5.6):
        box('FarmHouse | room divider',(cx,yy,z0+h/2),(maxx-minx-6.0,0.14,h),INT_WALL,0.02)
    # Door gaps represented by dark framed openings on selected floor partitions
    for yy in (cy-7.4,cy+5.6):
        box('FarmHouse | interior doorway lintel',(cx,yy,z0+h-0.40),(1.20,0.18,0.18),STONE)

# Interior lobby elevator core, reception/dining counter, chapter-room table.
box('FarmHouse | elevator core',(cx-3.8,cy+1.0,7.0),(2.4,2.0,13.4),INT_WALL,0.04)
box('FarmHouse | elevator door',(cx-2.57,cy+1.0,1.65),(0.08,1.2,2.4),METAL,0.02)
box('FarmHouse | dining serving counter',(cx+5,cy-6,1.1),(6.0,0.85,0.85),WOOD,0.04)
box('FarmHouse | chapter room table',(cx+4,cy+6.0,0.95),(5.2,1.4,0.22),WOOD,0.04)

# One expected asset object, with material slots retained. Joining produces a
# compact linked library while preserving the one-object manifest contract.
bpy.ops.object.select_all(action='DESELECT')
for ob in parts: ob.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
asset = bpy.context.object
asset.name = 'FarmHouse Fraternity, Purdue Chapter'
asset.data.name = 'FarmHouse detailed architectural shell and components'
for slot_i, slot_mat in enumerate(asset.data.materials):
    if slot_mat is None:
        asset.data.materials[slot_i] = STONE_LIGHT
asset['building_id'] = ASSET_ID
asset['footprint_source'] = 'OpenStreetMap way 301923755; local campus transform'
asset['height_status'] = 'estimated from published four-story-over-basement program; not surveyed'
asset['interior_status'] = 'schematic architectural program layout; not a measured interior survey'

# Configure a useful saved camera and soft studio lighting for direct review.
def aim(obj, point): obj.rotation_euler = (Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('FarmHouse exterior review camera')
cam=bpy.data.objects.new('FarmHouse exterior review camera',cam_data); review_collection.objects.link(cam)
cam.location=(maxx+44,miny-51,34); aim(cam,(cx,cy,8.0)); cam_data.lens=54; scene.camera=cam
area_data=bpy.data.lights.new('Large softbox key','AREA'); area_data.energy=12500; area_data.shape='DISK'; area_data.size=38
area=bpy.data.objects.new('Large softbox key',area_data); review_collection.objects.link(area); area.location=(cx-16,cy-20,35); aim(area,(cx,cy,7))
fill_data=bpy.data.lights.new('Sky fill','AREA'); fill_data.energy=5500; fill_data.size=45
fill=bpy.data.objects.new('Sky fill',fill_data); review_collection.objects.link(fill); fill.location=(cx+22,cy+18,24); aim(fill,(cx,cy,7))
world = bpy.data.worlds.new('FarmHouse review studio world')
world.use_nodes = True
world.color=(0.20,0.25,0.34)
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.20,0.25,0.34,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.45
scene.world=world
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.render.resolution_x=1400; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
render_path=os.path.join(EVIDENCE_DIR,'farmhouse_fraternity_exterior_review.png')
scene.render.filepath=render_path

# Disable camera and light from asset geometry count while retaining a scene
# that opens ready to preview. Keep them in the named collection by design.
os.makedirs(EVIDENCE_DIR,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
bpy.ops.render.render(write_still=True)

# Additional evidence views make the entry sign/column rhythm and intersecting
# roof wings legible without changing the saved overview camera.
main_cam_location=cam.location.copy()
main_cam_rotation=cam.rotation_euler.copy()
main_lens=cam_data.lens
main_res=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)
scene.cycles.samples=12
scene.render.resolution_x=1000; scene.render.resolution_y=760; scene.render.resolution_percentage=85
cam.location=(maxx+25,miny-31,11.5); aim(cam,(porch_cx,miny-0.4,7.0)); cam_data.lens=68
scene.render.filepath=os.path.join(EVIDENCE_DIR,'farmhouse_entry_porch_sign_review.png')
bpy.ops.render.render(write_still=True)
scene.render.resolution_x=900; scene.render.resolution_y=900
cam.location=(cx,cy,75); aim(cam,(cx,cy,0)); cam_data.lens=58
scene.render.filepath=os.path.join(EVIDENCE_DIR,'farmhouse_intersecting_roofs_plan_review.png')
bpy.ops.render.render(write_still=True)
cam.location=main_cam_location; cam.rotation_euler=main_cam_rotation; cam_data.lens=main_lens
scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=main_res
scene.cycles.samples=24; scene.render.filepath=render_path

def polygon_area(poly): return abs(signed_area(poly))
lengths=[math.dist(outline[i],outline[(i+1)%len(outline)]) for i in range(len(outline))]
world_verts=[asset.matrix_world @ v.co for v in asset.data.vertices]
asset_bounds_xyz=[[min(v[i] for v in world_verts),max(v[i] for v in world_verts)] for i in range(3)]
roof_pitches=[
    round(math.degrees(math.atan((19.15-EAVE)/((17.0-0.8)/2))),1),
    round(math.degrees(math.atan((17.95-EAVE)/((10.5-0.4)/2))),1),
    round(math.degrees(math.atan((18.30-EAVE)/(((maxx-0.45)-(maxx-11.8))/2))),1),
    round(math.degrees(math.atan((17.35-EAVE)/(((minx+16.4)-(minx+10.1))/2))),1)
]
with open(os.path.join(EVIDENCE_DIR,'evidence.json'),'w',encoding='utf-8') as f:
    gis_file=os.path.join(EVIDENCE_DIR,'sources','tippecanoe_buildings_feature_778_2026-10-26.json')
    with open(gis_file,'r',encoding='utf-8') as gf: gis_feature=json.load(gf)['feature']
    gis_ring=gis_feature['geometry']['rings'][0][:-1]
    gis_xy=[]
    for gx,gy in gis_ring:
        glon=math.degrees(gx/6378137.0)
        glat=math.degrees(2*math.atan(math.exp(gy/6378137.0))-math.pi/2)
        gis_xy.append(((glon-LON0)*111412.84*math.cos(math.radians(LAT0)),(glat-LAT0)*111040.0))
    gis_bounds=[min(p[0] for p in gis_xy),min(p[1] for p in gis_xy),max(p[0] for p in gis_xy),max(p[1] for p in gis_xy)]
    osm_bounds=[minx,miny,maxx,maxy]
    ix=max(0,min(maxx,gis_bounds[2])-max(minx,gis_bounds[0]))
    iy=max(0,min(maxy,gis_bounds[3])-max(miny,gis_bounds[1]))
    aabb_iou=(ix*iy)/((maxx-minx)*(maxy-miny)+(gis_bounds[2]-gis_bounds[0])*(gis_bounds[3]-gis_bounds[1])-ix*iy)
    osm_center=((minx+maxx)/2,(miny+maxy)/2)
    gis_center=((gis_bounds[0]+gis_bounds[2])/2,(gis_bounds[1]+gis_bounds[3])/2)
    gis_area=abs(sum(gis_xy[i][0]*gis_xy[(i+1)%len(gis_xy)][1]-gis_xy[(i+1)%len(gis_xy)][0]*gis_xy[i][1] for i in range(len(gis_xy)))*0.5)
    json.dump({
      'building_id': ASSET_ID,
      'asset_path': 'modular/buildings/'+ASSET_ID+'.blend',
      'retrieved_on': '2026-10-26',
      'sources': [
        {'provider':'OpenStreetMap / Overpass','url':'https://overpass-api.de/api/interpreter','feature':'way 301923755, name=FarmHouse Fraternity, Purdue Chapter; addr 1028 State Street','snapshot':'audit/farmhouse_fraternity_purdue_chapter/sources/overpass_buildings_near_farmhouse_2026-10-26.json','source_date':'OSM base timestamp '+osm['osm3s']['timestamp_osm_base'],'crs':'WGS84 EPSG:4326','method':'OSM polygon vertices converted to campus local XY using project approximation','uncertainty':'crowdsourced outline; source is building-tagged but not a survey'},
        {'provider':'Purdue University GIS / Tippecanoe County ArcGIS','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D778&outFields=*&returnGeometry=true&f=pjson','feature':'FID 778, BLDG_ABBR SOFH, BUILDING_N Farmhouse','snapshot':'audit/farmhouse_fraternity_purdue_chapter/sources/tippecanoe_buildings_feature_778_2026-10-26.json','source_date':'not exposed in feature attributes','crs':'EPSG:3857 Web Mercator (inferred from coordinate magnitude and service)','method':'converted ring vertices from Web Mercator to WGS84, then project campus-local XY','uncertainty':'conflicting footprint with different orientation and extent from OSM; evidence does not establish which outline is current or authoritative'},
        {'provider':'KJG Architecture','url':'https://www.kjgarchitecture.com/portfolio-1/farmhouse-fraternity','feature':'FarmHouse Fraternity Purdue project page','source_date':'2016 project as stated on page','snapshot':'audit/farmhouse_fraternity_purdue_chapter/sources/kjg_farmhouse_1.jpg; kjg_farmhouse_2.jpg; kjg_farmhouse_3.jpg; kjg_farmhouse_4.jpg','crs':'not applicable','method':'visual facade/roof/interior-form reference; four stories above basement per project description','uncertainty':'photos are architectural project imagery, not dimensioned elevations'},
        {'provider':'Shiel Sexton','url':'https://www.shielsexton.com/project/purdue-university-projects','feature':'Purdue FarmHouse new construction project','source_date':'not shown','snapshot':'web page only','crs':'not applicable','method':'published facility area and four-story / 56-bed program description','uncertainty':'project page gives gross floor area, not geodetic footprint'},
        {'provider':'FarmHouse Fraternity Purdue Chapter','url':'https://www.purduefarmhousefraternity.com/','feature':'Official chapter site and address/contact page','source_date':'not shown','snapshot':'audit/farmhouse_fraternity_purdue_chapter/sources/purdue_farmhouse_aerial.jpg; purdue_farmhouse_front.jpg','crs':'not applicable','method':'identity/address and visual entrance/brick/roof corroboration','uncertainty':'website photography is not dimensioned'}
      ],
      'geometry': {'footprint_vertex_count':len(outline),'area_m2_from_osm':polygon_area(outline),'structural_footprint_bounds_xy_m':[minx,miny,maxx,maxy],'structural_footprint_width_depth_m':[maxx-minx,maxy-miny],'asset_geometry_bounds_xyz_m':asset_bounds_xyz,'above_grade_window_rows':len(floors),'roof_ridge_heights_m':[19.15,17.95,18.30,17.35],'roof_pitch_estimates_degrees':roof_pitches,'vertical_bounds_m':asset_bounds_xyz[2],'height_status':'estimated from published four-story-over-basement program and project imagery; no measured elevation found','asset_bounds_note':'Overall mesh bounds include porch columns, projecting canopies, roof eaves, and entrance steps; use the OSM structural footprint bounds for wall-plan comparison.'},
      'comparison': {'osm_bounds_xy_m':osm_bounds,'tippecanoe_fid_778_bounds_xy_m':gis_bounds,'tippecanoe_polygon_area_m2':gis_area,'osm_aabb_iou_vs_tippecanoe':aabb_iou,'bbox_center_offset_m':math.dist(osm_center,gis_center),'original_massing_mesh_dimensions_m':[27.674,38.986,16.0],'original_manifest_bounds_xy_m':[-506.4974060059,-478.8236999512,-338.8829650879,-299.8968200684],'finding':'OSM bounds align with the original massing placement and its 27.674 x 38.986 m dimensions within rounding; Purdue GIS FID 778 is about 29.90 x 21.85 m, with 0.536 axis-aligned bbox IoU. This conflict remains unresolved: no source establishes which footprint is current or authoritative; an as-built survey or stronger dated source is needed.'},
      'model_edits':['Replaced cuboid mass with the named OSM outline and a separate basement plinth / four above-grade story brick shell','Reduced facade fenestration from five rows to four above-grade window rows; added limestone sills/jambs, story bands, quoin blocks, and divided-light sash','Replaced the broad shallow roof with four steep intersecting gabled wing roofs, based on KJG and Purdue photo references; ridge/valley geometry is estimated','Added a long white columned south porch with ground-connected supports and stone walking surface, plus a separate white gabled corner entrance portico, oak double entry, address plaque, and readable FarmHouse / Purdue Chapter sign','Added schematic basement and four-level floor plates, corridor/room partitions, elevator core, dining counter, chapter table','Added procedural running-bond brick UVs, stone, roof, glass, plaster, wood, and metal materials','Saved full exterior, porch/name-sign close, and roof-plan review renders']
    },f,indent=2)

print('BUILT',ASSET_PATH)
print('OUTLINE_BOUNDS',minx,miny,maxx,maxy,'AREA',polygon_area(outline),'HEIGHT',BASEMENT,RIDGE)
print('ASSET_COLLECTION_OBJECTS',len(collection.objects),'SCENE_OBJECTS',len(bpy.data.objects),'MATERIALS',len(bpy.data.materials),'MESH_VERTS',len(asset.data.vertices),'FACES',len(asset.data.polygons))
