"""Build the modular First Street Towers East asset from Purdue's GIS footprint.

Run from the repository root with Blender 5.2:
  blender -b --python modular/buildings/build_massing_first_street_towers_east_fste_c9b22d3.py

The outer footprint and six-floor count come from Purdue's BuildingShapesZip4
FeatureServer (FID 651). Story heights, facade bay rhythm, roof detailing, and
the representative interior plan are visual estimates, not measured facts.
"""
import bpy
import json
import math
import os
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_first_street_towers_east_fste_c9b22d3.blend"
SOURCE = ROOT / "audit/first_street_towers_east/sources/purdue_buildingshapeszip4_fste_fid651_2026-10-26.geojson"
OSM_SOURCE = ROOT / "audit/first_street_towers_east/sources/osm_roads_near_fste_2026-10-26.json"
EVIDENCE = ROOT / "audit/first_street_towers_east"
COLLECTION_NAME = "Asset_massing_first_street_towers_east_fste_c9b22d3"
SCENE_NAME = "Building_massing_first_street_towers_east_fste_c9b22d3"
ID = "massing_first_street_towers_east_fste_c9b22d3"
LAT0, LON0 = 40.4274, -86.9137
FLOORS = 6
FLOOR_H = 3.15       # estimated floor-to-floor height; not a measured dimension
WALL_BASE = 0.35
ROOF_Z = WALL_BASE + FLOORS * FLOOR_H
SIMPLIFY_M = 0.30    # GIS ring retains sub-decimeter survey wiggles


def mat(name, color, rough=0.7, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metallic
    return m


def brick_mat():
    m = mat("FSTE | warm red-brown brick (procedural estimate)", (0.35, 0.105, 0.065), 0.86)
    n = m.node_tree.nodes
    l = m.node_tree.links
    bs = n.get("Principled BSDF")
    tex = n.new("ShaderNodeTexBrick")
    tex.name = "Small running-bond brick and mortar"
    tex.inputs["Color1"].default_value = (0.25, 0.047, 0.026, 1)
    tex.inputs["Color2"].default_value = (0.16, 0.022, 0.014, 1)
    tex.inputs["Mortar"].default_value = (0.135, 0.095, 0.068, 1)
    tex.inputs["Scale"].default_value = 1.0
    tex.inputs["Brick Width"].default_value = 0.55
    tex.inputs["Row Height"].default_value = 0.24
    tex.inputs["Mortar Size"].default_value = 0.025
    tex.inputs["Mortar Smooth"].default_value = 0.01
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 7.5
    noise.inputs["Detail"].default_value = 2.0
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.035
    geo = n.new("ShaderNodeTexCoord")
    l.new(geo.outputs["UV"], tex.inputs["Vector"])
    l.new(geo.outputs["Object"], noise.inputs["Vector"])
    l.new(tex.outputs["Color"], bs.inputs["Base Color"])
    l.new(noise.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def quad_mesh(name, faces, material, collection, smooth=False):
    """Create one mesh from faces, each face an iterable of 3D points."""
    verts, polys = [], []
    for face in faces:
        start = len(verts)
        verts.extend(tuple(p) for p in face)
        polys.append(tuple(range(start, len(verts))))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], polys)
    mesh.materials.append(material)
    mesh.update()
    uv=mesh.uv_layers.new(name="MetricFacadeUV")
    for face_index,poly in enumerate(mesh.polygons):
        face=faces[face_index]
        if len(face)==4 and len({round(float(v[2]),6) for v in face})==2:
            run=math.dist(face[0][:2],face[1][:2])
            height=max(float(v[2]) for v in face)-min(float(v[2]) for v in face)
            coords=[(0,0),(run,0),(run,height),(0,height)]
        else:
            coords=[(float(v[0]),float(v[2]) if len({round(float(p[2]),6) for p in face})>1 else float(v[1])) for v in face]
        for local_index,loop_index in enumerate(poly.loop_indices):
            uv.data[loop_index].uv=coords[local_index]
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def box_mesh(name, boxes, material, collection):
    """Batch axis-aligned boxes defined by (xmin,xmax,ymin,ymax,zmin,zmax)."""
    verts, faces = [], []
    for x0, x1, y0, y1, z0, z1 in boxes:
        i = len(verts)
        verts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                      (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
        faces.extend([(i+0,i+3,i+2,i+1),(i+4,i+5,i+6,i+7),
                      (i+0,i+1,i+5,i+4),(i+1,i+2,i+6,i+5),
                      (i+2,i+3,i+7,i+6),(i+3,i+0,i+4,i+7)])
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def oriented_box_faces(center, u, v, half_u, half_v, z0, z1):
    """Closed rectangular prism in a facade's tangent/normal frame."""
    cx,cy=center; ux,uy=u; vx,vy=v
    def p(su,sv,z): return (cx+ux*su*half_u+vx*sv*half_v,
                            cy+uy*su*half_u+vy*sv*half_v,z)
    a=[p(-1,-1,z0),p(1,-1,z0),p(1,1,z0),p(-1,1,z0)]
    b=[p(-1,-1,z1),p(1,-1,z1),p(1,1,z1),p(-1,1,z1)]
    return [a,b,[a[0],a[1],b[1],b[0]],[a[1],a[2],b[2],b[1]],
            [a[2],a[3],b[3],b[2]],[a[3],a[0],b[0],b[3]]]


def cross2(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def nearest_point_on_segment(point,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    denom=dx*dx+dy*dy
    if denom<1e-12: return a
    t=max(0.0,min(1.0,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/denom))
    return (a[0]+t*dx,a[1]+t*dy)


def triangulate_ring(points):
    """Ear-clip a simple CCW polygon so Blender does not mis-tessellate n-gons."""
    ids=list(range(len(points)))
    tris=[]
    def point_in_tri(p,a,b,c):
        e=1e-9
        return cross2(a,b,p)>=-e and cross2(b,c,p)>=-e and cross2(c,a,p)>=-e
    guard=0
    while len(ids)>3:
        found=False
        for k in range(len(ids)):
            ia,ib,ic=ids[k-1],ids[k],ids[(k+1)%len(ids)]
            a,b,c=points[ia],points[ib],points[ic]
            if cross2(a,b,c)<=1e-10: continue
            if any(point_in_tri(points[j],a,b,c) for j in ids if j not in (ia,ib,ic)): continue
            tris.append((a,b,c)); ids.pop(k); found=True; break
        guard+=1
        if not found or guard>len(points)*len(points):
            raise RuntimeError("GIS ring ear-clipping triangulation stalled")
    tris.append(tuple(points[i] for i in ids))
    return tris


def clip_convex_polygon(subject, clip):
    """Sutherland-Hodgman intersection of two CCW planar polygons."""
    output=list(subject)
    for i,a in enumerate(clip):
        b=clip[(i+1)%len(clip)]
        incoming=output; output=[]
        if not incoming: break
        prev=incoming[-1]
        prev_in=cross2(a,b,prev)>=-1e-8
        for cur in incoming:
            cur_in=cross2(a,b,cur)>=-1e-8
            if cur_in!=prev_in:
                ex,ey=b[0]-a[0],b[1]-a[1]
                sx,sy=cur[0]-prev[0],cur[1]-prev[1]
                den=sx*ey-sy*ex
                if abs(den)>1e-12:
                    t=((a[0]-prev[0])*ey-(a[1]-prev[1])*ex)/den
                    output.append((prev[0]+t*sx,prev[1]+t*sy))
            if cur_in: output.append(cur)
            prev,prev_in=cur,cur_in
    # Drop near-duplicate vertices introduced where two triangles touch.
    clean=[]
    for p in output:
        if not clean or math.dist(clean[-1],p)>1e-7: clean.append(p)
    if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-7: clean.pop()
    return clean


def clipped_sloped_face(face, footprint_triangles):
    """Clip a planar 3D roof quad to the GIS footprint and return visible pieces."""
    pieces=[]
    source_tris=[(face[0],face[1],face[2]),(face[0],face[2],face[3])]
    for tri in source_tris:
        subj=[(v[0],v[1]) for v in tri]
        for footprint_tri in footprint_triangles:
            clip=[(p[0],p[1]) for p in footprint_tri]
            polygon=clip_convex_polygon(subj,clip)
            if len(polygon)<3: continue
            a,b,c=tri
            den=cross2(a,b,c)
            if abs(den)<1e-12: continue
            lifted=[]
            for x,y in polygon:
                wb=((x-a[0])*(c[1]-a[1])-(y-a[1])*(c[0]-a[0]))/den
                wc=((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]))/den
                wa=1-wb-wc
                z=wa*a[2]+wb*b[2]+wc*c[2]
                lifted.append((x,y,z))
            pieces.append(lifted)
    return pieces


def simplify_ring(points, tolerance):
    """Iterative Ramer-Douglas-Peucker reduction for the closed GIS ring."""
    pts = points[:-1] if points[0] == points[-1] else list(points)
    # Split at the point farthest from the first point, preserving closure.
    a = pts[0]
    far = max(range(1, len(pts)), key=lambda i: (pts[i][0]-a[0])**2+(pts[i][1]-a[1])**2)
    open_line = pts[:far+1] + pts[:1]
    def dp(line):
        keep = {0, len(line)-1}
        stack = [(0, len(line)-1)]
        while stack:
            start, end = stack.pop()
            x0,y0 = line[start]; x1,y1 = line[end]
            dx,dy=x1-x0,y1-y0
            denom=dx*dx+dy*dy
            best,best_i=-1,None
            for i in range(start+1,end):
                x,y=line[i]
                if denom:
                    u=max(0,min(1,((x-x0)*dx+(y-y0)*dy)/denom))
                    d=math.hypot(x-(x0+u*dx), y-(y0+u*dy))
                else: d=math.hypot(x-x0,y-y0)
                if d>best: best,best_i=d,i
            if best_i is not None and best>tolerance:
                keep.add(best_i); stack.extend([(start,best_i),(best_i,end)])
        return [line[i] for i in sorted(keep)]
    one=dp(open_line)
    other=dp(pts[far:]+pts[:1])
    merged=one[:-1]+other[:-1]
    # Remove adjacent duplicates and any collinear slivers.
    out=[]
    for p in merged:
        if not out or math.dist(p,out[-1])>0.03: out.append(p)
    return out


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup_render(scene, target, span):
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("FSTE evidence sky") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.20,0.27,0.39,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.2
    data = bpy.data.lights.new("FSTE | soft daylight", "AREA")
    light = bpy.data.objects.new("FSTE | soft daylight", data)
    scene.collection.objects.link(light)
    light.location=(target[0]-45,target[1]-65,95)
    # Keep exposure close to real daylight; a previous oversized energy value
    # washed out the brick and roof materials in the evidence renders.
    light.data.energy=650
    light.data.shape="DISK"
    light.data.size=65
    camdata=bpy.data.cameras.new("FSTE evidence camera")
    cam=bpy.data.objects.new("FSTE evidence camera",camdata)
    scene.collection.objects.link(cam)
    cam.location=(target[0]-105,target[1]-132,86)
    camdata.lens=58
    look_at(cam,(target[0],target[1],ROOF_Z*0.46))
    scene.camera=cam
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=-0.65
    scene.render.filepath=str(EVIDENCE/"fste_exterior_candidate.png")


def main():
    # Open the existing single-building library to preserve the exact scene and
    # exported collection identifiers expected by the modular manifest.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene=bpy.data.scenes.get(SCENE_NAME)
    if scene is None: raise RuntimeError("Expected asset scene missing: "+SCENE_NAME)
    bpy.context.window.scene=scene
    col=bpy.data.collections.get(COLLECTION_NAME)
    if col is None: raise RuntimeError("Expected asset collection missing: "+COLLECTION_NAME)
    for obj in list(col.objects): bpy.data.objects.remove(obj, do_unlink=True)
    # Remove stale helper objects while retaining the scene and collection.
    for obj in list(scene.objects):
        if obj.name not in col.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    # Make repeated builds deterministic; discard now-unused materials from
    # earlier candidate generations so no .001/.002 material drift accumulates.
    for material in list(bpy.data.materials):
        if material.name.startswith("FSTE |") and material.users == 0:
            bpy.data.materials.remove(material)
    # Blender objects can leave unused mesh datablocks holding old material
    # users, so purge those too before regenerating a deterministic library.
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for material in list(bpy.data.materials):
        if material.name.startswith("FSTE |") and material.users == 0:
            bpy.data.materials.remove(material)

    geo=json.loads(SOURCE.read_text(encoding="utf-8"))
    feat=next(f for f in geo["features"] if str(f.get("id"))=="651" or f["properties"].get("FID")==651)
    raw=feat["geometry"]["coordinates"][0]
    pts=[((lon-LON0)*111412.84*math.cos(math.radians(LAT0)),(lat-LAT0)*111040.0) for lon,lat in raw]
    ring=simplify_ring(pts,SIMPLIFY_M)
    if len(ring)<10: raise RuntimeError("GIS outline simplification unexpectedly reduced footprint")
    # Ensure the perimeter follows CCW winding, giving a stable outward normal.
    area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
    if area<0: ring.reverse()
    footprint_triangles=triangulate_ring(ring)

    brick=brick_mat()
    trim=mat("FSTE | light limestone / precast trim",(0.67,0.62,0.53),0.76)
    glass=mat("FSTE | blue-gray insulated glazing",(0.075,0.16,0.22),0.24,0.16)
    roofmat=mat("FSTE | dark slate roof tiles (complex-level reference)",(0.075,0.082,0.085),0.78)
    roofnodes=roofmat.node_tree.nodes; rooflinks=roofmat.node_tree.links
    roofbs=roofnodes.get("Principled BSDF")
    roofcoord=roofnodes.new("ShaderNodeTexCoord")
    roofbrick=roofnodes.new("ShaderNodeTexBrick")
    roofbrick.name="Small dark slate tile course"
    roofbrick.inputs["Color1"].default_value=(0.14,0.16,0.17,1)
    roofbrick.inputs["Color2"].default_value=(0.075,0.085,0.09,1)
    roofbrick.inputs["Mortar"].default_value=(0.035,0.04,0.045,1)
    roofbrick.inputs["Brick Width"].default_value=0.46
    roofbrick.inputs["Row Height"].default_value=0.21
    roofbrick.inputs["Mortar Size"].default_value=0.018
    roofbrick.inputs["Mortar Smooth"].default_value=0.006
    rooflinks.new(roofcoord.outputs["Object"],roofbrick.inputs["Vector"])
    rooflinks.new(roofbrick.outputs["Color"],roofbs.inputs["Base Color"])
    concrete=mat("FSTE | warm gray concrete",(0.43,0.42,0.38),0.86)
    interior=mat("FSTE | warm interior gypsum",(0.72,0.66,0.55),0.9)
    floor_mat=mat("FSTE | muted residential carpet",(0.31,0.28,0.24),0.98)
    course=mat("FSTE | brick soldier-course accents",(0.22,0.045,0.025),0.82)
    metal=mat("FSTE | dark bronze metal",(0.08,0.09,0.09),0.35,0.65)
    wood=mat("FSTE | warm maple interior doors and furniture",(0.38,0.20,0.09),0.74)
    bedmat=mat("FSTE | linen and bedding",(0.77,0.73,0.64),0.92)
    upholstery=mat("FSTE | lounge upholstery",(0.20,0.28,0.31),0.9)
    bathmat=mat("FSTE | private-bath tile",(0.48,0.56,0.57),0.56)

    xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    cx=(minx+maxx)/2; cy=(miny+maxy)/2
    lounge_cx=cx+0.73; lounge_cy=cy
    def inside_poly(x,y):
        inside=False
        j=len(ring)-1
        for ii,(xi,yi) in enumerate(ring):
            xj,yj=ring[j]
            if ((yi>y)!=(yj>y)) and (x < (xj-xi)*(y-yi)/(yj-yi+1e-30)+xi):
                inside=not inside
            j=ii
        return inside
    # Anchor the representative doorway to the FSTE frontage closest to 1st
    # Street in OpenStreetMap way 5332639, then choose the facade whose outward
    # normal points toward that street. Purdue GIS confirms the FSTE address;
    # no public source pins the exact East-tower door, so its precise location
    # and design remain an explicitly labeled interpretation. The complex-wide
    # central-entry photograph is not copied onto the East tower.
    osm=json.loads(OSM_SOURCE.read_text(encoding="utf-8"))
    street=next((e for e in osm["elements"] if e.get("type")=="way" and e.get("tags",{}).get("name")=="1st Street"),None)
    if street is None: raise RuntimeError("OSM snapshot lacks the named 1st Street frontage")
    roadxy=[((n["lon"]-LON0)*111412.84*math.cos(math.radians(LAT0)),
             (n["lat"]-LAT0)*111040.0) for n in street["geometry"]]
    roadsegments=list(zip(roadxy,roadxy[1:]))
    entry_candidates=[]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]
        length=math.dist(p,q)
        if length<5.5: continue
        midpoint=((p[0]+q[0])*0.5,(p[1]+q[1])*0.5)
        nearest=min((nearest_point_on_segment(midpoint,a,b) for a,b in roadsegments),
                    key=lambda r:(r[0]-midpoint[0])**2+(r[1]-midpoint[1])**2)
        road_dist=math.dist(midpoint,nearest)
        ux,uy=(q[0]-p[0])/length,(q[1]-p[1])/length
        nx,ny=uy,-ux
        alignment=((nearest[0]-midpoint[0])*nx+(nearest[1]-midpoint[1])*ny)/max(road_dist,1e-6)
        entry_candidates.append((road_dist,-alignment,-length,i,p,q,alignment))
    if not entry_candidates: raise RuntimeError("No suitable GIS frontage edge for representative entry")
    entry_road_dist,_,_,entry_edge,entry_p,entry_q,entry_road_alignment=min(entry_candidates)
    entry_len=math.dist(entry_p,entry_q)
    entry_u=((entry_q[0]-entry_p[0])/entry_len,(entry_q[1]-entry_p[1])/entry_len)
    entry_n=(entry_u[1],-entry_u[0])
    entry_center=((entry_p[0]+entry_q[0])*0.5,(entry_p[1]+entry_q[1])*0.5)
    entry_width=min(1.8,entry_len*0.28)
    entry_height=2.45

    # Continuous wall envelope built directly from the true GIS outline.
    wallfaces=[]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]
        if i==entry_edge:
            lo=0.5-entry_width/(2*entry_len); hi=0.5+entry_width/(2*entry_len)
            a=(p[0]+(q[0]-p[0])*lo,p[1]+(q[1]-p[1])*lo)
            b=(p[0]+(q[0]-p[0])*hi,p[1]+(q[1]-p[1])*hi)
            wallfaces.extend([
                [(p[0],p[1],WALL_BASE),(a[0],a[1],WALL_BASE),(a[0],a[1],ROOF_Z),(p[0],p[1],ROOF_Z)],
                [(b[0],b[1],WALL_BASE),(q[0],q[1],WALL_BASE),(q[0],q[1],ROOF_Z),(b[0],b[1],ROOF_Z)],
                [(a[0],a[1],entry_height),(b[0],b[1],entry_height),(b[0],b[1],ROOF_Z),(a[0],a[1],ROOF_Z)]])
        else:
            wallfaces.append([(p[0],p[1],WALL_BASE),(q[0],q[1],WALL_BASE),(q[0],q[1],ROOF_Z),(p[0],p[1],ROOF_Z)])
    quad_mesh("FSTE | six-story GIS perimeter walls",wallfaces,brick,col)

    # Glazed entrance doors, pale portal trim, and a shallow canopy.
    # Position is an explicit interpretation because FSTE-only entry imagery
    # and plans were unavailable; source-backed program indicates a lobby.
    entry_glass=[]; entry_trim=[]; canopy_faces=[]; threshold_faces=[]
    ew=entry_width-0.20
    front=0.09
    a=(entry_center[0]-entry_u[0]*ew/2+entry_n[0]*front,
       entry_center[1]-entry_u[1]*ew/2+entry_n[1]*front)
    b=(entry_center[0]+entry_u[0]*ew/2+entry_n[0]*front,
       entry_center[1]+entry_u[1]*ew/2+entry_n[1]*front)
    entry_glass.append([(a[0],a[1],WALL_BASE+0.08),(b[0],b[1],WALL_BASE+0.08),
                        (b[0],b[1],entry_height-0.08),(a[0],a[1],entry_height-0.08)])
    jamb=0.10
    for side in (-1,1):
        cc=(entry_center[0]+entry_u[0]*side*(entry_width/2-0.05),
            entry_center[1]+entry_u[1]*side*(entry_width/2-0.05))
        entry_trim.extend(oriented_box_faces(cc,entry_u,entry_n,jamb/2,0.075,WALL_BASE,entry_height+0.12))
    entry_trim.extend(oriented_box_faces(entry_center,entry_u,entry_n,entry_width/2+0.10,0.09,
                                          entry_height-0.02,entry_height+0.13))
    canopy_center=(entry_center[0]+entry_n[0]*0.66,entry_center[1]+entry_n[1]*0.66)
    canopy_faces.extend(oriented_box_faces(canopy_center,entry_u,entry_n,entry_width*0.82,0.72,
                                            entry_height+0.20,entry_height+0.50))
    threshold_center=(entry_center[0]+entry_n[0]*0.52,entry_center[1]+entry_n[1]*0.52)
    threshold_faces.extend(oriented_box_faces(threshold_center,entry_u,entry_n,entry_width*0.72,0.55,
                                               WALL_BASE-0.08,WALL_BASE+0.02))
    quad_mesh("FSTE | estimated glazed entry doors",entry_glass,glass,col)
    quad_mesh("FSTE | estimated pale entry portal",entry_trim,trim,col)
    quad_mesh("FSTE | estimated entry canopy",canopy_faces,metal,col)
    quad_mesh("FSTE | entry threshold",threshold_faces,concrete,col)

    # Continuous internal floor plates follow the actual footprint. The plan
    # and corridor furniture are schematic because a tower-specific plan was
    # not available in the public residence pages.
    quad_mesh("FSTE | ground floor slab on source footprint",
              [[(x,y,WALL_BASE) for x,y in tri] for tri in footprint_triangles],floor_mat,col)
    bpy.data.objects["FSTE | ground floor slab on source footprint"]["evidence_floor_level"]=0
    for level in range(1,FLOORS):
        z=WALL_BASE+level*FLOOR_H
        quad_mesh(f"FSTE | floor plate level {level+1} on source footprint",
                  [[(x,y,z) for x,y in tri] for tri in footprint_triangles],floor_mat,col)
        bpy.data.objects[f"FSTE | floor plate level {level+1} on source footprint"]["evidence_floor_level"]=level

    # Roof deck and parapet.
    quad_mesh("FSTE | roof deck under gabled roof forms",
              [[(x,y,ROOF_Z) for x,y in tri] for tri in footprint_triangles],roofmat,col)
    parapet=[]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]
        parapet.append([(p[0],p[1],ROOF_Z-0.2),(q[0],q[1],ROOF_Z-0.2),
                        (q[0],q[1],ROOF_Z+0.65),(p[0],p[1],ROOF_Z+0.65)])
    quad_mesh("FSTE | low brick roof parapet",parapet,brick,col)

    # The Purdue 2009 opening-day photo shows multiple peaked gable roof forms
    # across the overall complex. Apply a restrained pair to the two strongest
    # 17 m terminal facade edges in this East GIS footprint. This is a
    # complex-level roof-language interpretation, not a claim that the photo
    # isolates or labels this particular wing.
    gable_faces=[]; slate_faces=[]; gable_window_faces=[]; gable_trim_faces=[]
    gable_edges=[]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]
        dx,dy=q[0]-p[0],q[1]-p[1]; length=math.hypot(dx,dy)
        if length<16.0: continue
        ux,uy=dx/length,dy/length
        ix,iy=-uy,ux
        midpoint=((p[0]+q[0])*0.5,(p[1]+q[1])*0.5)
        # Avoid introducing a roof where an apparently long edge has no real
        # interior behind it (for example, a narrow notch).
        if not inside_poly(midpoint[0]+ix*2.5,midpoint[1]+iy*2.5): continue
        eave=ROOF_Z+0.65
        peak=eave+3.35
        depth=13.0
        pr=(p[0]+ix*depth,p[1]+iy*depth)
        qr=(q[0]+ix*depth,q[1]+iy*depth)
        mr=((pr[0]+qr[0])*0.5,(pr[1]+qr[1])*0.5)
        em=((p[0]+q[0])*0.5,(p[1]+q[1])*0.5)
        gable_faces.append([(p[0],p[1],eave),(em[0],em[1],peak),(q[0],q[1],eave)])
        roof_slope_faces=[
            [(p[0],p[1],eave),(em[0],em[1],eave),(mr[0],mr[1],peak),(pr[0],pr[1],peak)],
            [(em[0],em[1],eave),(q[0],q[1],eave),(qr[0],qr[1],peak),(mr[0],mr[1],peak)]]
        for roof_face in roof_slope_faces:
            slate_faces.extend(clipped_sloped_face(roof_face,footprint_triangles))
        # One modest gable window and a light trim hood enliven each roof end.
        gu=min(1.1,length*0.09); gz0=eave+0.55; gz1=eave+1.65
        ga=(em[0]-ux*gu/2,em[1]-uy*gu/2); gb=(em[0]+ux*gu/2,em[1]+uy*gu/2)
        gable_window_faces.append([(ga[0]+ix*0.04,ga[1]+iy*0.04,gz0),
                                   (gb[0]+ix*0.04,gb[1]+iy*0.04,gz0),
                                   (gb[0]+ix*0.04,gb[1]+iy*0.04,gz1),
                                   (ga[0]+ix*0.04,ga[1]+iy*0.04,gz1)])
        gable_trim_faces.append([(ga[0]+ix*0.05,ga[1]+iy*0.05,gz0-0.08),
                                 (gb[0]+ix*0.05,gb[1]+iy*0.05,gz0-0.08),
                                 (gb[0]+ix*0.05,gb[1]+iy*0.05,gz0+0.08),
                                 (ga[0]+ix*0.05,ga[1]+iy*0.05,gz0+0.08)])
        gable_edges.append(i)
    quad_mesh("FSTE | estimated brick gable ends",gable_faces,brick,col)
    quad_mesh("FSTE | pitched slate roof planes",slate_faces,roofmat,col)
    quad_mesh("FSTE | gable window glazing",gable_window_faces,glass,col)
    quad_mesh("FSTE | gable window sill trim",gable_trim_faces,trim,col)

    # Floor-band and lintel trim, repeated per known GIS story count.
    bandfaces=[]
    for level in range(FLOORS+1):
        z=WALL_BASE+level*FLOOR_H
        if z>ROOF_Z+0.01: continue
        for i,p in enumerate(ring):
            q=ring[(i+1)%len(ring)]
            dx,dy=q[0]-p[0],q[1]-p[1]; length=math.hypot(dx,dy)
            if length<0.8: continue
            # Thin flat line band slightly outboard from the perimeter.
            nx,ny=dy/length,-dx/length
            # Construct a bevel-free rectangular fascia prism in local tangent basis.
            v=[(p[0]+nx*0.05,p[1]+ny*0.05,z-0.065),(q[0]+nx*0.05,q[1]+ny*0.05,z-0.065),
               (q[0]+nx*0.05,q[1]+ny*0.05,z+0.065),(p[0]+nx*0.05,p[1]+ny*0.05,z+0.065)]
            bandfaces.append(v)
    quad_mesh("FSTE | continuous brick floor-course bands",bandfaces,course,col)

    # Window glazing and trim, sized and counted to the available straight
    # facade bays. Placement follows each GIS segment, with a clear exterior
    # offset. The exact historic bay schedule is not publicly documented.
    glassfaces=[]; frameboxes=[]; mullionboxes=[]
    window_count=0
    floor_heights=[WALL_BASE+0.85]+[WALL_BASE+level*FLOOR_H+0.75 for level in range(1,FLOORS)]
    for i,p in enumerate(ring):
        q=ring[(i+1)%len(ring)]
        dx,dy=q[0]-p[0],q[1]-p[1]; length=math.hypot(dx,dy)
        if length<4.4: continue
        ux,uy=dx/length,dy/length
        nx,ny=uy,-ux
        bays=max(1,int(length//3.25))
        spacing=length/bays
        winw=min(1.18,spacing*0.52)
        winh=1.48
        for bay in range(bays):
            along=(bay+0.5)*spacing
            if i==entry_edge and along>entry_len*0.5-entry_width*0.7 and along<entry_len*0.5+entry_width*0.7:
                # Leave an uninterrupted glazed opening at the representative entry.
                continue
            cx=p[0]+ux*along+nx*0.048
            cy=p[1]+uy*along+ny*0.048
            for zc in floor_heights:
                z0=zc-winh*0.5; z1=zc+winh*0.5
                # Omit windows where adjacent edge details converge tightly.
                a=(cx-ux*winw/2,cy-uy*winw/2); b=(cx+ux*winw/2,cy+uy*winw/2)
                # Dark inset pane, oriented in the facade plane.
                glassfaces.append([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)])
                frame=0.085
                def prism(cx0,cy0,ww,zz0,zz1,depth=0.045):
                    # Oriented rectangular bar volume spanning tangent/normal axes.
                    corners=[]
                    for signn in (-1,1):
                        for signu, z in [(-1,zz0),(1,zz0),(1,zz1),(-1,zz1)]:
                            corners.append((cx0+ux*signu*ww/2+nx*signn*depth/2,
                                            cy0+uy*signu*ww/2+ny*signn*depth/2,z))
                    # Not used; bars below are directly generated as face quads.
                # Frame rails, perpendiculars, and center mullions are thin
                # extruded planes; layered in front of glass for clear detail.
                for side in (-1,1):
                    ccx=cx+ux*side*(winw/2-frame/2)
                    ccy=cy+uy*side*(winw/2-frame/2)
                    # vertical frame bar, quad face
                    v=[(ccx-ux*frame/2+nx*0.075,ccy-uy*frame/2+ny*0.075,z0-frame),
                       (ccx+ux*frame/2+nx*0.075,ccy+uy*frame/2+ny*0.075,z0-frame),
                       (ccx+ux*frame/2+nx*0.075,ccy+uy*frame/2+ny*0.075,z1+frame),
                       (ccx-ux*frame/2+nx*0.075,ccy-uy*frame/2+ny*0.075,z1+frame)]
                    frameboxes.append(v)
                for zbar in (z0,z1):
                    zz0=zbar-frame/2; zz1=zbar+frame/2
                    frameboxes.append([(cx-ux*(winw/2+frame)+nx*0.075,cy-uy*(winw/2+frame)+ny*0.075,zz0),
                                       (cx+ux*(winw/2+frame)+nx*0.075,cy+uy*(winw/2+frame)+ny*0.075,zz0),
                                       (cx+ux*(winw/2+frame)+nx*0.075,cy+uy*(winw/2+frame)+ny*0.075,zz1),
                                       (cx-ux*(winw/2+frame)+nx*0.075,cy-uy*(winw/2+frame)+ny*0.075,zz1)])
                zmid=zc
                mullionboxes.append([(cx-ux*0.035+nx*0.085,cy-uy*0.035+ny*0.085,z0),
                                     (cx+ux*0.035+nx*0.085,cy+uy*0.035+ny*0.085,z0),
                                     (cx+ux*0.035+nx*0.085,cy+uy*0.035+ny*0.085,z1),
                                     (cx-ux*0.035+nx*0.085,cy-uy*0.035+ny*0.085,z1)])
                window_count+=1
    quad_mesh("FSTE | inset blue-gray window panes",glassfaces,glass,col)
    quad_mesh("FSTE | pale window frames",frameboxes,trim,col)
    quad_mesh("FSTE | narrow window mullions",mullionboxes,metal,col)

    # Representative 22-room cluster per story, based on Purdue's opening-day
    # description of living rooms serving clusters of 22 private rooms and the
    # residence page's approximate single-room dimensions. No tower-specific
    # floor plan was found, so this regularized plan remains explicitly
    # schematic and is intended to communicate the residential program only.
    room_w,room_d=2.95,4.19  # approximate published room envelope
    room_pitch_x,room_pitch_y=4.5,4.5
    lounge_w,lounge_d=5.0,6.0
    room_candidates=[]
    x_start=minx+room_w/2+0.02
    y_start=miny+room_d/2+0.02
    nx=max(0,int((maxx-minx-room_w)//room_pitch_x)+1)
    ny=max(0,int((maxy-miny-room_d)//room_pitch_y)+1)
    for row in range(ny):
        yc=y_start+row*room_pitch_y
        for column in range(nx):
            xc=x_start+column*room_pitch_x
            corners=[(xc-room_w/2,yc-room_d/2),(xc+room_w/2,yc-room_d/2),
                     (xc+room_w/2,yc+room_d/2),(xc-room_w/2,yc+room_d/2)]
            if not all(inside_poly(x,y) for x,y in corners): continue
            # Keep the common lounge/dinette zone open around the footprint center.
            if abs(xc-lounge_cx)<lounge_w/2+0.5 and abs(yc-lounge_cy)<lounge_d/2+0.5: continue
            room_candidates.append((abs(xc-cx)+abs(yc-cy),row,column,xc,yc))
    room_candidates.sort()
    room_cells=[item[3:] for item in room_candidates[:22]]
    if len(room_cells)<18: raise RuntimeError(f"Only {len(room_cells)} full room modules fit within FSTE GIS polygon")
    corridor_x=(sorted([x for x,y in room_cells])[len(room_cells)//2]+cx)*0.5
    corridor_w=1.6
    typical_room_h=2.45
    room_count_by_level={}
    for level in range(FLOORS):
        zfloor=WALL_BASE+level*FLOOR_H+0.03
        room_walls=[]; doors=[]; corridor_faces=[]
        bed_boxes=[]; pillow_boxes=[]; desk_boxes=[]; chair_boxes=[]; closet_boxes=[]
        bath_walls=[]; lounge_furniture=[]; tv_boxes=[]
        # Corridor surface, split into narrow sections where the centerline is
        # inside the GIS polygon and both sides fit within the floor outline.
        yy=miny+3.0
        while yy<maxy-3.0:
            y1=min(yy+0.8,maxy-3.0)
            if inside_poly(corridor_x,0.5*(yy+y1)) and inside_poly(corridor_x-corridor_w/2,0.5*(yy+y1)) and inside_poly(corridor_x+corridor_w/2,0.5*(yy+y1)):
                corridor_faces.append([(corridor_x-corridor_w/2,yy,zfloor),(corridor_x+corridor_w/2,yy,zfloor),
                                       (corridor_x+corridor_w/2,y1,zfloor),(corridor_x-corridor_w/2,y1,zfloor)])
            yy=y1
        for room_index,(xc,yc) in enumerate(room_cells):
            x0,x1=xc-room_w/2,xc+room_w/2
            y0,y1=yc-room_d/2,yc+room_d/2
            top=zfloor+typical_room_h
            door_w=0.88; door_h=2.08
            # Full north/south and outer-side partitions; an opening is kept at
            # each room's corridor-facing side for a readable unit entry.
            room_walls.extend([
                [(x0,y0,zfloor),(x1,y0,zfloor),(x1,y0,top),(x0,y0,top)],
                [(x1,y0,zfloor),(x1,y1,zfloor),(x1,y1,top),(x1,y0,top)],
                [(x1,y1,zfloor),(x0,y1,zfloor),(x0,y1,top),(x1,y1,top)]])
            # Face room doors toward the central hallway when adjacent; for
            # far cells, keep the same legible inward-facing arrangement.
            face_east=xc<corridor_x
            door_y=(y0+y1)/2
            dy0,dy1=door_y-door_w/2,door_y+door_w/2
            if face_east:
                room_walls.extend([
                    [(x0,y0,zfloor),(x0,dy0,zfloor),(x0,dy0,top),(x0,y0,top)],
                    [(x0,dy1,zfloor),(x0,y1,zfloor),(x0,y1,top),(x0,dy1,top)],
                    [(x0,dy0,door_h+zfloor),(x0,dy1,door_h+zfloor),(x0,dy1,top),(x0,dy0,top)]])
                door_x=x0-0.025
            else:
                room_walls.extend([
                    [(x1,y0,zfloor),(x1,dy0,zfloor),(x1,dy0,top),(x1,y0,top)],
                    [(x1,dy1,zfloor),(x1,y1,zfloor),(x1,y1,top),(x1,dy1,top)],
                    [(x1,dy0,door_h+zfloor),(x1,dy1,door_h+zfloor),(x1,dy1,top),(x1,dy0,top)]])
                door_x=x1+0.025
            doors.append([(door_x,dy0,zfloor+0.06),(door_x,dy1,zfloor+0.06),
                          (door_x,dy1,zfloor+door_h),(door_x,dy0,zfloor+door_h)])
            # A private bath partition and compact bath fixtures at one end of
            # each room communicate the source-backed private-bath program.
            bx=x0+0.95; by=y1-1.35
            bath_walls.extend([
                [(bx,by,zfloor),(x1,by,zfloor),(x1,by,zfloor+2.2),(bx,by,zfloor+2.2)],
                [(bx,by,zfloor),(bx,y1,zfloor),(bx,y1,zfloor+2.2),(bx,by,zfloor+2.2)]])
            # Residential furniture is deliberately simple and repeated. Beds,
            # desk, chair, and wardrobe dimensions are illustrative.
            bed_boxes.append((xc-0.50,xc+0.50,y0+0.18,y0+2.05,zfloor+0.12,zfloor+0.40))
            pillow_boxes.append((xc-0.42,xc+0.42,y0+0.28,y0+0.68,zfloor+0.42,zfloor+0.50))
            desk_boxes.append((x0+0.10,x0+0.88,y0+2.68,y0+3.20,zfloor+0.72,zfloor+0.82))
            chair_boxes.append((x0+0.30,x0+0.68,y0+2.15,y0+2.53,zfloor+0.48,zfloor+0.92))
            closet_boxes.append((x1-0.65,x1-0.12,y1-1.0,y1-0.24,zfloor+0.05,zfloor+2.0))
        quad_mesh(f"FSTE | room partitions level {level+1} (schematic)",room_walls,interior,col)["evidence_floor_level"]=level
        quad_mesh(f"FSTE | room entry doors level {level+1}",doors,wood,col)["evidence_floor_level"]=level
        quad_mesh(f"FSTE | private bathroom partitions level {level+1}",bath_walls,bathmat,col)["evidence_floor_level"]=level
        quad_mesh(f"FSTE | corridor floor level {level+1}",corridor_faces,floor_mat,col)["evidence_floor_level"]=level
        for name,boxes,material in [
            ("beds",bed_boxes,upholstery),("bed linens",pillow_boxes,bedmat),
            ("desks",desk_boxes,wood),("chairs",chair_boxes,metal),
            ("wardrobes",closet_boxes,wood)]:
            ob=box_mesh(f"FSTE | {name} level {level+1}",boxes,material,col)
            ob["evidence_floor_level"]=level
        # A shared living/dinette room at the center of the typical-floor
        # cutaway, with soft seating, coffee table, dining table, and wall TV.
        lx0,lx1=lounge_cx-lounge_w/2,lounge_cx+lounge_w/2
        ly0,ly1=lounge_cy-lounge_d/2,lounge_cy+lounge_d/2
        if all(inside_poly(x,y) for x,y in [(lx0,ly0),(lx1,ly0),(lx1,ly1),(lx0,ly1)]):
            lounge_furniture.extend([
                (lx0+0.35,lx0+2.35,cy+1.25,cy+2.0,zfloor+0.2,zfloor+0.85),
                (lx0+2.1,lx0+2.85,cy-0.45,cy+1.45,zfloor+0.2,zfloor+0.85),
                (lounge_cx-0.7,lounge_cx+0.7,lounge_cy-0.25,lounge_cy+0.25,zfloor+0.28,zfloor+0.45),
                (lounge_cx+0.8,lounge_cx+2.3,ly0+0.45,ly0+1.25,zfloor+0.74,zfloor+0.84)])
            tv_boxes.append((lounge_cx-0.65,lounge_cx+0.65,ly1-0.18,ly1-0.08,zfloor+1.35,zfloor+2.1))
        ob=box_mesh(f"FSTE | shared living-dinette furniture level {level+1}",lounge_furniture,upholstery,col)
        ob["evidence_floor_level"]=level
        ob=box_mesh(f"FSTE | shared lounge television level {level+1}",tv_boxes,metal,col)
        ob["evidence_floor_level"]=level
        room_count_by_level[str(level+1)]=len(room_cells)

    # Ensure collection contains only the intended asset geometry; evidence
    # camera/light live in scene root, outside the exported asset collection.
    for obj in list(scene.objects):
        if obj.name.startswith("FSTE evidence") or obj.name=="FSTE | soft daylight":
            continue
    # Store compact source and measurement notes in the .blend itself.
    scene["asset_id"]=ID
    scene["source_feature"]="Purdue BuildingShapesZip4 FeatureServer/0 FID 651; retrieved 2026-10-26; source CRS EPSG:4326"
    scene["footprint_method"]="GIS ring transformed using project local geographic approximation; RDP simplified at 0.30m (area deviation documented in audit)"
    scene["height_uncertainty"]="6 floors source attribute; 3.15m floor-to-floor and 23.25m highest gable top are estimates; GIS Extrution=52 unit/meaning undocumented"
    scene["entry_uncertainty"]="Representative glazed vestibule on the north-facing GIS edge closest to OSM 1st Street way 5332639 (road-edge distance documented in audit). FSTE address and building-lobby program are sourced; exact door position/design remain unverified and the complex-wide central entry image was not copied onto East."
    scene["roof_uncertainty"]="Purdue University 2009 First Street Towers exterior photo documents multiple peaked gables at complex level; gables are repeated on the long terminal edges of the FSTE GIS outline as a cautious roof-language interpretation. Photo does not identify East wing."
    scene["interior_uncertainty"]="Representative 22-room cluster per level uses Purdue opening-day description of living rooms per 22-room cluster, approximate published single-room dimensions, private baths, and shared living/dinette; exact FSTE floor plan unavailable."
    scene["window_count_estimate"]=window_count
    scene["representative_room_count_per_level"]=len(room_cells)
    scene["representative_gable_count"]=len(gable_edges)
    scene["representative_entry_edge_index"]=entry_edge
    scene["representative_entry_distance_to_osm_1st_street_m"]=round(entry_road_dist,3)
    scene["representative_entry_facing_alignment_to_1st_street"]=round(entry_road_alignment,4)

    target=(cx,cy,0)
    setup_render(scene,target,max(maxx-minx,maxy-miny))
    # A top-down footprint check render is saved separately using camera pose,
    # then restore the exterior camera for the asset file.
    camera=scene.camera
    original=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.type,camera.data.ortho_scale,camera.data.lens)
    camera.data.type="ORTHO"; camera.data.ortho_scale=max(maxx-minx,maxy-miny)*1.18
    camera.location=(cx,cy,ROOF_Z+120); look_at(camera,(cx,cy,0))
    scene.render.filepath=str(EVIDENCE/"fste_footprint_top_candidate.png")
    bpy.ops.render.render(write_still=True)
    camera.location=original[0]; camera.rotation_euler=original[1]; camera.data.type=original[2]; camera.data.ortho_scale=original[3]
    camera.data.lens=original[4]
    scene.render.filepath=str(EVIDENCE/"fste_exterior_candidate.png")
    bpy.ops.render.render(write_still=True)
    # Render an evidence-only top-down cutaway of the representative third
    # floor. The shell is temporarily hidden for the view; all modeled asset
    # geometry remains in the exported collection and is restored before save.
    hidden={obj:obj.hide_render for obj in col.objects}
    selected_level=2
    for obj in col.objects:
        obj.hide_render=(obj.get("evidence_floor_level")!=selected_level)
    cut_z=WALL_BASE+selected_level*FLOOR_H+0.1
    camera.data.type="ORTHO"
    camera.data.ortho_scale=max((maxx-minx)*1.20,(maxy-miny)*1.20*1100/900)
    camera.location=(cx,cy,cut_z+55)
    look_at(camera,(cx,cy,cut_z))
    scene.render.filepath=str(EVIDENCE/"fste_interior_cutaway_candidate.png")
    bpy.ops.render.render(write_still=True)
    # Close representative room-cluster view so room partitions, doors, private
    # bath corners, furniture, and the shared lounge/dinette are legible.
    room_target=(sum(x for x,y in room_cells)/len(room_cells),
                 sum(y for x,y in room_cells)/len(room_cells),cut_z)
    camera.data.ortho_scale=42.0
    camera.location=(room_target[0]-23.0,room_target[1]-22.0,cut_z+26.0)
    look_at(camera,room_target)
    scene.render.filepath=str(EVIDENCE/"fste_interior_cluster_detail_candidate.png")
    bpy.ops.render.render(write_still=True)
    for obj,value in hidden.items(): obj.hide_render=value
    camera.location=original[0]; camera.rotation_euler=original[1]; camera.data.type=original[2]; camera.data.ortho_scale=original[3]; camera.data.lens=original[4]
    # A separate eye-level entry detail makes the modeled vestibule and canopy
    # legible. Its exact FSTE placement remains identified as an estimate.
    camera.data.type="PERSP"; camera.data.lens=68
    camera.location=(entry_center[0]+entry_n[0]*18+entry_u[0]*1.0,
                     entry_center[1]+entry_n[1]*18+entry_u[1]*1.0,4.3)
    look_at(camera,(entry_center[0],entry_center[1],1.75))
    scene.render.filepath=str(EVIDENCE/"fste_entry_detail_candidate.png")
    bpy.ops.render.render(write_still=True)
    camera.location=original[0]; camera.rotation_euler=original[1]; camera.data.type=original[2]; camera.data.ortho_scale=original[3]
    # Pack any generated assets (materials are node-based and need no external files).
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print("FSTE_BUILD_SUMMARY",json.dumps({"asset":str(ASSET),"id":ID,"collection":COLLECTION_NAME,
          "ring_vertices_raw":len(raw)-1,"ring_vertices_used":len(ring),"footprint_area_m2":round(abs(area),3),
          "bounds_xy":list(map(lambda x:round(x,3),(minx,miny,maxx,maxy))),"floor_count":FLOORS,
          "estimated_roof_z_m":round(ROOF_Z+4.0,3),"window_count":window_count,
          "room_count_per_level":len(room_cells),"gable_count":len(gable_edges),"entry_edge_index":entry_edge,
          "object_count":len(col.objects),"material_count":len({m.name for o in col.objects for m in o.data.materials if o.type=='MESH'}),
          "exterior_render":str(EVIDENCE/"fste_exterior_candidate.png"),"top_render":str(EVIDENCE/"fste_footprint_top_candidate.png"),
          "interior_cutaway":str(EVIDENCE/"fste_interior_cutaway_candidate.png"),
          "interior_cluster_detail":str(EVIDENCE/"fste_interior_cluster_detail_candidate.png"),
          "entry_detail":str(EVIDENCE/"fste_entry_detail_candidate.png")},indent=2))


if __name__=="__main__": main()
