"""Replace the incomplete Armstrong roof presentation with a sourced, inferred wing canopy.

The canopy plan is traced from the 2023 orthophoto. Its height surface is an
explicit visual inference bounded by (not measured from) 2018 5-ft NDHM data.
Only the Neil asset and its building-specific audit folder are changed.
"""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
AUDIT = ROOT / "audit/neil_armstrong_hall_refine"
EXPECTED_SHA = "d3d90d21ad60b985826270be18c016220944e3c87545fc179af7b51d5084b8b4"

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

before_sha=sha256(ASSET)
if before_sha != EXPECTED_SHA:
    raise RuntimeError(f"Neil asset changed since inspection: {before_sha}")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset_col=bpy.data.collections.get("Asset_neil_armstrong_hall")
if not asset_col or len(asset_col.objects)!=445 or len(bpy.data.objects)!=445:
    raise RuntimeError("Unexpected asset collection/object count")

deck=bpy.data.objects.get("ARMS_Cantilever_Canopy_Deck")
if not deck or deck.type!="MESH" or len(deck.data.vertices)!=8 or len(deck.data.polygons)!=6:
    raise RuntimeError("Unexpected canopy deck geometry; refusing non-idempotent edit")
mesh=deck.data
old_verts=[[round(v.co.x,6),round(v.co.y,6),round(v.co.z,6)] for v in mesh.vertices]
old_faces=[[int(i) for i in p.vertices] for p in mesh.polygons]
old_mats=[m.name if m else None for m in mesh.materials]
asset_to_object=deck.matrix_world.inverted()

# Registered 2023 Indiana orthophoto extent (EPSG:3857), 2000 x 900 pixels.
# Pixel samples trace the visible red ACM outer edge and inner edge; the latter
# bounds the pale roof surface visible inside the cantilever. Pixel tracing
# is direct orthographic plan evidence, while the roof/wall separation remains
# explicitly uncertain because eaves can overhang the GIS wall footprint.
IMG_W,IMG_H=2000.0,900.0
XMIN,YMIN,XMAX,YMAX=(-9675473.17973648,4928688.31898462,-9675190.20021127,4928833.11569478)
LAT0,LON0=40.4274,-86.9137
MARK_X,MARK_Y=-109.0,400.1893310547
R=6378137.0

def pixel_to_local(px,py):
    mx=XMIN+(px/IMG_W)*(XMAX-XMIN)
    my=YMAX-(py/IMG_H)*(YMAX-YMIN)
    lon=math.degrees(mx/R)
    lat=math.degrees(2*math.atan(math.exp(my/R))-math.pi/2)
    x=(lon-LON0)*math.pi/180*R*math.cos(math.radians(LAT0))-MARK_X
    y=(lat-LAT0)*math.pi/180*R-MARK_Y
    return (x,y)

outer_px=[(345,153),(1509,173),(1720,441),(565,414),(376,355)]
inner_px=[(600,205),(1492,222),(1604,390),(565,358),(510,246)]
outer=[pixel_to_local(*p) for p in outer_px]
inner=[pixel_to_local(*p) for p in inner_px]
# 21.6 m is the median top of the R5 high LiDAR band, not a measured canopy
# elevation. The values below form a deliberately bounded, photo-based wing
# profile from that coarse ceiling down to the documented 16.15 m atrium.
z_outer=[21.50,21.10,20.90,20.35,20.15]
z_inner=[17.10,17.35,17.20,16.45,16.75]
MAX_LIDAR_CEILING=21.60
if max(z_outer)>MAX_LIDAR_CEILING:
    raise RuntimeError("Canopy exceeds the coarse LiDAR ceiling")

red=bpy.data.materials.get("ARMS_Mayflower_Red_ACM")
soffit=bpy.data.materials.get("ARMS_Sea_Wolf_ACM")
if not red or not soffit:
    raise RuntimeError("Expected existing ACM materials are missing")
new_verts=list(old_verts)
new_faces=[(tuple(f),0) for f in old_faces]
N_ALONG=8
N_ACROSS=3
THICKNESS=0.30

# Build each of the five plan bands as a gently warped, faceted wing plane.
# The top edge follows orthophoto-traced eaves, the inner edge follows the
# visible pale roof boundary, and the peak/underside profile is an inference
# from the geotagged 2016 photos and the LiDAR height-band ceiling.
for seg in range(5):
    nxt=(seg+1)%5
    grid_top=[]
    grid_bottom=[]
    for j in range(N_ACROSS+1):
        t=j/N_ACROSS
        row_top=[]; row_bottom=[]
        for k in range(N_ALONG+1):
            s=k/N_ALONG
            x0,y0=outer[seg]; x1,y1=outer[nxt]
            ix0,iy0=inner[seg]; ix1,iy1=inner[nxt]
            ox=x0*(1-s)+x1*s; oy=y0*(1-s)+y1*s
            qx=ix0*(1-s)+ix1*s; qy=iy0*(1-s)+iy1*s
            x=ox*(1-t)+qx*t; y=oy*(1-t)+qy*t
            zo=z_outer[seg]*(1-s)+z_outer[nxt]*s
            zi=z_inner[seg]*(1-s)+z_inner[nxt]*s
            warp=1.25*math.sin(math.pi*t)*math.sin(math.pi*s)
            z=zo*(1-t)+zi*t+warp
            row_top.append(len(new_verts)); new_verts.append(tuple(asset_to_object @ Vector((x,y,z))))
            row_bottom.append(len(new_verts)); new_verts.append(tuple(asset_to_object @ Vector((x,y,z-THICKNESS))))
        grid_top.append(row_top); grid_bottom.append(row_bottom)
    for j in range(N_ACROSS):
        for k in range(N_ALONG):
            # Upward-facing ACM top quads and downward-facing dark soffit quads.
            a,b=grid_top[j][k],grid_top[j][k+1]
            c,d=grid_top[j+1][k+1],grid_top[j+1][k]
            new_faces.append(((a,d,c,b),1))
            ab,bb=grid_bottom[j][k],grid_bottom[j][k+1]
            cb,db=grid_bottom[j+1][k+1],grid_bottom[j+1][k]
            new_faces.append(((ab,bb,cb,db),0))
    # Close the outer and inner fascia edges, plus each segment's end cheeks.
    for k in range(N_ALONG):
        a,b=grid_top[0][k],grid_top[0][k+1]
        ab,bb=grid_bottom[0][k],grid_bottom[0][k+1]
        new_faces.append(((a,b,bb,ab),1))
        a,b=grid_top[-1][k],grid_top[-1][k+1]
        ab,bb=grid_bottom[-1][k],grid_bottom[-1][k+1]
        new_faces.append(((b,a,ab,bb),0))
    for j in range(N_ACROSS):
        a,b=grid_top[j][0],grid_top[j+1][0]
        ab,bb=grid_bottom[j][0],grid_bottom[j+1][0]
        new_faces.append(((b,a,ab,bb),1))
        a,b=grid_top[j][-1],grid_top[j+1][-1]
        ab,bb=grid_bottom[j][-1],grid_bottom[j+1][-1]
        new_faces.append(((a,b,bb,ab),1))

newmesh=bpy.data.meshes.new("ARMS_R12_Orthophoto_Wing_Canopy_Mesh")
newmesh.from_pydata(new_verts,[],[f for f,_mi in new_faces])
newmesh.materials.clear()
newmesh.materials.append(soffit)
newmesh.materials.append(red)
newmesh.update(calc_edges=True)
for p,(_f,mi) in zip(newmesh.polygons,new_faces):
    p.material_index=mi
    p.use_smooth=False
deck.data=newmesh
deck.name="ARMS_Cantilever_Canopy_Deck"
deck["R12_plan_source"]="2023 Indiana Current Imagery orthophoto; red ACM outer/inner roof edges traced in image pixels"
deck["R12_height_source"]="Photo-based inferred wing profile bounded by R5 2018 NDHM high-band median 21.55 m / coarse 21.6 m ceiling; not a measured roof elevation"
deck["R12_uncertainty"]="Orthophoto traces roof/eaves only; it does not establish wall centerlines or exact overhang heights. 2016 photo positions are geotagged but headings are unavailable. Height warp is inferred."

# Keep the prior low entrance canopy and its downlights; it may be a separate
# lobby awning. Update the neighboring fascia finish only through its existing
# dark soffit material, without asserting that it is part of the high roof.

# Fix mesh normals and validate the collection inventory.
import bmesh
bm=bmesh.new(); bm.from_mesh(newmesh)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(newmesh); bm.free(); newmesh.update()
if len(asset_col.objects)!=445 or len(bpy.data.objects)!=445:
    raise RuntimeError("Object inventory changed during in-place canopy edit")

bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
after_sha=sha256(ASSET)

def bounds(obj):
    pts=[obj.matrix_world @ v.co for v in obj.data.vertices]
    return {"min":[round(min(v[i] for v in pts),3) for i in range(3)],"max":[round(max(v[i] for v in pts),3) for i in range(3)],"verts":len(obj.data.vertices),"polygons":len(obj.data.polygons)}

evidence={
  "building_id":"neil_armstrong_hall",
  "revision":"R12 roof geometry refinement",
  "date":"2026-10-25",
  "asset":"../../modular/buildings/neil_armstrong_hall.blend",
  "sha256_before":before_sha,
  "sha256_after":after_sha,
  "collection_object_count":len(asset_col.objects),
  "scene_object_count":len(bpy.data.objects),
  "changed_object":"ARMS_Cantilever_Canopy_Deck",
  "mesh_preservation":{"old_vertices":old_verts,"old_faces":old_faces,"old_materials":old_mats},
  "new_geometry":{
    "kind":"orthophoto-traced, photo-height-inferred red ACM wing/canopy shell",
    "outer_pixel_points":outer_px,
    "inner_pixel_points":inner_px,
    "outer_local_xy_m":[[round(x,3),round(y,3)] for x,y in outer],
    "inner_local_xy_m":[[round(x,3),round(y,3)] for x,y in inner],
    "outer_z_m":z_outer,
    "inner_z_m":z_inner,
    "max_height_m":MAX_LIDAR_CEILING,
    "thickness_m":THICKNESS,
    "warp_amplitude_m":1.25,
    "mesh_bounds":bounds(deck),
    "material_top":"ARMS_Mayflower_Red_ACM",
    "material_underside":"ARMS_Sea_Wolf_ACM",
    "uncertainty":"Plan edge is photo-traced; roof elevation and warp are inferred. NDHM supplies only a broad 5-ft height-band ceiling, not roof-specific dimensions. GIS is not used as a roof edge or wall plan."
  },
  "sources":[
    {"title":"Indiana Current Imagery, 2023 orthophoto tile","provider":"Indiana Geographic Information Office","url":"https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer","local_file":"../../audit/complete_neil_armstrong/sources/indiana_current_ortho_neil_extent.png","used_for":"Direct top-down trace of the visible red canopy/eave footprint and pale inner roof boundary; not used to assert walls."},
    {"title":"Indiana 3DEP 2018 Tippecanoe NDHM","provider":"Purdue Digital Forestry / iDiF","url":"https://lidar.digitalforestry.org/QL2_3DEP_LiDAR_IN_2017_2019_l2/tippecanoe/cog/tippecanoe_ndhm_2018.tif","local_file":"../../audit/complete_neil_armstrong/sources/tippecanoe_ndhm_clip_r5.tif","used_for":"Coarse height range; high-band median 21.55m and approximate 21.6m ceiling. 5-ft resolution cannot measure this roof form."},
    {"title":"Neil Armstrong Hall of Engineering Purdue University 2016 01","photographer":"Julian Herzog","license":"CC BY 4.0","url":"https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg","local_file":"sources_r12/arms_2016_01.jpg","camera_geotag_latlon":[40.431388,-86.916112],"focal_length_mm":38,"used_for":"Visual evidence of folded/wing-like shell, overhang, and glazed atrium. Camera position geotagged; heading/roll unavailable; dimensions not inferred."},
    {"title":"Neil Armstrong Hall of Engineering Purdue University 2016 03","photographer":"Julian Herzog","license":"CC BY 4.0","url":"https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_03.jpg","local_file":"../../audit/complete_neil_armstrong/sources/wikimedia_neil_2016_03_r8.jpg","camera_geotag_latlon":[40.431433,-86.916781],"focal_length_mm":48,"used_for":"Visual evidence of the same red metallic wing canopy, glazing, brick and entrance; heading/roll unavailable; dimensions not inferred."},
    {"title":"Neil Armstrong Hall of Engineering Purdue University 2016 02","photographer":"Julian Herzog","license":"CC BY 4.0","url":"https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_02.jpg","local_file":"sources_r12/arms_2016_02.jpg","camera_geotag_latlon":[40.430861,-86.915212],"focal_length_mm":24,"used_for":"Courtyard-side visual comparison for long glazed facades and roof relationship; heading/roll unavailable."}
  ],
  "validation_pending":"Reopen the saved asset, verify object/material inventory and geometry bounds, render side and top comparisons. No shared files or master blend were edited."
}
(AUDIT/"evidence_r12.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
print(json.dumps({"sha256_before":before_sha,"sha256_after":after_sha,"object_count":len(asset_col.objects),"new_mesh_bounds":bounds(deck),"new_vertices":len(newmesh.vertices),"new_polygons":len(newmesh.polygons)},indent=2))
