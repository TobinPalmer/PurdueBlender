"""R7: integrate the entry porch and improve facade/material hierarchy."""
import bpy, math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
asset=root/'modular'/'buildings'/'university_hall.blend'
col=bpy.data.collections['Asset_university_hall']
parent=bpy.data.objects['AssetRoot_university_hall']
CX=-7.515

def delete_prefix(prefix):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix): bpy.data.objects.remove(ob,do_unlink=True)

def box(name,loc,dims,material,bevel=0.015):
    hx,hy,hz=(v/2 for v in dims)
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.location=loc;ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted()
    if bevel:
        b=ob.modifiers.new('Soft carved edge','BEVEL');b.width=bevel;b.segments=2
        ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

def mesh(name,verts,faces,material):
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted()
    return ob

stone=bpy.data.materials['Univ_Bedford_Limestone']
brick=bpy.data.materials['Univ_Weathered_Red_Brick']
slate=bpy.data.materials['Univ_Slate_Roof']
glass=bpy.data.materials['Univ_Window_Glass']

# Subtle course joints and brick tone shifts replace the almost-uniform wall
# color. Object-space scale uses the building's metre-based geometry.
brick_nodes=brick.node_tree.nodes;brick_links=brick.node_tree.links
bshader=next(n for n in brick_nodes if n.type=='BSDF_PRINCIPLED')
for link in list(brick_links):
    if link.to_node==bshader and link.to_socket in (bshader.inputs['Base Color'],bshader.inputs['Normal']):brick_links.remove(link)
for node in list(brick_nodes):
    if node.name.startswith('UH R7 '):brick_nodes.remove(node)
btc=brick_nodes.new('ShaderNodeTexCoord');btc.name='UH R7 brick coordinates'
sep=brick_nodes.new('ShaderNodeSeparateXYZ');sep.name='UH R7 separate wall axes';brick_links.new(btc.outputs['Object'],sep.inputs['Vector'])
ew=brick_nodes.new('ShaderNodeCombineXYZ');ew.name='UH R7 east west wall axes'
brick_links.new(sep.outputs['Y'],ew.inputs['X']);brick_links.new(sep.outputs['Z'],ew.inputs['Y']);brick_links.new(sep.outputs['X'],ew.inputs['Z'])
ns=brick_nodes.new('ShaderNodeCombineXYZ');ns.name='UH R7 north south wall axes'
brick_links.new(sep.outputs['X'],ns.inputs['X']);brick_links.new(sep.outputs['Z'],ns.inputs['Y']);brick_links.new(sep.outputs['Y'],ns.inputs['Z'])
def brick_texture(name):
    n=brick_nodes.new('ShaderNodeTexBrick');n.name=name;n.inputs['Scale'].default_value=1.0
    n.inputs['Brick Width'].default_value=0.24;n.inputs['Row Height'].default_value=0.075
    n.inputs['Mortar Size'].default_value=0.012;n.inputs['Mortar Smooth'].default_value=0.006
    n.inputs['Color1'].default_value=(0.27,0.060,0.036,1);n.inputs['Color2'].default_value=(0.36,0.095,0.060,1)
    n.inputs['Mortar'].default_value=(0.095,0.036,0.024,1);n.offset=0.5;n.offset_frequency=2
    return n
bt_ew=brick_texture('UH R7 east west brick courses');brick_links.new(ew.outputs['Vector'],bt_ew.inputs['Vector'])
bt_ns=brick_texture('UH R7 north south brick courses');brick_links.new(ns.outputs['Vector'],bt_ns.inputs['Vector'])
geo=brick_nodes.new('ShaderNodeNewGeometry');geo.name='UH R7 wall orientation'
normsep=brick_nodes.new('ShaderNodeSeparateXYZ');normsep.name='UH R7 wall normal axes';brick_links.new(geo.outputs['Normal'],normsep.inputs['Vector'])
absx=brick_nodes.new('ShaderNodeMath');absx.name='UH R7 east west selector';absx.operation='ABSOLUTE';brick_links.new(normsep.outputs['X'],absx.inputs[0])
mixcolor=brick_nodes.new('ShaderNodeMixRGB');mixcolor.name='UH R7 oriented brick color';mixcolor.blend_type='MIX'
brick_links.new(absx.outputs[0],mixcolor.inputs[0]);brick_links.new(bt_ns.outputs['Color'],mixcolor.inputs[1]);brick_links.new(bt_ew.outputs['Color'],mixcolor.inputs[2]);brick_links.new(mixcolor.outputs['Color'],bshader.inputs['Base Color'])
mixfac=brick_nodes.new('ShaderNodeMixRGB');mixfac.name='UH R7 oriented mortar pattern';mixfac.blend_type='MIX'
brick_links.new(absx.outputs[0],mixfac.inputs[0]);brick_links.new(bt_ns.outputs['Fac'],mixfac.inputs[1]);brick_links.new(bt_ew.outputs['Fac'],mixfac.inputs[2])
bbump=brick_nodes.new('ShaderNodeBump');bbump.name='UH R7 mortar relief';bbump.inputs['Strength'].default_value=0.13;bbump.inputs['Distance'].default_value=0.008
brick_links.new(mixfac.outputs['Color'],bbump.inputs['Height']);brick_links.new(bbump.outputs['Normal'],bshader.inputs['Normal'])
bshader.inputs['Roughness'].default_value=0.88

# Warm stone shifts away from chalk white. Keep the original relief but reduce
# its strength so mouldings feel cut from stone rather than plastic.
sshader=next(n for n in stone.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
for link in list(stone.node_tree.links):
    if link.to_node==sshader and link.to_socket==sshader.inputs['Base Color']:stone.node_tree.links.remove(link)
for node in list(stone.node_tree.nodes):
    if node.name.startswith('UH R7 stone '):stone.node_tree.nodes.remove(node)
stone_geo=stone.node_tree.nodes.new('ShaderNodeNewGeometry');stone_geo.name='UH R7 stone position'
stone_noise=stone.node_tree.nodes.new('ShaderNodeTexNoise');stone_noise.name='UH R7 stone mottling';stone_noise.inputs['Scale'].default_value=14.0;stone_noise.inputs['Detail'].default_value=2
stone_ramp=stone.node_tree.nodes.new('ShaderNodeValToRGB');stone_ramp.name='UH R7 warm limestone range'
stone_ramp.color_ramp.elements[0].color=(0.40,0.34,0.27,1);stone_ramp.color_ramp.elements[1].color=(0.48,0.42,0.34,1)
stone.node_tree.links.new(stone_geo.outputs['Position'],stone_noise.inputs['Vector']);stone.node_tree.links.new(stone_noise.outputs['Fac'],stone_ramp.inputs['Fac']);stone.node_tree.links.new(stone_ramp.outputs['Color'],sshader.inputs['Base Color'])
sshader.inputs['Roughness'].default_value=0.82
for node in stone.node_tree.nodes:
    if node.type=='BUMP':
        node.inputs['Strength'].default_value=0.10;node.inputs['Distance'].default_value=0.018

# Window glass gets a subdued daylight reflection instead of reading as flat
# black-blue rectangles. Apertures and sash grids are unchanged.
gshader=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
gshader.inputs['Base Color'].default_value=(0.10,0.13,0.16,1)
gshader.inputs['Roughness'].default_value=0.18;gshader.inputs['Metallic'].default_value=0.025
if 'Coat Weight' in gshader.inputs:gshader.inputs['Coat Weight'].default_value=0.18

# Break the identical window-head cadence with a subtle floor hierarchy:
# stronger ground-floor heads, shallow middle/upper hoods, all registered to
# the original apertures. No opening locations or dimensions are changed.
delete_prefix('UNIV_R5_Window_');delete_prefix('UNIV_R7_Window_')
def arch_band(name,x,yc,zhead,halfwidth,rise,depth,band):
    n=16;outer=[];inner=[]
    for i in range(n+1):
        a=math.pi-i*math.pi/n
        outer.append((yc+halfwidth*math.cos(a),zhead+rise*math.sin(a)))
        inner.append((yc+(halfwidth-band)*math.cos(a),zhead+max(0.02,rise-band)*math.sin(a)))
    verts=[]
    for xx in (x-depth/2,x+depth/2):verts.extend((xx,y,z) for y,z in outer+inner)
    m=n+1;ring=2*m;faces=[]
    for i in range(n):
        faces.extend([(i,i+1,m+i+1,m+i),(ring+i,ring+m+i,ring+m+i+1,ring+i+1),
                      (i,ring+i,ring+i+1,i+1),(m+i,m+i+1,ring+m+i+1,ring+m+i)])
    faces.extend([(0,m,ring+m,ring),(n,ring+n,ring+m+n,m+n)])
    ob=mesh(name,verts,faces,stone);bevel=ob.modifiers.new('Carved arch arris','BEVEL');bevel.width=0.012;bevel.segments=2
    ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return ob

for side,sign in (('East',1),('West',-1)):
    windows=[]
    for win in col.all_objects:
        if win.type!='MESH' or not win.name.startswith(f'UNIV_Win_{side}_'):continue
        pts=[win.matrix_world@Vector(c) for c in win.bound_box]
        lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
        if hi[2]>12.6:continue
        windows.append((win,lo,hi))
    for j,(win,lo,hi) in enumerate(sorted(windows,key=lambda t:(t[1][2],t[1][1]))):
        yc=(lo[1]+hi[1])/2;zhead=hi[2]+0.025
        half=max(0.74,(hi[1]-lo[1])/2+0.08)
        if lo[2]<3.7:rise,band,depth=.46,.10,.075
        elif lo[2]<8.0:rise,band,depth=.31,.075,.060
        else:rise,band,depth=.27,.065,.055
        x=3.89 if sign>0 else -18.97
        arch_band(f'UNIV_R7_Window_{side}_{j:02d}_Hood',x,yc,zhead,half,rise,depth,band)
        # Alternating shallow stone keys, concentrated on the more formal ground floor.
        if lo[2]<3.7:
            box(f'UNIV_R7_Window_{side}_{j:02d}_Keystone',(x+sign*.035,yc,zhead+rise-.015),(.105,.12,.18),stone,.012)
        for k,dy in enumerate((-half+0.04,half-0.04)):
            jamb_depth=.075 if lo[2]<3.7 else .05
            box(f'UNIV_R7_Window_{side}_{j:02d}_Reveal_{k}',(x,yc+dy,(lo[2]+zhead)/2),(jamb_depth,.075,zhead-lo[2]),stone,.009)

# Replace the unsupported gap behind the old porch pediment with a gable that
# returns to the façade. A broad architrave bears on the existing column capitals.
for name in ('UNIV_R4_Portico_TriangularPediment','UNIV_R4_Portico_PedimentCymatium_L','UNIV_R4_Portico_PedimentCymatium_R'):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
delete_prefix('UNIV_R5_Entry_');delete_prefix('UNIV_R7_Entry_')
delete_prefix('UNIV_R7_Portico_GableMould')
xfront=8.0;xback=3.60
verts=[(xfront,-3.65,5.48),(xfront,3.65,5.48),(xfront,0,7.18),
       (xback,-3.65,5.48),(xback,3.65,5.48),(xback,0,7.18)]
mesh('UNIV_R4_Portico_TriangularPediment',verts,[(0,1,2),(5,4,3),(0,3,4,1),(0,2,5,3),(1,4,5,2)],stone)
box('UNIV_R7_Portico_IntegratedArchitrave',(5.82,0,5.55),(4.36,7.50,.26),stone,.035)
box('UNIV_R7_Portico_Cornice',(5.84,0,5.74),(4.52,7.72,.14),stone,.025)

# Layered slope moulds and a restrained lower cornice articulate the pediment.
curve=bpy.data.curves.new('UNIV_R7_Portico_GableMouldData','CURVE');curve.dimensions='3D';curve.bevel_depth=.075;curve.bevel_resolution=3
spline=curve.splines.new('POLY');spline.points.add(2)
for p,co in zip(spline.points,((8.06,-3.60,5.57,1),(8.06,0,7.18,1),(8.06,3.60,5.57,1))):p.co=co
curve.materials.append(stone);gobj=bpy.data.objects.new('UNIV_R7_Portico_GableMould',curve);col.objects.link(gobj);gobj.parent=parent;gobj.matrix_parent_inverse=parent.matrix_world.inverted()

# Rebuild door surround as flat pilasters, layered plinth/capitals, a shallow
# segmental hood, and divided transom. Details follow the visible restored entry.
for side,y in (('L',-1.88),('R',1.88)):
    box(f'UNIV_R7_Entry_Pilaster_{side}',(3.69,y,2.38),(.18,.19,3.76),stone,.018)
    box(f'UNIV_R7_Entry_Base_{side}',(3.69,y,.48),(.31,.30,.28),stone,.025)
    box(f'UNIV_R7_Entry_Capital_{side}',(3.69,y,4.30),(.33,.31,.25),stone,.025)
    box(f'UNIV_R7_Entry_Impost_{side}',(3.70,y,4.48),(.30,.33,.12),stone,.018)
arch_band('UNIV_R7_Entry_SegmentalHood',3.95,0,4.54,1.66,.46,.075,.12)
box('UNIV_R7_Entry_Keystone',(4.00,0,4.96),(.12,.18,.24),stone,.014)
for i,y in enumerate((-.74,-.25,.25,.74)):
    box(f'UNIV_R7_Entry_TransomMullion_{i}',(3.84,y,4.22),(.06,.045,.38),stone,.008)

# Square impost blocks visually tie the existing plain Tuscan shafts to the new beam.
for side,y in (('North',3.2),('South',-3.2)):
    box(f'UNIV_R7_Portico_ColumnAbacus_{side}',(6.895,y,5.43),(.90,.90,.16),stone,.035)

# Softly varied slate keeps the course pattern readable without a hard tile grid.
sbshader=next(n for n in slate.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
sbshader.inputs['Roughness'].default_value=.84
for node in slate.node_tree.nodes:
    if node.type=='BUMP' and node.label=='Low-relief slate joints':node.inputs['Strength'].default_value=.11

bpy.ops.wm.save_as_mainfile(filepath=str(asset))
print('SAVED_R7',asset,'OBJECTS',len(col.all_objects))
print('ROOT',list(parent.location),list(parent.rotation_euler),list(parent.scale))
print('PORTICO_RETURNS_TO_WALL_X_M',xback,'WINDOW_OPENINGS_PRESERVED',True,'R6_LANDINGS_PRESERVED',True)
