"""Build a source-informed Hillel massing asset from the GIS footprint.

Footprint: Purdue GIS feature 803, campus coordinates. The numeric wall height
is retained only as a visualization placeholder from the GIS Extrution=12
attribute whose units are undocumented; it is not a measured elevation.
Facade cues are based on the Purdue Hillel Spring 2022 newsletter photograph.
"""
import bpy, json, math, os
from mathutils import Vector

ASSET_ID = "massing_hillel_36d2ba1"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVIDENCE_DIR = os.path.join(ROOT, "audit", ASSET_ID)
ASSET_PATH = os.path.join(os.path.dirname(__file__), ASSET_ID + ".blend")
PREVIEW_PATH = os.path.join(EVIDENCE_DIR, "hillel_exterior_oblique_r2.png")
FRONT_PATH = os.path.join(EVIDENCE_DIR, "hillel_waldron_front_r2.png")
TOP_PATH = os.path.join(EVIDENCE_DIR, "hillel_roof_top_r2.png")
FOOTPRINT = [
    (-336.606908, -338.230284), (-337.395863, -338.216600),
    (-337.012980, -315.957570), (-328.980312, -316.094553),
    (-329.083244, -322.254434), (-312.853408, -322.525703),
    (-312.860388, -322.995098), (-305.997686, -323.236600),
    (-306.391508, -341.539272), (-320.729521, -341.231916),
    (-320.706012, -340.067610), (-336.637176, -339.748140),
]
# Preserve prior gross wall height only to keep the GIS massing stable. This is
# an explicit display placeholder, not an inferred or surveyed building height.
HEIGHT_PLACEHOLDER_M = 3.6576


def mat(name, color, rough=0.8, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    return m


def boxes(vertices, faces, center, axes, dims):
    c = Vector(center); xa, ya, za = axes
    hx, hy, hz = [d * 0.5 for d in dims]
    base = len(vertices)
    for sx, sy, sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
        vertices.append(tuple(c + xa*sx*hx + ya*sy*hy + za*sz*hz))
    faces.extend([[base+i for i in f] for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]])


def add_mesh(name, verts, faces, collection, material):
    me = bpy.data.meshes.new(name + "_Mesh"); me.from_pydata(verts, [], faces); me.materials.append(material); me.update()
    ob = bpy.data.objects.new(name, me); collection.objects.link(ob); return ob


def aim(ob, target):
    ob.rotation_euler = (Vector(target)-ob.location).to_track_quat("-Z", "Y").to_euler()


def build():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene; scene.name = SCENE_NAME
    for other in list(bpy.data.scenes):
        if other != scene: bpy.data.scenes.remove(other)
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(col)
    else:
        for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    for o in list(scene.objects):
        if o.type in {"CAMERA", "LIGHT"}: bpy.data.objects.remove(o, do_unlink=True)

    masonry = mat("Hillel | light buff masonry based on 2022 photo", (0.56, 0.48, 0.36), .88)
    roofmat = mat("Hillel | pale low-slope roof and broad eave", (0.43, 0.43, 0.39), .9)
    trim = mat("Hillel | pale window frames and entry surround", (0.78, 0.74, 0.65), .62)
    glass = mat("Hillel | dark reflective glazing", (0.045, 0.12, 0.15), .24, .12)
    doormat = mat("Hillel | entrance glazing", (0.07, 0.13, 0.15), .28, .08)

    area = sum(FOOTPRINT[i][0]*FOOTPRINT[(i+1)%len(FOOTPRINT)][1]-FOOTPRINT[(i+1)%len(FOOTPRINT)][0]*FOOTPRINT[i][1] for i in range(len(FOOTPRINT))) *.5
    ring = FOOTPRINT if area > 0 else list(reversed(FOOTPRINT)); n=len(ring)
    cx=sum(x for x,y in ring)/n; cy=sum(y for x,y in ring)/n
    wall_h=HEIGHT_PLACEHOLDER_M
    # Structural shell at source ring; outer roof ring supplies the photograph's
    # visible broad, flat overhang. Eave depth is a visual approximation.
    verts=[(x,y,z) for z in (0,wall_h) for x,y in ring]
    faces=[tuple(reversed(range(n)))]
    for i in range(n):
        j=(i+1)%n; faces.append((i,j,n+j,n+i))
    faces.append(tuple(range(n,2*n)))
    roof_base=len(verts); scale=1.045
    outer=[(cx+(x-cx)*scale, cy+(y-cy)*scale, wall_h+0.10) for x,y in ring]
    verts.extend(outer)
    for i in range(n): faces.append((n+i,n+(i+1)%n,roof_base+(i+1)%n,roof_base+i))
    faces.append(tuple(roof_base+i for i in range(n)))
    me=bpy.data.meshes.new("Hillel_Shell_Mesh"); me.from_pydata(verts,[],faces); me.materials.append(masonry); me.materials.append(roofmat); me.update()
    for poly in me.polygons:
        if poly.index >= n+2: poly.material_index=1
    shell=bpy.data.objects.new("Hillel",me); col.objects.link(shell)

    # The photograph shows one low, single-storey volume, pale masonry, broad
    # vertical window bays with light frames, and a prominent entry. Position
    # and exact sizes of individual openings remain illustrative. County minutes
    # establish only that the front faces west toward Waldron Street.
    winv=[]; winf=[]; glassv=[]; glassf=[]; framev=[]; framef=[]; doorv=[]; doorf=[]
    front_i=None
    for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        d=Vector((b[0]-a[0],b[1]-a[1],0)); length=d.length
        if length < 5: continue
        tangent=d.normalized(); outward=Vector((tangent.y,-tangent.x,0))
        # Pick the west-facing edge from GIS coordinates, the documented front
        # direction, not the photo's unregistered camera viewpoint.
        west=abs(a[0]+337.0)<0.9 and abs(b[0]+337.0)<0.9 and abs(a[1]-b[1])>10
        count=max(1, round(length/4.4))
        # Main facades use wider glass bays, with substantial pale vertical piers.
        for k in range(count):
            t=(k+0.5)/count; p=Vector((a[0],a[1],0)).lerp(Vector((b[0],b[1],0)),t)
            axes=(tangent,outward,Vector((0,0,1)))
            if west:
                if front_i is None: front_i=i
                # Center the entry bay; other west-front bays remain tall glazing.
                if abs(t-.5) < .5/count + .01:
                    door_center=p+outward*.12
                    boxes(framev,framef,(door_center.x,door_center.y,1.46),axes,(1.9,.12,2.72))
                    boxes(doorv,doorf,(*(p+outward*.21)[:2],1.42),axes,(1.58,.08,2.52))
                    # A restrained sign panel above the door references the
                    # large central masonry panel visible in the source photo.
                    panel=p+outward*.14
                    boxes(framev,framef,(panel.x,panel.y,3.05),axes,(2.5,.14,.42))
                    continue
            width=min(2.25,max(1.75,length/(count+1)*.62))
            zcenter=1.82; h=2.48
            fc=p+outward*.12; gc=p+outward*.22
            boxes(framev,framef,(fc.x,fc.y,zcenter),axes,(width+.18,.14,h+.16))
            # Two vertical lights per bay reflect the multi-pane framing in photo.
            for side in (-1,1):
                pane=p+tangent*(side*width*.245)+outward*.225
                boxes(glassv,glassf,(pane.x,pane.y,zcenter),axes,(width*.43,.08,h))
    # One mesh per facade material keeps the familiar five-object export.
    if framef: add_mesh("Hillel_Schematic_Windows_And_Entry_Frame",framev,framef,col,trim)
    if doorf: add_mesh("Hillel_Schematic_Entry_Glazing",doorv,doorf,col,doormat)
    if glassf: add_mesh("Hillel_Schematic_Window_Glazing",glassv,glassf,col,glass)
    # Ensure all facades render with five objects (empty arrays are not expected).

    # Scene and review cameras remain outside the exported asset collection.
    scene.render.engine="BLENDER_EEVEE_NEXT"
    scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
    scene.view_settings.view_transform="AgX"
    world=bpy.data.worlds.new("Hillel Review World") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world=world; world.use_nodes=True; bg=next(n for n in world.node_tree.nodes if n.type=="BACKGROUND")
    bg.inputs["Color"].default_value=(.72,.77,.82,1); bg.inputs["Strength"].default_value=.65
    center=(cx,cy,1.8)
    cd=bpy.data.cameras.new("Hillel Review Camera"); cam=bpy.data.objects.new("Hillel Review Camera",cd); scene.collection.objects.link(cam)
    cd.type="ORTHO"; cd.ortho_scale=49; scene.camera=cam
    ld=bpy.data.lights.new("Hillel Review Key","AREA"); light=bpy.data.objects.new("Hillel Review Key",ld); scene.collection.objects.link(light)
    ld.energy=2400; ld.shape="DISK"; ld.size=24
    def render(path,loc,scale,look=center):
        cam.location=loc; cd.ortho_scale=scale; aim(cam,look); light.location=(cx-18,cy-22,23); aim(light,look); scene.render.filepath=path; bpy.ops.render.render(write_still=True)
    render(PREVIEW_PATH,(cx-31,cy-25,19),49)
    # A nearly frontal west/Waldron view to assess broad window rhythm and entry.
    render(FRONT_PATH,(cx-45,cy-1,8),39,(cx,cy,1.75))
    render(TOP_PATH,(cx,cy,42),42,(cx,cy,1.8))
    bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
    print(json.dumps({"asset_id":ASSET_ID,"asset_path":ASSET_PATH,"collection":COLLECTION_NAME,"objects":len(col.objects),"footprint_vertices":n,"footprint_area_m2":round(abs(area),3),"wall_height_placeholder_m":wall_h,"xy_bounds_m":[[min(x for x,y in ring),max(x for x,y in ring)],[min(y for x,y in ring),max(y for x,y in ring)]],"roof_overhang_visual_approx_m":round((scale-1)*max(max(x for x,y in ring)-min(x for x,y in ring),max(y for x,y in ring)-min(y for x,y in ring))/2,3)},indent=2))

build()


