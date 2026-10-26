"""R3 candidate refinement after independent 5.6/10 review of SHA 227d6164.

Run against the standalone building library only. Original root, local origin,
manifest ID and main wall shell are preserved.
"""
import bpy, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular'/'buildings'/'university_hall.blend'
COL=bpy.data.collections['Asset_university_hall']
PARENT=bpy.data.objects['AssetRoot_university_hall']
CX=-7.515

def mat(name):return bpy.data.materials[name]
def delete_prefix(prefix):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):bpy.data.objects.remove(ob,do_unlink=True)
def remove(name):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)

def box(name,loc,dims,material,bevel=0.015):
    hx,hy,hz=(v/2 for v in dims)
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob.location=loc;ob.parent=PARENT;ob.matrix_parent_inverse=PARENT.matrix_world.inverted()
    if bevel:
        b=ob.modifiers.new('Architectural edge softness','BEVEL');b.width=bevel;b.segments=2
        ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return ob

def mesh(name,verts,faces,material,thickness=0.0):
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob.parent=PARENT;ob.matrix_parent_inverse=PARENT.matrix_world.inverted()
    if thickness:
        s=ob.modifiers.new('Roof panel thickness','SOLIDIFY');s.thickness=thickness;s.offset=-1
        b=ob.modifiers.new('Slate edge arris','BEVEL');b.width=0.025;b.segments=2
    return ob

def cylinder(name,loc,radius,depth,material,vertices=24):
    verts=[]
    for z in (-depth/2,depth/2):
        for i in range(vertices):
            a=2*math.pi*i/vertices;verts.append((radius*math.cos(a),radius*math.sin(a),z))
    faces=[tuple(range(vertices-1,-1,-1)),tuple(range(vertices,2*vertices))]
    faces += [(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    ob=mesh(name,verts,faces,material);ob.location=loc
    b=ob.modifiers.new('Turned metal edge','BEVEL');b.width=0.035;b.segments=2
    ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

def roof_panel(name,quad,material,thickness=0.20):
    # Double-sided shell with modest corner overlaps, all vertices stay in asset frame.
    xbar=sum(p[0] for p in quad)/4;ybar=sum(p[1] for p in quad)/4
    inner=[]
    for x,y,z in quad:
        dx=x-xbar;dy=y-ybar
        d=math.hypot(dx,dy) or 1
        inner.append((x-0.13*dx/d,y-0.13*dy/d,z-0.03))
    verts=list(quad)+inner
    faces=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh(name,verts,faces,material,thickness)

# Idempotence: a rerun replaces only this pass's geometry.
delete_prefix('UNIV_R5_')
# Remove the single-plane roof and isolated dormers; the shell is rebuilt in
# visibly different steep lower / shallow upper pitches with integrated dormers.
for prefix in ('UNIV_R2_Mansard_','UNIV_R2_Dormer_','UNIV_R2_RidgeDeck','UNIV_R2_SlateStandingSeam_'):
    delete_prefix(prefix)
slate=mat('Univ_Slate_Roof');stone=mat('Univ_Bedford_Limestone');brick=mat('Univ_Weathered_Red_Brick')
glass=mat('Univ_Window_Glass');iron=mat('UNIV_R2_Painted_Iron');wood=mat('Univ_Dark_Walnut')

# Make slate visibly darker, textured, and more readable under neutral daylight.
nt=slate.node_tree;shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
shader.inputs['Roughness'].default_value=0.70
color_link=next((l for l in nt.links if l.to_node==shader and l.to_socket==shader.inputs['Base Color']),None)
if color_link and color_link.from_node.type=='VALTORGB':
    ramp=color_link.from_node
    ramp.color_ramp.elements[0].color=(0.008,0.012,0.020,1)
    ramp.color_ramp.elements[1].color=(0.065,0.082,0.108,1)
# Make existing limestone warm and granular while retaining its material identity.
bs=next(n for n in stone.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(0.68,0.63,0.54,1);bs.inputs['Roughness'].default_value=0.78
if not any(n.name=='UH R3 limestone relief' for n in stone.node_tree.nodes):
    n=stone.node_tree.nodes.new('ShaderNodeTexNoise');n.name='UH R3 limestone relief';n.inputs['Scale'].default_value=32;n.inputs['Detail'].default_value=3
    b=stone.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=0.16;b.inputs['Distance'].default_value=0.025
    stone.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);stone.node_tree.links.new(b.outputs['Normal'],bs.inputs['Normal'])

# Outer shell and pitch break remain inside the current exterior-wall bounds.
bx0,bx1=CX-11.15,CX+11.15;by0,by1=-22.05,22.05
mx0,mx1=CX-10.05,CX+10.05;my0,my1=-20.95,20.95
tx0,tx1=CX-5.35,CX+5.35;ty0,ty1=-15.10,15.10
z0,zm,zt=12.58,14.40,16.75
lower=[
 ('East',[(bx1,by0,z0),(bx1,by1,z0),(mx1,my1,zm),(mx1,my0,zm)]),
 ('West',[(bx0,by1,z0),(bx0,by0,z0),(mx0,my0,zm),(mx0,my1,zm)]),
 ('North',[(bx1,by1,z0),(bx0,by1,z0),(mx0,my1,zm),(mx1,my1,zm)]),
 ('South',[(bx0,by0,z0),(bx1,by0,z0),(mx1,my0,zm),(mx0,my0,zm)])]
upper=[
 ('East',[(mx1,my0,zm),(mx1,my1,zm),(tx1,ty1,zt),(tx1,ty0,zt)]),
 ('West',[(mx0,my1,zm),(mx0,my0,zm),(tx0,ty0,zt),(tx0,ty1,zt)]),
 ('North',[(mx1,my1,zm),(mx0,my1,zm),(tx0,ty1,zt),(tx1,ty1,zt)]),
 ('South',[(mx0,my0,zm),(mx1,my0,zm),(tx1,ty0,zt),(tx0,ty0,zt)])]
for side,q in lower:roof_panel('UNIV_R5_Mansard_Lower_'+side,q,slate)
for side,q in upper:roof_panel('UNIV_R5_Mansard_Upper_'+side,q,slate)
# Pitch-break belt and flat deck around the tower keep the two slopes distinct.
box('UNIV_R5_Mansard_PitchBreak_E',(mx1+0.05,0,zm),(0.22,42.0,0.22),stone,0.025)
box('UNIV_R5_Mansard_PitchBreak_W',(mx0-0.05,0,zm),(0.22,42.0,0.22),stone,0.025)
box('UNIV_R5_Mansard_PitchBreak_N',(CX,my1+0.05,zm),(20.5,0.22,0.22),stone,0.025)
box('UNIV_R5_Mansard_PitchBreak_S',(CX,my0-0.05,zm),(20.5,0.22,0.22),stone,0.025)
box('UNIV_R5_Mansard_UpperDeck',(CX,0,16.63),(10.5,29.7,0.26),slate,0.035)

# Integrated east/west dormers: backs sink into the lower mansard plane, front
# glazing sits just outside it, and the cheek/roof form rises from the break zone.
for side,sign in (('East',1),('West',-1)):
    for i,y in enumerate((-13.0,-6.5,0.0,6.5,13.0)):
        roofx=11.15-(11.15-10.05)*(14.0-z0)/(zm-z0)
        cx=CX+sign*(roofx-0.22)
        body=box(f'UNIV_R5_Dormer_{side}_{i}_EmbeddedBrickCheeks',(cx,y,14.05),(1.35,1.95,1.9),brick,0.04)
        frontx=cx+sign*0.71
        box(f'UNIV_R5_Dormer_{side}_{i}_Sash',(frontx,y,14.12),(0.075,1.17,1.30),glass,0.015)
        for dy in (-0.69,0.69):
            box(f'UNIV_R5_Dormer_{side}_{i}_StoneJamb_{dy}',(frontx+sign*0.055,y+dy,14.10),(0.14,0.14,1.52),stone,0.018)
        box(f'UNIV_R5_Dormer_{side}_{i}_StoneSill',(frontx+sign*0.06,y,13.32),(0.18,1.62,0.16),stone,0.022)
        # Gable cheeks at the upper edge and two roof planes form an actual cap.
        gv=[(frontx,y-0.94,14.95),(frontx,y+0.94,14.95),(frontx,y,15.72),
            (frontx-sign*0.30,y-0.94,14.95),(frontx-sign*0.30,y+0.94,14.95),(frontx-sign*0.30,y,15.72)]
        mesh(f'UNIV_R5_Dormer_{side}_{i}_LimestoneGable',gv,[(0,1,2),(5,4,3),(0,3,4,1),(0,2,5,3),(1,4,5,2)],stone)
        rv=[(frontx+sign*0.15,y-1.12,15.56),(frontx+sign*0.15,y,16.10),(frontx+sign*0.15,y+1.12,15.56),
            (frontx-sign*0.56,y-1.12,15.56),(frontx-sign*0.56,y,16.10),(frontx-sign*0.56,y+1.12,15.56)]
        mesh(f'UNIV_R5_Dormer_{side}_{i}_SlateGableCap',rv,[(0,1,4,3),(1,2,5,4)],slate,0.08)

# Remove/rebuild the crown as a coherent supported shaft-to-belfry transition.
for prefix in ('UNIV_R3_Belfry_Hipped_SlateCap','UNIV_R3_OctagonalCopperLantern','UNIV_R3_SteepEightSidedCopperSpire','UNIV_R3_FinialStem','UNIV_R3_WeathervaneArrow'):
    delete_prefix(prefix)
slate_crown=slate;gold=mat('Univ_Gold_Accent')
# Four hipped roof planes span the pier tops and resolve to a raised lantern
# collar, so the upper feature visibly bears on the belfry stage.
bo=[(CX-4.45,-4.45,22.96),(CX+4.45,-4.45,22.96),(CX+4.45,4.45,22.96),(CX-4.45,4.45,22.96)]
ti=[(CX-1.80,-1.80,23.84),(CX+1.80,-1.80,23.84),(CX+1.80,1.80,23.84),(CX-1.80,1.80,23.84)]
for i in range(4):mesh(f'UNIV_R5_Belfry_Hip_{i}',[bo[i],bo[(i+1)%4],ti[(i+1)%4],ti[i]],[(0,1,2,3)],slate_crown,0.14)
box('UNIV_R5_LanternBaseRing',(CX,0,23.82),(3.6,3.6,0.20),stone,0.04)

def octagonal_taper(name,z0,z1,r0,r1,material):
    n=8;verts=[]
    for z,r in ((z0,r0),(z1,r1)):
        for i in range(n):
            a=2*math.pi*i/n+math.pi/8;verts.append((CX+r*math.cos(a),r*math.sin(a),z))
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    return mesh(name,verts,faces,material,0.08)
octagonal_taper('UNIV_R5_LanternDrum',23.85,25.05,1.75,1.40,slate_crown)
# Louver slots use subtle deep shadow reveals in the eight lantern faces.
for i in range(8):
    a=2*math.pi*i/8+math.pi/8;rad=1.48
    x=CX+rad*math.cos(a);y=rad*math.sin(a)
    ob=box(f'UNIV_R5_Lantern_Louver_{i}',(x,y,24.45),(0.05,0.08,0.62),iron,0.01)
    ob.rotation_euler[2]=a
octagonal_taper('UNIV_R5_LanternSpire',25.0,27.15,1.48,0.12,slate_crown)
box('UNIV_R5_FinialStem',(CX,0,27.36),(0.07,0.07,0.42),gold,0.012)
box('UNIV_R5_WeathervaneArrow',(CX,0,27.59),(1.2,0.07,0.11),gold,0.018)

# Replace old illustrative cast-iron columns with pieces that seat exactly on
# the ground/first-floor gallery and connect both ring floors.
delete_prefix('UNIV_R2_ReclaimedCastIronColumn_')
for level,(base,top) in enumerate(((0.155,4.05),(4.35,8.25))):
    for ix,x in enumerate((CX-4.2,CX+4.2)):
        for iy,y in enumerate((-6.8,6.8)):
            n=f'UNIV_R5_ReclaimedColumn_{level}_{ix}_{iy}'
            cylinder(n,(x,y,(base+top)/2),0.20,top-base,iron)
            for mark,z,r,h in (('Foot',base+0.10,0.34,0.16),('BaseCollar',base+0.30,0.27,0.14),('Capital',top-0.14,0.29,0.20)):
                cylinder(n+'_'+mark,(x,y,z),r,h,iron)

# Replace the two overlapping wedge flights with actual stepped profiles. The
# upper flight is offset beside the lower one and both end at floor elevations.
delete_prefix('UNIV_R2_GalleryStair_')
parquet=mat('Univ_Parquet_Wood')
def stair_profile(name,x,y_start,direction,z_base,z_top):
    n=18;run=6.12;step=run/n;rise=(z_top-z_base)/n
    y_end=y_start+direction*run
    # Polygon side profile contains explicit horizontal treads and vertical risers.
    profile=[(y_start,z_base)]
    for i in range(n):
        y0=y_start+direction*i*step;y1=y_start+direction*(i+1)*step
        z=z_base+(i+1)*rise
        profile.append((y0,z));profile.append((y1,z))
    profile.append((y_end,z_base))
    half=1.20;verts=[]
    for xx in (x-half,x+half):verts.extend((xx,y,z) for y,z in profile)
    L=len(profile);faces=[tuple(range(L-1,-1,-1)),tuple(range(L,2*L))]
    faces += [(i,(i+1)%L,(i+1)%L+L,i+L) for i in range(L)]
    mesh(name,verts,faces,parquet)
    return y_end
stair_profile('UNIV_R5_StairFlight_GroundToFirst',CX-7.35,-19.35,1,0.155,4.35)
stair_profile('UNIV_R5_StairFlight_FirstToSecond',CX-4.25,-13.20,-1,4.35,8.55)
box('UNIV_R5_StairLanding_First',(CX-5.80,-12.48,4.27),(4.7,1.7,0.16),parquet,0.025)
box('UNIV_R5_StairLanding_Second',(CX-5.80,-20.14,8.47),(4.7,1.7,0.16),parquet,0.025)
# Handrails use diagonal top rails and regularly spaced posts, attached at the
# stair edges. Their ends overlap the landings and main floor walking surfaces.
for level,(x,y0,direction,zstart,zend) in enumerate(((CX-7.35,-19.35,1,0.155,4.35),(CX-4.25,-13.2,-1,4.35,8.55))):
    for side in (-1,1):
        rx=x+side*1.28
        for i in range(10):
            t=i/9;y=y0+direction*6.12*t;z=zstart+(zend-zstart)*t
            box(f'UNIV_R5_StairRailPost_{level}_{side}_{i}',(rx,y,z+0.48),(0.055,0.055,0.96),iron,0.012)
        rail=box(f'UNIV_R5_StairHandrail_{level}_{side}',(rx,y0+direction*3.06,(zstart+zend)/2+0.96),(0.10,6.5,0.10),wood,0.025)
        # For an axis-aligned flight, tilting about X gives a diagonal in YZ.
        rail.rotation_euler[0]=direction*math.atan2(zend-zstart,6.12)

# Continuous two-story gallery railings on both gallery-floor edges and around
# the second-floor academy overlook. 1.0m guarded-height representation.
delete_prefix('UNIV_R4_Overlook_')
iron=mat('UNIV_R2_Painted_Iron')
def balustrade(prefix,z_base,hx,hy):
    z=z_base+0.53
    # Four sides, 13 posts on long sides and 9 on short sides.
    for i in range(13):
        y=-hy+2*hy*i/12
        for sx in (-1,1):box(f'{prefix}_LongPost_{sx}_{i}',(CX+sx*hx,y,z),(0.055,0.055,1.0),iron,0.012)
        if i<12:
            ymid=y+hy/6
            for sx in (-1,1):box(f'{prefix}_LongRail_{sx}_{i}',(CX+sx*hx,ymid,z+0.49),(0.055,2*hy/12,0.07),wood,0.012)
    for i in range(9):
        x=CX-hx+2*hx*i/8
        for sy in (-1,1):box(f'{prefix}_ShortPost_{sy}_{i}',(x,sy*hy,z),(0.055,0.055,1.0),iron,0.012)
        if i<8:
            xm=x+hx/4
            for sy in (-1,1):box(f'{prefix}_ShortRail_{sy}_{i}',(xm,sy*hy,z+0.49),(2*hx/8,0.055,0.07),wood,0.012)
balustrade('UNIV_R5_FirstGallery_Railing',4.35,3.8,6.0)
balustrade('UNIV_R5_AcademyOverlook_Railing',8.55,3.3,5.4)

# Entry portal: round paired shafts, proper door frame/double leaves, transom,
# and a triangular limestone pediment. Existing project envelope is untouched.
remove('UNIV_Portico_Col_North');remove('UNIV_Portico_Col_South');remove('UNIV_Portico_Pediment')
for side,y in (('North',3.2),('South',-3.2)):
    cylinder(f'UNIV_R5_Portico_RoundColumn_{side}',(6.895,y,3.50),0.42,3.50,stone,32)
    cylinder(f'UNIV_R5_Portico_ColumnBase_{side}',(6.895,y,1.78),0.57,0.22,stone,32)
    cylinder(f'UNIV_R5_Portico_ColumnCapital_{side}',(6.895,y,5.26),0.61,0.30,stone,32)
# Twin wood door leaves, transom glazing, side piers and lintel.
box('UNIV_R5_Entry_Threshold',(3.48,0,0.24),(0.36,3.55,0.18),stone,0.025)
for i,y in enumerate((-0.73,0.73)):
    box(f'UNIV_R5_Entry_DoorLeaf_{i}',(3.73,y,2.17),(0.12,1.38,3.45),wood,0.025)
    box(f'UNIV_R5_Entry_DoorInset_{i}',(3.80,y,2.35),(0.035,0.88,2.45),mat('Univ_Antique_Mahogany'),0.02)
    cylinder(f'UNIV_R5_Entry_DoorKnob_{i}',(3.87,y+(-0.10 if i==0 else 0.10),2.1),0.055,0.05,gold,12).rotation_euler[1]=math.pi/2
box('UNIV_R5_Entry_Transom',(3.76,0,4.22),(0.12,2.7,0.42),glass,0.02)
box('UNIV_R5_Entry_TransomStone',(3.67,0,4.48),(0.24,3.5,0.22),stone,0.025)
for y in (-1.78,1.78):box(f'UNIV_R5_Entry_StoneJamb_{y}',(3.60,y,2.52),(0.30,0.27,4.4),stone,0.03)
# Triangular gable shell above the portico columns: front and backing planes plus returns.
xfront=8.0;xback=5.0
v=[(xfront,-3.65,5.48),(xfront,3.65,5.48),(xfront,0,7.18),
   (xback,-3.65,5.48),(xback,3.65,5.48),(xback,0,7.18)]
mesh('UNIV_R5_Portico_TriangularPediment',v,[(0,1,2),(5,4,3),(0,3,4,1),(0,2,5,3),(1,4,5,2)],stone)
for side,ys in (('L',(-3.8,0)),('R',(0,3.8))):
    mesh(f'UNIV_R5_Portico_PedimentCymatium_{side}',[(8.05,ys[0],5.52),(8.05,ys[1],5.52),(8.05,0,7.22)],[(0,1,2)],gold,0.07)

# R5 asset save. Geometry writes only this asset and preserves the root.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('SAVED_R3',ASSET,'OBJECTS',len(COL.all_objects))
print('ROOT',list(PARENT.location),list(PARENT.rotation_euler),list(PARENT.scale))
print('MANSARD_PITCHES_LOWER_UPPER_RISES_M',round(zm-12.58,2),round(16.75-zm,2))
