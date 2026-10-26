"""Build evidence-backed massing for Purdue's Hanley Hall (HNLY).

The structural wall shell follows Purdue GIS OBJECTID 310. A current aerial
shows the larger OSM way 283275000 perimeter tracking the roof/eave projection;
that outline supplies the overhanging roof plan. Three floors are supported by
Purdue's 2026 emergency plan. Wall and ridge heights remain estimates.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ASSET_ID = "massing_hanley_hall_c8a4551"
ASSET_COLLECTION = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = str(ROOT / "modular/buildings/massing_hanley_hall_c8a4551.blend")
GIS_SOURCE = ROOT / "audit/massing_hanley_hall_c8a4551/sources/purdue_campus_gis_hanley.json"
OSM_SOURCE = ROOT / "audit/massing_hanley_hall_c8a4551/sources/osm_way_283275000_raw.json"
EAVE_Z = 14.8  # estimated wall/eave height; no measured elevation source found
HEIGHT = 16.08  # estimated roof ridge; three floors are supported, total height is not

def project_lonlat(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

# Purdue GIS OBJECTID 310 is the official wall-footprint source. The current
# aerial indicates that OSM's larger ring follows the roof/eave projection.
gis_doc=json.loads(GIS_SOURCE.read_text(encoding="utf-8-sig"))
gis_feature=next(f for f in gis_doc["features"] if f["attributes"].get("OBJECTID")==310)
RING=[project_lonlat(lon,lat) for lon,lat in gis_feature["geometry"]["rings"][0]]
if len(RING)>1 and math.dist(RING[0],RING[-1])<0.001: RING.pop()
osm_doc=json.loads(OSM_SOURCE.read_text(encoding="utf-8-sig"))
osm_nodes={n["id"]:n for n in osm_doc["nodes"]}
ROOF_RING=[project_lonlat(osm_nodes[nid]["lon"],osm_nodes[nid]["lat"]) for nid in osm_doc["way"]["nodes"]]
if len(ROOF_RING)>1 and math.dist(ROOF_RING[0],ROOF_RING[-1])<0.001: ROOF_RING.pop()

def point_line_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; den=dx*dx+dy*dy
    if den==0: return math.dist(p,a)
    t=max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def simplify_ring(points,tolerance=0.10):
    result=list(points); changed=True
    while changed and len(result)>3:
        changed=False
        for i,p in enumerate(result):
            if point_line_distance(p,result[i-1],result[(i+1)%len(result)])<=tolerance:
                result.pop(i); changed=True; break
    return result

DETAIL_RING=simplify_ring(RING)

def material(name, color, metallic=0.0, roughness=0.7):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.metallic=metallic; m.roughness=roughness
    return m

BRICK=material("Warm red-brown brick",(0.34,0.105,0.065))
LIMESTONE=material("Light limestone bands and frames",(0.72,0.66,0.53))
GLASS=material("Blue-gray glazing",(0.12,0.24,0.29),0.12,0.28)
ROOF=material("Dark gray standing-seam roof",(0.105,0.12,0.13),0.18,0.55)
GROUND=material("Recessed ground-level panels",(0.24,0.20,0.16))

def collection_get(name, scene):
    c=bpy.data.collections.get(name)
    if c is None: c=bpy.data.collections.new(name); scene.collection.children.link(c)
    for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
    return c

def mesh_obj(name, verts, faces, mats, assignments=None):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.materials.clear()
    for m in mats: me.materials.append(m)
    me.update(); o=bpy.data.objects.new(name,me); target.objects.link(o)
    if assignments:
        for p,i in zip(me.polygons,assignments): p.material_index=i
    return o

def extruded_shell():
    n=len(RING); verts=[(x,y,z) for z in (0,EAVE_Z) for x,y in RING]
    faces=[]; mats=[]
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n)); mats.append(0)
    # Concave ngon caps are triangulated by Blender's n-gon tessellator.
    faces.append(tuple(range(n,2*n))); mats.append(0)
    faces.append(tuple(reversed(range(n)))); mats.append(0)
    return mesh_obj("Hanley Hall | Purdue GIS wall footprint",verts,faces,[BRICK],mats)

def add_wall_details():
    verts=[]; faces=[]; mats_idx=[]
    def box_on_wall(cx,cy,z,tangent,normal,width,depth,height,matidx):
        start=len(verts); t=Vector((tangent[0],tangent[1],0)); n=Vector((normal[0],normal[1],0))
        center=Vector((cx,cy,z))
        # local box: width along facade, depth normal to facade, height vertical
        for dz in (-height/2,height/2):
            for dn in (-depth/2,depth/2):
                for dt in (-width/2,width/2):
                    q=center+t*dt+n*dn+Vector((0,0,dz)); verts.append(tuple(q))
        # six quad faces
        for f in ((0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)):
            faces.append(tuple(start+j for j in f)); mats_idx.append(matidx)
    for i,(ax,ay) in enumerate(DETAIL_RING):
        bx,by=DETAIL_RING[(i+1)%len(DETAIL_RING)]; dx,dy=bx-ax,by-ay; length=math.hypot(dx,dy)
        if length<4.0: continue
        tx,ty=dx/length,dy/length
        # Winding is clockwise as viewed from above: right-hand normal points out.
        nx,ny=ty,-tx
        count=max(1,round(length/3.4)); pitch=length/count
        for k in range(count):
            s=(k+0.5)*pitch; cx=ax+tx*s; cy=ay+ty*s
            # Ground floor: restrained translucent bay glazing.
            w=min(2.0,pitch*0.68)
            box_on_wall(cx,cy,2.65,(tx,ty),(nx,ny),w,0.045,2.8,2)
            # Second and third floors: punched windows with pale stone lintel/sill.
            for z in (6.65,11.45):
                ww=min(1.65,pitch*0.57)
                box_on_wall(cx,cy,z,(tx,ty),(nx,ny),ww,0.055,2.05,2)
                box_on_wall(cx,cy,z-1.12,(tx,ty),(nx,ny),ww+0.18,0.10,0.16,1)
                box_on_wall(cx,cy,z+1.12,(tx,ty),(nx,ny),ww+0.18,0.10,0.16,1)
        # Limestone floor bands register the three levels.
        for z in (4.85,9.65,14.45):
            box_on_wall((ax+bx)/2,(ay+by)/2,z,(tx,ty),(nx,ny),length,0.10,0.20,1)
    # The current aerial places a playground along the north edge; the HHS
    # facade image shows doors/glazing at the playground-facing ground level.
    # The image direction is not surveyed, so this entrance location is an
    # evidence-informed orientation estimate rather than a measured entrance.
    north=[]
    for i,a in enumerate(DETAIL_RING):
        b=DETAIL_RING[(i+1)%len(DETAIL_RING)]; length=math.dist(a,b)
        if length>=4.0: north.append(((a[1]+b[1])/2,length,a,b))
    if north:
        _,length,a,b=max(north,key=lambda row:row[0])
        dx,dy=b[0]-a[0],b[1]-a[1]; tx,ty=dx/length,dy/length; nx,ny=ty,-tx
        cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2
        door_w=min(2.4,length*.42)
        box_on_wall(cx,cy,1.55,(tx,ty),(nx,ny),door_w,.10,3.1,2)
        for off in (-door_w/2,door_w/2):
            px,py=cx+tx*off,cy+ty*off
            box_on_wall(px,py,1.55,(tx,ty),(nx,ny),.13,.16,3.05,1)
        box_on_wall(cx,cy,3.22,(tx,ty),(nx,ny),door_w+.22,.16,.18,1)
    mesh_obj("Hanley Hall | windows, limestone bands and entry",verts,faces,[BRICK,LIMESTONE,GLASS,ROOF],mats_idx)

def ring_centroid(points):
    area2=cx=cy=0.0
    for i,(x0,y0) in enumerate(points):
        x1,y1=points[(i+1)%len(points)]; cross=x0*y1-x1*y0
        area2+=cross; cx+=(x0+x1)*cross; cy+=(y0+y1)*cross
    return (cx/(3*area2),cy/(3*area2))

def add_roof_canopy():
    # OSM traces the outer roof/eave edge visible in current aerial imagery;
    # Purdue GIS supplies the smaller wall ring. A shallow hipped roof rises
    # toward an inset high plane. Pitch and ridge elevation are estimates.
    n=len(ROOF_RING); cx,cy=ring_centroid(RING); inset=.60
    inner=[(cx+(x-cx)*inset,cy+(y-cy)*inset) for x,y in ROOF_RING]
    verts=[(x,y,EAVE_Z) for x,y in ROOF_RING]+[(x,y,HEIGHT) for x,y in inner]
    faces=[]
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in inner]]):
        faces.append(tuple(n+i for i in tri))
    mesh_obj("Hanley Hall | hipped roof and OSM eave outline",verts,faces,[ROOF])

def setup_render(scene):
    scene.render.engine='BLENDER_WORKBENCH'; scene.render.resolution_x=1280; scene.render.resolution_y=960; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='BOTH'
    scene.display.shading.show_shadows=True; scene.display.shading.show_specular_highlight=True
    scene.display.shading.studio_light='paint.sl'
    scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'
    scene.render.image_settings.color_mode='RGBA'
    for name in ('Review camera','Large softbox'):
        old=bpy.data.objects.get(name)
        if old: bpy.data.objects.remove(old,do_unlink=True)
    center=Vector((-779.2,-298.0,7.2)); camdata=bpy.data.cameras.new('Review camera'); cam=bpy.data.objects.new('Review camera',camdata); scene.collection.objects.link(cam)
    cam.location=center+Vector((54,-70,46)); direction=center-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); camdata.lens=48; scene.camera=cam
    ld=bpy.data.lights.new('Large softbox','AREA'); lo=bpy.data.objects.new('Large softbox',ld); scene.collection.objects.link(lo); lo.location=center+Vector((8,-28,45)); ld.energy=3200; ld.size=38
    lo.rotation_euler=(center-lo.location).to_track_quat('-Z','Y').to_euler()
    scene.world.color=(0.22,0.22,0.22)

def main():
    global target
    scene=bpy.data.scenes.get(SCENE_NAME) or bpy.data.scenes.new(SCENE_NAME); bpy.context.window.scene=scene
    if scene.world is None: scene.world=bpy.data.worlds.new("Hanley Hall review world")
    target=collection_get(ASSET_COLLECTION,scene)
    # This is a standalone building library; discard Blender startup objects,
    # scenes and collections so none can leak into the exported file.
    for other in list(bpy.data.scenes):
        if other!=scene: bpy.data.scenes.remove(other)
    for obj in list(bpy.data.objects):
        if obj.name not in target.objects: bpy.data.objects.remove(obj,do_unlink=True)
    for c in list(bpy.data.collections):
        if c!=target: bpy.data.collections.remove(c,do_unlink=True)
    for c in list(scene.collection.children):
        if c.name!=target.name: scene.collection.children.unlink(c)
    extruded_shell(); add_wall_details(); add_roof_canopy(); setup_render(scene)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in target.objects: obj.select_set(True)
    shell=bpy.data.objects.get("Hanley Hall | Purdue GIS wall footprint"); bpy.context.view_layer.objects.active=shell
    bpy.ops.object.join(); shell.name="Hanley Hall"
    scene.render.filepath=str(ROOT/"audit/massing_hanley_hall_c8a4551/renders/hanley_hall_facade.png")
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
    bpy.ops.render.render(write_still=True)
    # Secondary view from the adjacent playground side helps inspect the
    # contextual entrance bay. Photo direction remains approximate.
    cam=scene.camera; old_location=cam.location.copy(); old_rotation=cam.rotation_euler.copy()
    target_point=Vector((-779.2,-298.0,7.2)); cam.location=target_point+Vector((-8,76,42))
    cam.rotation_euler=(target_point-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(ROOT/"audit/massing_hanley_hall_c8a4551/renders/hanley_entry_review.png")
    bpy.ops.render.render(write_still=True)
    cam.location=old_location; cam.rotation_euler=old_rotation
    light=bpy.data.objects.get('Large softbox')
    cam_data=cam.data if cam else None; light_data=light.data if light else None
    scene.camera=None
    if cam and cam.name in bpy.data.objects: bpy.data.objects.remove(cam,do_unlink=True)
    if light: bpy.data.objects.remove(light,do_unlink=True)
    if cam_data and cam_data.users==0: bpy.data.cameras.remove(cam_data)
    if light_data and light_data.users==0: bpy.data.lights.remove(light_data)
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)

if __name__=='__main__': main()
