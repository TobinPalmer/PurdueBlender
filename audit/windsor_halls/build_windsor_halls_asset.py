"""Build the Windsor halls assigned component asset from Purdue GIS footprints.

Run with Blender 5.2 in background mode from the repository root.  The source
libraries stay individually componentized, with the original stable scene and
collection names preserved.
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_windsor_halls_80aeb51.blend")
SOURCE = os.path.join(os.path.dirname(__file__), "sources", "purdue_gis_windsor_fids_63_66_277_278_2026-10-26.geojson")
ROOF_SOURCE = os.path.join(os.path.dirname(__file__), "roof_surfaces.json")
COLLECTION_NAME = "Asset_massing_windsor_halls_80aeb51"
SCENE_NAME = "Building_massing_windsor_halls_80aeb51"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
FEET_TO_METERS = 0.3048

FEATURES = {
    63: {"name": "Warren Residence Hall", "abbr": "WARN", "floors": 4, "roof": 5.0, "dormers": 2, "entry": "warren_arch"},
    64: {"name": "Wood Residence Hall", "abbr": "WOOD", "floors": 4, "roof": 5.7, "dormers": 1, "entry": "central_bay"},
    65: {"name": "Vawter Residence Hall", "abbr": "VAWT", "floors": 4, "roof": 4.5, "dormers": 2, "entry": "vawter_portico"},
    66: {"name": "Windsor Dining Court", "abbr": "WDC", "floors": 2, "roof": 0.35, "dormers": 0, "entry": "service"},
}

def xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)

def make_mat(name, color, roughness=0.78):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    output=m.node_tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf_new=m.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    m.node_tree.links.new(bsdf_new.outputs["BSDF"],output.inputs["Surface"])
    bsdf = bsdf_new
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    # Procedural surfaces remain portable and make the brick/roof read as
    # masonry and slate without external texture dependencies.
    if "brick" in name.lower():
        tex=m.node_tree.nodes.new("ShaderNodeTexBrick")
        tex.inputs["Color1"].default_value=(0.27,0.065,0.038,1)
        tex.inputs["Color2"].default_value=(0.39,0.115,0.073,1)
        tex.inputs["Mortar"].default_value=(0.18,0.145,0.12,1)
        tex.inputs["Scale"].default_value=2.5
        tex.inputs["Mortar Size"].default_value=0.018
        tex.inputs["Mortar Smooth"].default_value=0.01
        texcoord=m.node_tree.nodes.new("ShaderNodeTexCoord")
        m.node_tree.links.new(texcoord.outputs["UV"],tex.inputs["Vector"])
        m.node_tree.links.new(tex.outputs["Color"],bsdf.inputs["Base Color"])
        bump=m.node_tree.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=0.12; bump.inputs["Distance"].default_value=0.025
        m.node_tree.links.new(tex.outputs["Fac"],bump.inputs["Height"]); m.node_tree.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    elif "slate" in name.lower():
        noise=m.node_tree.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value=7.5; noise.inputs["Detail"].default_value=3.0; noise.inputs["Roughness"].default_value=.72
        geom=m.node_tree.nodes.new("ShaderNodeNewGeometry"); m.node_tree.links.new(geom.outputs["Position"],noise.inputs["Vector"])
        ramp=m.node_tree.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.2; ramp.color_ramp.elements[0].color=(.045,.055,.06,1)
        ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=(.15,.17,.18,1)
        m.node_tree.links.new(noise.outputs["Fac"],ramp.inputs["Fac"]); m.node_tree.links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
        bump=m.node_tree.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.14; bump.inputs["Distance"].default_value=.08
        m.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"]); m.node_tree.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    elif "limestone" in name.lower():
        noise=m.node_tree.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value=3.0; noise.inputs["Detail"].default_value=2.0
        geom=m.node_tree.nodes.new("ShaderNodeNewGeometry"); m.node_tree.links.new(geom.outputs["Position"],noise.inputs["Vector"])
        ramp=m.node_tree.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color=(.48,.43,.35,1); ramp.color_ramp.elements[1].color=(.74,.68,.57,1)
        m.node_tree.links.new(noise.outputs["Fac"],ramp.inputs["Fac"]); m.node_tree.links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
    return m

BRICK = BRICK_ALT = LIMESTONE = ROOF = GLASS = FRAME = DOOR = DINING = None
INTERIOR_FLOOR = INTERIOR_WALL = INTERIOR_FURNITURE = None
WARREN_TILE = WOOD_INTERIOR = VAWTER_INTERIOR = None

def initialize_materials():
    global BRICK, BRICK_ALT, LIMESTONE, ROOF, GLASS, FRAME, DOOR, DINING, INTERIOR_FLOOR, INTERIOR_WALL, INTERIOR_FURNITURE, WARREN_TILE, WOOD_INTERIOR, VAWTER_INTERIOR
    BRICK = make_mat("Windsor | warm red-brown brick", (0.36, 0.115, 0.075))
    BRICK_ALT = make_mat("Windsor | subtle brick variation", (0.43, 0.155, 0.105))
    LIMESTONE = make_mat("Windsor | pale limestone trim", (0.66, 0.61, 0.51))
    ROOF = make_mat("Windsor | charcoal slate roof", (0.095, 0.112, 0.12))
    GLASS = make_mat("Windsor | recessed dark window glass", (0.055, 0.105, 0.135), 0.24)
    FRAME = make_mat("Windsor | painted dark bronze window frames", (0.12, 0.11, 0.095))
    DOOR = make_mat("Windsor | dark stained entrance doors", (0.105, 0.07, 0.045))
    DINING = make_mat("Windsor Dining Court | pale stone and brick base", (0.48, 0.39, 0.29))
    INTERIOR_FLOOR = make_mat("SCHEMATIC ONLY | warm wood interior floor", (.42,.25,.12))
    INTERIOR_WALL = make_mat("SCHEMATIC ONLY | pale interior partitions", (.72,.67,.55))
    INTERIOR_FURNITURE = make_mat("SCHEMATIC ONLY | muted residence furniture", (.27,.31,.34))
    WARREN_TILE = make_mat("SCHEMATIC ONLY | Warren inspired polychrome lobby tile", (.39,.22,.32))
    WOOD_INTERIOR = make_mat("SCHEMATIC ONLY | Wood renovation color accents", (.17,.38,.36))
    VAWTER_INTERIOR = make_mat("SCHEMATIC ONLY | Vawter neutral room palette", (.43,.36,.26))

def link_object(obj, collection):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def make_mesh(name, verts, faces, mats, face_mats=None, collection=None):
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for m in mats: mesh.materials.append(m)
    mesh.update()
    if any("brick" in m.name.lower() for m in mats):
        uv=mesh.uv_layers.new(name="Generated masonry UV")
        for loop in mesh.loops:
            co=mesh.vertices[loop.vertex_index].co
            uv.data[loop.index].uv=(co.x,co.z)
    ob = bpy.data.objects.new(name, mesh)
    (collection or bpy.context.scene.collection).objects.link(ob)
    if face_mats:
        for p, idx in zip(mesh.polygons, face_mats): p.material_index = idx
    return ob

def simplify_ring(points, tol=0.12):
    # Preserve every GIS corner. The layer's stair-step vertices are part of
    # the authoritative footprint; this avoids cumulative drift from repeated
    # near-collinear removal.
    return points[:-1] if (Vector(points[0]) - Vector(points[-1])).length < 1e-5 else points[:]

def face_polygon(name, ring, z0, z1, mat, collection):
    n=len(ring); verts=[(x,y,z0) for x,y in ring]+[(x,y,z1) for x,y in ring]
    faces=[]
    faces.append(tuple(range(n-1,-1,-1)))
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    faces.append(tuple(range(n,2*n)))
    ob=make_mesh(name,verts,faces,[mat],collection=collection)
    uv=ob.data.uv_layers.new(name="Facade brick courses")
    cumulative=[0.0]
    for i in range(n): cumulative.append(cumulative[-1]+math.dist(ring[i],ring[(i+1)%n]))
    perimeter=cumulative[-1]
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            vi=ob.data.loops[li].vertex_index
            if 1 <= poly.index <= n:
                edge=poly.index-1
                if vi<n:
                    u=cumulative[vi]
                    if edge==n-1 and vi==0: u=perimeter
                    v=0.0
                else:
                    idx=vi-n; u=cumulative[idx]
                    if edge==n-1 and idx==0: u=perimeter
                    v=z1-z0
            else:
                x,y,_=verts[vi]; u=x; v=y
            uv.data[li].uv=(u,v)
    return ob

def create_box_mesh(name, verts, collection, material, faces=None):
    return make_mesh(name, verts, faces or [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)], [material], collection=collection)

def roof_mesh(name, fid, z_eave, rise, collection, roof_data):
    # Each residence hall has its own full-footprint, subdivided distance-field
    # roof. Ridges peak over the narrow GIS wings; no broad cap spans the
    # courtyards or covers the upper facade rows. FID66 keeps its low service roof.
    geometry=roof_data["components"][str(fid)]
    verts=[]; faces=[]; vertex_index={}
    triangles=geometry.get("roof_triangles",geometry.get("slope_triangles",[])+geometry.get("cap_triangles",[]))
    for tri in triangles:
        face=[]
        # Weld subdivided triangle vertices so smooth normals remove visible
        # triangulation seams while preserving the faceted roof profile.
        for x,y,t in tri:
            key=(round(x,6),round(y,6),round(z_eave+rise*t,5))
            if key not in vertex_index:
                vertex_index[key]=len(verts)
                verts.append((x,y,z_eave+rise*t))
            face.append(vertex_index[key])
        faces.append(tuple(face))
    obj=make_mesh(name,verts,faces,[ROOF],collection=collection)
    for poly in obj.data.polygons: poly.use_smooth=True
    return obj

def main_frontage(ring, preference="south"):
    """Choose a likely public frontage; Warren/Vawter lobby line faces south."""
    edges=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]; dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
        if length < 4.0: continue
        edges.append((a,b,(a[0]+b[0])/2,(a[1]+b[1])/2,dx,dy,length))
    if not edges: return ring[0],ring[1]
    if preference in ("south","warren_arch","vawter_portico"):
        horizontal=[e for e in edges if abs(e[4]) >= abs(e[5])*1.8 and e[6]>=6]
        pool=horizontal or edges
        return min(pool,key=lambda e:e[3])[:2]
    if preference=="central_bay":
        long=[e for e in edges if e[6]>=7]
        pool=long or edges
        # Wood's documented central entrance bay is represented on the
        # southern, public-facing elevation, not an arbitrary longest wall.
        low=min(e[3] for e in pool)
        pool=[e for e in pool if e[3]<=low+5]
        return max(pool,key=lambda e:e[6])[:2]
    return max(edges,key=lambda e:e[6])[:2]

def oriented_box(name, origin, u, v, center_u, center_v, width, depth, z, height, material, collection):
    c=(origin[0]+u[0]*center_u+v[0]*center_v,origin[1]+u[1]*center_u+v[1]*center_v)
    verts=[]
    for zz in (z,z+height):
        for su,sv in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            verts.append((c[0]+u[0]*su*width/2+v[0]*sv*depth/2,
                          c[1]+u[1]*su*width/2+v[1]*sv*depth/2,zz))
    return make_mesh(name,verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],[material],collection=collection)

def gable_dormers(name, edge, zbase, wall_h, rise, count, collection, large_center=False):
    """Visible gabled roof bays with slate shoulders and recessed windows."""
    a,b=edge; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if count<=0 or length<8:return
    u=(dx/length,dy/length); outward=(u[1],-u[0]); inward=(-outward[0],-outward[1])
    bays=count if not large_center else 1
    widths=[min(length/(bays+1)*0.66,3.1 if not large_center else 6.2)]*bays
    for j,width in enumerate(widths):
        t=(j+1)/(bays+1) if not large_center else .5
        px=a[0]+dx*t; py=a[1]+dy*t
        base=zbase+wall_h
        eave=base+max(.7,rise*.38); peak=base+rise*.92
        front_depth=.16
        # Five-point gable infill on the elevation; roof cheeks project above
        # the primary roof cap as a restrained, stone-trimmed dormer.
        poly=[(-width/2,base),(width/2,base),(width/2,eave),(0,peak),(-width/2,eave)]
        verts=[(px+u[0]*x+outward[0]*front_depth,py+u[1]*x+outward[1]*front_depth,z)
               for x,z in poly]
        face=[tuple(range(5))]
        mat=BRICK if not large_center else LIMESTONE
        make_mesh(name+f" | gabled dormer {j+1} front",verts,face,[mat],collection=collection)
        # Recessed dormer glazing with a center mullion.
        ww=width*.43; wh=max(.9,(eave-base)*.46); cz=base+(eave-base)*.55
        win=[]
        for x,z in [(-ww/2,cz-wh/2),(ww/2,cz-wh/2),(ww/2,cz+wh/2),(-ww/2,cz+wh/2)]:
            win.append((px+u[0]*x+outward[0]*(front_depth+.03),py+u[1]*x+outward[1]*(front_depth+.03),z))
        make_mesh(name+f" | gable window {j+1}",win,[(0,1,2,3)],[GLASS],collection=collection)
        # Two sloping slate cheeks turn the shallow front into a legible gable.
        backoffset=-inward[0]*1.25
        outerfront=[(px+u[0]*x+outward[0]*front_depth,py+u[1]*x+outward[1]*front_depth,z) for x,z in [(-width/2,eave),(0,peak),(width/2,eave)]]
        backpeak=(px+inward[0]*1.25,py+inward[1]*1.25,peak-.15)
        for side,backx in [(-1,0),(1,2)]:
            p0=outerfront[0 if side<0 else 2]; p1=outerfront[1]
            p2=(px+inward[0]*1.25,py+inward[1]*1.25,eave-.1)
            make_mesh(name+f" | slate gable cheek {j+1} {side}",[p0,p1,backpeak,p2],[(0,1,2,3)],[ROOF],collection=collection)

def add_entrance_portal(name, edge, zbase, style, collection, wall_h=14.4):
    a,b=edge; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    u=(dx/length,dy/length); outward=(u[1],-u[0]); cx=(a[0]+b[0])/2; cy=(a[1]+b[1])/2
    width=2.25 if style!="central_bay" else 2.6; height=2.7
    dwidth=width+1.0; stone_height=.28 if style!="central_bay" else .42
    # Stone jambs, heavy lintel and a projecting dark canopy establish the hall
    # entrance without moving the structural footprint.
    for side in (-1,1):
        verts=[]
        x=side*(width/2+.22)
        for z in (zbase,x*0+zbase+height):
            verts.extend([(cx+u[0]*(x-.11)+outward[0]*.12,cy+u[1]*(x-.11)+outward[1]*.12,z),
                          (cx+u[0]*(x+.11)+outward[0]*.12,cy+u[1]*(x+.11)+outward[1]*.12,z)])
        make_mesh(name+f" | entrance stone jamb {side}",verts,[(0,1,3,2)],[LIMESTONE],collection=collection)
    verts=[]
    for x,z in [(-dwidth/2,zbase+height),(dwidth/2,zbase+height),(dwidth/2,zbase+height+stone_height),(-dwidth/2,zbase+height+stone_height)]:
        verts.append((cx+u[0]*x+outward[0]*.14,cy+u[1]*x+outward[1]*.14,z))
    make_mesh(name+" | entrance stone lintel",verts,[(0,1,2,3)],[LIMESTONE],collection=collection)
    oriented_box(name+" | entrance canopy",(cx,cy),u,outward,0,.37,dwidth+.35,.72,zbase+height+stone_height,ROOF and .18,ROOF,collection)
    if style=="warren_arch":
        # Raised stone arch/gable over Warren's main aligned lobby entrance.
        peakz=zbase+height+stone_height+1.15; basez=zbase+height+stone_height
        pediment=[(cx-u[0]*(dwidth/2+.35)+outward[0]*.17,cy-u[1]*(dwidth/2+.35)+outward[1]*.17,basez),
                  (cx+u[0]*(dwidth/2+.35)+outward[0]*.17,cy+u[1]*(dwidth/2+.35)+outward[1]*.17,basez),
                  (cx+outward[0]*.17,cy+outward[1]*.17,peakz)]
        make_mesh(name+" | Warren stone entrance gable",pediment,[(0,1,2)],[LIMESTONE],collection=collection)
        # Small transom panel under the gable.
        tv=[]
        for x,z in [(-.7,basez-.82),(.7,basez-.82),(.7,basez-.12),(-.7,basez-.12)]:
            tv.append((cx+u[0]*x+outward[0]*.2,cy+u[1]*x+outward[1]*.2,z))
        make_mesh(name+" | Warren entrance transom",tv,[(0,1,2,3)],[GLASS],collection=collection)
    elif style=="vawter_portico":
        # Paired stone piers distinguish Vawter's vestibule while keeping the
        # lobby on the documented Duhme–Shealy–Warren–Vawter axis.
        for side in (-1,1):
            oriented_box(name+f" | Vawter portico pier {side}",(cx,cy),u,outward,side*(width/2+.44),.48,.36,.6,zbase,.0+height,LIMESTONE,collection)
    if style=="central_bay":
        # A broad gabled stone focal bay follows the central entrance described
        # in the Purdue-client Wood Hall renovation documentation.
        bayw=8.0; baydepth=.8; baybottom=zbase+3.05; baytop=zbase+wall_h-.55
        # projected bay body, with a stepped limestone belt and upper window.
        oriented_box(name+" | Wood central bay projection",(cx,cy),u,outward,0,.43,bayw,baydepth,baybottom,baytop-baybottom,BRICK,collection)
        oriented_box(name+" | Wood bay stone sill",(cx,cy),u,outward,0,.90,bayw+.35,.12,baybottom+2.55,.14,LIMESTONE,collection)
        winw=2.35; winh=2.05
        for floor_index,winz in enumerate((zbase+3.95,zbase+7.35,zbase+10.75)):
            vv=[]
            for x,z in [(-winw/2,winz),(winw/2,winz),(winw/2,winz+winh),(-winw/2,winz+winh)]:
                vv.append((cx+u[0]*x+outward[0]*.88,cy+u[1]*x+outward[1]*.88,z))
            make_mesh(name+f" | Wood central bay sash {floor_index+1}",vv,[(0,1,2,3)],[GLASS],collection=collection)
            for side in (-1,1):
                oriented_box(name+f" | Wood bay stone window jamb {floor_index+1} {side}",(cx,cy),u,outward,side*(winw/2+.07),.99,.14,.14,winz-.07,winh+.14,LIMESTONE,collection)
            oriented_box(name+f" | Wood bay stone window sill {floor_index+1}",(cx,cy),u,outward,0,.99,winw+.25,.14,winz-.10,.12,LIMESTONE,collection)
            oriented_box(name+f" | Wood bay stone window lintel {floor_index+1}",(cx,cy),u,outward,0,.99,winw+.25,.14,winz+winh+.01,.12,LIMESTONE,collection)
            oriented_box(name+f" | Wood bay sash vertical muntin {floor_index+1}",(cx,cy),u,outward,0,1.08,.055,.055,winz,.02+winh,FRAME,collection)
            oriented_box(name+f" | Wood bay sash horizontal muntin {floor_index+1}",(cx,cy),u,outward,0,1.08,winw,.055,winz+winh*.52,.055,FRAME,collection)
        # The renovation reference documents a symmetrical central bay,
        # carved stone ornament, a steep gable, and a formal arched entrance.
        # These restrained accents translate those cues without claiming a
        # measured elevation.
        for side in (-1,1):
            oriented_box(name+f" | Wood carved stone bay pier {side}",(cx,cy),u,outward,side*(bayw/2-.28),.89,.42,1.02,baybottom,.19,LIMESTONE,collection)
            oriented_box(name+f" | Wood entrance lantern {side}",(cx,cy),u,outward,side*(dwidth/2+.62),.22,.24,.25,zbase+2.05,.48,FRAME,collection)
        for j in range(3):
            px=(j-1)*1.05
            oriented_box(name+f" | Wood bay baluster {j+1}",(cx,cy),u,outward,px,1.00,.11,.16,zbase+12.65,.54,LIMESTONE,collection)
        oriented_box(name+" | Wood bay balustrade rail",(cx,cy),u,outward,0,1.00,3.5,.18,zbase+13.13,.13,LIMESTONE,collection)
        # Gable pediment with simple pale stone peak.
        tri=[(cx-u[0]*bayw/2+outward[0]*.2,cy-u[1]*bayw/2+outward[1]*.2,baytop),
             (cx+u[0]*bayw/2+outward[0]*.2,cy+u[1]*bayw/2+outward[1]*.2,baytop),
             (cx+outward[0]*.2,cy+outward[1]*.2,baytop+2.7)]
        make_mesh(name+" | Wood central gable pediment",tri,[(0,1,2)],[LIMESTONE],collection=collection)

def add_residence_schematic(name, edge, zbase, collection, floor_mat, wall_mat, furniture_mat, accent_mat=None, wall_height=1.15):
    """One explicitly schematic room/corridor slice using generic Windsor dimensions."""
    a,b=edge; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    u=(dx/length,dy/length); v=(-u[1],u[0]); origin=(a[0]+dx*.5,a[1]+dy*.5)
    # Model is a cutaway sample, not a geolocated floor plan. The 14 x 16 ft
    # generic room size comes from Purdue Housing's Windsor room illustration.
    width=2*4.267; depth=4.877; corridor=1.8; floor_z=zbase+3.2; h=wall_height; thick=.12
    prefix=name+" | SCHEMATIC INTERIOR (not a surveyed floor plan)"
    oriented_box(prefix+" | room floor",origin,u,v,0,depth/2,width,depth,floor_z,.12,floor_mat,collection)
    oriented_box(prefix+" | corridor floor",origin,u,v,0,depth+corridor/2,width,corridor,floor_z,.10,floor_mat,collection)
    oriented_box(prefix+" | shared lounge floor",origin,u,v,0,depth+corridor+2.25,width,4.5,floor_z,.10,accent_mat or floor_mat,collection)
    # room side walls, rear wall, center divider and corridor back wall
    for x in (-width/2,width/2): oriented_box(prefix+" | room side wall",origin,u,v,x,depth/2,thick,depth,floor_z+.12,h,wall_mat,collection)
    oriented_box(prefix+" | room rear wall",origin,u,v,0,depth,width,thick,floor_z+.12,h,wall_mat,collection)
    oriented_box(prefix+" | shared room divider",origin,u,v,0,depth/2,thick,depth,floor_z+.12,h,wall_mat,collection)
    oriented_box(prefix+" | corridor back wall",origin,u,v,0,depth+corridor,width,thick,floor_z+.12,h,wall_mat,collection)
    # Two furniture sets: bed, desk, chair, and dresser in each generic room.
    for side in (-1,1):
        center_u=side*width/4
        bedx=center_u-.55; bedy=depth*.60
        oriented_box(prefix+" | bed frame",origin,u,v,bedx,bedy,1.12,2.18,floor_z+.12,.31,DOOR,collection)
        oriented_box(prefix+" | twin bed mattress",origin,u,v,bedx,bedy,1.02,2.06,floor_z+.43,.20,accent_mat or furniture_mat,collection)
        oriented_box(prefix+" | bed pillow",origin,u,v,bedx,bedy+.77, .72,.42,floor_z+.64,.10,INTERIOR_WALL,collection)
        oriented_box(prefix+" | desk",origin,u,v,center_u+.95,depth*.70,1.25,.68,floor_z+.12,.74,DOOR,collection)
        oriented_box(prefix+" | desk chair seat",origin,u,v,center_u+.95,depth*.48,.55,.55,floor_z+.50,.12,FRAME,collection)
        oriented_box(prefix+" | dresser",origin,u,v,center_u+.95,depth*.19,.82,.55,floor_z+.12,.80,furniture_mat,collection)
    # Shared-room vignette: sofa, coffee table, and reading chairs, reflecting
    # Purdue Housing's reported lounges/living rooms and reading rooms.
    lounge_v=depth+corridor+2.25
    oriented_box(prefix+" | shared lounge sofa",origin,u,v,0,lounge_v,3.1,.92,floor_z+.12,.56,DOOR,collection)
    oriented_box(prefix+" | shared lounge sofa cushion",origin,u,v,0,lounge_v,2.82,.80,floor_z+.68,.17,furniture_mat,collection)
    oriented_box(prefix+" | shared lounge coffee table",origin,u,v,0,lounge_v-1.05,1.5,.72,floor_z+.12,.42,DOOR,collection)
    for side in (-1,1):
        oriented_box(prefix+" | lounge reading chair",origin,u,v,side*2.7,lounge_v-1.1,.85,.85,floor_z+.12,.76,furniture_mat,collection)
    return {"origin_xy_m":origin,"u":u,"v":v,"floor_z_m":floor_z,"rooms":2,"shared_lounge":True,"room_dimensions_ft":[14,16]}

def add_dining_schematic(name, ring, collection, floor_mat, furniture_mat):
    # Food court tables and a serving counter are generic amenity objects; the
    # GIS polygon is the only source for their general site envelope.
    cx=sum(p[0] for p in ring)/len(ring); cy=sum(p[1] for p in ring)/len(ring); origin=(cx,cy); u=(1,0); v=(0,1); z=-2.65
    prefix=name+" | SCHEMATIC DINING INTERIOR (not a surveyed floor plan)"
    oriented_box(prefix+" | dining floor",origin,u,v,0,0,18,12,z,.14,floor_mat,collection)
    oriented_box(prefix+" | serving counter",origin,u,v,0,4.2,8.5,.9,z+.14,1.05,furniture_mat,collection)
    for x in (-5.5,0,5.5):
        for y in (-2.5,1.0):
            oriented_box(prefix+" | dining table",origin,u,v,x,y,2.8,1.2,z+.14,.76,furniture_mat,collection)
            for dx in (-1.45,1.45):
                for dy in (-.8,.8): oriented_box(prefix+" | chair",origin,u,v,x+dx,y+dy,.42,.42,z+.14,.48,FRAME,collection)
    return {"origin_xy_m":origin,"tables":6,"layout":"schematic serving counter and tables; no exact dining plan source"}

def wall_decor(name, ring, zbase, wall_h, floor_count, collection):
    verts=[]; faces=[]; indices=[]
    # Continuous stone plinth, floor bands and cornice courses; these are kept
    # as slim architectural overlays rather than broad false facade bands.
    def add_prism(a,b,z,depth=0.045,height=0.10, idx=0):
        dx=b[0]-a[0]; dy=b[1]-a[1]; l=math.hypot(dx,dy)
        if l < 0.25:return
        nx,ny=dy/l,-dx/l
        base=len(verts)
        for t,zz,off in [(0,z,0),(1,z,0),(1,z+height,0),(0,z+height,0),
                         (0,z,depth),(1,z,depth),(1,z+height,depth),(0,z+height,depth)]:
            verts.append((a[0]+dx*t+nx*off,a[1]+dy*t+ny*off,zz))
        faces.extend([(base,base+1,base+2,base+3),(base+4,base+5,base+6,base+7),
                      (base,base+4,base+7,base+3),(base+1,base+5,base+6,base+2),
                      (base,base+1,base+5,base+4),(base+3,base+2,base+6,base+7)])
        indices.extend([idx]*6)
    levels=[zbase+0.52,zbase+wall_h-0.36]
    levels += [zbase+wall_h*f/floor_count for f in range(1,floor_count)]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]
        for z in levels: add_prism(a,b,z,idx=0)
    if faces: make_mesh(name+" | limestone courses",verts,faces,[LIMESTONE],indices,collection)

def facade_details(name, ring, zbase, wall_h, floors, collection, entry_edge, bay_pitch=4.35, window_width_scale=1.0, window_height_scale=1.0):
    # Recessed-looking window panels and limestone surrounds aligned with each
    # straight facade run. Windows are grouped per building for editability.
    verts=[]; faces=[]; mids=[]
    window_count=0
    floor_spacing=wall_h/floors
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length < 3.4: continue
        nx,ny=dy/length,-dx/length
        # main elevation bays spaced around 4.3m, excluding corners
        bays=max(1,int(round(length/bay_pitch)))
        for floor in range(floors):
            zc=zbase+floor_spacing*(floor+0.52)
            wh=min(1.58,floor_spacing*0.48)*window_height_scale
            for k in range(bays):
                t=(k+0.5)/bays
                center=(a[0]+dx*t,a[1]+dy*t)
                ww=min(1.25,length/bays*0.38)*window_width_scale
                # glazing with distinct stone lintel and sill edges
                base=len(verts)
                for xoff,zoff in [(-ww/2,-wh/2),(ww/2,-wh/2),(ww/2,wh/2),(-ww/2,wh/2)]:
                    verts.append((center[0]+dx/length*xoff+nx*0.035,
                                  center[1]+dy/length*xoff+ny*0.035,zc+zoff))
                faces.append((base,base+1,base+2,base+3)); mids.append(0)
                # Deep bronze muntins make the glazing read as framed sash,
                # rather than a flat repeated colored square.
                xmid=(center[0]+nx*.09,center[1]+ny*.09)
                barw=.055
                q=len(verts)
                verts.extend([(xmid[0]-dx/length*barw/2,xmid[1]-dy/length*barw/2,zc-wh*.48),
                              (xmid[0]+dx/length*barw/2,xmid[1]+dy/length*barw/2,zc-wh*.48),
                              (xmid[0]+dx/length*barw/2,xmid[1]+dy/length*barw/2,zc+wh*.48),
                              (xmid[0]-dx/length*barw/2,xmid[1]-dy/length*barw/2,zc+wh*.48)])
                faces.append((q,q+1,q+2,q+3)); mids.append(2)
                q=len(verts); barz=.04
                verts.extend([(center[0]-dx/length*ww*.46+nx*.09,center[1]-dy/length*ww*.46+ny*.09,zc-barz/2),
                              (center[0]+dx/length*ww*.46+nx*.09,center[1]+dy/length*ww*.46+ny*.09,zc-barz/2),
                              (center[0]+dx/length*ww*.46+nx*.09,center[1]+dy/length*ww*.46+ny*.09,zc+barz/2),
                              (center[0]-dx/length*ww*.46+nx*.09,center[1]-dy/length*ww*.46+ny*.09,zc+barz/2)])
                faces.append((q,q+1,q+2,q+3)); mids.append(2)
                # narrow stone surround and prominent sill/header
                for side in (-1,1):
                    q=len(verts); x=center[0]+dx/length*side*ww*0.58; y=center[1]+dy/length*side*ww*0.58
                    verts.extend([(x+nx*0.07,y+ny*0.07,zc-wh*0.56),(x+nx*0.07,y+ny*0.07,zc+wh*0.56),
                                  (x+nx*0.07+dx/length*0.095,y+ny*0.07+dy/length*0.095,zc+wh*0.56),
                                  (x+nx*0.07+dx/length*0.095,y+ny*0.07+dy/length*0.095,zc-wh*0.56)])
                    faces.append((q,q+1,q+2,q+3)); mids.append(1)
                for zedge in (zc-wh*0.58,zc+wh*0.58):
                    q=len(verts); left=(center[0]-dx/length*ww*0.58,center[1]-dy/length*ww*0.58)
                    right=(center[0]+dx/length*ww*0.58,center[1]+dy/length*ww*0.58)
                    verts.extend([(left[0]+nx*.07,left[1]+ny*.07,zedge-.07),(right[0]+nx*.07,right[1]+ny*.07,zedge-.07),
                                  (right[0]+nx*.07,right[1]+ny*.07,zedge+.07),(left[0]+nx*.07,left[1]+ny*.07,zedge+.07)])
                    faces.append((q,q+1,q+2,q+3)); mids.append(1)
                window_count+=1
    if faces:
        make_mesh(name+" | recessed window bays",verts,faces,[GLASS,LIMESTONE,FRAME],mids,collection)

    # Main entry location uses the historic lobby alignment for Warren/Vawter,
    # and a central focal bay for Wood; location is approximate to the facade.
    a,b=entry_edge; dx,dy=b[0]-a[0],b[1]-a[1]; l=math.hypot(dx,dy)
    nx,ny=dy/l,-dx/l; cx=(a[0]+b[0])/2; cy=(a[1]+b[1])/2
    width=2.15; doorh=2.55; z=zbase+0.05
    verts=[]
    for xo,zz in [(-width/2,z),(width/2,z),(width/2,z+doorh),(-width/2,z+doorh)]:
        verts.append((cx+dx/l*xo+nx*.12,cy+dy/l*xo+ny*.12,zz))
    make_mesh(name+" | entrance doors",verts,[(0,1,2,3)],[DOOR],collection=collection)
    return window_count

def main():
    # The existing library is a single rough mass; retain the stable scene and
    # collection but replace only this assigned asset's contents.
    bpy.ops.wm.open_mainfile(filepath=ASSET)
    initialize_materials()
    scene=bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
    col=bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(col)
    for ob in list(col.objects): bpy.data.objects.remove(ob,do_unlink=True)
    # prevent stale linked objects from an older scene in this self-contained library
    for ob in list(scene.objects):
        if ob.name == "Windsor Halls" or ob.name.startswith("Windsor review camera") or ob.name.startswith("Windsor key light"):
            bpy.data.objects.remove(ob,do_unlink=True)

    data=json.load(open(SOURCE,encoding="utf-8"))
    roof_data=json.load(open(ROOF_SOURCE,encoding="utf-8"))
    by_fid={f["properties"]["FID"]:f for f in data["features"]}
    component_report={}
    schematic_report={}
    for fid,cfg in FEATURES.items():
        feat=by_fid[fid]; prop=feat["properties"]
        raw=feat["geometry"]["coordinates"][0]
        ring=simplify_ring([xy(lon,lat) for lon,lat,*_ in raw])
        signed_area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
        # Consistent counter-clockwise winding gives facade overlays an outward
        # normal; the published ArcGIS rings arrive clockwise.
        if signed_area < 0: ring.reverse()
        # Elevation is unitless in the service schema. Values near 600 are
        # treated as feet by inference for relative grades, never as surveyed
        # building heights; this assumption is recorded in the audit.
        zbase=(prop["Elevation"]-by_fid[66]["properties"]["Elevation"])*FEET_TO_METERS
        if fid==66:
            # Dining Court is mapped below Warren and Vawter. The source gives
            # 3 levels but no interior plan; retain a low, partially-subgrade
            # service volume below the adjacent halls' inferred grade datum.
            zbase=-2.8; wall_h=3.7; floor_count=2; roof_rise=0.4
            bodymat=DINING
        else:
            wall_h=14.4; floor_count=cfg["floors"]; roof_rise=cfg["roof"]; bodymat=BRICK
        label=f"{cfg['name']} (FID {fid})"
        face_polygon(label+" | structural footprint shell",ring,zbase,zbase+wall_h,bodymat,col)
        roof_mesh(label+" | steep pitched roof facets",fid,zbase+wall_h,roof_rise,col,roof_data)
        wall_decor(label,ring,zbase,wall_h,floor_count,col)
        entry_edge=main_frontage(ring,cfg["entry"] if fid!=66 else "south")
        bay_pitch={63:4.1,64:3.65,65:4.45,66:5.2}[fid]
        window_width={63:1.0,64:.82,65:.9,66:1.0}[fid]
        window_height={63:1.0,64:1.04,65:.9,66:1.0}[fid]
        windows=facade_details(label,ring,zbase,wall_h,floor_count,col,entry_edge,bay_pitch=bay_pitch,
                               window_width_scale=window_width,window_height_scale=window_height)
        if fid!=66:
            add_entrance_portal(label,entry_edge,zbase,cfg["entry"],col,wall_h=wall_h)
            gable_dormers(label,entry_edge,zbase,wall_h,roof_rise,cfg["dormers"],col,large_center=(fid==64))
            furniture={63:INTERIOR_FURNITURE,64:WOOD_INTERIOR,65:VAWTER_INTERIOR}[fid]
            accent={63:WARREN_TILE,64:WOOD_INTERIOR,65:INTERIOR_WALL}[fid]
            schematic_report[str(fid)]=add_residence_schematic(cfg["name"],entry_edge,zbase,col,INTERIOR_FLOOR,INTERIOR_WALL,furniture,accent_mat=accent)
        else:
            schematic_report[str(fid)]=add_dining_schematic(cfg["name"],ring,col,INTERIOR_FLOOR,INTERIOR_FURNITURE)
        component_report[str(fid)]={
            "official_name":prop["BUILDING_N"],"abbr":prop["BLDG_ABBR"],"address":prop["ADDRESS"],
            "ring_vertices_source":len(raw),"ring_vertices_model":len(ring),
            "projected_bounds_m":{"xmin":min(p[0] for p in ring),"xmax":max(p[0] for p in ring),
                                  "ymin":min(p[1] for p in ring),"ymax":max(p[1] for p in ring)},
            "elevation_field_raw_no_published_unit":prop["Elevation"],"base_z_m_relative_to_FID66":zbase,
            "wall_height_m_estimated":wall_h,"roof_rise_m_estimated":roof_rise,
            "visible_window_bays_modelled":windows,"entry_edge_xy_m":[list(entry_edge[0]),list(entry_edge[1])],
            "entry_center_xy_m":[(entry_edge[0][0]+entry_edge[1][0])/2,(entry_edge[0][1]+entry_edge[1][1])/2],
            "entrance_style":cfg["entry"],"dormer_count_modelled":cfg["dormers"],"building_fid":fid
        }
    # Source collection is named exactly as expected and has a reusable local
    # marker object at the project geographic origin; geometry remains campus
    # coordinates, per this simple massing library's existing convention.
    marker=bpy.data.objects.new("Asset Origin | project geographic origin",None)
    marker.empty_display_type='PLAIN_AXES'; marker.empty_display_size=2
    marker.location=(0,0,0); col.objects.link(marker); marker.hide_render=True
    scene.name=SCENE_NAME
    scene.render.engine='BLENDER_EEVEE'
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=0.0; scene.view_settings.gamma=1.0
    scene.render.resolution_x=1500; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world.color=(0.08,0.09,0.12)
    if scene.world.use_nodes:
        background=scene.world.node_tree.nodes.get("Background")
        if background:
            background.inputs["Color"].default_value=(0.08,0.09,0.12,1.0)
            background.inputs["Strength"].default_value=0.22
    # Set a readable architectural inspection view with orthographic plan-like
    # framing and warm key light; render output remains in the asset evidence dir.
    center=Vector((-617,-123,8)); cam_data=bpy.data.cameras.new("Windsor review camera")
    cam=bpy.data.objects.new("Windsor review camera",cam_data); scene.collection.objects.link(cam)
    cam.location=center+Vector((190,-240,270)); direction=center-cam.location
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=255
    scene.camera=cam
    light_data=bpy.data.lights.new("Windsor key light","AREA"); light_data.energy=850; light_data.shape='DISK'; light_data.size=110
    light=bpy.data.objects.new("Windsor key light",light_data); scene.collection.objects.link(light); light.location=center+Vector((10,-80,170)); light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()

    # Add a clean top-down GIS comparison render after the oblique overview.
    bpy.ops.wm.save_as_mainfile(filepath=ASSET)
    report={"asset_id":"massing_windsor_halls_80aeb51","asset_path":"modular/buildings/massing_windsor_halls_80aeb51.blend",
            "collection":COLLECTION_NAME,"scene":SCENE_NAME,"coordinate_system":"project local campus meters; X east, Y north, Z up",
            "geographic_origin":{"latitude":ORIGIN_LAT,"longitude":ORIGIN_LON},"source_geojson":os.path.relpath(SOURCE,ROOT).replace('\\','/'),
            "source_crs":"EPSG:4326","transform":"X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0",
            "included_fids":[63,64,65,66],"excluded_adjacent_fids":{"277":"Shealy; separately Arjav-owned asset, excluded to prevent duplicate geometry","278":"Duhme; separate finished asset, excluded to prevent duplicate geometry"},
            "components":component_report,"schematic_interiors":schematic_report,
            "roof_method":"Warren, Wood, and Vawter use separately constrained full-footprint roof meshes refined twice and shaped by a concave distance-to-GIS-boundary profile. The estimated profiles peak at medial ridges and remove broad flat caps so upper/courtyard facades stay more visible. Heights differ by hall and remain estimates. FID66 retains its separate low roof form.",
            "surface_materials":"UV-mapped procedural running-bond brick with mortar and bump; textured slate, pale limestone and recessed sash details; portable and self-contained.",
            "preview_files":["previews/windsor_halls_overview.png","previews/warren_frontage.png","previews/wood_frontage.png","previews/vawter_frontage.png","previews/windsor_schematic_interior.png","previews/windsor_dining_schematic.png"],
            "overlap_notes":{"FID66":"Purdue GIS FID66 footprint has zero shared area with FIDs 63, 64, and 65 but touches each boundary. Purdue Housing states Dining Court is underneath Vawter and Warren; the model places its low shell below their inferred grade level without inventing horizontal overlap. Exact vertical extent is unverified."},
            "interior":"Clearly labeled, low-wall cutaway modules show generic Windsor dorm rooms, beds, desks, closets, corridor, lounge, and dining tables/counter. Dimensions follow Purdue's general Windsor 14 ft × 16 ft room illustration. Warren tile and oak cues are based on a Warren renovation description; Wood's color accent draws from its renovation project description. Objects and locations remain schematic, not surveyed floor-plan claims.",
            "height_uncertainties":"Purdue GIS NUM_LEVELS/Elevation/Extrution fields lack published units and differ from current Purdue emergency-plan descriptions of above-ground stories. Values near 600 are assumed to be feet only for relative grade offsets. Roof profiles/heights, entry locations, and dining court vertical extent are estimates; footprints use the official GIS polygons exactly.",
            "generated_utc":"2026-10-26"}
    os.makedirs(os.path.join(os.path.dirname(__file__),"previews"),exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__),"build_report.json"),"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
    scene.render.filepath=os.path.join(os.path.dirname(__file__),"previews","windsor_halls_overview.png")
    bpy.ops.render.render(write_still=True)
    # Close facade views make the hall-specific entrance work, sash relief,
    # brick texture, and different roof silhouettes inspectable.
    saved_camera_location=cam.location.copy(); saved_camera_rotation=cam.rotation_euler.copy(); saved_ortho=cam.data.ortho_scale
    for fid in (63,64,65):
        x,y=component_report[str(fid)]["entry_center_xy_m"]
        target=Vector((x,y,component_report[str(fid)]["base_z_m_relative_to_FID66"]+8.3))
        # Isolate each residence in its close view so adjoining, connected
        # roofs cannot occlude its courtyard walls and upper window rows.
        hall=FEATURES[fid]["name"]
        hidden_components=[]
        for ob in list(col.objects):
            if ob.type=="MESH" and hall not in ob.name:
                hidden_components.append((ob,ob.hide_render)); ob.hide_render=True
        edge=component_report[str(fid)]["entry_edge_xy_m"]
        ax,ay=edge[0]; bx,by=edge[1]; el=math.hypot(bx-ax,by-ay)
        outward=Vector(((by-ay)/el,-(bx-ax)/el,0))
        cam.location=target+outward*50+Vector((0,0,23))
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale=58
        scene.render.filepath=os.path.join(os.path.dirname(__file__),"previews",{63:"warren_frontage.png",64:"wood_frontage.png",65:"vawter_frontage.png"}[fid])
        bpy.ops.render.render(write_still=True)
        for ob,was_hidden in hidden_components: ob.hide_render=was_hidden
    cam.location=saved_camera_location; cam.rotation_euler=saved_camera_rotation; cam.data.ortho_scale=saved_ortho
    # Render one close top-down schematic slice separately. Hidden exterior
    # meshes are restored after rendering and remain visible in the saved file.
    main_camera=scene.camera
    hidden=[]
    for ob in list(col.objects):
        if ob.type=="MESH" and "SCHEMATIC" not in ob.name:
            hidden.append((ob,ob.hide_render)); ob.hide_render=True
    interior_center=schematic_report["63"]["origin_xy_m"]
    camdata=bpy.data.cameras.new("Windsor schematic interior preview camera")
    icam=bpy.data.objects.new("Windsor schematic interior preview camera",camdata); scene.collection.objects.link(icam)
    interior_target=Vector((interior_center[0],interior_center[1]+5.0,schematic_report["63"]["floor_z_m"]+.55))
    icam.location=interior_target+Vector((10,-13,15))
    icam.rotation_euler=(interior_target-icam.location).to_track_quat('-Z','Y').to_euler()
    icam.data.type='ORTHO'; icam.data.ortho_scale=19
    scene.camera=icam
    scene.render.filepath=os.path.join(os.path.dirname(__file__),"previews","windsor_schematic_interior.png")
    bpy.ops.render.render(write_still=True)
    dining_center=schematic_report["66"]["origin_xy_m"]
    icam.location=(dining_center[0],dining_center[1],schematic_report["66"]["origin_xy_m"][1]*0-2.65+34)
    icam.data.ortho_scale=22
    scene.render.filepath=os.path.join(os.path.dirname(__file__),"previews","windsor_dining_schematic.png")
    bpy.ops.render.render(write_still=True)
    for ob,was_hidden in hidden: ob.hide_render=was_hidden
    scene.camera=main_camera
    bpy.data.objects.remove(icam,do_unlink=True)

if __name__ == '__main__': main()
