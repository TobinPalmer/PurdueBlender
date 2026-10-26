"""Build the standalone First Street Towers West (FSTW) campus asset.

Run from the PurdueMap root with Blender 5.2:
  blender -b --python modular/buildings/build_massing_first_street_towers_west_fstw_b6c3bbe.py

Footprint/floor-count source: Purdue BuildingShapesZip4 FeatureServer 0, FID 858.
The six floor count is source data. Story heights, roof pitch/ridge, facade bay
spacing and room arrangement are clearly documented visual estimates.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[2]
ID="massing_first_street_towers_west_fstw_b6c3bbe"
ASSET=ROOT/f"modular/buildings/{ID}.blend"
SOURCE=ROOT/f"audit/first_street_towers_west_fstw_b6c3bbe/sources/purdue_buildingshapeszip4_fstw_fid858_2026-10-26.geojson"
EVIDENCE=ROOT/"audit/first_street_towers_west_fstw_b6c3bbe"
COLLECTION_NAME="Asset_"+ID
SCENE_NAME="Building_"+ID
LAT0,LON0=40.4274,-86.9137
FLOORS=6
FLOOR_H=3.08             # estimate; official GIS provides floor count but no documented height
WALL_BASE=0.28
EAVE_Z=WALL_BASE+FLOORS*FLOOR_H
RIDGE_RISE=3.8           # roof pitch/ridge height estimated from official complex photos
SIMPLIFY_M=0.28


def material(name, color, roughness=.72, metallic=0.0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=roughness
    bs.inputs["Metallic"].default_value=metallic
    return m


def brick_material():
    m=material("FSTW | estimated Purdue red-brown running brick",(.33,.105,.071),.86)
    n=m.node_tree.nodes; l=m.node_tree.links
    bs=next(x for x in n if x.type=="BSDF_PRINCIPLED")
    coord=n.new("ShaderNodeTexCoord")
    brick=n.new("ShaderNodeTexBrick")
    brick.inputs["Color1"].default_value=(.41,.15,.098,1)
    brick.inputs["Color2"].default_value=(.24,.065,.045,1)
    brick.inputs["Mortar"].default_value=(.32,.29,.25,1)
    brick.inputs["Scale"].default_value=1.0
    brick.inputs["Brick Width"].default_value=.22
    brick.inputs["Row Height"].default_value=.065
    brick.inputs["Mortar Size"].default_value=.007
    noise=n.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value=8.0; noise.inputs["Detail"].default_value=2.0
    bump=n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.10; bump.inputs["Distance"].default_value=.025
    l.new(coord.outputs["UV"],brick.inputs["Vector"]); l.new(coord.outputs["UV"],noise.inputs["Vector"])
    l.new(brick.outputs["Color"],bs.inputs["Base Color"]); l.new(noise.outputs["Fac"],bump.inputs["Height"]); l.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return m


def add_mesh(name, vertices, faces, mat, col):
    mesh=bpy.data.meshes.new(name+"Mesh")
    mesh.from_pydata(vertices,[],faces); mesh.materials.append(mat); mesh.update()
    # Metric planar UVs keep brick courses legible on all rotated facade planes.
    uv=mesh.uv_layers.new(name="Metric planar UV")
    for poly in mesh.polygons:
        ids=list(poly.vertices)
        if len(ids)<3: continue
        p0=Vector(mesh.vertices[ids[0]].co); p1=Vector(mesh.vertices[ids[1]].co); pn=Vector(mesh.vertices[ids[-1]].co)
        e1=(p1-p0).normalized(); normal=(p1-p0).cross(pn-p0)
        if normal.length<1e-8: continue
        normal.normalize(); e2=normal.cross(e1).normalized()
        for loop_idx,vid in zip(poly.loop_indices,ids):
            v=Vector(mesh.vertices[vid].co)-p0
            uv.data[loop_idx].uv=(v.dot(e1),v.dot(e2))
    obj=bpy.data.objects.new(name,mesh); col.objects.link(obj)
    return obj


def add_quads(name, quads, mat, col):
    v=[]; f=[]
    for quad in quads:
        base=len(v); v.extend(tuple(p) for p in quad); f.append(tuple(range(base,base+len(quad))))
    return add_mesh(name,v,f,mat,col)


def add_boxes(name, boxes, mat, col):
    v=[]; f=[]
    for x0,x1,y0,y1,z0,z1 in boxes:
        i=len(v); v.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                           (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
        f.extend([(i+0,i+3,i+2,i+1),(i+4,i+5,i+6,i+7),(i+0,i+1,i+5,i+4),
                  (i+1,i+2,i+6,i+5),(i+2,i+3,i+7,i+6),(i+3,i+0,i+4,i+7)])
    return add_mesh(name,v,f,mat,col)


def simplify_ring(points,tolerance):
    pts=list(points[:-1] if points[0]==points[-1] else points)
    a=pts[0]; far=max(range(1,len(pts)),key=lambda i:(pts[i][0]-a[0])**2+(pts[i][1]-a[1])**2)
    def dp(line):
        keep={0,len(line)-1}; stack=[(0,len(line)-1)]
        while stack:
            st,en=stack.pop(); x0,y0=line[st]; x1,y1=line[en]; dx=x1-x0; dy=y1-y0; denom=dx*dx+dy*dy
            best,bi=-1,None
            for j in range(st+1,en):
                x,y=line[j]
                u=max(0,min(1,((x-x0)*dx+(y-y0)*dy)/denom)) if denom else 0
                d=math.hypot(x-(x0+u*dx),y-(y0+u*dy))
                if d>best: best,bi=d,j
            if bi is not None and best>tolerance:
                keep.add(bi); stack.extend([(st,bi),(bi,en)])
        return [line[j] for j in sorted(keep)]
    first=dp(pts[:far+1]+pts[:1]); second=dp(pts[far:]+pts[:1])
    ring=first[:-1]+second[:-1]; out=[]
    for p in ring:
        if not out or math.dist(p,out[-1])>.04: out.append(p)
    return out


def point_inside(point,ring):
    x,y=point; inside=False; j=len(ring)-1
    for i,(xi,yi) in enumerate(ring):
        xj,yj=ring[j]
        if ((yi>y)!=(yj>y)) and x<(xj-xi)*(y-yi)/(yj-yi+1e-30)+xi: inside=not inside
        j=i
    return inside


def area2d(r):
    return .5*sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r)))


def look_at(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def make_render_setup(scene, center, label):
    scene.render.engine="CYCLES"; scene.cycles.samples=28
    scene.render.resolution_x=1500; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
    scene.render.image_settings.color_mode="RGBA"
    scene.view_settings.view_transform="AgX"; scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=.1
    world=bpy.data.worlds.new("FSTW | neutral evidence world"); world.use_nodes=True; scene.world=world
    background=next(n for n in world.node_tree.nodes if n.type=="BACKGROUND")
    background.inputs["Color"].default_value=(.25,.32,.43,1); background.inputs["Strength"].default_value=.65
    ld=bpy.data.lights.new("FSTW | soft daylight","AREA"); lo=bpy.data.objects.new(ld.name,ld); scene.collection.objects.link(lo)
    lo.location=(center[0]-56,center[1]-74,98); ld.energy=3600; ld.shape="DISK"; ld.size=70
    cd=bpy.data.cameras.new("FSTW | evidence camera"); cam=bpy.data.objects.new(cd.name,cd); scene.collection.objects.link(cam)
    cam.location=(center[0]-90,center[1]-145,53); cd.lens=58; look_at(cam,(center[0],center[1],EAVE_Z*.54)); scene.camera=cam
    scene.render.filepath=str(EVIDENCE/f"{label}.png")
    return cam


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene; scene.name=SCENE_NAME
    col=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(col)
    geo=json.loads(SOURCE.read_text(encoding="utf-8"))
    feat=next((f for f in geo["features"] if f["properties"].get("FID")==858),None)
    if not feat or feat["properties"].get("BLDG_ABBR")!="FSTW": raise RuntimeError("Expected official FSTW feature FID 858 missing")
    raw=feat["geometry"]["coordinates"][0]
    projected=[((lon-LON0)*111412.84*math.cos(math.radians(LAT0)),(lat-LAT0)*111040.0) for lon,lat in raw]
    ring=simplify_ring(projected,SIMPLIFY_M)
    if len(ring)<8: raise RuntimeError("GIS simplification unexpectedly collapsed footprint")
    if area2d(ring)<0: ring.reverse()
    minx=min(x for x,y in ring); maxx=max(x for x,y in ring); miny=min(y for x,y in ring); maxy=max(y for x,y in ring)
    cx=(minx+maxx)/2; cy=(miny+maxy)/2
    props=feat["properties"]

    brick=brick_material()
    stone=material("FSTW | warm limestone / precast estimates",(.70,.66,.58),.77)
    glass=material("FSTW | blue-gray residential glazing",(.075,.16,.22),.23,.12)
    darkglass=material("FSTW | recessed dark glazing",(.027,.055,.075),.30,.14)
    roofmat=material("FSTW | charcoal slate / standing-seam roof estimate",(.20,.215,.22),.76,.05)
    rn=roofmat.node_tree.nodes; rl=roofmat.node_tree.links
    rbs=next(n for n in rn if n.type=="BSDF_PRINCIPLED")
    rnoise=rn.new("ShaderNodeTexNoise"); rnoise.inputs["Scale"].default_value=18.0; rnoise.inputs["Detail"].default_value=2.0
    rbump=rn.new("ShaderNodeBump"); rbump.inputs["Strength"].default_value=.08; rbump.inputs["Distance"].default_value=.018
    rcoord=rn.new("ShaderNodeTexCoord"); rl.new(rcoord.outputs["Object"],rnoise.inputs["Vector"]); rl.new(rnoise.outputs["Fac"],rbump.inputs["Height"]); rl.new(rbump.outputs["Normal"],rbs.inputs["Normal"])
    roofedge=material("FSTW | slate ridge and flashing",(.19,.20,.20),.48,.28)
    slabmat=material("FSTW | interior warm gray concrete",(.48,.46,.41),.9)
    floor_mat=material("FSTW | carpet and corridor floor estimate",(.34,.31,.28),.94)
    interior=material("FSTW | interior gypsum partitions estimate",(.78,.73,.63),.88)
    metal=material("FSTW | dark bronze window metal",(.075,.09,.093),.36,.62)

    # GIS-derived continuous perimeter envelope.
    faces=[]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]
        faces.append([(p[0],p[1],WALL_BASE),(q[0],q[1],WALL_BASE),(q[0],q[1],EAVE_Z),(p[0],p[1],EAVE_Z)])
    walls=add_quads("FSTW | GIS perimeter walls, six levels",faces,brick,col)
    walls["basis"]="Purdue BuildingShapesZip4 FID 858, transformed EPSG:4326 to project local XY; RDP simplification 0.28m"

    # Foundation and ground-level masonry datum bands follow the true outline.
    base=[]; belt=[]; floorbands=[]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]; dx=q[0]-p[0]; dy=q[1]-p[1]; L=math.hypot(dx,dy)
        if L<.12: continue
        nx,ny=dy/L,-dx/L
        base.append([(p[0],p[1],.18),(q[0],q[1],.18),(q[0],q[1],.9),(p[0],p[1],.9)])
        belt.append([(p[0]+nx*.09,p[1]+ny*.09,WALL_BASE),(q[0]+nx*.09,q[1]+ny*.09,WALL_BASE),(q[0]+nx*.09,q[1]+ny*.09,WALL_BASE+.18),(p[0]+nx*.09,p[1]+ny*.09,WALL_BASE+.18)])
        for lev in range(1,FLOORS):
            z=WALL_BASE+lev*FLOOR_H
            floorbands.append([(p[0]+nx*.075,p[1]+ny*.075,z-.055),(q[0]+nx*.075,q[1]+ny*.075,z-.055),(q[0]+nx*.075,q[1]+ny*.075,z+.055),(p[0]+nx*.075,p[1]+ny*.075,z+.055)])
    add_quads("FSTW | limestone foundation / raised base",base,stone,col)
    add_quads("FSTW | narrow pale base course",belt,stone,col)
    add_quads("FSTW | restrained repeated story courses",floorbands,stone,col)

    # Triangulated slabs keep the exact concave GIS plan. Store one reusable shape and instance copies per level.
    loop=[Vector((x,y,0)) for x,y in ring]
    tris=tessellate_polygon([loop])
    slabv=[]; slabf=[]
    for tri in tris:
        idx=len(slabv); slabv.extend([tuple(loop[k]) for k in tri]); slabf.append((idx,idx+1,idx+2))
    floor_mesh=bpy.data.meshes.new("FSTW source-footprint floor mesh"); floor_mesh.from_pydata(slabv,[],slabf); floor_mesh.materials.append(floor_mat); floor_mesh.update()
    for lev in range(FLOORS):
        ob=bpy.data.objects.new(f"FSTW | interior floor plate {lev+1} of {FLOORS} (source outline)",floor_mesh.copy()); col.objects.link(ob)
        ob.location.z=WALL_BASE+lev*FLOOR_H+.03

    # Distinct room-cluster/corridor diagrams: two long wings and representative hall partitions.
    # The plan pattern is intentionally schematic; no publicly available as-built FSTW plan was found.
    room_faces=[]; corridor_faces=[]; partition_faces=[]
    # Known FSTW GIS outline separates two long arms around a courtyard. These survey-informed boxes only set the schematic circulation axis.
    arms=[(-1005.0,-992.0,-303.6,-255.4),(-978.0,-967.2,-309.7,-249.4)]
    for lev in range(FLOORS):
        z=WALL_BASE+lev*FLOOR_H+.06
        for ax0,ax1,ay0,ay1 in arms:
            mid=(ax0+ax1)/2
            # corridor runs along the long axis, both sides have a room band
            for y0 in [ay0+6.0+3.55*k for k in range(max(1,int((ay1-ay0-12)/3.55)) )]:
                y1=min(y0+2.7,ay1-2.5)
                if y1<=y0: continue
                if point_inside((mid,(y0+y1)/2),ring): corridor_faces.append([(mid-1.05,y0,z),(mid+1.05,y0,z),(mid+1.05,y1,z),(mid-1.05,y1,z)])
                for side in [-1,1]:
                    start=mid+side*1.05; end=mid+side*(min((ax1-ax0)/2-1.1,5.0))
                    for t in range(10):
                        yy=y0+(y1-y0)*(t+.5)/10; xx=(start+end)/2
                        if point_inside((xx,yy),ring):
                            x0=mid+side*1.05; x1=end
                            partition_faces.append([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)])
                            break
            # transverse room-entry/corridor divider lines at room module intervals
            step=3.75; y=ay0+6.0
            while y<ay1-5:
                x0=mid-1.05; x1=mid+1.05
                if point_inside((mid,y),ring):
                    partition_faces.append([(x0,y,z),(x1,y,z),(x1,y,z+2.48),(x0,y,z+2.48)])
                y+=step
    add_quads("FSTW | schematic lounge/corridor flooring",corridor_faces,floor_mat,col)
    parts=add_quads("FSTW | schematic residential room-cluster partitions",partition_faces,interior,col)
    parts["certainty"]="Illustrative interior circulation; Purdue’s public plan is generic, not tower-specific."

    # Window rhythm follows every substantial straight GIS segment. Facade bay dimensions are estimates.
    panes=[]; frames=[]; mullions=[]; sills=[]; window_count=0
    floor_centers=[WALL_BASE+.8]+[WALL_BASE+k*FLOOR_H+.76 for k in range(1,FLOORS)]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
        if length<3.0: continue
        ux,uy=dx/length,dy/length; nx,ny=uy,-ux
        bays=max(1,int(length//3.15)); spacing=length/bays; ww=min(1.24,spacing*.58); hh=1.68; frame=.09
        for b in range(bays):
            t=(b+.5)*spacing; x=p[0]+ux*t+nx*.09; y=p[1]+uy*t+ny*.09
            for zc in floor_centers:
                z0=zc-hh/2; z1=zc+hh/2
                a=(x-ux*ww/2,y-uy*ww/2); d=(x+ux*ww/2,y+uy*ww/2)
                panes.append([(a[0],a[1],z0),(d[0],d[1],z0),(d[0],d[1],z1),(a[0],a[1],z1)])
                # Frame surrounds are in limestone, set slightly proud of glass; one vertical divider and two lights.
                for side in [-1,1]:
                    cc=x+ux*side*(ww/2+frame/2); cyw=y+uy*side*(ww/2+frame/2)
                    frames.append([(cc-ux*frame/2+nx*.11,cyw-uy*frame/2+ny*.11,z0-frame/2),(cc+ux*frame/2+nx*.11,cyw+uy*frame/2+ny*.11,z0-frame/2),(cc+ux*frame/2+nx*.11,cyw+uy*frame/2+ny*.11,z1+frame/2),(cc-ux*frame/2+nx*.11,cyw-uy*frame/2+ny*.11,z1+frame/2)])
                for zz in [z0,z1]:
                    frames.append([(x-ux*(ww/2+frame)+nx*.11,y-uy*(ww/2+frame)+ny*.11,zz-frame/2),(x+ux*(ww/2+frame)+nx*.11,y+uy*(ww/2+frame)+ny*.11,zz-frame/2),(x+ux*(ww/2+frame)+nx*.11,y+uy*(ww/2+frame)+ny*.11,zz+frame/2),(x-ux*(ww/2+frame)+nx*.11,y-uy*(ww/2+frame)+ny*.11,zz+frame/2)])
                for u in [-.025,.025]:
                    mx=x+ux*u+nx*.14; my=y+uy*u+ny*.14
                    mullions.append([(mx-ux*.018,my-uy*.018,z0),(mx+ux*.018,my+uy*.018,z0),(mx+ux*.018,my+uy*.018,z1),(mx-ux*.018,my-uy*.018,z1)])
                zmid=zc
                mullions.append([(x-ux*ww*.44+nx*.14,y-uy*ww*.44+ny*.14,zmid-.025),(x+ux*ww*.44+nx*.14,y+uy*ww*.44+ny*.14,zmid-.025),(x+ux*ww*.44+nx*.14,y+uy*ww*.44+ny*.14,zmid+.025),(x-ux*ww*.44+nx*.14,y-uy*ww*.44+ny*.14,zmid+.025)])
                sills.append([(x-ux*(ww/2+frame)+nx*.16,y-uy*(ww/2+frame)+ny*.16,z0-.08),(x+ux*(ww/2+frame)+nx*.16,y+uy*(ww/2+frame)+ny*.16,z0-.08),(x+ux*(ww/2+frame)+nx*.16,y+uy*(ww/2+frame)+ny*.16,z0+.01),(x-ux*(ww/2+frame)+nx*.16,y-uy*(ww/2+frame)+ny*.16,z0+.01)])
                window_count+=1
    add_quads("FSTW | recessed blue-gray double-light glazing",panes,glass,col)
    add_quads("FSTW | pale stone window surrounds",frames,stone,col)
    add_quads("FSTW | dark slim window mullions",mullions,metal,col)
    add_quads("FSTW | projecting cast-stone sills",sills,stone,col)

    # Low-slope roof deck plus two longitudinal gabled wings and a connector roof.
    # GIS outlines define walls only; all pitch/ridge placements below are photo-based estimates.
    deck_tris=[]
    for tri in tris:
        base=len(deck_tris); deck_tris.extend([(loop[k].x,loop[k].y,EAVE_Z) for k in tri])
    roofdeck=add_mesh("FSTW | roof deck beneath estimated gabled roof",deck_tris,[tuple(range(i,i+3)) for i in range(0,len(deck_tris),3)],roofmat,col)
    roofdeck["certainty"]="Roof plan/pitch inferred from official complex photograph; no FSTW roof plan located."

    def gabled_bar(name,x0,x1,y0,y1,axis,peakrise):
        """Create two pitched roof planes and triangular gable ends over a simple rectangular wing."""
        if axis=="y":
            mid=(x0+x1)/2; z=EAVE_Z+peakrise
            quads=[[(x0,y0,EAVE_Z),(mid,y0,z),(mid,y1,z),(x0,y1,EAVE_Z)],
                   [(mid,y0,z),(x1,y0,EAVE_Z),(x1,y1,EAVE_Z),(mid,y1,z)]]
            # pitched roofs are clipped to the estimated wing rectangle
            add_quads(name+" | two pitched roof slopes",quads,roofmat,col)
            gables=[[(x0,y0,EAVE_Z),(x1,y0,EAVE_Z),(mid,y0,z)],[(x1,y1,EAVE_Z),(x0,y1,EAVE_Z),(mid,y1,z)]]
            add_quads(name+" | brick gable-end infill",gables,brick,col)
            # ridge cap & standing seams in low-relief strips
            add_boxes(name+" | ridge cap",[(mid-.10,mid+.10,y0-.12,y1+.12,z-.09,z+.09)],roofedge,col)
            seams=[]
            for sx in [x0+(x1-x0)*i/7 for i in range(1,7)]:
                rz=EAVE_Z+peakrise*(1-abs(sx-mid)/((x1-x0)/2))
                seams.append([(sx,y0,EAVE_Z+.025),(sx,y1,EAVE_Z+.025),(sx,y1,rz+.035),(sx,y0,rz+.035)])
            add_quads(name+" | subtle standing seams",seams,roofedge,col)
        else:
            mid=(y0+y1)/2; z=EAVE_Z+peakrise
            quads=[[(x0,y0,EAVE_Z),(x1,y0,EAVE_Z),(x1,mid,z),(x0,mid,z)],
                   [(x0,mid,z),(x1,mid,z),(x1,y1,EAVE_Z),(x0,y1,EAVE_Z)]]
            add_quads(name+" | two connector roof slopes",quads,roofmat,col)
            gables=[[(x0,y0,EAVE_Z),(x1,y0,EAVE_Z),(x1,mid,z),(x0,mid,z)],[(x0,y1,EAVE_Z),(x1,y1,EAVE_Z),(x1,mid,z),(x0,mid,z)]]
            add_boxes(name+" | connector roof ridge cap",[(x0-.1,x1+.1,mid-.1,mid+.1,z-.09,z+.09)],roofedge,col)
    # Long arms are source-footprint aligned: W wing (west), E wing (east), with small north/south roof junctions.
    gabled_bar("FSTW | west courtyard wing roof (estimated)",-1005.0,-992.0,-303.8,-255.2,"y",RIDGE_RISE)
    gabled_bar("FSTW | east courtyard wing roof (estimated)",-978.0,-967.1,-309.8,-249.3,"y",RIDGE_RISE)
    gabled_bar("FSTW | south wing junction roof (estimated)",-992.1,-977.8,-316.65,-307.0,"x",RIDGE_RISE*.9)
    gabled_bar("FSTW | north wing junction roof (estimated)",-992.1,-977.7,-251.9,-242.35,"x",RIDGE_RISE*.9)

    # A conservative, documented illustrative entrance facing the interior court;
    # the public photos show the FST complex entrance but do not isolate this tower's door.
    # Use a plaque-sized inset, stone portal and dark glazed door on inner courtyard wall.
    door_x=-992.08; door_y=-280.0
    if point_inside((door_x-.05,door_y),ring):
        # east-facing wall of the west wing; recessed door and transom
        portal=[[(door_x+.05,door_y-1.55,.28),(door_x+.05,door_y+1.55,.28),(door_x+.05,door_y+1.55,3.85),(door_x+.05,door_y-1.55,3.85)]]
        add_quads("FSTW | illustrative courtyard-facing entry portal",portal,stone,col)
        door=[[(door_x+.11,door_y-1.0,.3),(door_x+.11,door_y+1.0,.3),(door_x+.11,door_y+1.0,2.75),(door_x+.11,door_y-1.0,2.75)]]
        add_quads("FSTW | illustrative glazed secondary entry",door,darkglass,col)
        canopy=add_boxes("FSTW | modest entry canopy estimate",[(door_x-.65,door_x+.8,door_y-1.85,door_y+1.85,3.88,4.12)],stone,col)
        canopy["certainty"]="Illustrative location only; not isolated or verified in tower-specific photograph."

    # Scene notes for downstream modular asset users.
    scene["asset_id"]=ID
    scene["official_identity"]="Purdue BuildingShapesZip4 FID 858: First Street Towers, Western (FSTW); 1270 1st Street; 6 levels; built 2010 / occupied 2012 per epoch fields."
    scene["source_feature"]="Purdue BuildingShapesZip4 FeatureServer/0 FID 858; retrieved 2026-10-26; EPSG:4326"
    scene["footprint_method"]="Official GIS ring transformed using project local approximation; RDP simplified 0.28m; walls conform the simplified ring."
    scene["height_uncertainty"]="Six floors source-supported. 3.08m floor-to-floor, 18.76m wall top, 3.8m estimated gable rise; nominal plane ridge is 22.56m and ridge-cap detail reaches 22.65m. GIS Extrution=49 has undocumented units/meaning and is not treated as measured."
    scene["facade_uncertainty"]="Official Purdue exterior photos depict the connected First Street Towers complex and do not unambiguously isolate FSTW. Red-brown brick, pale window surrounds, and gabled roof silhouette are photo-supported at complex level; exact FSTW bay count and window schedule are estimates."
    scene["interior_uncertainty"]="Floor plates and room partitions are schematic residential clusters; Purdue public floor-plan illustration and general accommodations data do not establish an as-built FSTW floor plan."
    scene["window_count_estimate"]=window_count
    scene["osm_vs_gis_note"]="OSM way 283274997 agrees on location/identity but differs from Purdue GIS footprint: IoU 0.9415; max boundary distance 1.396m in project local frame. The Purdue GIS perimeter is modeled."

    center=(cx,cy)
    cam=make_render_setup(scene,center,"fstw_exterior_candidate")
    # exterior plus footprint top view
    old=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.type,cam.data.ortho_scale)
    cam.data.type="ORTHO"; cam.data.ortho_scale=max(maxx-minx,maxy-miny)*1.16
    cam.location=(cx,cy,EAVE_Z+105); look_at(cam,(cx,cy,0)); scene.render.filepath=str(EVIDENCE/"fstw_footprint_top_candidate.png")
    bpy.ops.render.render(write_still=True)
    cam.location=old[0]; cam.rotation_euler=old[1]; cam.data.type=old[2]; cam.data.ortho_scale=old[3]
    scene.render.filepath=str(EVIDENCE/"fstw_exterior_candidate.png"); bpy.ops.render.render(write_still=True)

    # Interior evidence: hide only outside facade/roof/window layers, leave floorplate and room-circulation models visible.
    to_hide=[walls,roofdeck]
    for obj in col.objects:
        if any(k in obj.name for k in ["pitched roof slopes","gable-end infill","roof ridge cap","standing seams","connector roof"]): to_hide.append(obj)
        if any(k in obj.name for k in ["glazing","window surrounds","mullions","sills","story courses","foundation","base course"]): to_hide.append(obj)
    original={o:o.hide_render for o in set(to_hide)}
    floors=[o for o in col.objects if "interior floor plate" in o.name]
    for o in floors[1:]: o.hide_render=True
    for o in to_hide:o.hide_render=True
    cam.data.type="ORTHO"; cam.data.ortho_scale=max(maxx-minx,maxy-miny)*1.16; cam.location=(cx,cy,95); look_at(cam,(cx,cy,0))
    scene.render.filepath=str(EVIDENCE/"fstw_schematic_interior_candidate.png"); bpy.ops.render.render(write_still=True)
    for o,v in original.items():o.hide_render=v
    for o in floors[1:]:o.hide_render=False
    cam.location=old[0]; cam.rotation_euler=old[1]; cam.data.type=old[2]; cam.data.ortho_scale=old[3]
    scene.render.filepath=str(EVIDENCE/"fstw_exterior_candidate.png")

    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    (EVIDENCE/"candidate_footprint_xy.json").write_text(json.dumps({
        "asset_id":ID,"source":"Purdue BuildingShapesZip4 FID 858","xy_m":ring,
        "local_frame":{"origin_lat":LAT0,"origin_lon":LON0,"x":"(lon+86.9137)*111412.84*cos(radians(40.4274))","y":"(lat-40.4274)*111040.0"},
        "simplification_tolerance_m":SIMPLIFY_M},indent=2),encoding="utf-8")
    print("FSTW_BUILD_SUMMARY",json.dumps({"asset":str(ASSET),"asset_id":ID,"collection":COLLECTION_NAME,"scene":SCENE_NAME,
        "fid":props["FID"],"levels":FLOORS,"raw_ring_vertices":len(raw)-1,"simplified_ring_vertices":len(ring),
        "candidate_plan_area_m2":round(abs(area2d(ring)),3),"candidate_bounds_xy":[round(minx,3),round(miny,3),round(maxx,3),round(maxy,3)],
        "window_count_estimate":window_count,"object_count":len(col.objects),"material_count":len({m.name for o in col.objects if o.type=="MESH" for m in o.data.materials}),
        "exterior_render":str(EVIDENCE/"fstw_exterior_candidate.png"),"top_render":str(EVIDENCE/"fstw_footprint_top_candidate.png"),
        "interior_render":str(EVIDENCE/"fstw_schematic_interior_candidate.png")},indent=2))


if __name__=="__main__": main()
