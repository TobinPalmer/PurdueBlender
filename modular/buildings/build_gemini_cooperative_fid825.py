"""Create a detailed, standalone Gemini Cooperative asset from Purdue GIS FID 825.

Run with Blender 5.2+ in background mode.  The wall footprint uses the official
Purdue building polygon; stories, facade arrangement, roof and interior partitions
are photographic/schematic interpretations, not surveyed dimensions.
"""
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "gemini"
GIS = EVIDENCE / "fid825.geojson"
OUT = ROOT / "modular" / "buildings" / "massing_gemini_cooperative_fid825.blend"
ASSET_ID = "massing_gemini_cooperative_fid825"
COLL_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
LAT0, LON0 = 40.4274, -86.9137

feature = json.loads(GIS.read_text(encoding="utf-8"))["features"][0]
assert feature["id"] == 825 and feature["properties"]["BUILDING_N"] == "Gemini"
ring_ll = feature["geometry"]["coordinates"][0]
ring_xy_campus = [((lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)),
                   (lat - LAT0) * 111040.0) for lon, lat in ring_ll[:-1]]
area2 = sum(ring_xy_campus[i][0] * ring_xy_campus[(i+1) % len(ring_xy_campus)][1] -
            ring_xy_campus[(i+1) % len(ring_xy_campus)][0] * ring_xy_campus[i][1]
            for i in range(len(ring_xy_campus)))
cx = sum((ring_xy_campus[i][0] + ring_xy_campus[(i+1) % len(ring_xy_campus)][0]) *
         (ring_xy_campus[i][0] * ring_xy_campus[(i+1) % len(ring_xy_campus)][1] -
          ring_xy_campus[(i+1) % len(ring_xy_campus)][0] * ring_xy_campus[i][1])
         for i in range(len(ring_xy_campus))) / (3.0 * area2)
cy = sum((ring_xy_campus[i][1] + ring_xy_campus[(i+1) % len(ring_xy_campus)][1]) *
         (ring_xy_campus[i][0] * ring_xy_campus[(i+1) % len(ring_xy_campus)][1] -
          ring_xy_campus[(i+1) % len(ring_xy_campus)][0] * ring_xy_campus[i][1])
         for i in range(len(ring_xy_campus))) / (3.0 * area2)
ring = [(x-cx, y-cy) for x, y in ring_xy_campus]

# Clear background scene and establish a single exported building collection.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.collections, bpy.data.materials, bpy.data.meshes):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset = bpy.data.collections.new(COLL_NAME)
scene.collection.children.link(asset)

def link(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    asset.objects.link(obj)
    return obj

def material(name, color, rough=.78, noise_scale=30, bump=.035, color2=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = rough
    if noise_scale:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = noise_scale
        tex.inputs["Detail"].default_value = 3
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*(color2 or tuple(c*.72 for c in color)), 1)
        ramp.color_ramp.elements[1].color = (*color, 1)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
        if bump:
            b = nt.nodes.new("ShaderNodeBump")
            b.inputs["Strength"].default_value = .18
            b.inputs["Distance"].default_value = bump
            nt.links.new(tex.outputs["Fac"], b.inputs["Height"])
            nt.links.new(b.outputs["Normal"], bs.inputs["Normal"])
    return m

brick = material("Gemini | dark red-brown brick", (.20,.075,.047), .88, 34, .025, (.13,.045,.029))
siding = material("Gemini | warm ivory horizontal siding", (.79,.72,.59), .82, 8, .012, (.68,.60,.47))
roofmat = material("Gemini | warm muted red-brown shingles", (.24,.105,.067), .9, 42, .02, (.16,.065,.042))
trim = material("Gemini | cream painted wood trim", (.84,.78,.65), .66, 16, .008)
siding_line = material("Gemini | subtle recessed siding joints", (.61,.55,.45), .82, 0)
darktrim = material("Gemini | dark bronze window sash", (.095,.075,.056), .5, 18, .004)
glass = material("Gemini | blue gray glazing", (.09,.17,.19), .2, 0)
glass.node_tree.nodes.get("Principled BSDF").inputs["Metallic"].default_value = .18
floor_mat = material("Gemini | schematic warm interior floor", (.48,.39,.29), .75, 12, .01)
wall_mat = material("Gemini | schematic interior partitions", (.78,.72,.61), .85, 12, .006)
stone = material("Gemini | pale concrete entry landing and steps", (.48,.43,.36), .92, 20, .025)

def mesh_obj(name, verts, faces, mat):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    asset.objects.link(ob)
    return ob

def cube(name, loc, scale, mat, rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    o.rotation_euler[2] = rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    return link(o)

def prism(name, outline, z0, z1, mat):
    n = len(outline)
    verts = [(x,y,z0) for x,y in outline] + [(x,y,z1) for x,y in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
    faces += [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
    return mesh_obj(name, verts, faces, mat)

def wall_band(name, z0, z1, mat):
    n=len(ring)
    verts=[(x,y,z) for z in (z0,z1) for x,y in ring]
    faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_obj(name,verts,faces,mat)

# Exterior shell follows the official outline.  Lower masonry and two light
# siding stories match the current official street-facing image.
prism("Gemini | footprint ground and lower-floor slab", ring, -.12, .12, floor_mat)
wall_band("Gemini | continuous lower brick facade", 0, 2.7, brick)
wall_band("Gemini | first upper siding story", 2.7, 5.55, siding)
wall_band("Gemini | second upper siding story", 5.55, 8.35, siding)
# Fine horizontal reveals suggest the lap siding visible in the official photo.
for i,p0 in enumerate(ring):
    p1=ring[(i+1)%len(ring)]
    d=Vector((p1[0]-p0[0],p1[1]-p0[1]))
    if d.length < 1.5: continue
    tangent=d.normalized(); outward=Vector((-tangent.y,tangent.x))
    midpoint=Vector(p0)+d*.5
    rot=math.atan2(tangent.y,tangent.x)
    z=2.83
    while z<8.30:
        if not (5.53<z<5.70):
            p=midpoint+outward*.035
            cube(f"Gemini | facade {i+1} horizontal siding reveal",(p.x,p.y,z),(d.length,.045,.022),siding_line,rot)
        z+=.28

# Main roof orientation is derived from the polygon's principal axis.  Roof
# planes are an architectural estimate based on the official exterior image.
mx=sum(x for x,y in ring)/len(ring); my=sum(y for x,y in ring)/len(ring)
xx=sum((x-mx)**2 for x,y in ring); yy=sum((y-my)**2 for x,y in ring)
xy=sum((x-mx)*(y-my) for x,y in ring)
theta=.5*math.atan2(2*xy,xx-yy)
axis=Vector((math.cos(theta),math.sin(theta)))
cross=Vector((-axis.y,axis.x))
proj_a=[Vector((x,y)).dot(axis) for x,y in ring]
proj_c=[Vector((x,y)).dot(cross) for x,y in ring]
amin,amax=min(proj_a)-.45,max(proj_a)+.45
cmin,cmax=min(proj_c)-.45,max(proj_c)+.45
ar=(amin+amax)/2
cm=(cmin+cmax)/2
eave=8.25; ridge=10.75
def roof_point(a,c,z):
    p=axis*a+cross*c
    return (p.x,p.y,z)
left=[roof_point(amin,cmin,eave),roof_point(amax,cmin,eave),roof_point(amax,cm,ridge),roof_point(amin,cm,ridge)]
right=[roof_point(amin,cm,ridge),roof_point(amax,cm,ridge),roof_point(amax,cmax,eave),roof_point(amin,cmax,eave)]
# Compound roof volumes reflect the lower west range, central ridge and raised
# east wing visible in the official exterior. Short overlaps close the stepped
# roof junctions; all dimensions remain photo estimates, not surveyed heights.
def gable_range(name,a0,a1,c0,c1,ev,rv):
    center=(c0+c1)/2
    l=[roof_point(a0,c0,ev),roof_point(a1,c0,ev),roof_point(a1,center,rv),roof_point(a0,center,rv)]
    r=[roof_point(a0,center,rv),roof_point(a1,center,rv),roof_point(a1,c1,ev),roof_point(a0,c1,ev)]
    mesh_obj("Gemini | "+name+" roof south plane",l,[(0,1,2,3)],roofmat)
    mesh_obj("Gemini | "+name+" roof north plane",r,[(0,1,2,3)],roofmat)
    for a,label in ((a0,"west"),(a1,"east")):
        mesh_obj(f"Gemini | {name} {label} gable",[roof_point(a,c0,ev),roof_point(a,c1,ev),roof_point(a,center,rv)],[(0,1,2)],siding)

span=amax-amin
# Roof extents follow the three GIS-visible plan ranges rather than repeating
# one full-width bar: shallow west wing, deep connector/rear wing, tall east
# gabled range. The joins overlap only 0.5 m, producing actual step/valley lines.
west_join=-11.0
east_join=2.0
gable_range("west lower wing",amin,west_join+.25,-7.85,8.0,8.15,9.72)
gable_range("central connector range",west_join-.25,east_join+.25,-10.90,9.65,8.05,9.78)
gable_range("east high wing",east_join-.25,amax,-5.40,9.85,8.35,11.25)

# Cross-gables project toward the front facade and intersect the main ranges,
# matching the source photo's gable faces and resulting roof valleys.
def cross_gable(name,a0,a1,c0,c1,ev,rv):
    ac=(a0+a1)/2
    p0=roof_point(a0,c0,ev); p1=roof_point(ac,c0,rv); p2=roof_point(a1,c0,ev)
    p3=roof_point(a0,c1,ev); p4=roof_point(ac,c1,rv); p5=roof_point(a1,c1,ev)
    mesh_obj("Gemini | "+name+" left plane",[p0,p1,p4,p3],[(0,1,2,3)],roofmat)
    mesh_obj("Gemini | "+name+" right plane",[p1,p2,p5,p4],[(0,1,2,3)],roofmat)
    mesh_obj("Gemini | "+name+" front gable",[p0,p2,p1],[(0,1,2)],siding)
    mesh_obj("Gemini | "+name+" rear gable",[p3,p4,p5],[(0,1,2)],siding)
    # Attic sash on both gable faces: the camera angle can expose either end.
    for side,label in ((-1,"front"),(1,"rear")):
        gp=axis*ac+cross*(c0-.06 if side<0 else c1+.06)
        zwin=ev+(rv-ev)*.47
        cube(f"Gemini | {name} {label} attic window frame",(gp.x,gp.y,zwin),(1.36,.11,1.24),darktrim,theta)
        glassp=gp+cross*(side*.07)
        cube(f"Gemini | {name} {label} attic glazing",(glassp.x,glassp.y,zwin),(1.05,.045,.94),glass,theta)
        mull=glassp+cross*(side*.03)
        cube(f"Gemini | {name} {label} attic sash mullion",(mull.x,mull.y,zwin),(.07,.06,.94),trim,theta)
cross_gable("west front cross gable",amin+span*.24,amin+span*.38,cmax-5.3,cmax+.35,8.15,10.65)
cross_gable("east front cross gable",amin+span*.66,amin+span*.98,cmax-5.6,cmax+.35,8.35,11.1)

# Dormers are substantial roof structures, not shallow boxes: each has a
# triangular front, deep cheeks and two pitched cap planes. Their widths and
# positions vary to follow the official image's separate roof wings.
def dormer(name,a,width,cfront,cback,base,height,peak):
    half=width*.5
    def point(aa,cc,zz):
        q=axis*aa+cross*cc
        return (q.x,q.y,zz)
    # Rectangular wall and triangular pediment on the street-facing plane.
    verts=[point(a-half,cfront,base),point(a+half,cfront,base),
           point(a+half,cfront,base+height),point(a-half,cfront,base+height),
           point(a,cfront,base+height+peak)]
    mesh_obj("Gemini | "+name+" front wall",verts,[(0,1,2,3),(3,2,4)],siding)
    # Solid side cheeks go back into the roof, giving visible depth.
    for side,label in ((-1,"left"),(1,"right")):
        aa=a+side*half
        mesh_obj(f"Gemini | {name} {label} cheek",
            [point(aa,cfront,base),point(aa,cback,base),point(aa,cback,base+height*.88),
             point(aa,cfront,base+height)],[(0,1,2,3)],siding)
    # The ridge runs back from its peaked gable; roof planes have real pitch.
    ridge_base=base+height+peak
    for side,label in ((-1,"left cap"),(1,"right cap")):
        aedge=a+side*half
        mesh_obj(f"Gemini | {name} {label}",
            [point(aedge,cfront,base+height),point(a,cfront,ridge_base),
             point(a,cback,ridge_base-.12),point(aedge,cback,base+height*.88)],[(0,1,2,3)],roofmat)
    # Framed sash is placed in the lower rectangular face, leaving the gable
    # triangle clear and visually distinct.
    z=base+height*.52
    gp=axis*a+cross*(cfront+.075)
    cube(f"Gemini | {name} sash frame",(gp.x,gp.y,z),(width*.64,.12,height*.63),darktrim,theta)
    glassp=gp+cross*.08
    cube(f"Gemini | {name} glazing",(glassp.x,glassp.y,z),(width*.54,.055,height*.52),glass,theta)
    mull=glassp+cross*.035
    cube(f"Gemini | {name} center mullion",(mull.x,mull.y,z),(.07,.07,height*.52),trim,theta)

# Short west shed-like dormer, broad central dormer, and a smaller east one.
dormer("west wing dormer",amin+span*.18,1.7,6.55,4.55,8.30,1.05,.68)
dormer("central wide dormer",amin+span*.46,4.9,8.35,5.0,8.16,1.15,.52)
dormer("east narrow dormer",amin+span*.63,2.0,8.95,6.9,8.69,1.15,.72)

# Three stacks anchor to their respective wing ridges, avoiding the floating
# appearance from using one global chimney base over unequal roof heights.
for i,(a,c,ridge_z,stack_h) in enumerate(((amin+2.8,.075,9.72,2.05),
                                           (-4.2,-.625,9.78,2.05),
                                           (11.8,2.225,11.25,1.9)),1):
    p=axis*a+cross*c
    base=ridge_z-.10
    cube(f"Gemini | brick chimney {i}",(p.x,p.y,base+stack_h/2),(.82,.90,stack_h),brick,theta)
    cube(f"Gemini | chimney {i} stone cap",(p.x,p.y,base+stack_h+.10),(1.04,1.10,.18),stone,theta)

# Windows are based on the photographed elevation: fewer, broader lower brick
# openings and offset upper rows. Positions are interpretations, not surveys.
def facade_windows():
    for i,p0 in enumerate(ring):
        p1=ring[(i+1)%len(ring)]
        d=Vector((p1[0]-p0[0],p1[1]-p0[1]))
        length=d.length
        if length < 3.1: continue
        tangent=d.normalized()
        # This official GIS ring is clockwise, so the exterior is on its left.
        outward=Vector((-tangent.y,tangent.x))
        rot=math.atan2(tangent.y,tangent.x)
        levels=[]
        if length>=6.5: levels.append((0,1.45,max(1,int(length/5.2))))
        # Wider intervals and different cadence per wing create the opening
        # rhythm seen in the reference instead of a repeated perimeter grid.
        levels += [(1,4.05,max(1,int(length/(4.05 if i%2 else 4.65)))),
                   (2,6.77,max(1,int(length/(4.85 if i%2 else 5.4))))]
        for story,zcenter,n in levels:
            for j in range(n):
                along=length*(j+.5+(0.10 if (i+j+story)%3==0 else -0.04 if (i+j)%4==0 else 0))/n
                # Preserve the photographed central doorway opening on the
                # long east/front wall (GIS ring edge 12).
                door_station=length*.5-6.0
                if i==12 and abs(along-door_station)<2.05: continue
                p=Vector(p0)+tangent*along+outward*.10
                w=min(1.45 if story==0 else 1.2,length/n*(.52 if (i+j)%2 else .43))
                h=1.02 if story==0 else 1.36 if story==1 else 1.20
                cube(f"Gemini | facade {i+1} story {story} window {j+1} recess",
                     (p.x,p.y,zcenter),(w+.18,.12,h+.18),darktrim,rot)
                pglass=p+outward*.075
                cube(f"Gemini | facade {i+1} story {story} window {j+1} glazing",
                     (pglass.x,pglass.y,zcenter),(w,.035,h),glass,rot)
                # center mullion plus top/bottom rails for unmistakable sash.
                pm=pglass+tangent*(w*.03)
                cube(f"Gemini | facade {i+1} story {story} window {j+1} mullion",
                     (pm.x,pm.y,zcenter),(.055,.055,h),trim,rot)
                for zoff in (-h/2,h/2):
                    q=pglass+outward*.026
                    cube(f"Gemini | facade {i+1} story {story} window {j+1} rail",
                         (q.x,q.y,zcenter+zoff),(w+.08,.065,.055),trim,rot)
                sill=p+outward*.02
                cube(f"Gemini | facade {i+1} story {story} window {j+1} sill",
                     (sill.x,sill.y,zcenter-h/2-.08),(w+.18,.24,.13),trim,rot)
facade_windows()

# Select the longest street-facing segment for a centered, covered entry. The
# entrance's precise facade is not marked in the GIS, so this is interpreted.
edges=[]
for i,p0 in enumerate(ring):
    p1=ring[(i+1)%len(ring)]
    d=Vector((p1[0]-p0[0],p1[1]-p0[1]))
    edges.append((d.length,i,Vector(p0),d.normalized()))
_,entry_i,entry_p,tangent=max(edges)
entry_d=Vector((ring[(entry_i+1)%len(ring)][0]-ring[entry_i][0],ring[(entry_i+1)%len(ring)][1]-ring[entry_i][1]))
outward=Vector((-tangent.y,tangent.x))
entry=entry_p+entry_d*.5-tangent*6.0+outward*.16
rot=math.atan2(tangent.y,tangent.x)
# Entry is on the main upper floor: the photo shows a raised, recessed porch
# above the lower brick story, reached by a long broad stair.
door_z=4.30
cube("Gemini | main entrance dark door",(entry.x,entry.y,door_z),(1.40,.20,2.50),darktrim,rot)
door_glass=entry+outward*.12
cube("Gemini | main entrance glazed panel",(door_glass.x,door_glass.y,door_z+.08),(.96,.07,1.92),glass,rot)
cube("Gemini | entrance transom",(entry.x,entry.y,door_z+1.14),(1.50,.24,.28),trim,rot)
landing_z=2.88
landing=entry+outward*.72
cube("Gemini | recessed porch landing",(landing.x,landing.y,landing_z),(5.9,2.1,.34),stone,rot)
# Four brick corner piers define a deep, recessed portico around the entrance.
for off_a in (-2.48,2.48):
    for off_c in (.05,2.15):
        q=entry+tangent*off_a+outward*off_c
        cube("Gemini | recessed porch brick pier",(q.x,q.y,4.12),(.54,.58,2.55),brick,rot)
        cube("Gemini | porch pier capital",(q.x,q.y,5.47),(.70,.72,.18),trim,rot)
# Two roof slopes, with a real ridge and gable fascia, replace the flat awning.
porch_c=entry+outward*1.05
a0=-3.05; a1=3.05
cb=-.55; cf=2.55
zedge=5.55; zridge=6.04
def pxy(aa,cc):
    q=entry+tangent*aa+outward*cc
    return (q.x,q.y)
for side,label in ((-1,"rear slope"),(1,"front slope")):
    cedge=cb if side<0 else cf
    # Roof ridge is aligned with the frontage; the pitches fall to front/back.
    q0=pxy(a0,cedge); q1=pxy(a1,cedge); qr0=pxy(a0,(cb+cf)/2); qr1=pxy(a1,(cb+cf)/2)
    mesh_obj("Gemini | porch gabled roof "+label,
        [(q0[0],q0[1],zedge),(q1[0],q1[1],zedge),(qr1[0],qr1[1],zridge),(qr0[0],qr0[1],zridge)],[(0,1,2,3)],roofmat)
for aa,label in ((a0,"west end"),(a1,"east end")):
    q0=pxy(aa,cb); q1=pxy(aa,cf); qr=pxy(aa,(cb+cf)/2)
    mesh_obj("Gemini | porch gable " + label,
        [(q0[0],q0[1],zedge),(q1[0],q1[1],zedge),(qr[0],qr[1],zridge)],[(0,1,2)],siding)
# Raised deck continues along the image-visible right wing and carries one
# continuous guardrail run; the central stair opening stays clear.
deck_center=entry+tangent*5.2+outward*.72
cube("Gemini | east wing raised porch deck",(deck_center.x,deck_center.y,landing_z),(7.9,1.9,.30),stone,rot)
rail_z=landing_z+.92
rail_center=entry+tangent*5.2+outward*1.70
cube("Gemini | continuous east wing porch top rail",(rail_center.x,rail_center.y,rail_z),(7.7,.15,.15),darktrim,rot)
for j in range(13):
    q=entry+tangent*(1.45+j*.62)+outward*1.70
    cube("Gemini | east wing porch baluster",(q.x,q.y,rail_z-.43),(.10,.11,.88),trim,rot)
# Front landing rails continue to both stair rails; center opening is 2 m wide.
for side in (-1,1):
    mid=entry+tangent*(side*2.0)+outward*1.72
    cube("Gemini | porch landing rail segment",(mid.x,mid.y,rail_z),(1.55,.15,.15),darktrim,rot)
    q=entry+tangent*(side*2.55)+outward*.65
    cube("Gemini | porch side handrail",(q.x,q.y,rail_z-.43),(.15,1.8,.15),darktrim,rot)
    for j in range(4):
        post=entry+tangent*(side*2.55)+outward*(.05+j*.52)
        cube("Gemini | porch side baluster",(post.x,post.y,rail_z-.43),(.10,.10,.86),trim,rot)
# Six broad masonry treads descend from the raised deck to grade.
for step in range(6):
    depth=2.05+step*.52
    top=landing_z-step*.45
    q=entry+outward*depth
    cube(f"Gemini | broad porch stair tread {step+1}",(q.x,q.y,top-.22),(4.85,.66,.44),stone,rot)
# Continuous sloped handrails and regularly spaced balusters follow both stair
# edges down to grade, connecting cleanly to the porch landing guardrails.
def beam_between(name,p0,p1,thickness,mat):
    start=Vector(p0); end=Vector(p1); direction=end-start
    bpy.ops.mesh.primitive_cube_add(size=1,location=(start+end)*.5)
    ob=bpy.context.object; ob.name=name
    ob.dimensions=(direction.length,thickness,thickness)
    ob.rotation_mode="QUATERNION"
    ob.rotation_quaternion=direction.to_track_quat("X","Z")
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    return link(ob)
for side in (-1,1):
    side_a=side*2.58
    rail_start=entry+tangent*side_a+outward*1.85
    rail_end=entry+tangent*side_a+outward*4.98
    beam_between("Gemini | continuous sloped stair handrail",
        (rail_start.x,rail_start.y,landing_z+.83),(rail_end.x,rail_end.y,1.45),.15,darktrim)
    for j in range(6):
        frac=j/5
        q=entry+tangent*side_a+outward*(2.0+frac*2.82)
        ztop=landing_z+.76-frac*2.20
        cube("Gemini | stair handrail baluster",(q.x,q.y,ztop-.44),(.11,.11,.88),trim,rot)

# Schematic open interior: simple floor plates and corridor/room partitions.
# The historic source notes 21 rooms, kitchen and computer room but provides no
# plan; partitions are intentionally representative and carry this caveat.
prism("Gemini | schematic interior floor plate lower",ring,.15,.25,floor_mat)
prism("Gemini | schematic interior floor plate level 2",ring,2.85,2.96,floor_mat)
prism("Gemini | schematic interior floor plate level 3",ring,5.70,5.81,floor_mat)
# A central circulation spine following the long principal axis; room dividers
# are kept clear of the facade glazing and are visibly labeled schematic.
for zbase in (.25,2.96,5.81):
    for side in (-1,1):
        for frac in (.13,.25,.37,.50,.63,.76,.87):
            a=amin+(amax-amin)*frac
            c=cm+side*2.1
            p=axis*a+cross*c
            cube("Gemini | schematic room partition",(p.x,p.y,zbase+1.25),(.10,3.8,2.5),wall_mat,theta)
    # Central corridor walls
    for side in (-1,1):
        c=cm+side*1.05
        p=axis*ar+cross*c
        cube("Gemini | schematic corridor wall",(p.x,p.y,zbase+1.25),(amax-amin-2,.10,2.5),wall_mat,theta)
# First-floor common room/kitchen hint, kept as labeled interior fittings.
for name,loc,scale in (
    ("schematic kitchen island",(ar,cm-5.0,1.0),(4.0,1.1,1.0)),
    ("schematic dining table",(ar,cm+5.0,1.25),(3.6,1.8,.16)),
    ("schematic computer-room desk",(ar-4,cm+5.0,1.0),(2.6,.75,.9)),
):
    cube("Gemini | " + name,loc,scale,stone,theta)

# This library is local-origin geometry. The master should place it at the
# polygon's area centroid converted by the project's conversion.
scene.cursor.location=(0,0,0)
scene.unit_settings.system="METRIC"
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=900
scene.render.resolution_y=650
scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18)
scene.view_settings.view_transform="Standard"
scene.view_settings.look="Medium High Contrast"
scene.view_settings.exposure=.75
scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.34,.39,.44,1)
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.65
scene.render.image_settings.file_format="PNG"
# Save a preview camera/light outside the exported asset collection.
preview=bpy.data.collections.new("Preview_only_context_exclude_from_master")
scene.collection.children.link(preview)
def link_preview(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    preview.objects.link(obj)
    return obj
# Aim the evidence view toward the longest GIS facade from its exterior side.
_,front_i,front_p,front_d=max(edges)
front_tangent=front_d.normalized()
front_out=Vector((-front_tangent.y,front_tangent.x))
view_origin=Vector((front_p.x+front_d.x*.5,front_p.y+front_d.y*.5,0))
camera_pos=view_origin+Vector((front_out.x*62,front_out.y*62,18))
bpy.ops.object.camera_add(location=camera_pos)
camera=link_preview(bpy.context.object); camera.name="Gemini | audit preview camera"
target=Vector((0,0,5.1)); camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
camera.data.lens=52; scene.camera=camera
for loc,power,size in (((-18,-24,30),8500,18),((22,20,24),6200,14)):
    bpy.ops.object.light_add(type="AREA",location=loc)
    light=link_preview(bpy.context.object); light.name="Gemini | audit preview area light"
    light.data.energy=power; light.data.shape="DISK"; light.data.size=size
    light.rotation_euler=(Vector((0,0,5))-light.location).to_track_quat("-Z","Y").to_euler()
scene.render.filepath=str(EVIDENCE/"gemini_preview.png")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)
# Render a second, source-like oblique view from the same entry elevation. It is
# temporary preview context and is removed before the build process exits.
scene.render.resolution_x=1000
scene.render.resolution_y=650
cam_pos=view_origin+Vector((front_out.x*50+front_tangent.x*16,
                            front_out.y*50+front_tangent.y*16,11))
bpy.ops.object.camera_add(location=cam_pos)
camera_oblique=link_preview(bpy.context.object)
camera_oblique.name="Gemini | audit oblique comparison camera"
camera_oblique.data.lens=46
camera_oblique.rotation_euler=(Vector((0,0,5.0))-camera_oblique.location).to_track_quat("-Z","Y").to_euler()
scene.camera=camera_oblique
scene.render.filepath=str(EVIDENCE/"gemini_preview_oblique.png")
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(camera_oblique,do_unlink=True)
scene.camera=camera
scene.render.filepath=str(EVIDENCE/"gemini_preview.png")
scene.render.resolution_x=900
scene.render.resolution_y=650

# Measurements and hash are emitted after saving and recorded for handoff.
verts=[o.matrix_world @ v.co for o in asset.objects if o.type=="MESH" for v in o.data.vertices]
bounds={"x":[min(v.x for v in verts),max(v.x for v in verts)],
        "y":[min(v.y for v in verts),max(v.y for v in verts)],
        "z":[min(v.z for v in verts),max(v.z for v in verts)]}
record={
    "building":"Gemini Cooperative House",
    "asset_id":ASSET_ID,
    "asset_path":"modular/buildings/"+OUT.name,
    "scene":SCENE_NAME,
    "collection":COLL_NAME,
    "source_feature":{"provider":"Purdue University GIS BuildingShapesZip4","fid":825,
        "name":"Gemini","address":"172 Littleton St","source_crs":"EPSG:4326",
        "source_file":"audit/gemini/fid825.geojson","retrieved":"2026-10-27"},
    "crosswalk":{"official_address":"172 Littleton Street","official_site":"https://www.geminicooperative.com/about",
        "purdue_coop_listing":"https://www.purdue.edu/fscl/councils/cooperatives/houses.php",
        "fid_identity_match":"verified by name=Gemini, owner=COOP, address=172 Littleton St; current official exterior photo sign independently reads Gemini / 172 Littleton"},
    "geographic_centroid":{"latitude":LAT0+cy/111040.0,"longitude":LON0+cx/(111412.84*math.cos(math.radians(LAT0))),
        "campus_xy_meters":[cx,cy]},
    "footprint":{"official_gis_area_m2":abs(area2)/2,"gis_ring_vertex_count":len(ring),
        "measurement":"polygon shoelace on project's local approximate lon/lat conversion; building polygon retained in local frame",
        "uncertainty":"GIS provider identifies feature as Gemini and wall outline candidate; imagery overlap/under-roof offsets cannot be independently separated; GIS area and conversion are approximate"},
    "local_geometry":{"local_origin":"area centroid of FID 825 footprint","bounds_m":bounds,
        "wall_footprint_xy_m":"official GIS polygon, translated to local origin","orientation":"unrotated local campus east/north axes; shape follows official ring",
        "floor_count":"three visible levels estimated from official exterior image; GIS NUM_LEVELS=1 conflicts, source field meaning unclear",
        "height":"main roof ridges estimated 9.72-11.25 m above datum; cross-gable peaks 10.65-11.1 m; entry porch ridge about 6.04 m; chimney stacks extend higher; interpreted, not surveyed",
        "interior":"schematic representative common spaces, corridor, resident rooms; not a measured floor plan"},
    "photo_guided_detail_estimates":{"roof_ranges_m":{"west":{"a_interval":[amin,west_join+.25],"c_interval":[-7.85,8.0],"eave_z":8.15,"ridge_z":9.72},"connector":{"a_interval":[west_join-.25,east_join+.25],"c_interval":[-10.90,9.65],"eave_z":8.05,"ridge_z":9.78},"east":{"a_interval":[east_join-.25,amax],"c_interval":[-5.40,9.85],"eave_z":8.35,"ridge_z":11.25}},"front_entry":{"door_center_z_m":door_z,"landing_center_z_m":landing_z,"broad_stair_treads":6,"entry_edge":"long front GIS edge, offset toward the center-wing junction to match the photo; interpretation, not survey"},"dormers":"three pitched dormers with modeled cheeks, gables and roof planes; spacing/size estimated from the official image"},
    "render_views":["audit/gemini/gemini_preview.png (front elevation)","audit/gemini/gemini_preview_oblique.png (source-like oblique)"],
    "imagery":[
        {"file":"audit/gemini/official_home_exterior.jpg","provider":"Gemini Cooperative official site (Wix CDN)","url":"https://static.wixstatic.com/media/95e9bb_01c28615d8194b95a9831dc88772f86f~mv2.jpeg","retrieved":"2026-10-27","used_for":"current exterior facade color, massing, roof, dormers, entry and lower brick/upper siding"},
        {"url":"https://www.geminicooperative.com/about","provider":"Gemini Cooperative official site","retrieved":"2026-10-27","used_for":"current house identity/address and historic co-op information"},
        {"url":"https://boilerlink.purdue.edu/organization/gemini","provider":"Purdue BoilerLink","retrieved":"2026-10-27","used_for":"independent address/organization crosswalk"}],
    "hash_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest(),
    "visible_elevation_interpretation":{"reference":"official_home_exterior.jpg","features":"distinct west, connector, and east roof ranges; two deep street-facing cross gables; large recessed upper-floor entry; broad stair and guardrail; varied wall openings and pitched dormers","dimensions":"measured only as image proportions; all elevations and the entry edge/offset are estimates because no calibrated facade elevation was found"},
    "quality_notes":"Current official Gemini photo informs the separated stepped roof wings, deep intersecting front gables/valleys, varied pitched dormers with cheeks, brick base, less repetitive opening rhythm, elevated recessed porch, broad stair and continuous railing. GIS wall outline is directly preserved. Roof intersections, opening locations, porch depth and interior partitions remain estimates because no surveyed elevations or floor plans were found.",
}
(EVIDENCE/"asset_evidence.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps(record,indent=2))
