"""Build the Beta Sigma Psi Purdue chapter house from its official GIS polygon.

Run with Blender 5.x:
  blender -b --python modular/buildings/build_massing_house_301841254_29ab02d.py

Campus coordinates stay in the simple-massing coordinate frame. Interior
room arrangement, finish materials, roof shape and fenestration are schematic
because no measured elevations or plans are available. Current Google Street
View provides direct visual evidence of the street facade and roof silhouette.
"""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path
from urllib.request import urlopen

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_house_301841254_29ab02d"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "beta_sigma_psi" / "sources" / "purdue_gis_fid793_2026-10-26.json"
EVIDENCE_PATH = ROOT / "audit" / "beta_sigma_psi" / "build_evidence.json"
PREVIEW_EXTERIOR = ROOT / "audit" / "beta_sigma_psi" / "beta_sigma_psi_exterior.png"
PREVIEW_INTERIOR = ROOT / "audit" / "beta_sigma_psi" / "beta_sigma_psi_interior.png"
COLLECTION = f"Asset_{ASSET_ID}"
SCENE = f"Building_{ASSET_ID}"
OBJECT = "House_301841254"
ORIGIN_LAT = 40.4274


def campus_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - 40.4274) * 111040.0)


def mat(name, rgba, roughness=0.78):
    material = bpy.data.materials.new(name)
    material.diffuse_color = rgba
    material.use_nodes = True
    bsdf = next(n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def add_brick_texture(material, color_a, color_b, mortar, brick_width, row_height, bump_distance, wall_map=False):
    """Procedural, portable brick/shingle courses in real-world shader coordinates."""
    tree=material.node_tree
    nodes=tree.nodes; links=tree.links
    bsdf=next(n for n in nodes if n.type=="BSDF_PRINCIPLED")
    geometry=nodes.new("ShaderNodeNewGeometry"); geometry.location=(-650,100)
    tex=nodes.new("ShaderNodeTexBrick"); tex.location=(-430,130)
    tex.inputs["Color1"].default_value=color_a
    tex.inputs["Color2"].default_value=color_b
    tex.inputs["Mortar"].default_value=mortar
    tex.inputs["Scale"].default_value=1.0
    tex.inputs["Mortar Size"].default_value=0.018 if "Masonry" in material.name else 0.009
    tex.inputs["Mortar Smooth"].default_value=0.008
    tex.inputs["Brick Width"].default_value=brick_width
    tex.inputs["Row Height"].default_value=row_height
    if wall_map:
        coords=nodes.new("ShaderNodeTexCoord"); coords.location=(-850,240)
        separate=nodes.new("ShaderNodeSeparateXYZ"); separate.location=(-650,280)
        combine=nodes.new("ShaderNodeCombineXYZ"); combine.location=(-430,320)
        links.new(coords.outputs["Generated"],separate.inputs["Vector"])
        links.new(separate.outputs["X"],combine.inputs["X"])
        links.new(separate.outputs["Z"],combine.inputs["Y"])
        links.new(combine.outputs["Vector"],tex.inputs["Vector"])
    else:
        links.new(geometry.outputs["Position"],tex.inputs["Vector"])
    bump=nodes.new("ShaderNodeBump"); bump.location=(-150,-70)
    bump.inputs["Strength"].default_value=0.18
    bump.inputs["Distance"].default_value=bump_distance
    links.new(tex.outputs["Fac"],bump.inputs["Height"])
    links.new(tex.outputs["Color"],bsdf.inputs["Base Color"])
    links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])


def cube(name, center, dims, material, collection, rotation=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler.z = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def prism(name, outline, z0, z1, material, collection):
    n = len(outline)
    verts = [(x, y, z0) for x, y in outline] + [(x, y, z1) for x, y in outline]
    faces = [tuple(reversed(range(n))), tuple(n + i for i in range(n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - Vector(obj.location)).to_track_quat("-Z", "Y").to_euler()


def make_scene():
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(SOURCE_PATH)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8-sig"))
    feats = payload.get("features", [])
    if len(feats) != 1:
        raise RuntimeError("Expected one official Purdue GIS feature")
    f = feats[0]
    attrs = f["attributes"]
    if attrs.get("FID") != 793 or attrs.get("BUILDING_N") != "Beta Sigma Psi" or attrs.get("ADDRESS") != "525 University St":
        raise RuntimeError(f"GIS identity/address mismatch: {attrs}")
    ring = f["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    footprint = [campus_xy(lon, lat) for lon, lat in ring]
    if len(footprint) < 4:
        raise RuntimeError("Official footprint ring is incomplete")
    signed_area = sum(footprint[i][0]*footprint[(i+1)%len(footprint)][1]
                      - footprint[(i+1)%len(footprint)][0]*footprint[i][1]
                      for i in range(len(footprint)))/2
    outward_sign = 1.0 if signed_area > 0 else -1.0
    computed_footprint_area_m2 = abs(signed_area)
    computed_footprint_perimeter_m = sum(math.dist(footprint[i],footprint[(i+1)%len(footprint)])
                                         for i in range(len(footprint)))
    cx = sum(x for x, y in footprint) / len(footprint)
    cy = sum(y for x, y in footprint) / len(footprint)
    # Principal plan direction, used only for the estimated roof ridge and room grid.
    xx = sum((x-cx)**2 for x,y in footprint)/len(footprint)
    yy = sum((y-cy)**2 for x,y in footprint)/len(footprint)
    xy = sum((x-cx)*(y-cy) for x,y in footprint)/len(footprint)
    theta = 0.5 * math.atan2(2*xy, xx-yy)
    ax, ay = math.cos(theta), math.sin(theta)
    bx, by = -ay, ax
    along = [(x-cx)*ax+(y-cy)*ay for x,y in footprint]
    across = [(x-cx)*bx+(y-cy)*by for x,y in footprint]
    amin, amax, bmin, bmax = min(along), max(along), min(across), max(across)
    length, width = amax-amin, bmax-bmin

    # Replace only the contents of this dedicated generated scene.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name != "Collection":
            bpy.data.collections.remove(c)
    scene = bpy.context.scene
    scene.name = SCENE
    asset = bpy.data.collections.new(COLLECTION)
    scene.collection.children.link(asset)
    preview = bpy.data.collections.new("Preview_Rigs")
    scene.collection.children.link(preview)

    brick = mat("BetaSigmaPsi_Warm_Masonry_Estimated", (0.34, 0.14, 0.09, 1))
    trim = mat("BetaSigmaPsi_Limestone_Trim_Estimated", (0.72, 0.66, 0.53, 1))
    roofmat = mat("BetaSigmaPsi_Dark_Roof_Estimated", (0.11, 0.14, 0.16, 1))
    glass = mat("BetaSigmaPsi_Window_Glass_Estimated", (0.055, 0.13, 0.18, 1), 0.24)
    wood = mat("BetaSigmaPsi_Interior_Wood_Schematic", (0.34, 0.19, 0.095, 1))
    wall = mat("BetaSigmaPsi_Interior_Wall_Schematic", (0.76, 0.72, 0.62, 1))
    floor = mat("BetaSigmaPsi_Interior_Floor_Schematic", (0.47, 0.39, 0.29, 1))
    upholstery = mat("BetaSigmaPsi_Upholstery_Schematic", (0.26, 0.31, 0.29, 1))
    white = mat("BetaSigmaPsi_Bedding_Schematic", (0.83, 0.81, 0.75, 1))
    metal = mat("BetaSigmaPsi_Metal", (0.18, 0.20, 0.20, 1), 0.35)
    door_mat = mat("BetaSigmaPsi_Entry_Door_Estimated", (0.48, 0.035, 0.025, 1))
    shutter_mat = mat("BetaSigmaPsi_Dark_Window_Shutters_Estimated", (0.055, 0.105, 0.085, 1))
    add_brick_texture(brick,(0.34,0.14,0.09,1),(0.39,0.18,0.12,1),(0.27,0.135,0.10,1),.15,.10,.006,True)
    add_brick_texture(roofmat,(0.095,0.12,0.14,1),(0.16,0.19,0.20,1),(0.055,0.065,0.072,1),.82,.36,.018)

    objects = []
    # Topographic slab is schematic; wall outline exactly follows official GIS.
    objects.append(prism("footprint foundation", footprint, -0.15, 0.0, trim, asset))
    # Two-storey shell is supported by 2012 exact-address rental information
    # describing shared bathrooms on each floor. The GIS one-level field conflicts,
    # so the floor-to-floor and roof heights remain estimates.
    floor_to_floor = 3.15
    wall_h, eave_h, peak_h, gable_peak_h = 6.3, 6.55, 8.10, 9.00
    # Google Street View panorama is taken from west of the house and shows its
    # west-facing public facade. Use the longest western GIS edge for that face.
    west_x=min(x for x,y in footprint)
    front_candidates=[i for i in range(len(footprint))
                      if (footprint[i][0]+footprint[(i+1)%len(footprint)][0])/2 <= west_x+1.3]
    front_edge_i=max(front_candidates,key=lambda i:math.dist(footprint[i],footprint[(i+1)%len(footprint)]))
    entry_edge=(footprint[front_edge_i],footprint[(front_edge_i+1)%len(footprint)])
    for i,(p,q) in enumerate(zip(footprint, footprint[1:]+footprint[:1])):
        dx,dy=q[0]-p[0],q[1]-p[1]; seg=math.hypot(dx,dy)
        if seg < .25: continue
        tx,ty=dx/seg,dy/seg; nx,ny=ty*outward_sign,-tx*outward_sign
        angle=math.atan2(ty,tx)
        # Entrance is placed on the photo-confirmed west-facing public facade.
        is_entry = i==front_edge_i
        nwin=max(1,round(seg/4.6)) if seg>3.8 else 0
        groups={}
        if nwin:
            for j in range(nwin):
                t=(j+1)/(nwin+1)
                group=groups.setdefault(round(t,5),[])
                group.append((1.38,1.22,2.48,"window"))
                group.append((1.38,4.35,5.62,"window"))
        if is_entry:
            group=groups.setdefault(.32,[])
            group.append((1.12,0.0,2.36,"door"))
        openings=sorted((t,items) for t,items in groups.items())
        cursor=0.0
        for t,items in openings:
            ow=max(item[0] for item in items)
            half=ow/(2*seg)
            t0=max(cursor,t-half); t1=min(1.0,t+half)
            if t0>cursor+.003:
                c=(p[0]+dx*(cursor+t0)/2+nx*.055,p[1]+dy*(cursor+t0)/2+ny*.055,wall_h/2)
                objects.append(cube("masonry facade pier",c,(seg*(t0-cursor),.18,wall_h),brick,asset,angle))
            zcursor=0.0
            for ow,zlo,zhi,kind in sorted(items,key=lambda x:x[1]):
                if zlo>zcursor:
                    c=(p[0]+dx*t+nx*.06,p[1]+dy*t+ny*.06,(zlo+zcursor)/2)
                    objects.append(cube("masonry below opening",c,(ow,.18,zlo-zcursor),brick,asset,angle))
                if kind=="door":
                    objects.append(cube("red entry door",(p[0]+dx*t+nx*.14,p[1]+dy*t+ny*.14,(zhi+zlo)/2),(ow-.08,.10,zhi-zlo-.06),door_mat,asset,angle))
                else:
                    zmid=(zlo+zhi)/2
                    objects.append(cube("glazed sash window",(p[0]+dx*t+nx*.12,p[1]+dy*t+ny*.12,zmid),(ow-.16,.10,zhi-zlo-.12),glass,asset,angle))
                    for z in (zlo,zhi):
                        objects.append(cube("pale stone window head and sill",(p[0]+dx*t+nx*.19,p[1]+dy*t+ny*.19,z),(ow+.13,.19,.11),trim,asset,angle))
                    for side in (-1,1):
                        objects.append(cube("pale stone window jamb",(p[0]+dx*t+nx*.19+tx*side*(ow/2),p[1]+dy*t+ny*.19+ty*side*(ow/2),zmid),(.10,.19,zhi-zlo+.10),trim,asset,angle))
                        if is_entry:
                            objects.append(cube("dark facade window shutter",(p[0]+dx*t+nx*.17+tx*side*(ow/2+.24),p[1]+dy*t+ny*.17+ty*side*(ow/2+.24),zmid),(.34,.11,zhi-zlo-.04),shutter_mat,asset,angle))
                    objects.append(cube("window center mullion",(p[0]+dx*t+nx*.22,p[1]+dy*t+ny*.22,zmid),(.065,.22,zhi-zlo-.08),trim,asset,angle))
                zcursor=zhi
            if zcursor<wall_h:
                c=(p[0]+dx*t+nx*.06,p[1]+dy*t+ny*.06,(wall_h+zcursor)/2)
                objects.append(cube("masonry above opening",c,(ow,.18,wall_h-zcursor),brick,asset,angle))
            cursor=t1
        if cursor<1.0:
            c=(p[0]+dx*(cursor+1)/2+nx*.055,p[1]+dy*(cursor+1)/2+ny*.055,wall_h/2)
            objects.append(cube("masonry facade pier",c,(seg*(1-cursor),.18,wall_h),brick,asset,angle))
        # A horizontal masonry belt marks the floor line visible in current imagery.
        if i==front_edge_i:
            c=((p[0]+q[0])/2+nx*.07,(p[1]+q[1])/2+ny*.07,floor_to_floor)
            objects.append(cube("second floor masonry belt",c,(seg+.04,.20,.12),trim,asset,angle))
        # Continuous eave fascia/gutter aligns the roof with the mapped wall perimeter.
        midx=(p[0]+q[0])/2+nx*.07; midy=(p[1]+q[1])/2+ny*.07
        objects.append(cube("roof eave fascia",(midx,midy,eave_h-.13),(seg+.06,.18,.26),roofmat,asset,angle))
    # Low-pitch main roof follows the mapped perimeter. The April 2026 image shows
    # a mostly dark shallow roof with small dormers; pitches and exact framing are estimated.
    ridge_a0, ridge_a1 = amin + length*.19, amin + length*.81
    eaves=[(x,y,eave_h) for x,y in footprint]
    ridge_by_vertex=[]
    for x,y in footprint:
        t=(x-cx)*ax+(y-cy)*ay
        tr=max(ridge_a0,min(ridge_a1,t))
        ridge_by_vertex.append((cx+tr*ax+((bmin+bmax)/2)*bx,
                                cy+tr*ay+((bmin+bmax)/2)*by,peak_h))
    verts=[]; faces=[]
    for i in range(len(footprint)):
        j=(i+1)%len(footprint)
        k=len(verts); verts.extend((eaves[i],eaves[j],ridge_by_vertex[j],ridge_by_vertex[i]))
        faces.append((k,k+1,k+2,k+3))
    # Roof underside remains open in the cutaway view.
    rmesh=bpy.data.meshes.new("estimated hip roof mesh"); rmesh.from_pydata(verts, [], faces); rmesh.materials.append(roofmat)
    roof_obj=bpy.data.objects.new("estimated hip roof", rmesh); asset.objects.link(roof_obj); objects.append(roof_obj)
    # A continuous inset roof deck closes seams between the roof facets and the wall/eaves.
    roof_deck_obj=prism("continuous roof deck closes facet seams",footprint,eave_h-.19,eave_h-.045,roofmat,asset)
    objects.append(roof_deck_obj)
    ridge_center=(cx+((ridge_a0+ridge_a1)/2)*ax+((bmin+bmax)/2)*bx,
                  cy+((ridge_a0+ridge_a1)/2)*ay+((bmin+bmax)/2)*by)
    objects.append(cube("roof ridge cap",(ridge_center[0],ridge_center[1],peak_h+.015),
                         (ridge_a1-ridge_a0,.16,.15),roofmat,asset,theta))
    # Entry trim and approach use the exact same west frontage edge as the opening.
    p,q=entry_edge
    tx,ty=q[0]-p[0],q[1]-p[1]; seg=math.hypot(tx,ty); tx/=seg; ty/=seg
    nx,ny=ty*outward_sign,-tx*outward_sign; angle=math.atan2(ty,tx)
    # The panorama places the portico to the right of the gabled wing along the facade.
    ex=p[0]+tx*seg*.32; ey=p[1]+ty*seg*.32
    # Door casing visually frames the door leaf set into the west facade.
    for side in (-1,1):
        objects.append(cube("entry casing jamb",(ex+nx*.22+tx*side*.60,ey+ny*.22+ty*side*.60,1.16),(.12,.20,2.32),trim,asset,angle))
    objects += [cube("entry casing lintel",(ex+nx*.22,ey+ny*.22,2.34),(1.32,.20,.14),trim,asset,angle),
                cube("portico landing",(ex+nx*1.0,ey+ny*1.0,.14),(6.4,2.1,.28),trim,asset,angle),
                cube("portico step upper",(ex+nx*2.0,ey+ny*2.0,.11),(5.8,.44,.22),trim,asset,angle),
                cube("portico step lower",(ex+nx*2.38,ey+ny*2.38,.07),(5.4,.42,.14),trim,asset,angle),
                cube("portico entablature",(ex+nx*.66,ey+ny*.66,6.07),(7.6,1.15,.38),trim,asset,angle),
                cube("portico cornice",(ex+nx*.66,ey+ny*.66,6.29),(8.0,1.28,.12),trim,asset,angle)]
    # Four attached square white columns follow the current panorama's prominent
    # full-height portico; count/spacing are visually estimated from perspective.
    for side in (-1,1):
        for lateral in (1.75,3.10):
            px=ex+nx*1.02+tx*side*lateral; py=ey+ny*1.02+ty*side*lateral
            objects.append(cube("portico white column",(px,py,3.12),(.40,.40,5.72),trim,asset,angle))
            for z,depth in ((.30,.62),(5.88,.56)):
                objects.append(cube("portico column base or capital",(px,py,z),(.58,depth,.22),trim,asset,angle))
    # Small roof dormers are visible on the 2026 panorama; simplified, repeated
    # forms avoid implying undocumented dimensions or interior use.
    for idx,t in enumerate((.50,.62,.74,.86)):
        px=entry_edge[0][0]+(entry_edge[1][0]-entry_edge[0][0])*t
        py=entry_edge[0][1]+(entry_edge[1][1]-entry_edge[0][1])*t
        px-=nx*3.0; py-=ny*3.0
        objects.append(cube(f"roof dormer {idx+1} cheek",(px,py,7.34),(.82,.72,.90),brick,asset,angle))
        objects.append(cube(f"roof dormer {idx+1} window",(px+nx*.39,py+ny*.39,7.40),(.50,.10,.55),glass,asset,angle))
        objects.append(cube(f"roof dormer {idx+1} cap",(px,py,7.82),(1.05,.92,.16),roofmat,asset,angle))
    # Gabled left wing is visible in the panorama. This triangle marks the
    # front-facing gable end; exact wing boundary and pitch are approximate.
    gx=entry_edge[0][0]+(entry_edge[1][0]-entry_edge[0][0])*.82
    gy=entry_edge[0][1]+(entry_edge[1][1]-entry_edge[0][1])*.82
    half=4.15
    verts=[(gx-tx*half,gy-ty*half,6.26),(gx+tx*half,gy+ty*half,6.26),(gx,gy,gable_peak_h),
           (gx+nx*.18-tx*half,gy+ny*.18-ty*half,6.26),(gx+nx*.18+tx*half,gy+ny*.18+ty*half,6.26),(gx+nx*.18,gy+ny*.18,gable_peak_h)]
    mesh=bpy.data.meshes.new("front gable masonry mesh"); mesh.from_pydata(verts,[],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]); mesh.materials.append(brick)
    obj=bpy.data.objects.new("front gable masonry",mesh); asset.objects.link(obj); objects.append(obj)
    # Paired compact wall lights anchor the doorway without detached props.
    for side in (-1,1):
        px=ex+nx*.21+tx*side*1.22; py=ey+ny*.21+ty*side*1.22
        objects.append(cube("entry wall lantern",(px,py,2.05),(.16,.10,.38),metal,asset,angle))

    # Schematic lower-floor room plan; internal layout is not survey evidence.
    def xy(a,b): return (cx+a*ax+b*bx, cy+a*ay+b*by)
    mid_a=(amin+amax)/2
    # Corridor and partitions stay within the official outline bounding envelope.
    # Use several short panels so the rooms remain readable in top-down cutaway.
    part_t=0.13
    for b in (bmin+width*.36, bmin+width*.66):
        p1=xy(amin+1.1,b); p2=xy(amax-1.1,b)
        lengthp=math.dist(p1,p2)
        # doors represented by gaps on the corridor wall
        for fraction in (.16,.31,.48,.64,.80):
            center_a=amin+1.1+lengthp*fraction
            c=xy(center_a,b)
            # use partition panels in segments between doors
        # segments over width, interrupted by door openings
        cuts=[0,.12,.21,.27,.39,.45,.56,.62,.74,.80,.91,1]
        for u,v in zip(cuts[::2],cuts[1::2]):
            c=xy(amin+1.1+lengthp*(u+v)/2,b)
            objects.append(cube("interior partition",(c[0],c[1],1.45),(lengthp*(v-u),part_t,2.9),wall,asset,theta))
    # End partitions segment study/library, kitchen/dining and sleeping rooms.
    for a in (amin+length*.25, amin+length*.48, amin+length*.73):
        p=xy(a,bmin+width*.08)
        objects.append(cube("interior cross partition",(p[0],p[1],1.45),(part_t,width*.22,2.9),wall,asset,theta))
    # Interior floor covering follows the footprint and sits above the foundation.
    floor_obj=prism("interior floor", footprint, .01, .075, floor, asset)
    objects.append(floor_obj)
    # Dining room: shared table and chairs.
    d=xy(amin+length*.36,bmin+width*.51)
    objects.append(cube("chapter dining table",(d[0],d[1],.78),(length*.18,1.35,.12),wood,asset,theta))
    for k in range(6):
        a=amin+length*.28+k*length*.032
        for side in (-1,1):
            p=xy(a,bmin+width*.51+side*1.0)
            objects.append(cube("dining chair",(p[0],p[1],.48),(.42,.42,.88),upholstery,asset,theta))
    # Kitchen counters and island at east end of the central plan.
    for b in (bmin+width*.14,bmin+width*.30):
        p=xy(amin+length*.82,b)
        objects.append(cube("kitchen counter",(p[0],p[1],.48),(length*.23,.58,.96),wood,asset,theta))
    island=xy(amin+length*.83,bmin+width*.23)
    objects.append(cube("kitchen island",(island[0],island[1],.48),(length*.13,.82,.96),trim,asset,theta))
    # Common room sofas, coffee table, and wall-mounted media cabinet.
    lounge=xy(amin+length*.24,bmin+width*.48)
    objects += [cube("common room sofa",(lounge[0],lounge[1],.48),(length*.13,.82,.92),upholstery,asset,theta),
                cube("common room coffee table",(lounge[0]+ax*2.0,lounge[1]+ay*2.0,.38),(1.25,.7,.72),wood,asset,theta),
                cube("chapter room credenza",(lounge[0]-ax*2.3,lounge[1]-ay*2.3,.46),(length*.09,.5,.9),wood,asset,theta)]
    # Private bedroom modules with bed, pillow and nightstand; use the back wing.
    for idx, (a,b) in enumerate(((amin+length*.16,bmin+width*.80),(amin+length*.34,bmin+width*.80),
                                 (amin+length*.55,bmin+width*.80),(amin+length*.76,bmin+width*.80))):
        p=xy(a,b)
        objects += [cube(f"bed {idx+1}",(p[0],p[1],.34),(2.0,2.8,.40),wood,asset,theta),
                    cube(f"bedding {idx+1}",(p[0],p[1],.58),(1.88,2.48,.12),white,asset,theta),
                    cube(f"nightstand {idx+1}",(p[0]+ax*1.5,p[1]+ay*1.5,.42),(.5,.5,.8),wood,asset,theta)]
    # Laundry/storage and bathrooms are represented as legible fixtures.
    for idx,a in enumerate((amin+length*.57,amin+length*.66)):
        p=xy(a,bmin+width*.13)
        objects += [cube("bathroom vanity",(p[0],p[1],.44),(1.25,.55,.88),trim,asset,theta),
                    cube("bathroom basin",(p[0],p[1],.91),(.48,.34,.08),white,asset,theta)]
    # Make a separate render setup outside the exported collection.
    rx=xy(amax+12,bmin-18)
    camera_data=bpy.data.cameras.new("Beta Sigma Psi preview camera"); camera=bpy.data.objects.new("Beta Sigma Psi preview camera",camera_data); preview.objects.link(camera)
    camera.location=(cx+length*.95, cy-width*1.4, 27); aim(camera,(cx,cy,2.5)); camera.data.lens=45; scene.camera=camera
    light_data=bpy.data.lights.new("Beta Sigma Psi preview softbox", "AREA"); light=bpy.data.objects.new("Beta Sigma Psi preview softbox",light_data); preview.objects.link(light)
    light.location=(cx+nx*18,cy+ny*18,19); light.data.energy=6500; light.data.shape="DISK"; light.data.size=18; aim(light,(cx,cy,0))
    scene.world.color=(.36,.42,.52)
    scene.world.use_nodes=True
    background=next(n for n in scene.world.node_tree.nodes if n.type=="BACKGROUND")
    background.inputs["Color"].default_value=(.38,.46,.60,1)
    background.inputs["Strength"].default_value=.52
    scene.render.engine="BLENDER_EEVEE"; scene.render.resolution_x=1280; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
    scene.view_settings.view_transform="Standard"; scene.view_settings.look="None"; scene.view_settings.exposure=.45
    # Render full exterior then interior cutaway with the roof hidden from camera only.
    viewdist=max(length,width)*2.4
    scene.camera.data.lens=39; scene.camera.location=(cx+nx*viewdist+tx*2.0,cy+ny*viewdist+ty*2.0,17.0); aim(camera,(cx,cy,4.0))
    scene.render.filepath=str(PREVIEW_EXTERIOR); bpy.ops.render.render(write_still=True)
    roof_obj.hide_render=True
    roof_deck_obj.hide_render=True
    floor_obj.hide_render=True
    scene.camera.data.lens=42; scene.camera.location=(cx+nx*max(length,width)*1.45+tx*length*.20,cy+ny*max(length,width)*1.45+ty*length*.20, max(length,width)*1.22); aim(camera,(cx,cy,2.6))
    scene.render.filepath=str(PREVIEW_INTERIOR); bpy.ops.render.render(write_still=True)
    roof_obj.hide_render=False
    roof_deck_obj.hide_render=False
    floor_obj.hide_render=False
    # Join all asset geometry into the legacy one-object collection interface.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(asset.objects): obj.select_set(True)
    bpy.context.view_layer.objects.active=asset.objects[0]
    bpy.ops.object.join()
    primary=bpy.context.object; primary.name=OBJECT
    primary.data.name="Beta Sigma Psi detailed schematic mesh"
    # Restore a useful exterior opening view and save only this building library.
    scene.render.filepath="//"
    ASSET_PATH.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    bounds=[
        [min(v.co.x + primary.location.x for v in primary.data.vertices),max(v.co.x + primary.location.x for v in primary.data.vertices)],
        [min(v.co.y + primary.location.y for v in primary.data.vertices),max(v.co.y + primary.location.y for v in primary.data.vertices)],
        [min(v.co.z + primary.location.z for v in primary.data.vertices),max(v.co.z + primary.location.z for v in primary.data.vertices)],
    ]
    gis_area_attr=float(attrs.get("Shape__Area",0.0)); gis_length_attr=float(attrs.get("Shape__Length",0.0))
    evidence={
      "asset_id":ASSET_ID,"asset_path":"modular/buildings/"+ASSET_ID+".blend","collection":COLLECTION,"scene":SCENE,"object":OBJECT,
      "identity":{"name":attrs["BUILDING_N"],"address":attrs["ADDRESS"],"purdue_gis_fid":793,"osm_way_id":301841254},
      "sources":[
        {"provider":"Purdue University campus GIS, BuildingShapesZip4 ArcGIS FeatureServer layer 0","url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D793&outFields=*&returnGeometry=true&outSR=4326&f=pjson","feature_id":"FID 793; Beta Sigma Psi; 525 University St","retrieved":"2026-10-26","source_date":"service last edit metadata not populated for this feature","source_crs":"WGS 84 (EPSG:4326) response; source layer metadata captured alongside snapshot","method":"projected all vertices using documented local campus approximation, then compared plan polygon, centroid, and dimensions","uncertainty":"GIS polygon represents mapped building outline; absolute exterior-wall registration may differ from roofing/overhang line; reported source area is not an as-built survey"},
        {"provider":"Purdue University campus GIS, BuildingShapesZip4 ArcGIS FeatureServer layer 0","url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D793&outFields=*&returnGeometry=true&outSR=2968&f=pjson","feature_id":"FID 793; projected comparison snapshot","retrieved":"2026-10-26","source_date":"service last edit metadata not populated for this feature","source_crs":"EPSG:2968 (NAD83 / Indiana West, US survey feet), converted to meters using 0.3048006096","method":"independent projected coordinate calculation of polygon area/perimeter and dimensions","uncertainty":"source Shape__Area/Shape__Length attributes do not match the geometry-derived measures; unresolved source-attribute units or update status"},
        {"provider":"OpenStreetMap contributors, campus OSM snapshot","url":"https://www.openstreetmap.org/way/301841254","feature_id":"way 301841254; addr:housenumber=525; building=school","retrieved":"2026-10-22T03:45:50Z snapshot","source_date":"feature edit timestamp unavailable in snapshot","source_crs":"WGS 84 (EPSG:4326)","method":"way node coordinate polygon cross-check against official Purdue GIS footprint","uncertainty":"OSM building class tag is generic and provides no height or style evidence"},
        {"provider":"Purdue University BoilerLink organization listing","url":"https://boilerlink.purdue.edu/organization/betasigmapsi","feature_id":"Beta Sigma Psi, Purdue University","retrieved":"2026-10-26","source_date":"current page; date unavailable","source_crs":"not applicable","method":"cross-check chapter name and address","uncertainty":"page identifies chapter and address but supplies no measured building plans or elevations"},
        {"provider":"Beta Sigma Psi National Fraternity, Active Chapters","url":"https://www.betasigmapsi.org/active-chapters/","feature_id":"Purdue University, Beta Chapter","retrieved":"2026-10-26","source_date":"current page; date unavailable","source_crs":"not applicable","method":"cross-check chapter identity and active status","uncertainty":"does not document the Purdue house architecture"},
        {"provider":"BoilerApartments historical rental listing for 525 N University","url":"https://www.boilerapartments.com/listing/15365","feature_id":"Beta Sigma Psi / 525 N University","retrieved":"2026-10-26","source_date":"listing source is circa 2012; exact page publication date not displayed","source_crs":"not applicable","method":"program/floor-count cross-check only","uncertainty":"describes a multi-unit house, shared bathrooms on each floor, porch, game room and parking; historical listing is not a current facade image or measured plan"},
        {"provider":"Google Street View, pano Y4KmPWdSoh5sr7LgMX0bpw","url":"https://www.google.com/maps/@40.4300068,-86.9170988,2847a,13.1y/data=!3m5!1e1!3m3!1sY4KmPWdSoh5sr7LgMX0bpw!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D90%26panoid%3DY4KmPWdSoh5sr7LgMX0bpw%26yaw%3D0?entry=ttu","thumbnail_url":"https://streetviewpixels-pa.clients6.google.com/v1/thumbnail?cb_client=maps_sv.tactile&w=900&h=600&pitch=0&panoid=Y4KmPWdSoh5sr7LgMX0bpw&yaw=270","image_snapshot":"audit/beta_sigma_psi/sources/google_streetview_pano_Y4KmPWdSoh5sr7LgMX0bpw_2026-04.jpg","feature_id":"Exact address 525 N University; Google place header and foreground Beta Sigma Psi sign in panorama","retrieved":"2026-10-26","source_date":"panorama dated April 2026","source_crs":"WGS 84 panorama location shown by Google Maps; image is perspective, not orthographic","method":"visual inspection of exact-address facade pano; yaw 270, pitch 0 thumbnail used for readable frontal view","observed":"two-story connected red-brick masses, left-facing front gable, prominent white-column portico, red entry door, pale window trim/shutters, low dark roof with small dormers, brick retaining wall and approach","uncertainty":"pano verifies visible facade elements and relative silhouette, but perspective does not establish measured height, exact window dimensions, roof pitch, or concealed elevations; model dimensions are estimates"},
        {"provider":"Purdue University Debris Yearbook, 1966, accessed via e-yearbook.com","url":"https://www.e-yearbook.com/yearbooks/Purdue_University_Debris_Yearbook/1966/Page_1.html","feature_id":"Chapter narrative near printed page 326","retrieved":"2026-10-26","source_date":"1965-66 yearbook","source_crs":"not applicable","method":"historical identity/context source","uncertainty":"says Beta Sigma Psi took over its new chapter house from Alpha Chi Omega; does not provide verified elevations or dimensions"}],
      "footprint":{"source_fid":793,"vertex_count":len(footprint),"geometry_derived_area_m2_local_approx":round(computed_footprint_area_m2,3),"geometry_derived_perimeter_m_local_approx":round(computed_footprint_perimeter_m,3),"stateplane_2968_geometry_derived_area_m2_approx":410.79,"stateplane_2968_geometry_derived_perimeter_m_approx":87.96,"api_shape_area_attribute":gis_area_attr,"api_shape_length_attribute":gis_length_attr,"api_shape_attribute_status":"unresolved metadata discrepancy: API attributes are not used as polygon area/length; values differ substantially from measures computed from vertices; units or stale-field status unknown","attribute_difference_pct_vs_geometry":{"shape_area":round((gis_area_attr/computed_footprint_area_m2-1)*100,1),"shape_length":round((gis_length_attr/computed_footprint_perimeter_m-1)*100,1)},"projected_dimensions_m":{"length":round(length,3),"width":round(width,3)},"campus_xy_center_m":[round(cx,3),round(cy,3)],"projection":"X=(lon+86.9137)*111412.84*cos(40.4274deg), Y=(lat-40.4274)*111040; independent check EPSG:2968 in US survey feet converted at 0.3048006096 m/ft","geometry_source":"authoritative GIS FID 793 polygon; used without rescaling"},
      "geometry":{"wall_height_m_estimated":wall_h,"roof_eave_m_estimated":eave_h,"main_roof_ridge_m_estimated":peak_h,"front_gable_apex_m_estimated":gable_peak_h,"maximum_model_height_m_estimated":max(peak_h,gable_peak_h),"story_count_model":2,"height_status":"estimated; Street View visually supports two storeys but no surveyed elevations; GIS NUM_LEVELS=1 conflicts with 2012 listing's shared bathrooms on each floor; GIS Extrution=22 units/meaning not independently verified","roof_form":"shallow dark main roof and small dormers plus taller left front gable visible in April 2026 panorama; all pitches and structure are estimated","facade":"April 2026 exact-address panorama directly supports two connected red-brick masses, west-facing gabled wing, white-column portico, red entry door, pale-trim sash windows/shutters and dormers; dimensions and hidden details estimated","interior":"schematic lower-floor common room, dining, kitchen, bedrooms, bathrooms and circulation informed by historical 2012 program description; not a measured plan"},
      "validation":{"asset_bounds_world_m":bounds,"asset_collection_objects":[OBJECT],"object_count":1,"materials":len(primary.data.materials),"preview_exterior":"audit/beta_sigma_psi/beta_sigma_psi_exterior.png","preview_interior":"audit/beta_sigma_psi/beta_sigma_psi_interior.png","saved":"fresh-open check pending"},
      "edits":["Replaced the single 16 m placeholder block with the exact official GIS FID 793 footprint.","Added estimated two-storey wall envelope, photo-guided west facade, gabled wing, white-column portico, red entry, window rhythm, shallow roof and dormers.","Added schematic lower-floor shared-house room plan based on historical exact-address program evidence.","No campus position, origin, collection, object name or asset path was changed."],
      "limitations":["GIS vertex-derived area/perimeter conflict with the API Shape__Area/Length attributes; the discrepancy remains unresolved metadata and the polygon vertices remain the geometry authority.","GIS NUM_LEVELS=1 conflicts with exact-address historical multi-floor bathroom evidence and the two-storey current panorama; story count and all heights remain estimates.","No measured elevations or as-built interior plan were located. Roof dimensions, facade dimensions, concealed elevations and room arrangement are approximate."]}
    EVIDENCE_PATH.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print("BETA_SIGMA_PSI_BUILD_RESULT="+json.dumps({"path":str(ASSET_PATH),"bounds":bounds,"footprint_points":len(footprint),"parts_joined":len(objects),"materials":len(primary.data.materials),"previews":[str(PREVIEW_EXTERIOR),str(PREVIEW_INTERIOR)]}))


if __name__ == "__main__":
    make_scene()
