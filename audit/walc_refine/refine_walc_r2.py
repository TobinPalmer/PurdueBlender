import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular/buildings/walc.blend'
OUT = ROOT / 'audit/walc_refine'
asset = bpy.data.collections['Asset_walc']

# Make the existing linked foliage library portable from this asset file.
foliage = next((lib for lib in bpy.data.libraries if 'engineering_foliage_library.blend' in lib.filepath), None)
if foliage:
    foliage.filepath = '//../site/foliage_library/engineering_foliage_library.blend'

def principled(mat):
    if not mat.use_nodes:
        mat.use_nodes = True
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def setup_masonry(name, kind, base_color, roughness, bump_strength, bump_distance):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*base_color, 1)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = roughness
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tex = nt.nodes.new('ShaderNodeTexCoord')
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3.0 if kind == 'brick' else 6.0
    noise.inputs['Detail'].default_value = 3.0
    noise.inputs['Roughness'].default_value = 0.72
    nt.links.new(tex.outputs['Object'], noise.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    if kind == 'brick':
        dark = (base_color[0]*0.64, base_color[1]*0.60, base_color[2]*0.58, 1)
        light = (min(1,base_color[0]*1.20), min(1,base_color[1]*1.18), min(1,base_color[2]*1.13), 1)
    else:
        dark = (base_color[0]*0.82, base_color[1]*0.82, base_color[2]*0.80, 1)
        light = (min(1,base_color[0]*1.10), min(1,base_color[1]*1.10), min(1,base_color[2]*1.09), 1)
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = dark
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = light
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = bump_strength
    bump.inputs['Distance'].default_value = bump_distance
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

brick = setup_masonry('WALC_Reference_Brick', 'brick', (0.30,0.075,0.043), 0.86, 0.18, 0.035)
limestone = setup_masonry('WALC_Reference_Limestone', 'stone', (0.67,0.64,0.56), 0.82, 0.10, 0.018)
glass = bpy.data.materials.get('WALC_Reference_Glass')
if glass:
    bsdf = principled(glass)
    bsdf.inputs['Base Color'].default_value = (0.075, 0.13, 0.16, 1)
    bsdf.inputs['Roughness'].default_value = 0.23
    bsdf.inputs['Metallic'].default_value = 0.24
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.22

# A modest glazed facade bay rhythm: thin, slightly proud bronze fins at
# roughly 3.2 m intervals on longer glass spans. Source wall meshes/footprint
# and their elevations are left untouched; fin placement follows each segment.
bronze = bpy.data.materials.get('Bronze.009')
if bronze:
    b = principled(bronze)
    b.inputs['Base Color'].default_value = (0.095, 0.082, 0.060, 1)
    b.inputs['Metallic'].default_value = 0.78
    b.inputs['Roughness'].default_value = 0.34

verts=[]; faces=[]; generated=0
mesh_objs = [o for o in asset.all_objects if o.type == 'MESH' and o.name.startswith('WALC_Source906_Edge_') and '_Band' in o.name]
glass_spans = [o for o in mesh_objs if any(o.name.endswith('_Band'+str(n)) for n in (2,4,6))]
all_bounds = [o.matrix_world @ Vector(corner) for o in [bpy.data.objects.get('WALC_Source906_Edge_0_Band2')] if o for corner in o.bound_box]
# Estimate plan centroid robustly from all facade section centers.
centers=[]
for o in glass_spans:
    c=o.matrix_world.translation
    centers.append((c.x,c.y))
cx=sum(x for x,y in centers)/len(centers); cy=sum(y for x,y in centers)/len(centers)

def box(cx,cy,cz,sx,sy,sz):
    global generated
    base=len(verts)
    for x,y,z in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)):
        verts.append((cx+x*sx/2,cy+y*sy/2,cz+z*sz/2))
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(base+i for i in f))
    generated+=1

for o in glass_spans:
    corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
    xmin=min(p.x for p in corners); xmax=max(p.x for p in corners)
    ymin=min(p.y for p in corners); ymax=max(p.y for p in corners)
    zmin=min(p.z for p in corners); zmax=max(p.z for p in corners)
    dx=xmax-xmin; dy=ymax-ymin; length=max(dx,dy); thickness=min(dx,dy)
    if length < 4.5 or thickness > 0.65: continue
    along_x = dx > dy
    nfin=max(1, int(length/3.2)-1)
    for k in range(1,nfin+1):
        t=k/(nfin+1)
        if along_x:
            px=xmin+dx*t; py=(ymin+ymax)/2
            outward=1 if py>=cy else -1
            box(px,py+outward*(thickness/2+0.035),(zmin+zmax)/2,0.095,0.09,zmax-zmin-0.12)
        else:
            px=(xmin+xmax)/2; py=ymin+dy*t
            outward=1 if px>=cx else -1
            box(px+outward*(thickness/2+0.035),py,(zmin+zmax)/2,0.09,0.095,zmax-zmin-0.12)

if verts:
    me=bpy.data.meshes.new('WALC_Facade_Bay_Piers_R2_Mesh')
    me.from_pydata(verts, [], faces); me.update()
    obj=bpy.data.objects.new('WALC_Facade_Bay_Piers_R2', me)
    obj['evidence_note']='Subtle bronze facade fins subdivide long glazed spans; approximate 3.2 m rhythm, not a measured as-built bay schedule.'
    asset.objects.link(obj)
    if bronze: obj.data.materials.append(bronze)

# Keep requested asset identity and local root transform unchanged.
root=bpy.data.objects.get('AssetRoot_walc')
if root:
    assert tuple(round(v,6) for v in root.location)==(0,0,0)
    assert tuple(round(v,6) for v in root.rotation_euler)==(0,0,0)
    assert tuple(round(v,6) for v in root.scale)==(1,1,1)

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET), compress=True)
print(json.dumps({'saved':str(ASSET),'fins':generated,'library_path':foliage.filepath if foliage else None,'materials':{m.name:len(m.node_tree.nodes) if m.use_nodes else 0 for m in (brick,limestone,glass) if m}}))
