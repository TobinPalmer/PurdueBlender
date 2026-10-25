import bpy,math,json
from mathutils import Vector
ASSET=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET);asset=bpy.data.collections['Asset_lawson_hall'];root=bpy.data.objects['AssetRoot_lawson_hall']
can=bpy.data.objects.get('LWSN_R7_GIS_Matched_Vestibule_Canopy')
if can:
 bpy.data.objects.remove(can,do_unlink=True)
gis=json.load(open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/target_buildings_gis.json',encoding='utf8'))['LWSN']['world_polygon']
marker=(-282.5,44.0)
ring=[(round(p[0]-marker[0],3),round(p[1]-marker[1],3)) for p in gis]
# Full ordered FID 59 vestibule contour, avoiding the previous diagonal shortcuts.
segments=list(zip(ring[42:52],ring[43:53]))
pts=[segments[0][0]]+[b for a,b in segments];ctr=(sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts));off=.55;z0=3.50;z1=3.78;t=.28
# radial offsets at each route vertex; canopy ribbon is segmented from GIS outline.
q=[]
for p in pts:
 vx=p[0]-ctr[0];vy=p[1]-ctr[1];ll=max(1e-6,math.hypot(vx,vy));q.append((p[0]+off*vx/ll,p[1]+off*vy/ll))
verts=[];faces=[]
def add_prism(poly,zlo,zhi):
 base=len(verts);n=len(poly);verts.extend([(x,y,zlo) for x,y in poly]+[(x,y,zhi) for x,y in poly]);faces.append(tuple(base+n+i for i in range(n)));faces.append(tuple(base+i for i in reversed(range(n))))
 for i in range(n):faces.append((base+i,base+(i+1)%n,base+n+(i+1)%n,base+n+i))
for i,(a,b) in enumerate(segments):add_prism([a,b,q[i+1],q[i]],z0,z1)
# Fill each faceted curve joint so adjacent canopy panels meet without holes.
for i in range(1,len(pts)-1):
 poly=[pts[i],q[i-1],q[i]]
 # Skip near-degenerate tips, which can occur where adjacent offset normals are collinear.
 area=abs((poly[1][0]-poly[0][0])*(poly[2][1]-poly[0][1])-(poly[1][1]-poly[0][1])*(poly[2][0]-poly[0][0]))
 if area>1e-5:add_prism(poly,z0,z1)
me=bpy.data.meshes.new('R7 connected GIS curve-following canopy mesh');me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials['LWSN_Bedford_Limestone']);me.update();can=bpy.data.objects.new('LWSN_R7_GIS_Matched_Vestibule_Canopy',me);asset.objects.link(can);can.parent=root;can.matrix_parent_inverse=__import__('mathutils').Matrix.Identity(4)
for k,v in {'source':'Purdue CS first-floor plan + GIS FID 59 footprint + Purdue exterior photograph','footprint_status':'Exact footprint contour follows GIS-only vestibule boundary; 0.55 m overhang is estimated','height_status':'3.78 m top is an appearance estimate from the exterior photograph, not measured','uncertainty':'Roof elevation and exact canopy projection are not published.'}.items():can[k]=v
# Add clear bronze jambs/transom/central stile to the paired entrance panels.
a=Vector((segments[4][0][0],segments[4][0][1],0));b=Vector((segments[4][1][0],segments[4][1][1],0));d=b-a;L=d.length;d.normalize();mid=a.lerp(b,.5);op=2.1;t0=(1-op/L)/2;t1=1-t0
j0=a.lerp(b,t0);jm=a.lerp(b,(t0+t1)/2);j1=a.lerp(b,t1)
bronze=bpy.data.materials['LWSN_Dark_Aluminum_Bronze']
def beam(name,center,length,depth,height,angle,z):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(center[0],center[1],z));o=bpy.context.object;o.name=name;o.dimensions=(length,depth,height);o.rotation_euler.z=angle;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 asset.objects.link(o);o.parent=root;o.matrix_parent_inverse=__import__('mathutils').Matrix.Identity(4);o.data.materials.append(bronze);o['source']='Illustrative door framing within plan-marked vestibule opening';o['evidence_status']='Presence/location plan-supported; member dimensions illustrative';return o
angle=math.atan2(d.y,d.x);normal=Vector((-d.y,d.x,0));# orient beams in wall plane
for idx,p in enumerate((j0,j1)):beam('LWSN_R7_Vestibule_Door_Jamb_'+str(idx+1),p,0.075,0.075,2.75,angle,2.175)
beam('LWSN_R7_Vestibule_Door_Center_Stile',jm,0.055,0.08,2.75,angle,2.175)
beam('LWSN_R7_Vestibule_Door_Head',jm,2.1,0.075,0.08,angle,3.51)
# Two small bronze pull handles, projected onto the glass plane.
for s in (-1,1):
 p=jm+d*(s*.38)+normal*.055; beam('LWSN_R7_Vestibule_Door_Pull_'+str(s),p,.32,.045,.045,angle,1.75)
# Name plaque is explicitly photo-supported, set on the canopy fascia at the entry opening.
# Use a compact object-level sign; precise lettering size and position remain illustrative.
bpy.ops.object.text_add(location=(jm.x+normal.x*.14,jm.y+normal.y*.14,3.56))
txt=bpy.context.object;txt.name='LWSN_R7_Vestibule_Sign_Text';txt.data.body='LAWSON COMPUTER SCIENCE BUILDING';txt.data.align_x='CENTER';txt.data.size=.20;txt.data.extrude=.002
# Align the sign with entrance wall tangent and face out.
from mathutils import Matrix as M
t=Vector((d.x,d.y,0));n=Vector((normal.x,normal.y,0));up=Vector((0,0,1));txt.rotation_euler=M((t,up,n)).transposed().to_euler()
for c in list(txt.users_collection):c.objects.unlink(txt)
asset.objects.link(txt);txt.parent=root;txt.matrix_parent_inverse=M.Identity(4);txt.data.materials.append(bronze);txt['source']='Purdue exterior photograph of Lawson entrance';txt['evidence_status']='Building name source-supported; text size and plaque placement illustrative.'
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(json.dumps({'canopy':can.name,'faces':len(can.data.polygons),'bounds':list(can.dimensions),'door_frames_added':7},indent=2))
