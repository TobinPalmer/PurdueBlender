import bpy, math, os, json
from mathutils import Vector
from mathutils import Matrix
asset=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=asset)
scene=bpy.context.scene
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
portico=bpy.data.collections['SC_Portico_and_Entrances']
interior=bpy.data.collections['SC_Interior_Shell']

def world_bounds(obj):
    pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return Vector(tuple(min(p[i] for p in pts) for i in range(3))), Vector(tuple(max(p[i] for p in pts) for i in range(3)))

def transform_mesh_world(obj, offset=(0,0,0), scale=(1,1,1), pivot=None):
    lo,hi=world_bounds(obj)
    ctr=pivot if pivot is not None else (lo+hi)*0.5
    inv=obj.matrix_world.inverted()
    for v in obj.data.vertices:
        p=obj.matrix_world @ v.co
        p=Vector((ctr.x+(p.x-ctr.x)*scale[0]+offset[0], ctr.y+(p.y-ctr.y)*scale[1]+offset[1], ctr.z+(p.z-ctr.z)*scale[2]+offset[2]))
        v.co=inv @ p
    obj.data.update()

def mesh_from_box(name, bounds, material, collection):
    x0,y0,z0=bounds[0]; x1,y1,z1=bounds[1]
    verts=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+'_Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    obj=bpy.data.objects.new(name,mesh); collection.objects.link(obj); obj.parent=root
    return obj

def replace_with_boxes(obj, boxes, material):
    verts=[]; faces=[]
    for ((x0,y0,z0),(x1,y1,z1)) in boxes:
        base=len(verts)
        verts += [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
        faces += [tuple(base+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
    mesh=bpy.data.meshes.new(obj.name+'_RebuiltMesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    old=obj.data; obj.data=mesh
    if old.users==0: bpy.data.meshes.remove(old)

def mat(name): return bpy.data.materials[name]

# Scale the entry stairs to a photo-supported width and depth.
for o in list(portico.objects):
    if o.name.startswith('SC_Portico_Step_'):
        transform_mesh_world(o, scale=(0.68,0.55,1.0), pivot=Vector((27.8,-3.95,0)))
    elif o.name.startswith('SC_Portico_Balustrade_'):
        transform_mesh_world(o, scale=(0.68,0.55,1.0), pivot=Vector((27.8,-3.95,0)))
    elif o.name.startswith('SC_Portico_Pedestal_'):
        transform_mesh_world(o, scale=(0.68,0.55,1.0), pivot=Vector((27.8,-3.95,0)))

# Keep two columns, move them close to the door and shorten to match the photographed entrance.
for idx, dy in [(0,2.65),(3,-2.75)]:
    for part in ('Plinth','Shaft','Capital'):
        o=bpy.data.objects.get(f'SC_Portico_Column_{part}_{idx}')
        if o:
            zoff=0.0 if part=='Plinth' else (-0.85 if part=='Shaft' else -1.05)
            zscale=0.84 if part=='Shaft' else 1.0
            transform_mesh_world(o,offset=(-1.05,dy,zoff),scale=(1.0,1.0,zscale))
# Remove unsupported extra column pair.
for idx in (1,2):
    for part in ('Plinth','Shaft','Capital'):
        o=bpy.data.objects.get(f'SC_Portico_Column_{part}_{idx}')
        if o: bpy.data.objects.remove(o,do_unlink=True)

# Replace oversized free-standing arch and triangular pediment with a simple portal surround and lintel.
for nm in ('SC_Portico_Molded_Arch','SC_Portico_Arch_Keystone'):
    o=bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o,do_unlink=True)
ped=bpy.data.objects.get('SC_Portico_Classical_Pediment')
if ped:
    bpy.data.objects.remove(ped,do_unlink=True)
# Shallow limestone frame around the doors and transom (dimensions estimated from current Purdue exterior photo).
portal_boxes=[
 ((28.00,-6.85,1.95),(28.38,-6.25,7.65)),
 ((28.00,-1.65,1.95),(28.38,-1.05,7.65)),
 ((28.00,-6.85,7.05),(28.50,-1.05,7.70)),
]
mesh_from_box('SC_Portico_Rectangular_Stone_Portal_Surround',portal_boxes[0],mat('Bedford_Indiana_Limestone'),portico)
# Consolidate remaining two frame bars into one named object after the side jamb object above.
surround=bpy.data.objects['SC_Portico_Rectangular_Stone_Portal_Surround']
replace_with_boxes(surround,portal_boxes,mat('Bedford_Indiana_Limestone'))
# Replace the heavy projection with a narrow flat lintel over the two columns.
ent=bpy.data.objects.get('SC_Portico_Entablature')
if ent:
    replace_with_boxes(ent,[((28.15,-6.65,7.10),(30.65,-1.25,7.75))],mat('Bedford_Indiana_Limestone'))
# A modest roof/cap instead of a deep classical pediment.
canopy=mesh_from_box('SC_Portico_Flat_Stone_Canopy',((28.05,-6.9,7.72),(30.95,-1.0,8.02)),mat('Bedford_Indiana_Limestone'),portico)
# Reduce the existing fanlight to a transom band immediately above the doors.
for nm in ('SC_Main_Fanlight_Glass','SC_Main_Fanlight_Bronze_Frame'):
    o=bpy.data.objects.get(nm)
    if o: transform_mesh_world(o,scale=(0.8,0.64,0.48),pivot=Vector((27.845,-4.01,6.025)))
# Keep lettering on the front of the smaller lintel, and lower it.
text=bpy.data.objects.get('SC_Portico_3D_Text')
if text:
    mw=text.matrix_world.copy(); mw.translation += Vector((-1.15,0,-1.1)); text.matrix_world=mw
# Make the door leaves read as modern glazed entrance; current photo shows glass doors, not wood panels.
for nm in ('SC_Main_Door_Left','SC_Main_Door_Right'):
    o=bpy.data.objects.get(nm)
    if o and o.type=='MESH':
        o.data.materials.clear(); o.data.materials.append(mat('Dark_Bronze_Framing'))
# Broaden existing panes vertically within the double-leaf doors.
for nm in ('SC_Main_Door_Glass_L','SC_Main_Door_Glass_R'):
    o=bpy.data.objects.get(nm)
    if o:
        transform_mesh_world(o,scale=(1.0,1.0,1.65),pivot=Vector((27.98,-4.0,3.75)))
# Warm the stone and paving, whose previous light grey read as untextured white in review renders.
for mn, color in [('Bedford_Indiana_Limestone',(0.69,0.59,0.46,1)),('Limestone_WaterTable_Cap',(0.69,0.59,0.46,1)),('Paving_Concrete',(0.42,0.40,0.36,1))]:
    m=bpy.data.materials.get(mn)
    if m:
        m.diffuse_color=color
        if m.use_nodes:
            bsdf=m.node_tree.nodes.get('Principled BSDF')
            if bsdf: bsdf.inputs['Base Color'].default_value=color

# Add schematic, evidence-labeled student hub and work/research fit-out.
# Purdue's 2025 account supports these room functions; exact locations/layout remain unverified.
mat_wood=mat('Historic_Oak_Door'); mat_floor=mat('Polished_Terrazzo'); mat_metal=mat('Dark_Bronze_Framing'); mat_lime=mat('Bedford_Indiana_Limestone')
# Create neutral interior materials with warm wood and textile accents.
def simple_mat(name, color, rough=0.75):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=color; m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs: bs.inputs['Base Color'].default_value=color; bs.inputs['Roughness'].default_value=rough
    return m
wood=simple_mat('SC_Interior_Maple_Wood',(0.34,0.19,0.095,1))
seat=simple_mat('SC_Interior_Deep_Red_Upholstery',(0.30,0.055,0.038,1))
metal=simple_mat('SC_Interior_Dark_Metal',(0.10,0.12,0.13,1))
white=simple_mat('SC_Interior_Light_Panel',(0.74,0.72,0.66,1))

def cube(name, center, dims, material, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o=bpy.context.object; o.name=name
    o.dimensions=dims; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for m in list(o.data.materials): o.data.materials.clear()
    o.data.materials.append(material)
    for c in list(o.users_collection): c.objects.unlink(o)
    interior.objects.link(o); o.parent=root
    if bevel>0:
        mod=o.modifiers.new('Soft furniture edges','BEVEL'); mod.width=bevel; mod.segments=2
        mod2=o.modifiers.new('Weighted furniture normals','WEIGHTED_NORMAL')
    return o

def chair(prefix,x,y,z):
    cube(prefix+'_Seat',(x,y,z+0.48),(0.52,0.52,0.12),seat,0.05)
    cube(prefix+'_Back',(x,y+0.23,z+0.82),(0.52,0.10,0.62),seat,0.05)
    for dx in (-0.20,0.20):
      for dy in (-0.20,0.20): cube(prefix+f'_Leg_{dx}_{dy}',(x+dx,y+dy,z+0.23),(0.055,0.055,0.48),metal,0.015)
# Two shared study tables, eight seats and table task lamps in the ground-floor graduate hub zone.
for ti, (cx,cy) in enumerate([(22.8,-9.3),(22.8,-4.9)]):
    cube(f'SC_GradHub_CommunalTable_{ti}',(cx,cy,2.60),(3.1,1.15,0.12),wood,0.06)
    for dx in (-1.32,1.32): cube(f'SC_GradHub_TableLeg_{ti}_{dx}',(cx+dx,cy,2.20),(0.10,0.95,0.80),metal,0.025)
    for sx in (-0.9,0.9):
        chair(f'SC_GradHub_Chair_{ti}_N_{sx}',cx+sx,cy+0.85,1.84)
        chair(f'SC_GradHub_Chair_{ti}_S_{sx}',cx+sx,cy-0.85,1.84)
# Quiet seating nook and bookcases along the inside wall.
cube('SC_GradHub_Lounge_Bench_Base',(20.1,-4.1,2.15),(2.0,0.72,0.48),seat,0.10)
cube('SC_GradHub_Lounge_Bench_Back',(20.1,-3.8,2.68),(2.0,0.18,0.72),seat,0.08)
cube('SC_GradHub_CoffeeTable',(20.1,-5.2,2.35),(1.0,0.65,0.10),wood,0.05)
for i in range(3):
    cube(f'SC_GradHub_Bookcase_{i}',(18.65,-10.7+i*2.1,2.75),(0.32,1.75,1.75),wood,0.03)
    for z in (2.35,2.75,3.15): cube(f'SC_GradHub_Bookshelf_{i}_{z}',(18.45,-10.7+i*2.1,z),(0.10,1.75,0.06),white,0.015)
# A separate schematic work/research bay on the next level.
for ti,(cx,cy) in enumerate([(-7.0,5.0),(-1.5,5.0)]):
    cube(f'SC_ResearchBench_{ti}',(cx,cy,6.25),(3.7,0.90,0.10),white,0.03)
    cube(f'SC_ResearchBench_Cabinet_{ti}',(cx,cy,5.85),(3.5,0.75,0.70),wood,0.03)
    for stool_i,dx in enumerate((-1.0,0.0,1.0)):
        cube(f'SC_ResearchStool_{ti}_{stool_i}_seat',(cx+dx,cy+0.8,6.05),(0.42,0.42,0.12),seat,0.05)
        cube(f'SC_ResearchStool_{ti}_{stool_i}_stem',(cx+dx,cy+0.8,5.82),(0.07,0.07,0.38),metal,0.02)
# Archive the evidence and attribution in scene custom properties.
scene['SC interior note']='Schematic furnishings only. Purdue describes graduate student hub, English office, research labs (2025); room-by-room current plan and exact furniture positions unverified.'
scene['SC exterior note']='Entry shape revised from direct Purdue CLA exterior photo; massing, dimensions and roof height remain estimated.'
scene['SC historical plan note']='2022 Board of Trustees renovation plan is historical project scope, not proof of current room layout.'
# Save the library. Do not alter master or manifest.
bpy.ops.wm.save_as_mainfile(filepath=asset)
print('SAVED',asset,'asset_objects',len(bpy.data.collections['Asset_stanley_coulter_hall'].all_objects),'root_transform',list(root.location),list(root.rotation_euler),list(root.scale))
