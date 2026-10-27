"""Build a source-backed, local-coordinate Lambertus Hall asset.

Run from the repository root:
  blender --background --python modular/buildings/build_lambertus_hall.py

The GIS perimeter is exact to the downloaded official Purdue feature after the
project's local geographic approximation. Story elevations and internal layouts
are explicitly modeled as estimates because published floor plans were not found.
"""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "lambertus_hall"
SOURCE = AUDIT / "sources" / "purdue_fid433.json"
ASSET = ROOT / "modular" / "buildings" / "lambertus_hall.blend"
ORIGIN = (-86.9117600, 40.4276100)  # geographic local-frame anchor, degrees
LON0, LAT0 = ORIGIN
X_SCALE = 111412.84 * math.cos(math.radians(40.4274))
Y_SCALE = 111040.0
_BATCHES = {}
_BATCHING = False


def xy(lon, lat):
    return ((lon - LON0) * X_SCALE, (lat - LAT0) * Y_SCALE)


def material(name, color, rough=0.55, metal=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, alpha)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if alpha < 1:
        mat.blend_method = 'BLEND'
        bsdf.inputs["Alpha"].default_value = alpha
    return mat


def mesh_obj(name, verts, faces, mat, collection, props=None):
    if _BATCHING:
        bucket = _BATCHES.setdefault((collection.name, mat.name), {"verts": [], "faces": [], "props": []})
        offset = len(bucket["verts"])
        bucket["verts"].extend(tuple(v) for v in verts)
        bucket["faces"].extend(tuple(offset + i for i in f) for f in faces)
        if props:
            bucket["props"].append(props)
        return None
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    if props:
        for key, val in props.items():
            ob[key] = val
    return ob


def flush_batches(root):
    global _BATCHING
    _BATCHING = False
    for (collection_name, material_name), bucket in _BATCHES.items():
        mesh = bpy.data.meshes.new(f"{material_name} | combined detail mesh")
        mesh.from_pydata(bucket["verts"], [], bucket["faces"])
        mesh.materials.append(bpy.data.materials[material_name])
        mesh.update()
        ob = bpy.data.objects.new(f"Lambertus | {material_name} assembled detail", mesh)
        bpy.data.collections[collection_name].objects.link(ob)
        ob["combined_detail_faces"] = len(bucket["faces"])
        if bucket["props"]:
            ob["evidence_status"] = "Combined architectural details; individual bay and room dimensions are approximate."
    _BATCHES.clear()


def box(name, center, size, mat, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Move from scene root into the building's named collection.
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Soft manufactured edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return ob


def bar(name, p0, p1, width, depth, mat, collection):
    a, b = Vector(p0), Vector(p1)
    d = b - a
    if d.length < 0.01:
        return None
    if abs(d.z) > d.length * 0.85:
        side = Vector((1, 0, 0))
    else:
        side = Vector((-d.y, d.x, 0)).normalized()
    normal = d.normalized().cross(side).normalized()
    hw, hd = width / 2, depth / 2
    verts = [a-side*hw-normal*hd, b-side*hw-normal*hd,
             b+side*hw-normal*hd, a+side*hw-normal*hd,
             a-side*hw+normal*hd, b-side*hw+normal*hd,
             b+side*hw+normal*hd, a+side*hw+normal*hd]
    return mesh_obj(name, verts, [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)], mat, collection)


def setup_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name != "Collection":
            bpy.data.collections.remove(c)
    scene = bpy.context.scene
    scene.name = "Building_lambertus_hall"
    root = bpy.data.collections.get("Collection")
    root.name = "Asset_lambertus_hall"
    scene.collection.children.unlink(root) if root in scene.collection.children[:] else None
    scene.collection.children.link(root)
    root["building_id"] = "lambertus_hall"
    root["coordinate_frame"] = "local meters; origin lon -86.9117600 lat 40.4276100; X east, Y north, Z up"
    return scene, root


def create_building(root):
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    feature = raw["features"][0]
    assert feature["attributes"]["FID"] == 433 and feature["attributes"]["BLDG_ABBR"] == "LMBS"
    ring_geo = feature["geometry"]["rings"][0]
    ring = [xy(lon, lat) for lon, lat in ring_geo]
    if ring[0] == ring[-1]:
        ring.pop()
    # Keep raw GIS vertex sequence: its wall outline is the primary verified geometry.
    brick = material("Lambertus | warm red-brown brick", (0.46, 0.18, 0.105), .78)
    brick_alt = material("Lambertus | subtle brick variation", (0.40, 0.16, 0.095), .8)
    concrete = material("Lambertus | pale precast frame", (.70,.68,.63), .65)
    glass = material("Lambertus | blue-gray low-e glazing estimate", (.075,.20,.25), .22,.12)
    mullion = material("Lambertus | charcoal aluminum", (.055,.065,.067), .38,.48)
    terra = material("Lambertus | terracotta solar screen estimate", (.60,.24,.13), .48,.03)
    roof = material("Lambertus | roof membrane", (.18,.19,.19), .85)
    floor_mat = material("Lambertus | exposed concrete interior floors", (.48,.47,.43), .72)
    interior_wall = material("Lambertus | warm interior partition", (.58,.49,.38), .7)
    safety = material("Lambertus | lab safety yellow", (.94,.52,.035), .4,.12)
    green = material("Lambertus | catwalk green rail", (.18,.32,.22), .45,.5)
    steel = material("Lambertus | lab equipment steel", (.26,.30,.31), .36,.55)
    wood = material("Lambertus | collaboration wood", (.30,.17,.095), .68)
    white = material("Lambertus | interior light concrete", (.75,.73,.67), .76)

    global _BATCHING

    h = 16.0 # Envelope top follows current manifest massing; height remains estimated.
    # Shell uses GIS outline, leaving architecture legible in aerial and axon views.
    verts = [(x,y,z) for z in (0,h) for x,y in ring]
    n = len(ring)
    faces = [tuple(range(n-1,-1,-1)), tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    shell = mesh_obj("Lambertus Hall | GIS perimeter shell", verts, faces, brick, root,
        {"source_feature":"Purdue BuildingShapesZip4 FID 433 / LMBS", "height_status":"estimated 16.0 m; no reliable surveyed height found", "perimeter_status":"official GIS ring converted with project local approximation"})
    shell.data.materials.append(brick_alt)
    shell.data.materials.append(roof)
    shell.data.polygons[1].material_index = 2
    # Subtle brick course texture: shader noise remains procedural and portable.
    bsdf = next(n for n in brick.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    tex = brick.node_tree.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 85
    tex.inputs["Detail"].default_value = 2
    bump = brick.node_tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .17
    bump.inputs["Distance"].default_value = .035
    brick.node_tree.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    brick.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    _BATCHING = True

    floors = [0.25, 3.35, 6.45, 9.55, 12.65, 15.75]
    # Slabs are in the interior and draw through transparent facade openings.
    for i,z in enumerate(floors[:-1]):
        slabverts=[(x,y,z) for x,y in ring]
        mesh_obj(f"Interior | floor slab L{i}", slabverts,[tuple(range(n))],floor_mat,root,
                 {"story_elevation_m":z,"status":"approximate level inferred from five-floor public sources"})

    # Facade zones, mullions, white vertical piers, terracotta fins. The long
    # east and south-facing runs get the curtainwall expression in published photos.
    for i,(a,b) in enumerate(zip(ring, ring[1:]+ring[:1])):
        ax,ay=a; bx,by=b; dx,dy=bx-ax,by-ay; length=math.hypot(dx,dy)
        if length < .55: continue
        tangent=Vector((dx/length,dy/length,0))
        midpoint=Vector(((ax+bx)/2,(ay+by)/2,0))
        # Purdue GIS ring is clockwise (negative signed area), so the left
        # normal points outward; use the opposite normal for counter-clockwise.
        outward=Vector((-tangent.y,tangent.x,0))
        # Select broad east/south faces for the visible screened-glazing system.
        main_glass = (length > 8 and (outward.x > .42 or outward.y < -.44))
        facade_depth=.075
        p=Vector((ax,ay,0))+outward*facade_depth
        q=Vector((bx,by,0))+outward*facade_depth
        usable0=min(.45,length*.12); usable1=max(usable0,length-.45)
        count=max(1,int((usable1-usable0)/2.35))
        for level in range(5):
            z0=.55+level*3.1; z1=min(z0+2.42,h-.32)
            if z1<=z0: continue
            # Repeated vision panels across the rhythm. Maintain brick piers between.
            for bay in range(count):
                lo=usable0+(usable1-usable0)*(bay+.12)/count
                hi=usable0+(usable1-usable0)*(bay+.88)/count
                pl=p+tangent*lo+Vector((0,0,z0)); pr=p+tangent*hi+Vector((0,0,z0))
                qr=pr+Vector((0,0,z1-z0)); ql=pl+Vector((0,0,z1-z0))
                mesh_obj(f"Facade | {'curtainwall' if main_glass else 'punched window'} edge{i} floor{level} bay{bay}",
                         [pl,pr,qr,ql],[(0,1,2,3)],glass,root,
                         {"visual_basis":"2022-23 Ennead/BSA project photography; specific facade mapping is partly uncertain"})
                # Aluminum perimeter and vertical dividers.
                bar(f"Facade mullion | edge{i} f{level} b{bay}",pl,ql,.055,.09,mullion,root)
                bar(f"Facade mullion | edge{i} f{level} b{bay}R",pr,qr,.055,.09,mullion,root)
            # White precast structural pier at bay divisions.
            for j in range(count+1):
                t=usable0+(usable1-usable0)*j/count
                pt=p+tangent*t
                bar(f"Precast pier | edge{i} f{level} p{j}", (pt.x,pt.y,z0-.22), (pt.x,pt.y,z1+.17), .105,.13,concrete,root)
            # Floor line, plus closely spaced rust-red vertical solar fins on selected elevations.
            bar(f"Facade floor belt | edge{i} floor{level}",(p.x,p.y,z0-.12),(q.x,q.y,z0-.12),.09,.08,concrete,root)
            if main_glass:
                for fin in range(0,count*2+1):
                    t=usable0+(usable1-usable0)*fin/(count*2)
                    pt=p+tangent*t+outward*.10
                    bar(f"Terracotta shade fin | edge{i} floor{level} n{fin}",
                        (pt.x,pt.y,z0-.10),(pt.x,pt.y,z1+.05),.075,.12,terra,root)
        # Ground floor entry portal and canopy at the main facade's midpoint.
        if main_glass and length > 10:
            c=p+tangent*((usable0+usable1)/2)
            box(f"Entry | glazed portal edge{i}",(c.x,c.y,1.45),(2.5,.16,2.65),glass,root)
            canopy_center=c+outward*.85+Vector((0,0,3.05))
            box(f"Entry | thin terracotta canopy edge{i}",canopy_center,(3.6,1.9,.16),terra,root,.05)

    # Roof edge parapet and muted mechanical plant, kept below the existing 16 m cap.
    for i,(a,b) in enumerate(zip(ring, ring[1:]+ring[:1])):
        if math.dist(a,b) < .6: continue
        bar(f"Roof | parapet segment {i}",(a[0],a[1],15.65),(b[0],b[1],15.65),.18,.20,concrete,root)
    # compact rooftop service screen as a restrained, plausible inference
    xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
    box("Roof | screened mechanical plant",((min(xs)+max(xs))*.53,(min(ys)+max(ys))*.48,15.22),(7.8,4.4,.8),roof,root,.12)

    # Plausible evidence-backed interior: high-bay Build @Scale lab, crane/catwalk,
    # offices/collaboration and a circulation core. Exact room layout is inferred.
    span_x=max(xs)-min(xs); span_y=max(ys)-min(ys)
    # Put a high-bay workshop in the north-west half (where its ground footprint allows).
    cx=min(xs)+span_x*.36; cy=min(ys)+span_y*.68
    # Visible industrial floor zone, work cells and equipment.
    box("Interior | high-bay manufacturing lab floor",(cx,cy,.12),(11.0,15.0,.24),floor_mat,root)
    # Light neutral inner partitions make the cutaway read as a real lab bay;
    # positions are schematic because no public room plan was located.
    box("Interior | high-bay north partition",(cx,cy+7.35,3.65),(11.0,.18,7.0),white,root)
    box("Interior | high-bay east partition",(cx+5.35,cy,3.65),(.18,14.7,7.0),white,root)
    for i in range(4):
        xx=cx-4.1+i*2.7
        box(f"Build@Scale | machine cell {i+1}",(xx,cy-1.2,1.0),(1.5,3.0,1.4),steel,root,.08)
        box(f"Build@Scale | safety base {i+1}",(xx,cy-1.2,.28),(1.75,3.2,.12),safety,root)
    # Overhead crane rails and bridge, consistent with high-bay imagery.
    for xx in (cx-5.4,cx+5.4):
        box("High-bay | overhead crane runway beam",(xx,cy,7.5),(.22,13.5,.26),steel,root)
    box("High-bay | yellow overhead bridge crane",(cx,cy+2,7.8),(11.2,.40,.34),safety,root,.06)
    box("High-bay | hanging crane trolley",(cx,cy+2,7.2),(1.25,.55,.72),steel,root,.07)
    for xx in (cx-3.8,cx+3.8):
        box("High-bay | catwalk platform",(xx,cy+4.6,5.3),(2.0,7.0,.16),steel,root)
        for k in range(8):
            y=cy+1.2+k*.88
            bar("High-bay | green catwalk guardrail",(xx-1,y,5.85),(xx+1,y,5.85),.065,.065,green,root)
        for side in (-1,1):
            bar("High-bay | green catwalk top rail",(xx+side,cy+1.1,5.85),(xx+side,cy+8.1,5.85),.075,.075,green,root)
    # A light-filled office/collaboration zone with a stair/circulation block.
    ox=min(xs)+span_x*.69; oy=min(ys)+span_y*.31
    box("Interior | collaboration commons wood feature wall",(ox,oy,5.4),(9.0,.18,3.0),wood,root)
    for i in range(5):
        box(f"Interior | commons table {i+1}",(ox-3.3+(i%3)*3.1,oy-1.8+(i//3)*2.4,3.75),(1.7,.8,.10),wood,root,.04)
        for dx in (-.67,.67):
            box("Interior | table leg",(ox-3.3+(i%3)*3.1+dx,oy-1.8+(i//3)*2.4,3.48),(.07,.07,.54),steel,root)
    # Central stair flights, repeated landings between levels.
    sx=ox+span_x*.08; sy=oy+span_y*.08
    for floor in range(4):
        z=1.0+floor*3.1
        for step in range(10):
            box(f"Interior | stair flight {floor+1} step {step+1}",(sx+step*.19,sy,z+step*.17),(.36,1.35,.17),white,root)
        box(f"Interior | stair landing {floor+1}",(sx+2.2,sy, z+1.65),(.95,1.55,.15),floor_mat,root)
    # A small set of open partitions suggests offices without claiming a plan.
    for i in range(4):
        x=ox-5+i*2.8
        box(f"Interior | inferred office glass divider {i+1}",(x,oy+3.2,4.8),(.08,4.0,2.2),glass,root)
    # Circulation / laboratory casework on the upper nuclear engineering floor.
    nuke_z=13.35
    box("Interior | fifth-floor nuclear engineering study bench",(ox,oy+5.4,nuke_z),(6.4,.8,.12),wood,root)
    for i in range(4):
        box(f"Interior | fifth-floor study seat {i+1}",(ox-2.4+i*1.6,oy+4.3,nuke_z+.45),(.7,.7,.9),interior_wall,root,.04)

    flush_batches(root)
    return ring, floors


def camera_for(scene, name, location, target, lens=50, resolution=(1400,1050), ortho_scale=None):
    data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); scene.collection.objects.link(cam)
    cam.location=location
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    if ortho_scale:
        cam.data.type='ORTHO'
        cam.data.ortho_scale=ortho_scale
    scene.camera=cam
    scene.render.resolution_x=resolution[0]; scene.render.resolution_y=resolution[1]
    return cam


def lighting(scene):
    world=bpy.data.worlds.new("Lambertus | soft daylight")
    world.use_nodes=True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.31,.40,.52,1)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.45
    scene.world=world
    data=bpy.data.lights.new("Large softbox key","AREA"); ob=bpy.data.objects.new("Large softbox key",data); scene.collection.objects.link(ob)
    ob.location=(28,-34,48); data.energy=9000; data.shape='DISK'; data.size=28
    data=bpy.data.lights.new("Interior fill","AREA"); ob=bpy.data.objects.new("Interior fill",data); scene.collection.objects.link(ob)
    ob.location=(-8,-4,18); data.energy=3000; data.shape='DISK'; data.size=18


def main():
    scene,root=setup_scene()
    ring,floors=create_building(root)
    scene.render.engine='CYCLES'
    scene.cycles.samples=12
    scene.cycles.use_denoising=True
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=.55
    lighting(scene)
    # Save a useful viewport orientation in the individual asset.
    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=72
            area.spaces.active.region_3d.view_location=(0,0,7)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    # Three grade-ready views: exterior axon, site-like top, and lab interior.
    (AUDIT/'renders').mkdir(parents=True,exist_ok=True)
    xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
    span_x=max(xs)-min(xs); span_y=max(ys)-min(ys)
    center=((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,7.8)
    scene.render.image_settings.file_format='PNG'
    scene.render.resolution_x=1300;scene.render.resolution_y=950
    camera_for(scene,"Evidence exterior axon",(48,-82,29),center,52,(1300,950),88)
    scene.render.filepath=str(AUDIT/'renders'/'01_exterior_axon.png');bpy.ops.render.render(write_still=True)
    camera_for(scene,"Evidence roof and perimeter",(0,-5,100),(0,0,0),55,(950,950),88)
    scene.render.filepath=str(AUDIT/'renders'/'02_roof_perimeter.png');bpy.ops.render.render(write_still=True)
    # Interior close-up points through a glazed edge toward the furnished lab.
    shell=bpy.data.objects.get("Lambertus Hall | GIS perimeter shell")
    shell.hide_render=True
    hidden_details=[]
    for ob in root.objects:
        if "assembled detail" in ob.name or ob.name.startswith("Roof |"):
            hidden_details.append((ob,ob.hide_render))
            ob.hide_render=True
    lab_center=(min(xs)+span_x*.36,min(ys)+span_y*.68)
    camera_for(scene,"Evidence lab interior",(lab_center[0]-12,lab_center[1]-18,12.0),(lab_center[0]+1,lab_center[1]+2,4.2),42,(1100,850),26)
    scene.render.filepath=str(AUDIT/'renders'/'03_high_bay_interior.png');bpy.ops.render.render(write_still=True)
    shell.hide_render=False
    for ob,old_state in hidden_details:
        ob.hide_render=old_state
    # Leave exterior view as the active saved camera after evidence rendering.
    camera_for(scene,"Evidence exterior axon",(48,-82,29),center,52,(1300,950),88)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    # Model facts computed from source geometry, separated from render embellishments.
    ring_geo=json.loads(SOURCE.read_text())['features'][0]['geometry']['rings'][0]
    global_pts=[xy(lon,lat) for lon,lat in ring_geo]
    gx=[p[0]+(LON0+86.9137)*X_SCALE for p in global_pts]
    gy=[p[1]+(LAT0-40.4274)*Y_SCALE for p in global_pts]
    bounds=[[min(gx),max(gx)],[min(gy),max(gy)],[0.0,16.0]]
    placement_xy=[(LON0+86.9137)*X_SCALE,(LAT0-40.4274)*Y_SCALE]
    local_bounds=[[bounds[0][0]-placement_xy[0],bounds[0][1]-placement_xy[0]],
                  [bounds[1][0]-placement_xy[1],bounds[1][1]-placement_xy[1]],bounds[2]]
    evidence={
      "building_id":"lambertus_hall","asset":str(ASSET.relative_to(ROOT)),"asset_scene":"Building_lambertus_hall","collection":"Asset_lambertus_hall",
      "retrieved_utc":"2026-10-26","coordinate_frame":{"origin_lon_lat":list(ORIGIN),"axes":"X east, Y north, Z up","units":"m","conversion":"project local approximation: X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040; detailed mesh shifted by geographic anchor"},
      "master_integration":{"placement_origin_xy_m":placement_xy,"expected_shell_local_bounds_m":local_bounds,"required_shared_changes":"Set manifest kind to detailed; set placement_origin_xy_m and local bounds; make a Placement_lambertus_hall collection-instance marker using Asset_lambertus_hall; replace/suppress the campus-coordinate massing. Do not use geometry-world coordinates for this local asset."},
      "source_findings":[
        {"provider":"Purdue University ArcGIS BuildingShapesZip4 FeatureServer/0","feature_id":433,"official_code":"LMBS","url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D433&outFields=*&returnGeometry=true&outSR=4326&f=pjson","snapshot":"sources/purdue_fid433.json","retrieved":"2026-10-26","crs":"EPSG:4326 (returned geographic coordinates)","method":"40-vertex official building perimeter converted with project local approximation; duplicate closing coordinate removed for mesh","uncertainty":"No published survey accuracy metadata; local conversion is approximate; excludes facade projections and shared Dudley structure."},
        {"provider":"Purdue University ArcGIS BuildingShapesZip4 FeatureServer/0","feature_id":432,"official_code":"DUDL","url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D432&outFields=*&returnGeometry=true&outSR=4326&f=pjson","snapshot":"sources/related_dudley_fid432.json","retrieved":"2026-10-26","crs":"EPSG:4326","method":"Adjacent feature boundary comparison","uncertainty":"Lambertus and Dudley are joined in the architecture; GIS represents separate neighboring footprints and is treated as the Lambertus boundary."},
        {"provider":"Ennead Architects","url":"https://ennead.com/work/purdue-university-dudley-and-lambertus-hall/","retrieved":"2026-10-26","source_date":"2022 project; page accessed 2026-10-26","snapshot":"sources/ennead_layer_1.jpg through sources/ennead_layer_6.jpg and Ennead project page","crs":"not applicable","method":"Design narrative and six massing-layer diagrams; used for campus gateway massing, entry, daylit transparent ground story, modulated scale, and connective corridor","uncertainty":"Published images describe combined Dudley/Lambertus complex; some elevations cannot be assigned unambiguously to one GIS wing."},
        {"provider":"BSA LifeStructures","url":"https://www.bsadesign.com/project/dudley-hall-and-lambertus-hall/","retrieved":"2026-10-26","source_date":"project photography published 2022-2023","snapshot":"sources/bsa_exterior_n288.webp; sources/bsa_exterior_n313.webp; sources/ennead_interior_*.jpg","crs":"not applicable","method":"Exterior and interior photography used for brick/terracotta/glass/white frame material language, high-bay lab/catwalk and collaboration cues","uncertainty":"Photo facade wing labels are not consistently visible; facade assignment and detailed room layout are inferred."},
        {"provider":"Purdue Board of Trustees","url":"https://www.purdue.edu/bot/meetings/past-meetings/2020/06.%20june/stated/lambertus%20hall.pdf","retrieved":"2026-10-26","source_date":"2020 naming proposal","snapshot":"online primary document (URL above)","crs":"not applicable","method":"Published Lambertus area and site relationship used as scale check","uncertainty":"Proposal says approximately 110,000 sq ft; GIS area is footprint, not floor area."},
        {"provider":"Purdue School of Nuclear Engineering","url":"https://engineering.purdue.edu/NE/news/2023/the-dedication-of-dudley-and-lambertus-halls-marks-a-new-home-for-purdue8217s-school-of-nuclear-engineering-","retrieved":"2026-10-26","source_date":"2023 dedication","snapshot":"online primary document (URL above)","crs":"not applicable","method":"Supports 2023 opening, fifth-floor north-wing Nuclear Engineering use, offices, study and lab spaces","uncertainty":"Does not provide a Lambertus-only measured height or floor plan."},
        {"provider":"Purdue Industrial Engineering / First Build @Scale","url":"https://engineering.purdue.edu/IE/Research/Gateway%20Labs/lambertus","retrieved":"2026-10-26","crs":"not applicable","method":"Ground-floor Build @Scale lab supports industrial machines, flexible automation and prototype line interior props","uncertainty":"Web description is functional evidence, not a floor plan."}
      ],
      "verified_geometry":{"world_bounds_m":bounds,"official_ring_vertices":len(ring_geo),"converted_ring_area_m2":abs(sum(global_pts[i][0]*global_pts[(i+1)%len(global_pts)][1]-global_pts[(i+1)%len(global_pts)][0]*global_pts[i][1] for i in range(len(global_pts))))*.5,"footprint_match":"source ring modeled directly; raw GIS vertices retained without fitting/scaling"},
      "estimated_dimensions":{"height_m":16.0,"stories":5,"story_spacing_m":3.1,"basis":"existing asset envelope plus published five-floor/fifth-floor evidence; not survey verified"},
      "interior":"High-bay manufacturing lab, overhead bridge crane, catwalk, collaboration/study zone, stairs and upper-floor nuclear-engineering study area are evidence-backed typologies but exact room locations and layout are plausible inferences; no public floor plan found.",
      "renders":["renders/01_exterior_axon.png","renders/02_roof_perimeter.png","renders/03_high_bay_interior.png"],
      "remaining_uncertainties":["Exact Lambertus-vs-Dudley allocation of facade photographs","No published Lambertus-only elevation or floor plan located","Story elevations and top-of-roof height estimated","Geographic conversion is not a survey-grade projection"]
    }
    (AUDIT/'evidence.json').write_text(json.dumps(evidence,indent=2)+"\n",encoding='utf-8')
    print(json.dumps({"asset":str(ASSET),"local_origin":list(ORIGIN),"bounds_world_m":bounds,"vertices":len(ring_geo),"renders":evidence["renders"]},indent=2))


if __name__ == '__main__':
    main()
