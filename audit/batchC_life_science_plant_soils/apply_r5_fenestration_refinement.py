import bpy
from mathutils import Vector

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
ASSET = ROOT + r'\modular\buildings\life_science_plant_and_soils_laboratory.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)

collection = bpy.data.collections.get('LSPS_Facade')
assert collection is not None
old = bpy.data.objects.get('LSPS R5 | window frame and transom detail')
if old:
    bpy.data.objects.remove(old, do_unlink=True)

mat = bpy.data.materials.get('LSPS | charcoal anodized metal')
assert mat is not None
verts, faces = [], []

def add_box(center, size):
    cx, cy, cz = center
    sx, sy, sz = (v * 0.5 for v in size)
    b = len(verts)
    verts.extend([(cx-sx,cy-sy,cz-sz),(cx+sx,cy-sy,cz-sz),(cx+sx,cy+sy,cz-sz),(cx-sx,cy+sy,cz-sz),
                  (cx-sx,cy-sy,cz+sz),(cx+sx,cy-sy,cz+sz),(cx+sx,cy+sy,cz+sz),(cx-sx,cy+sy,cz+sz)])
    faces.extend([tuple(b+i for i in q) for q in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])

windows = [o for o in bpy.data.objects if o.type == 'MESH' and 'facade bay' in o.name and 'glazing' in o.name]
assert len(windows) > 0, 'No facade glazing found'
for o in windows:
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = [min(p[i] for p in corners) for i in range(3)]
    hi = [max(p[i] for p in corners) for i in range(3)]
    dims = [hi[i]-lo[i] for i in range(3)]
    normal_axis = 0 if dims[0] < dims[1] else 1
    width_axis = 1-normal_axis
    inward = -1 if (lo[normal_axis]+hi[normal_axis])*0.5 > 0 else 1
    depth_center = (lo[normal_axis]+hi[normal_axis])*0.5 - inward*0.055
    depth = min(0.070, dims[normal_axis]*0.85)
    width = dims[width_axis]
    height = dims[2]
    edge = min(0.055, width*0.045, height*0.04)
    zc = (lo[2]+hi[2])*0.5
    wc = (lo[width_axis]+hi[width_axis])*0.5
    # Slim dark frame edges are kept within the existing glazing depth to avoid
    # expanding the GIS footprint. One horizontal transom divides each pane.
    for z in (lo[2]+edge/2, hi[2]-edge/2):
        c=[0.0,0.0,z]; s=[0.0,0.0,edge]
        c[normal_axis]=depth_center; c[width_axis]=wc
        s[normal_axis]=depth; s[width_axis]=width
        add_box(c,s)
    for w in (lo[width_axis]+edge/2, hi[width_axis]-edge/2):
        c=[0.0,0.0,zc]; s=[0.0,0.0,height]
        c[normal_axis]=depth_center; c[width_axis]=w
        s[normal_axis]=depth; s[width_axis]=edge
        add_box(c,s)
    # A narrow mid-height rail is a restrained, generic window detail.
    c=[0.0,0.0,zc]; s=[0.0,0.0,edge*0.72]
    c[normal_axis]=depth_center; c[width_axis]=wc
    s[normal_axis]=depth; s[width_axis]=width-edge*1.5
    add_box(c,s)

mesh=bpy.data.meshes.new('LSPS R5 | window frame detail mesh')
mesh.from_pydata(verts, [], faces); mesh.materials.append(mat); mesh.update()
obj=bpy.data.objects.new('LSPS R5 | window frame and transom detail', mesh)
collection.objects.link(obj)
obj['evidence_status']='Schematic shallow frame and transom detail over existing glazing; 2019 Street View only supports qualitative glazing/material cues, not measured frame profiles or spacing.'
obj['source_basis']='Existing LSPS facade glazing bays; generic dark anodized framing added for depth/readability. No unsupported facade dimensions are asserted.'
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(f'R5 saved: {len(windows)} facade glazing panels, {len(faces)//6} frame primitives, one combined mesh object')

