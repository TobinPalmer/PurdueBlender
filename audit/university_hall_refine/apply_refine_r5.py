"""R5 refinement of the standalone University Hall library.

Preserves the original shell/root and edits only R4-specific gallery,
window, and procedural material details. Interior positions remain schematic.
"""
import bpy, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular'/'buildings'/'university_hall.blend'
COL=bpy.data.collections['Asset_university_hall']
PARENT=bpy.data.objects['AssetRoot_university_hall']
CX=-7.515

def delete_prefix(prefix):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix): bpy.data.objects.remove(ob,do_unlink=True)

def box(name,loc,dims,material,bevel=0.012):
    hx,hy,hz=(v/2 for v in dims)
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob.location=loc;ob.parent=PARENT;ob.matrix_parent_inverse=PARENT.matrix_world.inverted()
    if bevel:
        b=ob.modifiers.new('Fine stone arris','BEVEL');b.width=bevel;b.segments=2
        ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return ob

def cylinder(name,loc,radius,depth,material,vertices=32):
    verts=[]
    for z in (-depth/2,depth/2):
        for i in range(vertices):
            a=2*math.pi*i/vertices;verts.append((radius*math.cos(a),radius*math.sin(a),z))
    faces=[tuple(range(vertices-1,-1,-1)),tuple(range(vertices,2*vertices))]
    faces += [(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob.location=loc;ob.parent=PARENT;ob.matrix_parent_inverse=PARENT.matrix_world.inverted()
    b=ob.modifiers.new('Turned iron edge','BEVEL');b.width=0.018;b.segments=2
    ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

stone=bpy.data.materials['Univ_Bedford_Limestone']
brick=bpy.data.materials['Univ_Weathered_Red_Brick']
slate=bpy.data.materials['Univ_Slate_Roof']
iron=bpy.data.materials['UNIV_R2_Painted_Iron']
wood=bpy.data.materials['Univ_Dark_Walnut']

# The official close view shows a distinct weathered copper/verdigris spire;
# keep the roof slate blue while separating the lantern/spire metal.
patina=bpy.data.materials.get('UH_R5_CopperPatina') or bpy.data.materials.new('UH_R5_CopperPatina')
patina.use_nodes=True;patina.node_tree.nodes.clear()
pout=patina.node_tree.nodes.new('ShaderNodeOutputMaterial')
pbs=patina.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
pbs.inputs['Metallic'].default_value=0.16;pbs.inputs['Roughness'].default_value=0.62
pt=patina.node_tree.nodes.new('ShaderNodeTexNoise');pt.inputs['Scale'].default_value=7;pt.inputs['Detail'].default_value=3;pt.inputs['Roughness'].default_value=0.72
pr=patina.node_tree.nodes.new('ShaderNodeValToRGB');pr.color_ramp.elements[0].color=(0.006,0.025,0.023,1);pr.color_ramp.elements[1].color=(0.025,0.075,0.065,1)
ptc=patina.node_tree.nodes.new('ShaderNodeTexCoord');patina.node_tree.links.new(ptc.outputs['Generated'],pt.inputs['Vector']);patina.node_tree.links.new(pt.outputs['Fac'],pr.inputs['Fac']);patina.node_tree.links.new(pr.outputs['Color'],pbs.inputs['Base Color'])
pbump=patina.node_tree.nodes.new('ShaderNodeBump');pbump.inputs['Strength'].default_value=0.08;pbump.inputs['Distance'].default_value=0.012
patina.node_tree.links.new(pt.outputs['Fac'],pbump.inputs['Height']);patina.node_tree.links.new(pbump.outputs['Normal'],pbs.inputs['Normal']);patina.node_tree.links.new(pbs.outputs['BSDF'],pout.inputs['Surface'])
patina.diffuse_color=(0.018,0.055,0.048,1)
for obj in COL.all_objects:
    if obj.name in ('UNIV_R4_LanternDrum','UNIV_R4_LanternSpire') and obj.type=='MESH':
        obj.data.materials.clear();obj.data.materials.append(patina)

# Give slate legible, subdued staggered courses. Procedural coordinates keep
# the asset portable without external maps; no claim is made about exact quarry.
nt=slate.node_tree;nodes=nt.nodes;links=nt.links
bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
for link in list(links):
    if link.to_node==bs and link.to_socket in (bs.inputs['Base Color'],bs.inputs['Normal']): links.remove(link)
tc=nodes.new('ShaderNodeTexCoord');tc.label='Local roof panel coordinates'
bricktex=nodes.new('ShaderNodeTexBrick');bricktex.label='Subtle staggered slate courses';bricktex.inputs['Scale'].default_value=8.5
bricktex.inputs['Mortar Size'].default_value=0.018;bricktex.inputs['Mortar Smooth'].default_value=0.06
bricktex.inputs['Color1'].default_value=(0.035,0.046,0.062,1);bricktex.inputs['Color2'].default_value=(0.075,0.091,0.112,1)
bricktex.inputs['Mortar'].default_value=(0.012,0.018,0.028,1);bricktex.offset=0.5;bricktex.offset_frequency=2
links.new(tc.outputs['Generated'],bricktex.inputs['Vector']);links.new(bricktex.outputs['Color'],bs.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump');bump.label='Low-relief slate joints';bump.inputs['Strength'].default_value=0.18;bump.inputs['Distance'].default_value=0.018
links.new(bricktex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
bs.inputs['Metallic'].default_value=0.02;bs.inputs['Roughness'].default_value=0.78

# Improve brick variation while keeping a restrained historic red palette.
bsb=next(n for n in brick.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bricknodes=brick.node_tree.nodes;bricklinks=brick.node_tree.links
if not any(n.name=='UH R5 brick variation' for n in bricknodes):
    tex=bricknodes.new('ShaderNodeTexNoise');tex.name='UH R5 brick variation';tex.inputs['Scale'].default_value=14;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=0.72
    ramp=bricknodes.new('ShaderNodeValToRGB');ramp.name='UH R5 warm brick range'
    ramp.color_ramp.elements[0].color=(0.20,0.035,0.024,1);ramp.color_ramp.elements[1].color=(0.44,0.105,0.060,1)
    texcoord=bricknodes.new('ShaderNodeTexCoord');bricklinks.new(texcoord.outputs['Object'],tex.inputs['Vector']);bricklinks.new(tex.outputs['Fac'],ramp.inputs['Fac'])
    for link in list(bricklinks):
        if link.to_node==bsb and link.to_socket==bsb.inputs['Base Color']:bricklinks.remove(link)
    bricklinks.new(ramp.outputs['Color'],bsb.inputs['Base Color'])
    bumpb=bricknodes.new('ShaderNodeBump');bumpb.name='UH R5 brick grain';bumpb.inputs['Strength'].default_value=0.10;bumpb.inputs['Distance'].default_value=0.012
    bricklinks.new(tex.outputs['Fac'],bumpb.inputs['Height']);bricklinks.new(bumpb.outputs['Normal'],bsb.inputs['Normal'])
bsb.inputs['Roughness'].default_value=0.84

# Replace the heavy, applied semicircular curves with shallow stone hood arches,
# understated jamb reveals, and small keystones registered to actual window bounds.
delete_prefix('UNIV_R4_ArchedWindowHeadMoulds')
delete_prefix('UNIV_R5_Window')
def arch_band(name,x,yc,zhead,halfwidth,rise,depth=0.105,band=0.12):
    # Segmental arch in the YZ plane with a closed, shallow stone band.
    n=16;outer=[];inner=[]
    for i in range(n+1):
        a=math.pi-i*math.pi/n
        outer.append((yc+halfwidth*math.cos(a),zhead+rise*math.sin(a)))
        inner.append((yc+(halfwidth-band)*math.cos(a),zhead+max(0.02,rise-band)*math.sin(a)))
    verts=[]
    for xx in (x-depth/2,x+depth/2):
        verts.extend((xx,y,z) for y,z in outer+inner)
    m=n+1;ring=2*m;faces=[]
    for i in range(n):
        faces.append((i,i+1,m+i+1,m+i))
        faces.append((ring+i,ring+m+i,ring+m+i+1,ring+i+1))
        faces.append((i,ring+i,ring+i+1,i+1))
        faces.append((m+i,m+i+1,ring+m+i+1,ring+m+i))
    faces.extend([(0,m,ring+m,ring),(n,ring+n,ring+m+n,m+n)])
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(stone);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob.parent=PARENT;ob.matrix_parent_inverse=PARENT.matrix_world.inverted()
    bevel=ob.modifiers.new('Carved arris','BEVEL');bevel.width=0.018;bevel.segments=2
    ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

for side,sign in (('East',1),('West',-1)):
    prefix=f'UNIV_Win_{side}_'
    windows=[]
    for win in COL.all_objects:
        if win.type!='MESH' or not win.name.startswith(prefix):continue
        pts=[win.matrix_world@Vector(c) for c in win.bound_box]
        lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
        if hi[2]>12.6:continue
        windows.append((win,(lo,hi)))
    for j,(win,(lo,hi)) in enumerate(sorted(windows,key=lambda it:(it[1][0][2],it[1][0][1]))):
        yc=(lo[1]+hi[1])/2;zhead=hi[2]+0.035
        width=max(0.74,(hi[1]-lo[1])/2+0.10)
        ground_floor=lo[2]<3.7
        rise=0.44 if ground_floor else 0.34
        x=(3.91 if sign>0 else -18.99)
        arch_band(f'UNIV_R5_Window_{side}_{j:02d}_SegmentalHood',x,yc,zhead,width,rise,0.11,0.11)
        # The keystone is intentionally restrained, set just proud of the arch.
        box(f'UNIV_R5_Window_{side}_{j:02d}_Keystone',(x+sign*0.04,yc,zhead+rise-0.025),(0.15,0.18,0.26),stone,0.018)
        # Shallow jamb strips give the hood a continuous reveal without changing apertures.
        for k,dy in enumerate((-width+0.055,width-0.055)):
            box(f'UNIV_R5_Window_{side}_{j:02d}_Jamb_{k}',(x,yc+dy,(lo[2]+zhead)/2),(0.10,0.11,zhead-lo[2]),stone,0.012)

# Entry receives a layered archivolt and a molded cornice integrated with the
# existing porch composition. It remains image-derived, not a measured drawing.
delete_prefix('UNIV_R5_Entry')
for i,(dx,w,z,h) in enumerate(((0.10,3.05,4.55,0.16),(0.17,3.32,4.78,0.12),(0.07,2.72,4.34,0.10))):
    box(f'UNIV_R5_Entry_TransomMoulding_{i}',(3.66+dx,0,z),(0.18,w,h),stone,0.025)
for side,y in (('L',-1.92),('R',1.92)):
    box(f'UNIV_R5_Entry_PilasterBase_{side}',(3.67,y,0.47),(0.42,0.45,0.30),stone,0.03)
    box(f'UNIV_R5_Entry_PilasterCapital_{side}',(3.67,y,4.42),(0.44,0.47,0.30),stone,0.03)

# Replace the eight indistinguishable supports with five documented display
# columns, visually separated by floor/story and south stairwell role. Their
# exact positions are schematic because Purdue has not published a measured plan.
delete_prefix('UNIV_R4_ReclaimedColumn_')
delete_prefix('UNIV_R5_ReclaimedDisplayColumn_')
def display_column(name,x,y,base,top):
    h=top-base;mid=(base+top)/2
    cylinder(name+'_Shaft',(x,y,mid),0.17,h*0.73,iron,24)
    # Fluted shaft: eight subtle raised arrises (not a field of separate posts).
    for i in range(8):
        a=2*math.pi*i/8;rx=x+0.15*math.cos(a);ry=y+0.15*math.sin(a)
        cylinder(name+f'_Flute_{i}',(rx,ry,mid),0.018,h*0.69,iron,8)
    for tag,z,r,dh in (('Foot',base+0.08,0.33,0.16),('LowerMould',base+0.23,0.27,0.12),
                       ('Neck',top-0.28,0.24,0.12),('Capital',top-0.12,0.36,0.20)):
        cylinder(name+'_'+tag,(x,y,z),r,dh,iron,32)

# Two at ground level, two at the third-floor gallery, one by the south stair.
display_column('UNIV_R5_ReclaimedDisplayColumn_Ground_A',CX-2.9,-4.7,0.18,4.05)
display_column('UNIV_R5_ReclaimedDisplayColumn_Ground_B',CX+2.9,-4.7,0.18,4.05)
display_column('UNIV_R5_ReclaimedDisplayColumn_Third_A',CX-2.9,4.5,8.55,12.15)
display_column('UNIV_R5_ReclaimedDisplayColumn_Third_B',CX+2.9,4.5,8.55,12.15)
display_column('UNIV_R5_ReclaimedDisplayColumn_SouthStair',CX-5.8,-18.0,0.18,4.05)

# Improve the entry-facing brick/stone contrast and keep full-height root intact.
for ob in COL.all_objects:
    if ob.name.startswith('UNIV_R4_EaveConsole_') and ob.type=='MESH':
        ob.scale=(ob.scale.x*0.82,ob.scale.y*0.82,ob.scale.z*0.82)
    if ob.name.startswith('UNIV_R4_Portico_PedimentCymatium_') and ob.type=='MESH':
        # The thin inner mould is limestone in the Purdue exterior reference.
        ob.data.materials.clear();ob.data.materials.append(stone)

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('SAVED_R5',ASSET,'OBJECTS',len(COL.all_objects))
print('ROOT',list(PARENT.location),list(PARENT.rotation_euler),list(PARENT.scale))
print('DOCUMENTED_DISPLAY_COLUMNS',5,'POSITIONS_SCHEMATIC',True)
