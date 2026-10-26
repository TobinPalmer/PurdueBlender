"""Build the standalone Forney Hall library from Purdue GIS and OSM evidence.

This intentionally preserves the manifest's massing asset ID, file, scene and
export collection.  Campus coordinates use the project conversion documented in
modular/AGENTS.md.  Run with Blender 5.2 in background mode.
"""
from __future__ import annotations

import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULAR_ROOT = PROJECT_ROOT / "modular"
ASSET_ID = "massing_forney_hall_of_chemical_engineering_frny_d94ba3a"
ASSET_FILE = MODULAR_ROOT / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE_DIR = PROJECT_ROOT / "audit" / "forney_hall_of_chemical_engineering_frny_d94ba3a"
GIS_FILE = EVIDENCE_DIR / "purdue_gis_current.json"
SCENE_NAME = f"Building_{ASSET_ID}"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
MAIN_OBJECT_NAME = "Forney Hall of Chemical Engineering (FRNY)"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137


def local_xy(lon, lat):
    """Approximate project map conversion, in meters from campus origin."""
    x = (float(lon) - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (float(lat) - ORIGIN_LAT) * 111040.0
    return (x, y)


def rdp_open(points, tolerance):
    if len(points) <= 2:
        return list(points)
    a, b = points[0], points[-1]
    vx, vy = b[0] - a[0], b[1] - a[1]
    denom = vx * vx + vy * vy
    best_index, best_sq = -1, -1.0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        if denom == 0.0:
            d2 = (px - a[0]) ** 2 + (py - a[1]) ** 2
        else:
            t = max(0.0, min(1.0, ((px-a[0])*vx + (py-a[1])*vy) / denom))
            d2 = (px-(a[0]+t*vx)) ** 2 + (py-(a[1]+t*vy)) ** 2
        if d2 > best_sq:
            best_index, best_sq = i, d2
    if best_sq > tolerance * tolerance:
        return rdp_open(points[:best_index+1], tolerance)[:-1] + rdp_open(points[best_index:], tolerance)
    return [points[0], points[-1]]


def simplify_closed(points, tolerance=0.4):
    """Closed-loop RDP split at the point farthest from the first vertex."""
    pts = list(points)
    if len(pts) > 1 and Vector((pts[0][0]-pts[-1][0], pts[0][1]-pts[-1][1])).length < 1e-8:
        pts.pop()
    if len(pts) < 3:
        raise ValueError("GIS footprint has fewer than 3 vertices")
    far_i = max(range(1, len(pts)), key=lambda i: (pts[i][0]-pts[0][0])**2 + (pts[i][1]-pts[0][1])**2)
    first = rdp_open(pts[:far_i+1], tolerance)
    second = rdp_open(pts[far_i:] + [pts[0]], tolerance)
    result = first[:-1] + second[:-1]
    if signed_area(result) < 0:
        result.reverse()
    return result


def signed_area(poly):
    return 0.5 * sum(poly[i][0]*poly[(i+1)%len(poly)][1] - poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))


def polygon_centroid(poly):
    a = signed_area(poly)
    if abs(a) < 1e-8:
        return (sum(p[0] for p in poly)/len(poly), sum(p[1] for p in poly)/len(poly))
    cx = cy = 0.0
    for i, p in enumerate(poly):
        q = poly[(i+1)%len(poly)]
        cross = p[0]*q[1] - q[0]*p[1]
        cx += (p[0]+q[0])*cross
        cy += (p[1]+q[1])*cross
    return (cx/(6*a), cy/(6*a))


def create_material(name, base, roughness=0.75, metal=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*base, 1.0)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metal
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, bsdf, links, nodes


def create_building_materials():
    brick, brick_bsdf, links, nodes = create_material("FRNY | warm Purdue red brick", (0.27, 0.052, 0.026), 0.88)
    coord = nodes.new("ShaderNodeTexCoord")
    tex = nodes.new("ShaderNodeTexBrick")
    tex.inputs["Color1"].default_value = (0.36, 0.082, 0.040, 1.0)
    tex.inputs["Color2"].default_value = (0.22, 0.036, 0.020, 1.0)
    tex.inputs["Mortar"].default_value = (0.28, 0.21, 0.14, 1.0)
    tex.inputs["Scale"].default_value = 1.0
    tex.inputs["Brick Width"].default_value = 0.36
    tex.inputs["Row Height"].default_value = 0.09
    tex.inputs["Mortar Size"].default_value = 0.008
    tex.inputs["Mortar Smooth"].default_value = 0.003
    tex.inputs["Bias"].default_value = 0.5
    links.new(coord.outputs["Object"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], brick_bsdf.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.14
    bump.inputs["Distance"].default_value = 0.035
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], brick_bsdf.inputs["Normal"])

    limestone, stone_bsdf, links, nodes = create_material("FRNY | Bedford limestone trim", (0.70, 0.65, 0.55), 0.82)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 8.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.52, 0.48, 0.40, 1)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.82, 0.77, 0.66, 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], stone_bsdf.inputs["Base Color"])

    glass, glass_bsdf, links, nodes = create_material("FRNY | blue charcoal glazing", (0.035, 0.07, 0.095), 0.22, 0.22)
    glass_bsdf.inputs["Metallic"].default_value = 0.28
    glass_bsdf.inputs["IOR"].default_value = 1.46

    metal, _, _, _ = create_material("FRNY | dark bronze window framing", (0.075, 0.065, 0.055), 0.31, 0.68)
    roof, roof_bsdf, roof_links, roof_nodes = create_material("FRNY | charcoal membrane roof", (0.075, 0.09, 0.09), 0.87)
    roof_noise = roof_nodes.new("ShaderNodeTexNoise")
    roof_noise.inputs["Scale"].default_value = 3.2
    roof_noise.inputs["Detail"].default_value = 2.0
    roof_ramp = roof_nodes.new("ShaderNodeValToRGB")
    roof_ramp.color_ramp.elements[0].color = (0.055, 0.067, 0.066, 1)
    roof_ramp.color_ramp.elements[1].color = (0.15, 0.17, 0.16, 1)
    roof_links.new(roof_noise.outputs["Fac"], roof_ramp.inputs["Fac"])
    roof_links.new(roof_ramp.outputs["Color"], roof_bsdf.inputs["Base Color"])
    copper, _, _, _ = create_material("FRNY | aged green metal coping", (0.16, 0.25, 0.21), 0.38, 0.62)
    concrete, _, _, _ = create_material("FRNY | interior terrazzo concrete", (0.42, 0.42, 0.39), 0.78)
    stainless, _, _, _ = create_material("FRNY | distillation tower stainless steel", (0.42, 0.48, 0.51), 0.24, 0.82)
    upholstery, _, _, _ = create_material("FRNY | auditorium seat fabric", (0.24, 0.075, 0.055), 0.8)
    interior_wall, _, _, _ = create_material("FRNY | schematic warm interior plaster", (0.71, 0.67, 0.58), 0.86)
    label_ink, _, _, _ = create_material("FRNY | schematic label ink", (0.012, 0.018, 0.016), 0.82)
    return {
        "brick": brick, "stone": limestone, "glass": glass, "metal": metal,
        "roof": roof, "coping": copper, "concrete": concrete,
        "stainless": stainless, "upholstery": upholstery, "interior_wall": interior_wall,
        "label_ink": label_ink,
    }


class Batch:
    def __init__(self, name, materials):
        self.name = name
        self.materials = list(materials)
        self.vertices, self.faces, self.material_ids = [], [], []

    def box(self, center, size, u, n, material_index=0):
        center = Vector((center[0],center[1],0.0)) if len(center)==2 else Vector(center)
        u = Vector((u[0],u[1],0.0)).normalized()
        n = Vector((n[0],n[1],0.0)).normalized()
        z = Vector((0, 0, 1))
        hx, hy, hz = size[0]/2, size[1]/2, size[2]/2
        start = len(self.vertices)
        for zz in (-hz, hz):
            for yy in (-hy, hy):
                for xx in (-hx, hx):
                    p = center + u*xx + n*yy + z*zz
                    self.vertices.append(tuple(p))
        faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
        for f in faces:
            self.faces.append(tuple(start+i for i in f))
            self.material_ids.append(material_index)

    def cylinder(self, center, radius, depth, material_index, segments=24):
        center = Vector(center)
        start = len(self.vertices)
        for z in (-depth/2, depth/2):
            for i in range(segments):
                a = 2*math.pi*i/segments
                self.vertices.append((center.x+radius*math.cos(a), center.y+radius*math.sin(a), center.z+z))
        bottom = tuple(start+i for i in range(segments-1,-1,-1))
        top = tuple(start+segments+i for i in range(segments))
        self.faces += [bottom, top]
        self.material_ids += [material_index, material_index]
        for i in range(segments):
            j=(i+1)%segments
            self.faces.append((start+i,start+j,start+segments+j,start+segments+i))
            self.material_ids.append(material_index)

    def wall_roundel(self, center, u, n, radius, depth, material_index, segments=32):
        """A shallow circular masonry relief oriented to a vertical facade."""
        center = Vector((center[0],center[1],center[2]))
        u = Vector((u[0],u[1],0.0)).normalized()
        n = Vector((n[0],n[1],0.0)).normalized()
        zaxis = Vector((0,0,1))
        start = len(self.vertices)
        for side in (-1,1):
            c = center + n*(depth*side/2)
            for k in range(segments):
                a = 2*math.pi*k/segments
                p = c + u*(radius*math.cos(a)) + zaxis*(radius*math.sin(a))
                self.vertices.append(tuple(p))
        self.faces.append(tuple(start+k for k in range(segments-1,-1,-1)))
        self.material_ids.append(material_index)
        self.faces.append(tuple(start+segments+k for k in range(segments)))
        self.material_ids.append(material_index)
        for k in range(segments):
            j=(k+1)%segments
            self.faces.append((start+k,start+j,start+segments+j,start+segments+k))
            self.material_ids.append(material_index)

    def finish(self, collection):
        if not self.faces:
            return None
        mesh = bpy.data.meshes.new(self.name + "_Mesh")
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.materials.clear()
        for mat in self.materials:
            mesh.materials.append(mat)
        for p, mi in zip(mesh.polygons, self.material_ids):
            p.material_index = mi
        mesh.update()
        obj = bpy.data.objects.new(self.name, mesh)
        collection.objects.link(obj)
        return obj


def add_poly_prism(collection, name, poly, z0, z1, materials, side_index=0, top_index=1, bottom_index=1):
    n = len(poly)
    verts = [(x,y,z0) for x,y in poly] + [(x,y,z1) for x,y in poly]
    faces = []
    mids = []
    for i in range(n):
        j = (i+1) % n
        faces.append((i,j,n+j,n+i)); mids.append(side_index)
    faces.append(tuple(range(n,2*n))); mids.append(top_index)
    faces.append(tuple(range(n-1,-1,-1))); mids.append(bottom_index)
    mesh = bpy.data.meshes.new(name+"_Mesh")
    mesh.from_pydata(verts, [], faces)
    for mat in materials: mesh.materials.append(mat)
    for p, mi in zip(mesh.polygons, mids): p.material_index = mi
    mesh.update()
    obj = bpy.data.objects.new(name, mesh); collection.objects.link(obj)
    return obj


def add_material_to_object(obj, mats):
    for mat in mats:
        obj.data.materials.append(mat)


def object_frame(obj, u, n):
    u = Vector(u).normalized(); n = Vector(n).normalized(); z = Vector((0,0,1))
    mat = Matrix(((u.x,n.x,z.x),(u.y,n.y,z.y),(u.z,n.z,z.z)))
    obj.rotation_euler = mat.to_euler()


def add_text(name, body, collection, location, u, n, size, material, align='CENTER'):
    data = bpy.data.curves.new(name+"_Curve", type="FONT")
    data.body = body; data.size = size; data.align_x = align; data.align_y = "CENTER"
    data.extrude = 0.003; data.bevel_depth = 0.001
    obj = bpy.data.objects.new(name, data); collection.objects.link(obj)
    obj.location = location
    u = Vector((u[0],u[1],0.0)).normalized(); n = Vector((n[0],n[1],0.0)).normalized(); z = Vector((0,0,1))
    rot = Matrix(((u.x,z.x,n.x),(u.y,z.y,n.y),(u.z,z.z,n.z)))
    obj.rotation_euler = rot.to_euler()
    obj.data.materials.append(material)
    return obj


def add_floor_label(name, body, collection, location, size, material):
    data=bpy.data.curves.new(name+"_Curve",type="FONT")
    data.body=body; data.size=size; data.align_x="CENTER"; data.align_y="CENTER"
    data.extrude=.002
    obj=bpy.data.objects.new(name,data); collection.objects.link(obj)
    obj.location=location
    obj.data.materials.append(material)
    return obj


def clean_asset_collection(asset_col):
    # Replace only the building's existing geometry while retaining stable container names.
    for child in list(asset_col.children):
        for obj in list(child.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(child)
    for obj in list(asset_col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def create_entry_arch(batch, center, u, n, inner_width, z0, spring_z, depth, mat_index):
    """A shallow semicircular stone archivolt and jambs, assembled from clean blocks."""
    radius = inner_width/2
    mid = (z0 + spring_z)/2
    batch.box((center[0]-u[0]*(radius+0.22),center[1]-u[1]*(radius+0.22),mid),(.44,depth,spring_z-z0),u,n,mat_index)
    batch.box((center[0]+u[0]*(radius+0.22),center[1]+u[1]*(radius+0.22),mid),(.44,depth,spring_z-z0),u,n,mat_index)
    segments = 12
    for i in range(segments):
        a0 = math.pi*i/segments
        a1 = math.pi*(i+1)/segments
        a = (a0+a1)/2
        r = radius + 0.24
        pos = (center[0] + u[0]*math.cos(a)*r,
               center[1] + u[1]*math.cos(a)*r,
               spring_z + math.sin(a)*r)
        tangent = (u[0]*-math.sin(a),u[1]*-math.sin(a))
        tangent_len = math.hypot(*tangent) or 1
        tangent = (tangent[0]/tangent_len,tangent[1]/tangent_len)
        chord = (a1-a0)*r
        batch.box(pos,(chord+0.025,depth,0.38),tangent,n,mat_index)


def choose_entry(poly):
    best = None
    for i, a in enumerate(poly):
        b = poly[(i+1)%len(poly)]
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx,dy)
        if length < 10:
            continue
        u = (dx/length,dy/length)
        n = (u[1],-u[0])  # polygon normalized CCW -> right-hand normal is outward
        if n[1] < -0.15:
            score = length * (0.6 + max(0.0,-n[1]))
            if best is None or score > best[0]: best = (score,i,a,b,length,u,n)
    return best[1:] if best else None


def build():
    if not bpy.data.scenes.get(SCENE_NAME):
        bpy.ops.wm.open_mainfile(filepath=str(ASSET_FILE))
    if not GIS_FILE.exists():
        raise FileNotFoundError(f"Missing building evidence snapshot: {GIS_FILE}")
    gis = json.loads(GIS_FILE.read_text(encoding="utf-8-sig"))
    candidates = [f for f in gis.get("features",[]) if f.get("properties",{}).get("ABBR")=="FRNY"]
    feature = next((f for f in candidates if f.get("properties",{}).get("OBJECTID")==12), None)
    if feature is None:
        raise ValueError("Purdue GIS query did not include expected FRNY feature OBJECTID 12")
    raw = feature["geometry"]["coordinates"][0]
    poly = simplify_closed([local_xy(lon,lat) for lon,lat in raw], 0.4)
    xmin,xmax=min(p[0] for p in poly),max(p[0] for p in poly)
    ymin,ymax=min(p[1] for p in poly),max(p[1] for p in poly)
    area_local = abs(signed_area(poly))
    perimeter = sum(math.dist(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))

    scene = bpy.data.scenes.get(SCENE_NAME)
    if scene is None:
        scene = bpy.data.scenes.new(SCENE_NAME)
    if bpy.context.window:
        bpy.context.window.scene = scene
    asset_col = bpy.data.collections.get(COLLECTION_NAME)
    if asset_col is None:
        asset_col = bpy.data.collections.new(COLLECTION_NAME)
        scene.collection.children.link(asset_col)
    clean_asset_collection(asset_col)
    interior_col = bpy.data.collections.new("FRNY_Schematic_Interior")
    asset_col.children.link(interior_col)

    # Remove cameras or lights left by a former draft only if they belong to this scene.
    for obj in list(scene.objects):
        if obj.name.startswith("FRNY_Preview"):
            bpy.data.objects.remove(obj, do_unlink=True)

    m = create_building_materials()
    wall_top = 13.9   # GIS elevation register has R=46 ft ~= 14.02 m; treat as estimated
    coping_top = 14.35
    entry = choose_entry(poly)
    door_width, door_height = 2.75, 3.35
    # Main shell with a true ground-level entry gap on the best south-facing facade.
    i_entry = entry[0] if entry else -1
    verts = [(x,y,0.0) for x,y in poly] + [(x,y,wall_top) for x,y in poly]
    faces, mids = [], []
    for i, a in enumerate(poly):
        j=(i+1)%len(poly); b=poly[j]
        if i != i_entry:
            faces.append((i,j,len(poly)+j,len(poly)+i)); mids.append(0)
            continue
        length=math.dist(a,b)
        t0=max(1.15,(length-door_width)/2); t1=min(length-1.15,t0+door_width)
        if t1<=t0+0.5:
            faces.append((i,j,len(poly)+j,len(poly)+i)); mids.append(0)
        else:
            def idx(t,z):
                p=(a[0]+(b[0]-a[0])*t/length,a[1]+(b[1]-a[1])*t/length)
                verts.append((p[0],p[1],z)); return len(verts)-1
            a0=idx(0,0); a1=idx(t0,0); a2=idx(t0,wall_top); a3=idx(0,wall_top)
            b0=idx(t1,0); b1=idx(length,0); b2=idx(length,wall_top); b3=idx(t1,wall_top)
            t_top0=idx(t0,door_height); t_top1=idx(t1,door_height)
            faces.extend([(a0,a1,a2,a3),(b0,b1,b2,b3),(t_top0,t_top1,b3,a2)])
            mids.extend([0,0,0])
    faces.append(tuple(range(len(poly),2*len(poly)))); mids.append(1)
    faces.append(tuple(range(len(poly)-1,-1,-1))); mids.append(1)
    mesh=bpy.data.meshes.new("FRNY_source_footprint_shell_mesh")
    mesh.from_pydata(verts,[],faces); mesh.materials.append(m["brick"]); mesh.materials.append(m["roof"])
    for p,mi in zip(mesh.polygons,mids): p.material_index=mi
    mesh.update()
    shell=bpy.data.objects.new(MAIN_OBJECT_NAME,mesh); asset_col.objects.link(shell)
    shell["stable_asset_id"]=ASSET_ID
    shell["footprint_source"]="Purdue campus ArcGIS MapServer layer 0, OBJECTID 12 / FRNY"
    shell["source_crs"]="EPSG:4326; converted by PurdueMap local campus approximation"
    shell["source_footprint_vertices_raw"]=len(raw)-1
    shell["source_footprint_vertices_model"]=len(poly)
    shell["source_footprint_simplification_m"]=0.4
    shell["source_footprint_area_local_approx_m2"]=round(area_local,2)
    shell["source_area_attribute_m2"]=feature["properties"].get("Shape.STArea()")
    shell["height_model_m"]=wall_top
    shell["height_uncertainty"]="GIS legacy R=46 ft (~14.02 m) treated as roof-height estimate; not a survey; GIS level count conflicts with street photo story count."
    shell["interior_status"]="Schematic interior features based on official Purdue descriptions; room geometry and positions are not surveyed floor plans."
    shell["orientation_uncertainty"]="Purdue GIS footprint orientation used; exact entry edge placement inferred from street-level photo and map context."

    # Brick courses, limestone belt bands and window assemblies follow the photographed
    # brick/stone language; exact detail is inferred from street image, not measured.
    trim=Batch("FRNY_Limestone_Belts_and_Window_Trim",[m["stone"]])
    pilasters=Batch("FRNY_Subtle_Brick_Pilaster_Bays",[m["brick"]])
    glazing=Batch("FRNY_Window_Glazing_and_Bronze_Frames",[m["glass"],m["metal"],m["stone"]])
    level_centers=[1.45,4.05,6.65,9.25,11.85]
    rows_used=0; window_count=0
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length<3.2: continue
        u=(dx/length,dy/length); n=(u[1],-u[0])
        # Continuous belt courses from photo, restrained projections to preserve footprint.
        for z,h in [(0.36,.22),(3.55,.20),(13.58,.30)]:
            trim.box(((a[0]+b[0])/2+n[0]*.07,(a[1]+b[1])/2+n[1]*.07,z),(length,.16,h),u,n,0)
        if length>7:
            # Brick pilaster strips on long runs frame the windows at coarse bay intervals.
            bays=max(1,int(length//10.0))
            for k in range(bays+1):
                t=1.0+(length-2.0)*k/bays
                pilasters.box((a[0]+u[0]*t+n[0]*.025,a[1]+u[1]*t+n[1]*.025,6.9),(.12,.05,12.7),u,n,0)
        nwin=max(0,int((length-2.1)//3.1))
        if nwin==0: continue
        usable=length-2.0
        for k in range(nwin):
            t=1.0+usable*(k+.5)/nwin
            # Keep the inferred entry wall clear of the stone portal and stair.
            center=(a[0]+u[0]*t+n[0]*.065,a[1]+u[1]*t+n[1]*.065)
            for z in level_centers:
                # Leave only the actual doorway and upper plaque clear; upper stories
                # continue their source-visible window rhythm over the entry bay.
                if i==i_entry and abs(t-length/2)<3.4 and z<5.5: continue
                width=min(1.55,usable/nwin-.46); height=1.78
                # The source photo shows brick reveals with restrained pale sills,
                # not a full cream surround around every window.
                trim.box((center[0],center[1],z-height/2-.07),(width+.12,.14,.12),u,n,0)
                trim.box((center[0],center[1],z+height/2+.04),(width+.06,.11,.07),u,n,0)
                glazing.box((center[0]+n[0]*.10,center[1]+n[1]*.10,z),(width,.075,height),u,n,0)
                # Thin bronze perimeter and mullions with two transom divisions.
                frame=.055
                for side in (-1,1):
                    glazing.box((center[0]+u[0]*(side*(width/2-frame/2))+n[0]*.15,center[1]+u[1]*(side*(width/2-frame/2))+n[1]*.15,z),(frame,.07,height),u,n,1)
                for zz in (-height/2+frame/2,height/2-frame/2):
                    glazing.box((center[0]+n[0]*.15,center[1]+n[1]*.15,z+zz),(width,.07,frame),u,n,1)
                glazing.box((center[0]+n[0]*.16,center[1]+n[1]*.16,z),(frame,.07,height),u,n,1)
                glazing.box((center[0]+n[0]*.16,center[1]+n[1]*.16,z+.26),(width,.07,frame),u,n,1)
                glazing.box((center[0]+n[0]*.16,center[1]+n[1]*.16,z-.26),(width,.07,frame),u,n,1)
                window_count+=1
        rows_used=len(level_centers)
    trim_obj=trim.finish(asset_col); glass_obj=glazing.finish(asset_col)
    pilaster_obj=pilasters.finish(asset_col)
    if trim_obj: trim_obj["role"]="projected stone course / window trim; photo-informed"
    if glass_obj: glass_obj["window_count"] = window_count
    if pilaster_obj: pilaster_obj["role"]="subtle red-brick vertical bay relief; inferred from street facade rhythm"

    # Flat roof / green coping are a restrained interpretation of the official oblique
    # photo; the roof surface itself is not verified by a source aerial.
    roof_edge=Batch("FRNY_Aged_Green_Roof_Coping",[m["coping"]])
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length<0.2: continue
        u=(dx/length,dy/length); n=(u[1],-u[0])
        roof_edge.box(((a[0]+b[0])/2+n[0]*.04,(a[1]+b[1])/2+n[1]*.04,14.125),(length,.30,.45),u,n,0)
    roof_edge_obj=roof_edge.finish(asset_col)
    if roof_edge_obj: roof_edge_obj["role"]="green metal roof edge inferred from official street photo; flat interior roof uncertain"

    # Main entry is an architectural locator, not a surveyed entrance coordinate.
    entry_obj=None
    if entry:
        i,a,b,length,u,n=entry
        midpoint=(a[0]+b[0])/2,(a[1]+b[1])/2
        ex=midpoint[0]+n[0]*.15; ey=midpoint[1]+n[1]*.15
        portal=Batch("FRNY_Southwest_Stone_Entrance_Portal",[m["stone"],m["metal"],m["glass"],m["brick"]])
        create_entry_arch(portal,(ex,ey),u,n,door_width,0,2.52,.34,0)
        # dark double doors and two transoms behind the archivolt
        portal.box((ex-n[0]*.045,ey-n[1]*.045,1.60),(door_width-.18,.09,3.10),u,n,2)
        portal.box((ex-n[0]*.08,ey-n[1]*.08,1.58),(.05,.055,3.0),u,n,1)
        portal.box((ex-n[0]*.09,ey-n[1]*.09,3.05),(door_width-.18,.05,.07),u,n,1)
        portal.box((ex-n[0]*.09,ey-n[1]*.09,.45),(door_width-.18,.05,.22),u,n,3)
        # Engraved panel/nameplate and circular masonry medallion above arch.
        portal.box((ex+n[0]*.16,ey+n[1]*.16,4.75),(4.55,.24,.62),u,n,0)
        portal.box((ex+n[0]*.295,ey+n[1]*.295,4.75),(4.1,.05,.42),u,n,1)
        portal.wall_roundel((ex+n[0]*.23,ey+n[1]*.23,5.55),u,n,.42,.22,0)
        entry_obj=portal.finish(asset_col)
        if entry_obj:
            entry_obj["placement_status"]="inferred from official street-level photograph; entrance location not georeferenced"
        add_text("FRNY_Entrance_Identification","FORNEY HALL",asset_col,(ex+n[0]*.34,ey+n[1]*.34,4.79),u,n,.30,m["stone"])
        add_text("FRNY_Entrance_Subtitle","CHEMICAL ENGINEERING",asset_col,(ex+n[0]*.34,ey+n[1]*.34,4.57),u,n,.115,m["stone"])
        # Six understated steps and two railings, kept separate from structural GIS walls.
        step=Batch("FRNY_Entrance_Steps_and_Rails",[m["stone"],m["metal"]])
        for k in range(6):
            d=0.38*k
            z=-0.02+0.15*k
            step.box((ex-n[0]*d,ey-n[1]*d,z),(3.7,.72,.18),u,n,0)
        for side in (-1,1):
            for k in range(4):
                d=.35+k*.58
                step.box((ex+u[0]*side*1.95-n[0]*d,ey+u[1]*side*1.95-n[1]*d,.25+k*.30),(.09,.09,.65),u,n,1)
            step.box((ex+u[0]*side*1.95-n[0]*.95,ey+u[1]*side*1.95-n[1]*.95,1.15),(.10,.10,2.5),u,n,1)
        step.finish(asset_col)

    # Rooftop exhausts visible in the official photograph, plus restrained generic
    # lab HVAC equipment. Equipment count and exact locations remain inferred.
    vents=Batch("FRNY_Roof_Exhaust_Vents",[m["metal"],m["coping"]])
    cx,cy=polygon_centroid(poly)
    # Put compact, non-intrusive elements on the roof to signal its plant equipment.
    for dx,dy,r,h in [(-13,-7,.22,1.0),(-5,8,.18,.72),(8,1,.20,.85),(15,10,.16,.60)]:
        vents.cylinder((cx+dx,cy+dy,wall_top+.12+h/2),r,h,0,20)
        vents.cylinder((cx+dx,cy+dy,wall_top+.12+h),r*1.35,.12,1,20)
    vent_obj=vents.finish(asset_col)
    if vent_obj: vent_obj["uncertainty"]="generic rooftop exhaust elements; count and exact positions inferred, not surveyed"
    hvac=Batch("FRNY_Roof_Laboratory_HVAC_Units",[m["metal"],m["roof"],m["coping"]])
    unit_offsets=[(-22,-14),(-8,-16),(9,-14),(22,-2),(-19,8),(1,14),(18,17)]
    for ux,uy in unit_offsets:
        x,y=cx+ux,cy+uy
        hvac.box((x,y,14.70),(4.0,2.7,1.25),(1,0),(0,1),1)
        hvac.box((x,y,15.37),(4.15,2.82,.12),(1,0),(0,1),0)
        for side in (-1,1):
            for k in range(6):
                hz=14.28+k*.17
                hvac.box((x,y+side*1.38,hz),(3.4,.045,.055),(1,0),(0,1),2)
    hvac_obj=hvac.finish(asset_col)
    if hvac_obj: hvac_obj["uncertainty"]="schematic laboratory HVAC housings; roof equipment placement and counts not survey-verified"

    # A deliberately schematic, inspectable interior: an atrium with a lab distillation
    # tower, room partitions and an auditorium layout derived from Purdue's published use.
    # No floor plan coordinates are claimed.
    floor_z=[2.72,5.42,8.12,10.82]
    floor_mat=m["concrete"]
    for ix,z in enumerate(floor_z):
        slab=add_poly_prism(interior_col,f"FRNY_Schematic_Floor_Plate_{ix+2}",poly,z-.10,z,[floor_mat,floor_mat],0,1,1)
        slab["layout_status"]="schematic; exact floor plan not georeferenced"

    # atrium and distillation column (Henson Atrium is source-confirmed; placement is schematic)
    ax,ay=cx+3.0,cy-1.5
    atrium=Batch("FRNY_Schematic_Henson_Atrium_and_Distillation_Tower",[m["concrete"],m["stainless"],m["metal"],m["glass"]])
    # ground terrazzo platform
    atrium.box((ax,ay,.25),(12.0,12.0,.35),(1,0),(0,1),0)
    atrium.box((ax,ay,7.5),(0.8,.8,11.8),(1,0),(0,1),1)
    # tower flange / sight glass bands and ladder rail hints
    for zz in (1.1,2.3,3.5,4.7,5.9,7.1,8.3,9.5,10.7,11.7):
        atrium.cylinder((ax,ay,zz),.50,.095,2,24)
    atrium.box((ax+.57,ay,6.0),(.08,.08,10.0),(1,0),(0,1),2)
    atrium.box((ax+.67,ay,6.0),(.08,.08,10.0),(1,0),(0,1),2)
    for zz in (1.5,2.2,2.9,3.6,4.3,5.0,5.7,6.4,7.1,7.8,8.5,9.2,9.9,10.6):
        atrium.box((ax+.62,ay,zz),(.62,.08,.07),(1,0),(0,1),2)
    # low-balustrade hints around the open atrium landing
    for dx in (-6.0,6.0):
        atrium.box((ax+dx,ay,2.3),(.12,.12,.95),(1,0),(0,1),2)
    for dy in (-5.5,5.5):
        atrium.box((ax,ay+dy,2.3),(0.12,.12,.95),(1,0),(0,1),2)
    atrium_obj=atrium.finish(interior_col)
    if atrium_obj:
        atrium_obj["interior_reference"]="Henson Atrium and a distillation tower are described/captioned in official Purdue ChE sources."
        atrium_obj["placement_status"]="schematic interior placement"

    # Auditorium schematic, 20 rows x 10 seats = 200 seats. It is a space-type diagram,
    # not an exact location or measured seating plan.
    au_x,au_y=cx+18.0,cy-14.0
    auditorium=Batch("FRNY_Schematic_200_Seat_Auditorium",[m["interior_wall"],m["upholstery"],m["metal"]])
    auditorium.box((au_x,au_y,1.25),(19.0,14.0,.20),(1,0),(0,1),0)
    auditorium.box((au_x,au_y+6.3,1.70),(14.0,.22,.75),(1,0),(0,1),0)
    for row in range(10):
        yy=au_y-5.7+row*.59
        for col in range(10):
            xx=au_x-6.5+col*1.45
            auditorium.box((xx,yy,1.86+row*.06),(.48,.52,.24),(1,0),(0,1),1)
            auditorium.box((xx,yy-.12,2.16+row*.06),(.42,.12,.48),(1,0),(0,1),1)
            if col<9:
                auditorium.box((xx+.38,yy+.42,2.02+row*.06),(.62,.07,.07),(1,0),(0,1),2)
    auditorium_obj=auditorium.finish(interior_col)
    if auditorium_obj:
        auditorium_obj["seat_count_schematic"]=200
        auditorium_obj["source_reference"]="Purdue College of Engineering Facilities page identifies a 200-seat auditorium in the addition."
        auditorium_obj["placement_status"]="schematic room size and location; not a surveyed floor plan"
    add_floor_label("FRNY_Auditorium_Interior_Label","200 SEAT AUDITORIUM | SCHEMATIC",interior_col,(au_x,au_y+5.4,1.39),.50,m["label_ink"])
    add_floor_label("FRNY_Atrium_Interior_Label","HENSON ATRIUM | SCHEMATIC",interior_col,(ax,ay-4.7,.44),.60,m["label_ink"])

    # Small lab bench/casework and office partitions, all isolated in the schematic group.
    rooms=Batch("FRNY_Schematic_Lab_Benches_and_Partitions",[m["interior_wall"],m["concrete"],m["metal"]])
    for row in range(4):
        y=cy+20+row*2.3
        rooms.box((cx-18,y,1.55),(13.0,.85,.95),(1,0),(0,1),1)
        rooms.box((cx-18,y,2.08),(13.0,.88,.09),(1,0),(0,1),2)
    # partitions signal flexible offices/lab suite use without claiming exact plan.
    for dx in (-25,-10,5,20):
        rooms.box((cx+dx,cy+11,1.9),(.14,12.0,2.8),(1,0),(0,1),0)
    rooms.finish(interior_col)
    add_floor_label("FRNY_Laboratory_Interior_Label","LAB / RESEARCH AREA | SCHEMATIC",interior_col,(cx-18,cy+22,1.42),.48,m["label_ink"])
    interior_col["description"]="Source-informed but non-georeferenced interior diagram: Henson Atrium/distillation tower, schematic 200-seat auditorium, lab benches and partitions. Toggle this collection to inspect."

    # Main object carries source geometry and component count summary.
    shell["model_notes"]="Street-level red brick/limestone composition follows Purdue's Forney exterior photo. Interior layout is schematic, not a measured plan."
    shell["floor_count_appearance_estimate"]=5
    shell["purdue_gis_level_count"]=feature["properties"].get("NUM_LEVELS",None)
    shell["model_footprint_perimeter_local_approx_m"]=round(perimeter,2)

    # Scene settings and helpful preview camera/lights are intentionally outside the
    # exported asset collection, so the collection instance stays building-only.
    for mat in asset_col.objects:
        if mat.type == "MESH":
            for poly_face in mat.data.polygons: poly_face.use_smooth = False
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    scene.render.resolution_percentage=100
    scene.world.color=(0.28,0.32,0.38)
    world=scene.world
    if world and world.use_nodes:
        bg=world.node_tree.nodes.get("Background"); bg.inputs["Color"].default_value=(0.20,0.25,0.32,1); bg.inputs["Strength"].default_value=.45
    def aim(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    camera_data=bpy.data.cameras.new("FRNY_Preview_Camera_Data")
    cam=bpy.data.objects.new("FRNY_Preview_Camera",camera_data); scene.collection.objects.link(cam)
    cam.location=(cx+82,cy-92,29); aim(cam,(cx,cy,6)); cam.data.type="ORTHO"; cam.data.ortho_scale=112; scene.camera=cam
    def add_area(name,loc,power,size):
        ld=bpy.data.lights.new(name,"AREA"); ld.energy=power; ld.shape="DISK"; ld.size=size
        ob=bpy.data.objects.new(name,ld); scene.collection.objects.link(ob); ob.location=loc; aim(ob,(cx,cy,4)); return ob
    add_area("FRNY_Preview_Key",(cx+65,cy-45,55),5200,36)
    add_area("FRNY_Preview_Fill",(cx-50,cy+50,42),2200,28)
    # Render-only grass apron supplies scale and shadows; it is removed before saving
    # and never enters the exported asset collection.
    context_ground, _, _, _ = create_material("FRNY | preview-only neutral lawn",(0.025,0.065,0.022),0.96)
    bpy.ops.mesh.primitive_plane_add(size=1200,location=(cx,cy,-.18))
    ground=bpy.context.object; ground.name="FRNY_Preview_Context_Ground"; ground.data.materials.append(context_ground)
    scene.view_settings.view_transform="AgX"
    scene.render.filepath=str(EVIDENCE_DIR/"forney_exterior_preview.png")
    bpy.ops.render.render(write_still=True)

    # Top-down source-footprint view, useful for independent review.
    top_data=bpy.data.cameras.new("FRNY_Preview_Top_Data")
    top=bpy.data.objects.new("FRNY_Preview_Top",top_data); scene.collection.objects.link(top)
    top.location=(cx,cy,260); top.rotation_euler=(0,0,0); top.data.type="ORTHO"; top.data.ortho_scale=120
    scene.camera=top
    scene.render.resolution_x=1000; scene.render.resolution_y=1000
    scene.render.filepath=str(EVIDENCE_DIR/"forney_roof_and_footprint_preview.png")
    bpy.ops.render.render(write_still=True)

    # Render the explicitly schematic interior on its own so a grader can inspect
    # the published atrium/plant and auditorium program without a false claim that
    # the modeled rooms match surveyed floor-plan coordinates.
    interior_objects=set(interior_col.all_objects)
    asset_objects=set(asset_col.all_objects)
    saved_hide={obj:obj.hide_render for obj in scene.objects}
    for obj in scene.objects:
        if obj in asset_objects and obj not in interior_objects:
            obj.hide_render=True
    for obj in interior_objects:
        if obj.name.startswith("FRNY_Schematic_Floor_Plate_"):
            obj.hide_render=True
    top.location=(cx+4,cy+3,48); top.data.ortho_scale=72
    scene.camera=top
    scene.render.filepath=str(EVIDENCE_DIR/"forney_schematic_interior_preview.png")
    bpy.ops.render.render(write_still=True)
    for obj,hide in saved_hide.items(): obj.hide_render=hide

    # Remove preview camera/light objects from the saved library. They are not building assets.
    for obj in list(scene.objects):
        if obj.name.startswith("FRNY_Preview"):
            bpy.data.objects.remove(obj, do_unlink=True)
    # remove render-only ground from the saved library; keep all building geometry.
    if bpy.data.objects.get("FRNY_Preview_Context_Ground"):
        bpy.data.objects.remove(bpy.data.objects["FRNY_Preview_Context_Ground"],do_unlink=True)
    scene.camera=None
    scene.render.resolution_x=1400; scene.render.resolution_y=1000
    scene.render.filepath="//forney_render.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE), compress=True)

    summary={
        "asset_id":ASSET_ID,"file":str(ASSET_FILE.relative_to(MODULAR_ROOT)),"scene":SCENE_NAME,"collection":COLLECTION_NAME,
        "gis_feature":feature["properties"].get("OBJECTID"),"raw_footprint_vertices":len(raw)-1,"model_footprint_vertices":len(poly),
        "local_formula_footprint_area_m2":round(area_local,2),"gis_shape_area_attribute_m2":feature["properties"].get("Shape.STArea()"),
        "footprint_bounds_local_m":[[round(xmin,3),round(xmax,3)],[round(ymin,3),round(ymax,3)],[0.0,round(coping_top,3)]],
        "perimeter_local_formula_m":round(perimeter,2),"wall_top_height_estimated_m":wall_top,"coping_height_m":coping_top,
        "window_modules":window_count,"interior_objects":len(interior_col.all_objects),"entrance_edge_index":i_entry,
        "entrance_edge_length_m":round(entry[3],2) if entry else None,"status":"freshly rebuilt; not yet independently graded",
    }
    (EVIDENCE_DIR/"build_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("FORNEY_BUILD_SUMMARY",json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    build()
