"""WALC R3: improve legibility and surface treatment without changing the massing."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular/buildings/walc.blend'
EXPECTED = '66e77776b04dd142c8a1292ff2f297c5a4b3a9b3f676ff62243bf81376714850'
actual = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if actual != EXPECTED:
    raise RuntimeError(f'WALC changed since R2 assignment: {actual}')

asset = bpy.data.collections['Asset_walc']
assert bpy.data.scenes.get('Building_walc') and bpy.data.objects.get('AssetRoot_walc')

def principled(mat):
    return next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if mat.use_nodes else None

# Workbench and material-preview colors are kept in sync with the existing PBR
# node graphs so the architectural hierarchy is legible in the project's normal views.
colors = {
    'WALC_Reference_Brick': (0.48, 0.185, 0.115, 1.0),
    'WALC_Reference_Limestone': (0.72, 0.69, 0.61, 1.0),
    'WALC_Reference_Glass': (0.30, 0.43, 0.49, 1.0),
    'WALC_Reference_Roof': (0.31, 0.34, 0.37, 1.0),
    'Bronze.009': (0.52, 0.34, 0.16, 1.0),
    'Tile.009': (0.55, 0.55, 0.51, 1.0),
    'Limestone.009': (0.69, 0.66, 0.59, 1.0),
}
for name, color in colors.items():
    mat = bpy.data.materials.get(name)
    if not mat: continue
    mat.diffuse_color = color

brick = bpy.data.materials['WALC_Reference_Brick']
brick_bsdf = principled(brick)
if brick_bsdf:
    # Use a regular, subdued running-bond pattern, keeping the noisy bump already
    # in the material for slight surface variation. Brick dimensions are visual
    # texture parameters and are not a measured masonry schedule.
    nt = brick.node_tree
    texcoord = next((n for n in nt.nodes if n.type == 'TEX_COORD'), None)
    bsdf_input = brick_bsdf.inputs.get('Base Color')
    if texcoord and bsdf_input:
        tex = next((n for n in nt.nodes if n.type == 'TEX_BRICK'), None)
        if tex is None:
            tex = nt.nodes.new('ShaderNodeTexBrick')
        tex.inputs['Color1'].default_value = (0.48, 0.175, 0.11, 1)
        tex.inputs['Color2'].default_value = (0.34, 0.105, 0.068, 1)
        tex.inputs['Mortar'].default_value = (0.22, 0.175, 0.14, 1)
        tex.inputs['Scale'].default_value = 1.0
        tex.inputs['Brick Width'].default_value = 0.48
        tex.inputs['Row Height'].default_value = 0.115
        tex.inputs['Mortar Size'].default_value = 0.025
        tex.inputs['Mortar Smooth'].default_value = 0.08
        nt.links.new(texcoord.outputs['Object'], tex.inputs['Vector'])
        nt.links.new(tex.outputs['Color'], bsdf_input)

glass = bpy.data.materials['WALC_Reference_Glass']
g = principled(glass)
if g:
    g.inputs['Base Color'].default_value = (0.12, 0.22, 0.28, 1.0)
    g.inputs['Roughness'].default_value = 0.19
    g.inputs['Metallic'].default_value = 0.12
    if 'Coat Weight' in g.inputs: g.inputs['Coat Weight'].default_value = 0.3

bronze = bpy.data.materials.get('Bronze.009')
b = principled(bronze) if bronze else None
if b:
    b.inputs['Base Color'].default_value = (0.24, 0.13, 0.055, 1)
    b.inputs['Metallic'].default_value = 0.68
    b.inputs['Roughness'].default_value = 0.34

# Regenerate the prior bay-fin mesh with slightly deeper, more visible mullion
# blades on the long glazed runs. This follows each source wall section and
# keeps the source footprint/roof/coordinate frame untouched. Approximate spacing
# is for visual articulation only; no architectural bay schedule was found.
old = bpy.data.objects.get('WALC_Facade_Bay_Piers_R2')
if old:
    bpy.data.objects.remove(old, do_unlink=True)
for name in ('WALC_Facade_Bay_Piers_R3', 'WALC_Facade_Bay_Piers_R3_Mesh'):
    datablock = bpy.data.meshes.get(name)
    if datablock: bpy.data.meshes.remove(datablock)

glass_spans = [o for o in asset.all_objects if o.type == 'MESH' and o.name.startswith('WALC_Source906_Edge_') and any(o.name.endswith(f'_Band{k}') for k in (2,4,6))]
centers = [(o.matrix_world.translation.x, o.matrix_world.translation.y) for o in glass_spans]
cx = sum(x for x, y in centers) / len(centers)
cy = sum(y for x, y in centers) / len(centers)
verts, faces, count = [], [], 0
def box(x,y,z,sx,sy,sz):
    base=len(verts)
    for a,c,d in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)):
        verts.append((x+a*sx/2,y+c*sy/2,z+d*sz/2))
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(base+i for i in f))

for o in glass_spans:
    corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
    xmin,xmax=min(p.x for p in corners),max(p.x for p in corners)
    ymin,ymax=min(p.y for p in corners),max(p.y for p in corners)
    zmin,zmax=min(p.z for p in corners),max(p.z for p in corners)
    dx,dy=xmax-xmin,ymax-ymin
    length=max(dx,dy); thickness=min(dx,dy)
    if length < 4.4 or thickness > 0.7: continue
    along_x=dx>dy
    n=max(1, int(length/2.8)-1)
    for k in range(1,n+1):
        t=k/(n+1)
        if along_x:
            px=xmin+dx*t; py=(ymin+ymax)/2
            outward=1 if py>=cy else -1
            box(px,py+outward*(thickness/2+0.055),(zmin+zmax)/2,0.14,0.12,zmax-zmin-0.16)
        else:
            px=(xmin+xmax)/2; py=ymin+dy*t
            outward=1 if px>=cx else -1
            box(px+outward*(thickness/2+0.055),py,(zmin+zmax)/2,0.12,0.14,zmax-zmin-0.16)
        count+=1

mesh=bpy.data.meshes.new('WALC_Facade_Bay_Piers_R3_Mesh')
mesh.from_pydata(verts, [], faces); mesh.update()
obj=bpy.data.objects.new('WALC_Facade_Bay_Piers_R3', mesh)
obj['evidence_note']='Approximate vertical facade-bay articulation on existing glazed wall runs; official exterior imagery supports tall rectangular window rhythm, but exact mullion dimensions/spacing are unverified.'
asset.objects.link(obj)
obj.data.materials.append(bronze)

# Retain and normalize the relative foliage link used by the existing asset.
foliage=next((lib for lib in bpy.data.libraries if 'engineering_foliage_library.blend' in lib.filepath),None)
if foliage: foliage.filepath='//../site/foliage_library/engineering_foliage_library.blend'

root=bpy.data.objects['AssetRoot_walc']
assert tuple(round(v,6) for v in root.location)==(0,0,0)
assert tuple(round(v,6) for v in root.rotation_euler)==(0,0,0)
assert tuple(round(v,6) for v in root.scale)==(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET), compress=True)
print(json.dumps({'saved':str(ASSET),'new_fins':count,'glass_spans':len(glass_spans),'relative_foliage':foliage.filepath if foliage else None,'changed_viewport_colors':colors},indent=2))
