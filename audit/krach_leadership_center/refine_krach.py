import bpy, math, json, os
from mathutils import Vector

src = bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend'), src
asset_col = bpy.data.collections.get('Asset_krach_leadership_center')
assert asset_col is not None
structure = bpy.data.collections.get('Schematic_Interior')
if structure is None:
    structure=bpy.data.collections.new('Schematic_Interior'); bpy.context.scene.collection.children.link(structure)

def cleanup(prefixes):
    for o in list(bpy.data.objects):
        if any(o.name.startswith(p) for p in prefixes): bpy.data.objects.remove(o, do_unlink=True)
cleanup(['KRCH documented fourth-floor slab','KRCH open stair |','KRCH etched lobby rail |','KRCH stair landing |'])

# Procedural, packed-independent materials: no external file dependencies.
def mat(name, color, rough=0.55, metallic=0.0, alpha=1.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,alpha); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(*color,alpha)
        bs.inputs['Roughness'].default_value=rough
        bs.inputs['Metallic'].default_value=metallic
        if 'Alpha' in bs.inputs: bs.inputs['Alpha'].default_value=alpha
    if alpha < 1:
        m.surface_render_method='DITHERED'
    return m

floor_mat=mat('KRCH | documented upper-floor terrazzo (schematic)',(0.48,0.45,0.39),0.73)
tread_mat=mat('KRCH | lobby stair cast stone', (0.57,0.55,0.49),0.62)
rail_mat=mat('KRCH | etched laminated lobby glass', (0.60,0.72,0.73),0.28,0.02,0.42)
metal_mat=mat('KRCH | satin dark stair handrail', (0.12,0.15,0.16),0.3,0.72)

# The official emergency plan enumerates basement through fourth floor. Existing floor plates
# stopped at level 3; add the missing level 4 at the established 3.90 m story rhythm.
shell=bpy.data.objects.get('KRCH structural shell | GIS outline')
assert shell is not None
# Reuse the ordered GIS base ring exactly; do not duplicate the extruded shell upward.
base_poly=next(p for p in shell.data.polygons if all(abs(shell.data.vertices[i].co.z + 1.0) < 1e-4 for i in p.vertices))
ring=[shell.data.vertices[i].co for i in base_poly.vertices]
plate_mesh=bpy.data.meshes.new('KRCH fourth-floor schematic plate | GIS outline')
plate_mesh.from_pydata([(v.x,v.y,14.68) for v in ring],[],[tuple(range(len(ring)))])
plate_mesh.materials.append(floor_mat)
slab=bpy.data.objects.new('KRCH documented fourth-floor slab | level +14.68m',plate_mesh)
structure.objects.link(slab)
slab['evidence']='Four above-grade floors are documented; fourth-floor slab inferred at existing 3.90 m spacing, exact elevation unverified.'
slab['status']='schematic level plate; floorplan not surveyed'

# Stairs within the published multi-level lobby/stair zone. Stair geometry is interpretive;
# Purdue and glass fabricator sources substantiate the multilevel interior and glass rails.
verts=[]; faces=[]
def add_box(cx,cy,cz,sx,sy,sz):
    start=len(verts)
    for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
        verts.append((cx+x*sx/2,cy+y*sy/2,cz+z*sz/2))
    faces.extend([(start+0,start+3,start+2,start+1),(start+4,start+5,start+6,start+7),(start+0,start+1,start+5,start+4),(start+1,start+2,start+6,start+5),(start+2,start+3,start+7,start+6),(start+3,start+0,start+4,start+7)])

def add_quad(a,b,c,d):
    k=len(verts); verts.extend([a,b,c,d]); faces.append((k,k+1,k+2,k+3))

def add_rail_segment(a,b,y,rad=0.035):
    # narrow square handrail segment along a stair pitch, centered on y
    av=Vector((a[0],y,a[1])); bv=Vector((b[0],y,b[1])); diff=bv-av
    center=(av+bv)*0.5
    # create bevelled box local long axis aligned to the segment in XZ
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o=bpy.context.object; o.name='KRCH open stair | handrail segment'
    # move into owned asset collection only
    for c in list(o.users_collection): c.objects.unlink(o)
    structure.objects.link(o)
    o.dimensions=(diff.length,rad*2,rad*2); o.rotation_euler[1]=-math.atan2(diff.z,diff.x)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(metal_mat)
    o['evidence']='Interpretive stair handrail; material/height not specified by source.'

levels=[-0.92,2.98,6.88,10.78,14.68]
yA=-1.25; yB=1.25
x0=18.3; xmid=22.2; xend=26.1
n=11; tread_depth=0.34; rise=(levels[1]-levels[0])/2
for idx,(lo,hi) in enumerate(zip(levels[:-1],levels[1:])):
    mid=(lo+hi)/2
    # Flight A rises west to east; Flight B rises east to west. Individual treads make the stair legible through glass.
    for j in range(n):
        z=lo+(j+1)*rise/n
        x=x0+(j+0.5)*(xmid-x0)/n
        add_box(x,yA,z-0.09,(xmid-x0)/n+0.015,1.35,0.18)
        zb=mid+(j+1)*rise/n
        xb=xend-(j+0.5)*(xend-xmid)/n
        add_box(xb,yB,zb-0.09,(xend-xmid)/n+0.015,1.35,0.18)
    # Robust mid-floor turn landing and a small floor landing at the top/bottom of each run
    add_box((xmid+xend)/2,0,mid-0.10,xend-xmid,3.9,0.20)
    add_box(x0-0.65,0,lo+0.04,1.3,3.8,0.18)
    add_box(xend+0.65,0,hi-0.04,1.3,3.8,0.18)
    # Etched glass guarding on each open side, with a sloped top cap; source confirms glass rails.
    for xa,xb,ya,zlo,zhi,forward in [(x0,xmid,yA-0.69,lo,mid,True),(x0,xmid,yA+0.69,lo,mid,True),(xmid,xend,yB-0.69,mid,hi,False),(xmid,xend,yB+0.69,mid,hi,False)]:
        p0=(xa,ya,zlo+0.15); p1=(xb,ya,zhi+0.15)
        # for descending plan direction the elevation still rises as x moves from xend toward xmid
        if not forward: p0=(xb,ya,zlo+0.15); p1=(xa,ya,zhi+0.15)
        low0=(p0[0],ya,zlo); low1=(p1[0],ya,zhi)
        add_quad(low0,low1,p1,p0)
        add_rail_segment((p0[0],p0[2]),(p1[0],p1[2]),ya)

mesh=bpy.data.meshes.new('KRCH open stair system | evidence-informed schematic geometry')
mesh.from_pydata(verts,[],faces); mesh.materials.append(tread_mat); mesh.materials.append(rail_mat)
# First faces are solid tread boxes, then glass quads; assign transparent material to the glass faces.
for poly in mesh.polygons: poly.material_index=0
for poly in list(mesh.polygons)[n*2*len(levels[:-1])+3*len(levels[:-1]):]:
    # material assignment for quad panes (also some later faces depending on face order)
    pass
# Quads appended after boxes; each tread box contributes 6 faces, then 4 guard panes per story.
box_face_count=sum(6*(2*n+3) for _ in levels[:-1])
for poly in mesh.polygons[box_face_count:]: poly.material_index=1
stairs=bpy.data.objects.new('KRCH open stair | 4-floor lobby flights and etched glass balustrade',mesh)
structure.objects.link(stairs)
stairs['evidence']='Visible multi-level stair use is documented by Purdue Stories (2022); etched laminated glass rails throughout main lobby are documented by McGrory Glass. Exact stair position, dimensions, flight arrangement and material details remain schematic.'
stairs['floor_levels_m']=levels
stairs['source_urls']='https://stories.purdue.edu/the-top-10-best-study-locations-at-purdue/ ; https://mcgrory.com/projects/purdue-university/'

# Add consistent object metadata to the floor-level representation without changing existing source geometry.
for o in [slab,stairs]:
    o['building_id']='krach_leadership_center'
    o['local_frame']='project local meters; placement controlled by master marker'

# Ensure all objects remain in the expected exported Asset collection through its existing children.
# Save the modular library only; no master scene is opened or touched.
bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'collection':asset_col.name,'floor_levels_m':levels,'treads':n*2*len(levels[:-1]),'stair_object':stairs.name,'materials':[m.name for m in mesh.materials]},indent=2))

