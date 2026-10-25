"""R12.9 localized folded roof apex and photo-supported curtainwall shading."""
import bpy, bmesh, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
EXPECTED='59fd4e7ac4b4887cad2951e06ded82cf09e713592d320ca4fab4e0445e97649e'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(ASSET)!=EXPECTED: raise RuntimeError('Asset changed since R12.8; refusing to overwrite: '+sha(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_neil_armstrong_hall'];root=bpy.data.objects['AssetRoot_neil_armstrong_hall']
deck=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
if len(col.objects)!=445 or len(deck.data.vertices)!=371 or len(deck.data.polygons)!=342:
    raise RuntimeError('R12.8 inventory/cleanup changed; refusing edits')

# Reshape only the inferred Z profile. The 2023 orthophoto/eaves XY trace and
# peak ceiling are preserved; the photo-based peak is concentrated at the
# north-west corner to produce a folded triangular wing instead of a broad arch.
inner=[17.10,17.35,17.20,16.45,16.75]
inner_next=[17.35,17.20,16.45,16.75,17.10]
inv=deck.matrix_world.inverted()
for seg in range(5):
    for j in range(4):
        t=j/3
        for k in range(9):
            s=k/8
            if seg==0: zo=21.5*(1-s)+17.6*s
            elif seg==4: zo=17.6*(1-s)+21.5*s
            else: zo=17.6
            zi=inner[seg]*(1-s)+inner_next[seg]*s
            warp=.35*math.sin(math.pi*t)*math.sin(math.pi*s)
            z=zo*(1-t)+zi*t+warp
            base=8+((seg*4+j)*9+k)*2
            for idx,dz in ((base,0.0),(base+1,-.18)):
                w=deck.matrix_world@deck.data.vertices[idx].co;w.z=z+dz
                deck.data.vertices[idx].co=inv@w
deck.data.update()
deck['R12_9_folded_wing']='Photo-based inferred profile concentrates the existing <=21.5 m peak at the north-west roof corner and tapers along the two adjacent eaves to 17.6 m. Registered orthophoto XY and 0.18 m shell thickness are unchanged. No measured roof elevation/profile is available.'
deck['R12_9_eaves_limit']='The 2023 imagery traces visible roof/eaves only and does not verify structural walls or courtyard edges.'

# Extend the existing photo-derived long-wing glazing band down one facade bay
# height and add a clear steel mullion rhythm. This stays on the existing wall
# object; stationing and height are still visual inference, not a schedule.
wall=bpy.data.objects['ARMS_West_Wall_North'];mesh=wall.data
glass_faces=[]
for p in mesh.polygons:
    if p.material_index!=1: continue
    pts=[wall.matrix_world@mesh.vertices[i].co for i in p.vertices]
    xs=[v.x for v in pts];zs=[v.z for v in pts]
    if max(xs)-min(xs)>40 and min(zs)>14 and max(zs)>18:
        glass_faces.append(p)
if len(glass_faces)!=1: raise RuntimeError(f'Expected one upper glazing strip face, found {len(glass_faces)}')
glass=glass_faces[0]
for i in glass.vertices:
    w=wall.matrix_world@mesh.vertices[i].co
    if w.z<16: w.z=12.35
    mesh.vertices[i].co=wall.matrix_world.inverted()@w
steel=bpy.data.materials['ARMS_Mullion_Steel']
steel_i=list(mesh.materials).index(steel)
bm=bmesh.new();bm.from_mesh(mesh)
def add_wall_quad(points,mi):
    vs=[bm.verts.new(wall.matrix_world.inverted()@Vector(p)) for p in points]
    f=bm.faces.new(vs);f.material_index=mi
# Vertical rhythm based on photo-visible curtainwall framing; 2.4 m pitch is
# a drawing estimate and is explicitly not an as-built facade schedule.
x0,x1=-59.0,-13.0;ybar=-3.855;z0,z1=12.35,18.85
pitch=2.4;count=round((x1-x0)/pitch)
for n in range(1,count):
    x=x0+n*(x1-x0)/count;h=.055
    add_wall_quad([(x-h,ybar,z0),(x+h,ybar,z0),(x+h,ybar,z1),(x-h,ybar,z1)],steel_i)
# Additional transom line visually subdivides the enlarged curtainwall field.
z=15.55;h=.065
add_wall_quad([(x0,ybar,z-h),(x1,ybar,z-h),(x1,ybar,z+h),(x0,ybar,z+h)],steel_i)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free();mesh.update()
wall['R12_9_photo_glazing']='Expanded R12.5 visual window band to z=12.35–18.85 m and added vertical framing plus a middle transom using the large curtainwall zone visible in the 2016 project photographs. Approximate location/cadence; no dimensioned elevation.'

# Kawneer identifies a Versoleil outrigger sunshade system; project photos show
# projecting horizontal members on the glazed atrium. Make one mesh object with
# bay-by-bay fins aligned to the existing curtainwall transoms.
alum=bpy.data.materials.get('ARMS_R12_9_Versoleil_Aluminum') or bpy.data.materials.new('ARMS_R12_9_Versoleil_Aluminum')
alum.use_nodes=True;bs=next(n for n in alum.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(.46,.50,.53,1);bs.inputs['Metallic'].default_value=.72;bs.inputs['Roughness'].default_value=.28
alum.diffuse_color=(.46,.50,.53,1)
verts=[];faces=[]
def add_fin(a,b,norm,depth=.65,thick=.14):
    # The glass-front line is the back edge; extend the aluminum blade outward.
    half=thick/2;off=norm.normalized()*depth
    pts=[Vector((a.x,a.y,level-half)) for level in (0,)] # placeholder overridden below
    zlevel=(a.z+b.z)/2
    p0=Vector((a.x,a.y,zlevel-half));p1=Vector((b.x,b.y,zlevel-half))
    p2=p1+off;p3=p0+off
    p4=Vector((a.x,a.y,zlevel+half));p5=Vector((b.x,b.y,zlevel+half));p6=p5+off;p7=p4+off
    base=len(verts);verts.extend([tuple(p) for p in (p0,p1,p2,p3,p4,p5,p6,p7)])
    faces.extend([tuple(base+i for i in f) for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0))])

added_bays=0
for i in range(16):
    o=bpy.data.objects.get(f'ARMS_Curtain_Glass_Bay_{i}')
    if o is None: raise RuntimeError(f'Missing curtainwall bay {i}')
    radial=Vector((.027*((o.bound_box[0][0]+o.bound_box[6][0])/2),1,0)).normalized()
    candidates=[]
    for p in o.data.polygons:
        n=(o.matrix_world.to_3x3()@p.normal).normalized()
        pts=[o.matrix_world@o.data.vertices[v].co for v in p.vertices]
        zs=[v.z for v in pts]
        if max(zs)-min(zs)>15:
            candidates.append((n.dot(radial),p,pts))
    if not candidates: raise RuntimeError(f'No broad vertical curtainwall face for bay {i}')
    score,p,front=max(candidates,key=lambda q:q[0])
    if score<.6: raise RuntimeError(f'Curtainwall bay {i} outward normal is ambiguous: {score}')
    low=sorted([v for v in front if v.z<1],key=lambda v:v.x)
    if len(low)!=2: raise RuntimeError(f'Unexpected front-edge geometry at bay {i}')
    a,b=low
    for level in (4.8,9.6,14.4):
        aa=Vector((a.x,a.y,level));bb=Vector((b.x,b.y,level));add_fin(aa,bb,radial)
    added_bays+=1

# Matching slim outriggers across the expanded long-wall glazing. They face
# south from the candidate facade; their exact direction/spacing remains visual.
for level in (14.5,17.2):
    intervals=19
    for n in range(intervals):
        a=x0+n*(x1-x0)/intervals+.03;b=x0+(n+1)*(x1-x0)/intervals-.03
        add_fin(Vector((a,-3.855,level)),Vector((b,-3.855,level)),Vector((0,-1,0)),depth=.55,thick=.12)

sunmesh=bpy.data.meshes.new('ARMS_R12_9_Versoleil_Outrigger_Mesh')
sunmesh.from_pydata(verts,[],faces);sunmesh.materials.append(alum);sunmesh.update(calc_edges=True)
bm=bmesh.new();bm.from_mesh(sunmesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(sunmesh);bm.free();sunmesh.update()
sunobj=bpy.data.objects.new('ARMS_R12_9_Versoleil_Outriggers',sunmesh);col.objects.link(sunobj);sunobj.parent=root
sunobj['source_note']='Photo-derived projecting aluminum fins aligned to curtainwall transoms; Kawneer identifies a Versoleil outrigger shading system. Fin depth, location and cadence are visual estimates, not an as-built schedule.'
sunobj['scope']='48 fins on sixteen curtainwall bays at three transom levels; 38 fins on expanded north-side glazing at two levels.'

bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'revision':'R12.9','asset':str(ASSET),'sha256':sha(ASSET),'collection_objects':len(col.objects),'scene_objects':len(bpy.data.objects),'canopy_vertices':len(deck.data.vertices),'canopy_faces':len(deck.data.polygons),'roof_profile':'localized NW triangular apex, existing XY/eaves trace preserved','upper_glazing_vertices':len(wall.data.vertices),'upper_glazing_faces':len(wall.data.polygons),'sunshade_object':sunobj.name,'sunshade_fins':len(faces)//6,'curtainwall_bays':added_bays,'sunshade_mesh_vertices':len(sunmesh.vertices),'sunshade_mesh_faces':len(sunmesh.polygons)},indent=2))
