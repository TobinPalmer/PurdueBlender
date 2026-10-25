"""R12.1 color and photo-supported northwest roof pocket refinement."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET=ROOT/"modular/buildings/neil_armstrong_hall.blend"
AUDIT=ROOT/"audit/neil_armstrong_hall_refine"
EXPECTED="6262855f445c84b194fd0f8f11041b925f9114ebb69e0ae7a6a9255989a472a2"
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
if sha(ASSET)!=EXPECTED:raise RuntimeError("Neil asset changed after R12; refusing to overwrite")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
obj=bpy.data.objects["ARMS_Cantilever_Canopy_Deck"]
asset_col=bpy.data.collections["Asset_neil_armstrong_hall"]
if len(asset_col.objects)!=445 or len(obj.data.vertices)!=368 or len(obj.data.polygons)!=356:
    raise RuntimeError("Unexpected R12 asset inventory")

# Match the muted, dark terracotta visible in the photo/orthophoto. This is a
# dedicated material on the new wing surfaces; the shared Mayflower material
# used elsewhere is untouched.
red=bpy.data.materials.get("ARMS_R12_Wing_Red_ACM") or bpy.data.materials.new("ARMS_R12_Wing_Red_ACM")
red.use_nodes=True
bsdf=next(n for n in red.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value=(0.32,0.16,0.12,1.0)
bsdf.inputs["Metallic"].default_value=0.32
bsdf.inputs["Roughness"].default_value=0.42
red.diffuse_color=(0.32,0.16,0.12,1.0)
if len(obj.data.materials)<2:raise RuntimeError("R12 ACM material slot missing")
obj.data.materials[1]=red

# A small dark inset triangle marks the northwestern opening visible in the
# 2023 ortho and 2016 photographs. It is a shallow visual pocket, not a claim
# of a measured structural aperture.
shadow=bpy.data.materials.get("ARMS_R12_Wing_Recess_Shadow") or bpy.data.materials.new("ARMS_R12_Wing_Recess_Shadow")
shadow.use_nodes=True
sbsdf=next(n for n in shadow.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
sbsdf.inputs["Base Color"].default_value=(0.035,0.017,0.014,1.0)
sbsdf.inputs["Metallic"].default_value=0.28
sbsdf.inputs["Roughness"].default_value=0.52
shadow.diffuse_color=(0.035,0.017,0.014,1.0)

# Match the pixel-trace transform used in R12.
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
    return ((lon-LON0)*math.pi/180*R*math.cos(math.radians(LAT0))-MARK_X,
            (lat-LAT0)*math.pi/180*R-MARK_Y)

inv=obj.matrix_world.inverted()
px_points=[(460,210),(505,215),(492,235)]
world_hits=[]
for px,py in px_points:
    x,y=pixel_to_local(px,py)
    origin_local=inv@Vector((x,y,60.0))
    down_local=(inv.to_3x3()@Vector((0,0,-1))).normalized()
    hit,loc,nor,face=obj.ray_cast(origin_local,down_local)
    if not hit:
        raise RuntimeError(f"Roof ray failed at traced point {(px,py)} -> {(x,y)}")
    w=obj.matrix_world@loc
    world_hits.append((x,y,w.z+0.012))

old_faces=[(list(p.vertices),p.material_index) for p in obj.data.polygons]
old_verts=[tuple(v.co) for v in obj.data.vertices]
faces=[(f,mi) for f,mi in old_faces]
verts=list(old_verts)
world_vertices=[tuple(inv@Vector(p)) for p in world_hits]
base=len(verts); verts.extend(world_vertices)
patch_face=(base,base+1,base+2)
if len(obj.data.materials)<3:obj.data.materials.append(shadow)
else:obj.data.materials[2]=shadow
faces.append((patch_face,2))
newmesh=bpy.data.meshes.new("ARMS_R12_1_Wing_Canopy_Mesh")
newmesh.from_pydata(verts,[],[f for f,_ in faces])
for m in obj.data.materials:newmesh.materials.append(m)
newmesh.update(calc_edges=True)
for p,(_f,mi) in zip(newmesh.polygons,faces):p.material_index=mi
import bmesh
bm=bmesh.new();bm.from_mesh(newmesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(newmesh);bm.free();newmesh.update()
oldmesh=obj.data
obj.data=newmesh
obj["R12_1_finish_note"]="Dedicated muted terracotta ACM finish for the inferred wing surface; shared Mayflower material left unchanged."
obj["R12_1_notch_note"]="Shallow dark triangular inset traced from the NW roof pocket visible in 2023 orthophoto and 2016 photos; not a measured structural opening."
if len(asset_col.objects)!=445:raise RuntimeError("Object count changed")
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
newsha=sha(ASSET)

ev={
 "building_id":"neil_armstrong_hall","revision":"R12.1 canopy finish and NW pocket","date":"2026-10-25",
 "parent_sha256":EXPECTED,"asset":"../../modular/buildings/neil_armstrong_hall.blend","sha256":newsha,
 "object_count":len(asset_col.objects),"mesh_object":"ARMS_Cantilever_Canopy_Deck",
 "new_material":{"name":red.name,"base_color_linear":[0.32,0.16,0.12,1],"metallic":0.32,"roughness":0.42,"scope":"new wing roof surface only; shared Mayflower ACM left unchanged"},
 "roof_pocket":{"kind":"shallow dark triangular inset","orthophoto_pixel_vertices":px_points,"asset_local_xyz_m":[[round(x,3),round(y,3),round(z,3)] for x,y,z in world_hits],"limitation":"The dark pocket is visual inference from aerial/photo evidence, not a verified structural aperture."},
 "sources":[
  {"title":"Indiana Current Imagery 2023 ortho","url":"https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer","local_file":"../../audit/complete_neil_armstrong/sources/indiana_current_ortho_neil_extent.png","supports":"Red roof pocket and overall roof plan; no elevation."},
  {"title":"Neil Armstrong Hall 2016 photo 01","url":"https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg","license":"CC BY 4.0","local_file":"sources_r12/arms_2016_01.jpg","supports":"Folded wing shell and dark opening beneath the northwest apex; visual only, not scale registered."},
  {"title":"Neil Armstrong Hall 2016 photo 03","url":"https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_03.jpg","license":"CC BY 4.0","local_file":"../../audit/complete_neil_armstrong/sources/wikimedia_neil_2016_03_r8.jpg","supports":"Canopy finish and folded roof silhouette; visual only, not scale registered."}
 ],
 "validation_pending":"Reopen and validate the saved asset; render all sides and roof with the underside fill light; then send to separate grader."
}
(AUDIT/"evidence_r12_1.json").write_text(json.dumps(ev,indent=2),encoding="utf-8")
print(json.dumps({"sha256":newsha,"objects":len(asset_col.objects),"mesh_vertices":len(newmesh.vertices),"mesh_polygons":len(newmesh.polygons),"pocket_world_vertices":[[round(c,3) for c in p] for p in world_hits]},indent=2))
