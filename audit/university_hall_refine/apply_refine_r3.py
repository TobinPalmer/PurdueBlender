"""Tower and end-elevation pass for University Hall; safe to rerun."""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular'/'buildings'/'university_hall.blend'
COL=bpy.data.collections['Asset_university_hall']
ROOTOBJ=bpy.data.objects['AssetRoot_university_hall']
CX=-7.515

def remove_prefix(prefix):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix): bpy.data.objects.remove(ob,do_unlink=True)

def box(name,loc,dims,material,bevel=0.025):
    hx,hy,hz=(d/2 for d in dims)
    v=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],f);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob.location=loc;ob.parent=ROOTOBJ;ob.matrix_parent_inverse=ROOTOBJ.matrix_world.inverted()
    if bevel:
        b=ob.modifiers.new('Crisp architectural arris','BEVEL');b.width=bevel;b.segments=2
        ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return ob

def mesh(name,verts,faces,material):
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob.parent=ROOTOBJ;ob.matrix_parent_inverse=ROOTOBJ.matrix_world.inverted();return ob

def cylinder(name,loc,radius,depth,material,axis='Z',vertices=48):
    # Directly build a disc mesh; the specified axis is the disc normal.
    verts=[]
    for z in (-depth/2,depth/2):
        for i in range(vertices):
            a=2*math.pi*i/vertices;verts.append((radius*math.cos(a),radius*math.sin(a),z))
    faces=[tuple(range(vertices-1,-1,-1)),tuple(range(vertices,2*vertices))]
    faces += [(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    ob=mesh(name,verts,faces,material);ob.location=loc
    if axis=='X':ob.rotation_euler[1]=math.pi/2
    if axis=='Y':ob.rotation_euler[0]=math.pi/2
    b=ob.modifiers.new('Clock rim edge','BEVEL');b.width=0.035;b.segments=2
    return ob

def add_cupola(material):
    # Eight-sided copper lantern drum above the bell stage.
    n=8;r0=2.35;r1=1.60;z0=23.65;z1=25.1
    verts=[]
    for z,r in ((z0,r0),(z1,r1)):
        for i in range(n):
            a=2*math.pi*i/n+math.pi/8;verts.append((CX+r*math.cos(a),r*math.sin(a),z))
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    mesh('UNIV_R3_OctagonalCopperLantern',verts,faces,material)
    # Narrow, octagonal taper terminates in an acorn finial; old total height kept.
    vertices=[]
    for z,r in ((25.05,1.72),(26.95,0.23)):
        for i in range(n):
            a=2*math.pi*i/n+math.pi/8;vertices.append((CX+r*math.cos(a),r*math.sin(a),z))
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
    mesh('UNIV_R3_SteepEightSidedCopperSpire',vertices,fs,material)
    box('UNIV_R3_FinialStem',(CX,0,27.30),(0.09,0.09,0.7),bpy.data.materials['Univ_Gold_Accent'],0.015)
    box('UNIV_R3_WeathervaneArrow',(CX,0,27.64),(1.3,0.08,0.12),bpy.data.materials['Univ_Gold_Accent'],0.02)

remove_prefix('UNIV_R3_')
brick=bpy.data.materials['Univ_Weathered_Red_Brick']
stone=bpy.data.materials['Univ_Bedford_Limestone']
slate=bpy.data.materials['Univ_Slate_Roof']
glass=bpy.data.materials['Univ_Window_Glass']
gold=bpy.data.materials['Univ_Gold_Accent']
copper=bpy.data.materials['Univ_Verdigris_Copper']
iron=bpy.data.materials['UNIV_R2_Painted_Iron']
dark=bpy.data.materials['Univ_Chalkboard_Slate']

# Darken the slate from the first pass: slate should read as charcoal blue-gray.
nt=slate.node_tree
shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
base_link=next((l for l in nt.links if l.to_node==shader and l.to_socket==shader.inputs['Base Color']),None)
if base_link and base_link.from_node.type=='VALTORGB':
    ramp=base_link.from_node
    ramp.color_ramp.elements[0].color=(0.025,0.035,0.055,1)
    ramp.color_ramp.elements[1].color=(0.12,0.15,0.19,1)
shader.inputs['Roughness'].default_value=0.74

# Rebuild the open belfry cap as a steep hipped slate roof and a narrow copper
# lantern/spire. The preserved elevation height comes from the existing asset.
for name in ('UNIV_Belfry_Roof_Slab','UNIV_Copper_Cupola_Base','UNIV_Cupola_Spire_Spire','UNIV_Cupola_Finial_Rod','UNIV_Cupola_Weathervane_Arrow'):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
b0,b1=4.45,2.55;h0,h1=22.95,23.80
v=[(CX-b0,-b0,h0),(CX+b0,-b0,h0),(CX+b0,b0,h0),(CX-b0,b0,h0),
   (CX-b1,-b1,h1),(CX+b1,-b1,h1),(CX+b1,b1,h1),(CX-b1,b1,h1)]
f=[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
mesh('UNIV_R3_Belfry_Hipped_SlateCap',v,f,slate)
add_cupola(copper)

# Individually sized clock faces, one at each cardinal face of the central shaft.
face_mat=bpy.data.materials.get('UNIV_R3_ClockIvory') or bpy.data.materials.new('UNIV_R3_ClockIvory')
face_mat.diffuse_color=(0.88,0.80,0.63,1);face_mat.use_nodes=True
face_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(0.72,0.62,0.43,1)
face_mat.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0.2
face_mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=0.42
for side,loc,axis in (('East',(CX+4.28,0,17.9),'X'),('West',(CX-4.28,0,17.9),'X'),('North',(CX,4.28,17.9),'Y'),('South',(CX,-4.28,17.9),'Y')):
    sign=1 if side in ('East','North') else -1
    normal=(sign,0,0) if axis=='X' else (0,sign,0)
    base=Vector(loc)+Vector(normal)*0.11
    bezel=cylinder(f'UNIV_R3_{side}_ClockStoneBezel',base,1.13,0.20,stone,axis)
    if axis=='X':bezel.rotation_euler[1]=math.pi/2 if side=='East' else -math.pi/2
    else:bezel.rotation_euler[0]=-math.pi/2 if side=='North' else math.pi/2
    face=base+Vector(normal)*0.13
    faceob=cylinder(f'UNIV_R3_{side}_ClockFace',face,0.92,0.13,face_mat,axis)
    if axis=='X':faceob.rotation_euler[1]=math.pi/2 if side=='East' else -math.pi/2
    else:faceob.rotation_euler[0]=-math.pi/2 if side=='North' else math.pi/2
    # Two high-contrast hands; a slim vertical spindle and horizontal minute bar.
    hand_center=face+Vector(normal)*0.085
    dims=(0.055,0.07,0.65) if axis=='X' else (0.07,0.055,0.65)
    box(f'UNIV_R3_{side}_ClockHourHand',hand_center,dims,gold,0.015)
    dims2=(0.055,0.07,0.85) if axis=='X' else (0.07,0.055,0.85)
    minhand=box(f'UNIV_R3_{side}_ClockMinuteHand',hand_center,dims2,gold,0.015)
    if axis=='X':minhand.rotation_euler[0]=math.radians(90)
    else:minhand.rotation_euler[1]=math.radians(90)

# Louver panels give the open upper stage the readable belfry character seen in
# Purdue's historic references while retaining air gaps at the corners.
for side in ('East','West','North','South'):
    for i in range(5):
        if side in ('East','West'):
            x=CX+(4.0 if side=='East' else -4.0);y=-1.55+i*0.78
            box(f'UNIV_R3_Belfry_{side}_Louver_{i}',(x,y,21.35),(0.06,0.10,1.85),iron,0.015)
        else:
            y=4.0 if side=='North' else -4.0;x=CX-1.55+i*0.78
            box(f'UNIV_R3_Belfry_{side}_Louver_{i}',(x,y,21.35),(0.10,0.06,1.85),iron,0.015)

# Tall arched limestone surrounds replace the previous rectangular hood blocks
# on the long window elevations. Geometry is kept on the exterior face.
for ob in list(bpy.data.objects):
    if ob.name.startswith(('UNIV_WinHood_East_','UNIV_WinHood_West_','UNIV_WinKeystone_East_','UNIV_WinKeystone_West_')):
        bpy.data.objects.remove(ob,do_unlink=True)
arch_data=bpy.data.curves.new('UNIV_R3_ArchedWindowMoulds','CURVE');arch_data.dimensions='3D';arch_data.bevel_depth=0.075;arch_data.bevel_resolution=3
arch_obj=bpy.data.objects.new('UNIV_R3_ArchedWindowMoulds_EastWest',arch_data);COL.objects.link(arch_obj);arch_data.materials.append(stone);arch_obj.parent=ROOTOBJ;arch_obj.matrix_parent_inverse=ROOTOBJ.matrix_world.inverted()
for side,sign in (('East',1),('West',-1)):
    for fz in (2.6,6.4,10.4):
        for y in range(-255,-217,5):
            if side=='East' and fz<3 and abs(y+236.53)<4:continue
            x=(3.435 if side=='East' else -18.475)+sign*0.30
            sp=arch_data.splines.new('POLY');sp.points.add(16)
            # Quarter-arch semicircle sits over window head and joins short returns.
            pts=[(x,y-1.0,fz+0.9),(x,y-1.0,fz+1.18)]
            pts += [(x,y+math.cos(math.pi-k*math.pi/16),fz+1.18+math.sin(math.pi-k*math.pi/16)) for k in range(17)]
            pts += [(x,y+1.0,fz+0.9)]
            # Replace spline point count exactly, then assign 3D coordinates.
            sp.points.add(len(pts)-len(sp.points)-1)
            for p,co in zip(sp.points,pts):p.co=(co[0],co[1],co[2],1)

# Add the missing north/south gable-end fenestration: nine tall sash windows per
# short elevation, with stone jambs, sills, headers and keystones.
for side,sgn in (('North',1),('South',-1)):
    y=sgn*21.92
    for floor,z in enumerate((2.6,6.4,10.4)):
        for bay,dx in enumerate((-5.8,0.0,5.8)):
            x=CX+dx
            surf=y+sgn*0.08
            box(f'UNIV_R3_{side}_Window_{floor}_{bay}_Glazing',(x,surf,z),(2.0,0.08,2.4),glass,0.02)
            box(f'UNIV_R3_{side}_Window_{floor}_{bay}_MullionV',(x,surf+sgn*0.06,z),(0.07,0.06,2.25),stone,0.01)
            box(f'UNIV_R3_{side}_Window_{floor}_{bay}_MullionH',(x,surf+sgn*0.065,z),(1.9,0.06,0.07),stone,0.01)
            for j,off in enumerate((-1.12,1.12)):
                box(f'UNIV_R3_{side}_Window_{floor}_{bay}_Jamb_{j}',(x+off,surf+sgn*0.13,z),(0.18,0.20,2.65),stone,0.025)
            box(f'UNIV_R3_{side}_Window_{floor}_{bay}_Sill',(x,surf+sgn*0.15,z-1.30),(2.35,0.30,0.18),stone,0.025)
            box(f'UNIV_R3_{side}_Window_{floor}_{bay}_Header',(x,surf+sgn*0.13,z+1.30),(2.22,0.22,0.18),stone,0.02)
            box(f'UNIV_R3_{side}_Window_{floor}_{bay}_Keystone',(x,surf+sgn*0.16,z+1.45),(0.30,0.20,0.32),stone,0.018)

# Fresh save, standalone asset only.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('SAVED_R3',ASSET,'object_count',len(COL.all_objects))
print('ROOT_IDENTITY',list(ROOTOBJ.location),list(ROOTOBJ.rotation_euler),list(ROOTOBJ.scale))
