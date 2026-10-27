"""Build the YONG asset from the official Purdue GIS footprint.

The library retains the stable collection and campus-world coordinate frame.
Run through Blender in background mode; no external runtime dependencies.
"""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_young_hall_yong_cae1b95.blend"
GIS = ROOT / "audit/young_hall_yong_cael95/purdue_gis_yong_fid70.json"
COLL_NAME = "Asset_massing_young_hall_yong_cae1b95"
SCENE_NAME = "Building_massing_young_hall_yong_cae1b95"
OBJECT_NAME = "Young Hall (YONG)"
ORIGIN_LON, ORIGIN_LAT = -86.9137, 40.4274
HEIGHT_M = 102 * 0.3048

def mat(name, color, roughness=0.72, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m

BRICK = mat("YONG | red brick", (0.30, 0.085, 0.055))
PANEL = mat("YONG | pale exterior wall panels", (0.63, 0.62, 0.58), 0.7)
PANEL_ALT = mat("YONG | subtly varied exterior panels", (0.49, 0.49, 0.47), 0.75)
MORTAR = mat("YONG | warm mortar", (0.63, 0.55, 0.46))
GLASS = mat("YONG | blue gray glazing", (0.105, 0.19, 0.24), 0.22, 0.18)
METAL = mat("YONG | dark bronze aluminum", (0.16, 0.18, 0.18), 0.34, 0.55)
STONE = mat("YONG | pale limestone trim", (0.70, 0.67, 0.61), 0.56)
INTERIOR = mat("YONG | interior wall", (0.83, 0.80, 0.73))
FLOOR = mat("YONG | interior floor", (0.44, 0.43, 0.39))
FURNITURE = mat("YONG | furniture", (0.25, 0.19, 0.14))

brick_bsdf = next(n for n in BRICK.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
brick_tex = BRICK.node_tree.nodes.new("ShaderNodeTexBrick")
brick_tex.inputs["Color1"].default_value = (0.32, 0.075, 0.045, 1)
brick_tex.inputs["Color2"].default_value = (0.21, 0.045, 0.03, 1)
brick_tex.inputs["Mortar"].default_value = (0.46, 0.37, 0.30, 1)
brick_tex.inputs["Scale"].default_value = 220
brick_tex.inputs["Mortar Size"].default_value = 0.025
coord = BRICK.node_tree.nodes.new("ShaderNodeTexCoord")
BRICK.node_tree.links.new(coord.outputs["Generated"], brick_tex.inputs["Vector"])
BRICK.node_tree.links.new(brick_tex.outputs["Color"], brick_bsdf.inputs["Base Color"])
ROOF = mat("YONG | charcoal flat roof", (0.16, 0.17, 0.17), 0.82)

def get_collection():
    coll = bpy.data.collections.get(COLL_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLL_NAME)
        bpy.context.scene.collection.children.link(coll)
    for obj in list(coll.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    return coll

BOXES = {}

def cube(name, loc, size, material, coll):
    # Buffer repeated facade modules and create a few efficient grouped meshes.
    category = name.split("|", 1)[1].strip().split()[0] if "|" in name else name
    key = (material.name, category, coll.name)
    BOXES.setdefault(key, []).append((name, tuple(loc), tuple(size), material, coll))

def flush_boxes():
    for (mat_name, category, coll_name), boxes in BOXES.items():
        verts, faces = [], []
        for _, (cx,cy,cz), (sx,sy,sz), _, _ in boxes:
            base=len(verts)
            verts.extend([(cx+dx*sx/2,cy+dy*sy/2,cz+dz*sz/2)
                          for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                          (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
            faces.extend([tuple(base+i for i in f) for f in
                          [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
        mesh=bpy.data.meshes.new(f"YONG {category} mesh")
        mesh.from_pydata(verts,[],faces); mesh.materials.append(bpy.data.materials[mat_name])
        mesh.update()
        obj=bpy.data.objects.new(f"YONG | {category} modules",mesh)
        bpy.data.collections[coll_name].objects.link(obj)
    BOXES.clear()

def mesh_object(name, verts, faces, material, coll):
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    mesh.validate(clean_customdata=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    return obj

def get_points():
    feature = json.loads(GIS.read_text(encoding="utf-8"))["features"][0]
    ring = feature["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    return [((lon-ORIGIN_LON)*111412.84*math.cos(math.radians(ORIGIN_LAT)),
             (lat-ORIGIN_LAT)*111040.0) for lon, lat in ring]

def levels():
    return [v*0.3048 for v in [0,13.1,21.85,30.6,39.35,48.1,56.85,65.6,74.35,83.1]]

def shell(points, coll):
    n = len(points)
    verts = [(x,y,0) for x,y in points] + [(x,y,HEIGHT_M) for x,y in points]
    faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    obj = mesh_object(OBJECT_NAME, verts, faces, PANEL, coll)
    obj.data.materials.append(ROOF)
    for poly in obj.data.polygons:
        if all(abs(obj.data.vertices[i].co.z-HEIGHT_M)<0.001 for i in poly.vertices):
            poly.material_index = 1
    obj["source"] = "Purdue GIS BuildingShapesZip4 FID 70, BLDG_ABBR YONG"
    obj["height_basis"] = "GIS R=102 ft interpreted as roof height; 31.09 m"
    obj["floor_count_basis"] = "GIS CountOfFLO=11; Archives description: 10 stories"
    return obj

def elevation_edges(points):
    xs=[p[0] for p in points]; ys=[p[1] for p in points]
    return [
        (min(xs)+1.7,min(ys)+7,max(ys)-7,-1),
        (max(xs)-1.7,min(ys)+7,-512,1),
        (270.1,-497,max(ys)-7,1),
    ]

def windows(points, coll):
    for side,y0,y1,normal in elevation_edges(points):
        span=y1-y0; bays=max(1,round(span/3.7))
        for i in range(bays):
            y=y0+(i+0.5)*span/bays
            for f,zbase in enumerate(levels()):
                z=zbase+(1.05 if f==0 else 0.9)
                h=2.05 if f==0 else 2.15
                w=min(1.35,span/bays*0.48)
                tag=f"{side:.1f} {i:02d} {f:02d}"
                cube("YONG | elevation glazing "+tag,(side+normal*.08,y,z),(.12,w,h),GLASS,coll)
                cube("YONG | window sill "+tag,(side+normal*.17,y,z-h/2-.04),(.20,w+.20,.08),STONE,coll)
                for dy in (-w/2-.045,w/2+.045):
                    cube("YONG | window jamb "+tag,(side+normal*.16,y+dy,z),(.20,.07,h+.18),STONE,coll)
                cube("YONG | window mullion "+tag,(side+normal*.18,y,z),(.11,.055,h),METAL,coll)
                if f>0 and i%3==1:
                    cube("YONG | facade panel infill "+tag,
                         (side-normal*.015,y,zbase+2.25),(.08,span/bays*.70,.45),PANEL_ALT,coll)
        for j,frac in enumerate((.27,.53,.79)):
            y=y0+span*frac
            cube(f"YONG | vertical facade pier {side:.1f} {j}",
                 (side+normal*.02,y,HEIGHT_M/2),(.26,.55,HEIGHT_M-.5),PANEL,coll)
    xs=[p[0] for p in points]; ys=[p[1] for p in points]
    for y,normal in ((min(ys)+1.6,-1),(max(ys)-1.6,1)):
        for i in range(4):
            x=min(xs)+4.7+i*7.4
            for f,zbase in enumerate(levels()):
                z=zbase+(1.0 if f==0 else .95)
                tag=f"{normal} {i} {f}"
                cube("YONG | end glazing "+tag,(x,y+normal*.08,z),(1.7,.12,1.5),GLASS,coll)
                for dx in (-.94,.94):
                    cube("YONG | end frame "+tag+str(dx),(x+dx,y+normal*.15,z),(.08,.14,1.7),STONE,coll)

def entry(points,coll):
    x=max(p[0] for p in points); y=-504.1
    cube("YONG | red brick entry sign wall",(x+.03,y,3.25),(.18,8.8,4.8),BRICK,coll)
    cube("YONG | entrance glass doors",(x+.23,y,1.85),(.16,3.8,3.25),GLASS,coll)
    for dy in (-2.12,2.12):
        cube("YONG | limestone entrance pier",(x+.38,y+dy,1.95),(.35,.30,4.05),STONE,coll)
    cube("YONG | entry canopy fascia",(x+1.1,y,4.05),(2.4,5,.24),STONE,coll)
    cube("YONG | entry landing",(x+1.45,y,.16),(3.7,7,.32),STONE,coll)
    for i in range(5):
        cube(f"YONG | entry stair {i+1}",(x+3.65+i*.52,y,.05+i*.17),(.62,7.2,.10),STONE,coll)
    cu=bpy.data.curves.new("YONG sign lettering","FONT")
    cu.body="YOUNG HALL"; cu.size=1.05; cu.extrude=.025
    txt=bpy.data.objects.new("YONG | Young Hall sign",cu); coll.objects.link(txt)
    txt.location=(x+.30,y-3.4,4.8)
    txt.rotation_euler=(math.radians(90),0,math.radians(90))
    cu.materials.append(STONE)

def roof_and_courses(points,coll):
    xs=[p[0] for p in points]; ys=[p[1] for p in points]
    xmin,xmax,ymin,ymax=min(xs),max(xs),min(ys),max(ys)
    for k,z in enumerate(levels()[1:]+[HEIGHT_M-.75]):
        cube(f"YONG | floor course west {k:02d}",(xmin-.03,(ymin+ymax)/2,z),(.12,ymax-ymin-5,.07),STONE,coll)
        cube(f"YONG | floor course east {k:02d}",(xmax+.03,(ymin+ymax)/2,z),(.12,ymax-ymin-5,.07),STONE,coll)
    cube("YONG | flat roof coping",((xmin+xmax)/2,(ymin+ymax)/2,HEIGHT_M-.06),(xmax-xmin+.40,ymax-ymin+.40,.18),ROOF,coll)

def representative_interior(points,coll):
    # Representative lobby slice; detailed floor plan unavailable in public evidence.
    x=max(p[0] for p in points)-8; y=-504
    cube("YONG | first floor interior floor",(x,y,.22),(12,24,.24),FLOOR,coll)
    cube("YONG | first floor corridor partition",(x-2,y,1.75),(.16,18,3),INTERIOR,coll)
    cube("YONG | vestibule wall",(x-4.4,y+5,1.55),(.15,4.8,2.6),INTERIOR,coll)
    for j in range(2):
        cube(f"YONG | elevator core wall {j}",(x-5+j*3.2,y-2,1.8),(.18,5.6,3.2),INTERIOR,coll)
    for j in range(3):
        yy=y+7-j*6
        cube(f"YONG | study table {j}",(x-1.1,yy,.82),(1.55,2.2,.12),FURNITURE,coll)
        for dx in (-.55,.55):
            cube(f"YONG | table pedestal {j} {dx}",(x-1.1+dx,yy,.45),(.12,.12,.62),METAL,coll)
    cube("YONG | lobby reception desk",(x-3.8,y+8.4,.72),(1.1,3.2,1.3),FURNITURE,coll)

def configure_render(coll,points):
    scene=bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
    scene.name=SCENE_NAME
    if coll.name not in scene.collection.children:
        scene.collection.children.link(coll)
    for obj in list(bpy.data.objects):
        if obj.name.startswith(("YONG preview camera", "YONG key", "YONG fill")):
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.render.engine="CYCLES"; scene.cycles.samples=24
    scene.render.resolution_x=1500; scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(ROOT/"audit/young_hall_yong_cael95/preview_exterior.png")
    scene.world.color=(.11,.13,.17)
    cx=sum(x for x,y in points)/len(points); cy=sum(y for x,y in points)/len(points)
    target=Vector((cx,cy,HEIGHT_M/2))
    cd=bpy.data.cameras.new("YONG preview camera"); cam=bpy.data.objects.new("YONG preview camera",cd)
    scene.collection.objects.link(cam); cam.location=(cx+155,cy-195,105)
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    cd.type="ORTHO"; cd.ortho_scale=175; scene.camera=cam
    for name,loc,energy,size in [
        ("YONG key",(cx+55,cy-110,150),2600,80),
        ("YONG fill",(cx-90,cy-10,95),900,70)]:
        ld=bpy.data.lights.new(name,"AREA"); lo=bpy.data.objects.new(name,ld)
        scene.collection.objects.link(lo); lo.location=loc; ld.energy=energy; ld.size=size
        lo.rotation_euler=(target-lo.location).to_track_quat("-Z","Y").to_euler()
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=-0.5
    return scene

def main():
    coll=get_collection(); pts=get_points()
    shell(pts,coll); windows(pts,coll); entry(pts,coll)
    roof_and_courses(pts,coll); representative_interior(pts,coll)
    flush_boxes()
    scene=configure_render(coll,pts)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    bpy.context.window.scene=scene
    bpy.ops.render.render(write_still=True)
    print("YONG_BUILD_COMPLETE",len(coll.objects),"objects","height_m",HEIGHT_M)

if __name__=="__main__":
    main()
