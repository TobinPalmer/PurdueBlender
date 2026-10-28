import bpy, os, math
import bmesh
import json
from mathutils import Vector

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT=os.path.join(ROOT,"audit","circle_pines_fid761")
ASSET=os.path.join(ROOT,"modular","buildings","massing_house_301841609_c6c9ac4.blend")
GIS=json.load(open(os.path.join(AUDIT,"initial_inspection.json"),encoding="utf-8"))["gis_ring_xy_local_m"]
if GIS[0]==GIS[-1]: GIS=GIS[:-1]
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
obj=bpy.data.objects["House_301841609"]
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1500; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
scene.view_settings.exposure=0; scene.view_settings.gamma=1
scene.world.use_nodes=True
world_bg=next(n for n in scene.world.node_tree.nodes if n.type=="BACKGROUND")
world_bg.inputs["Color"].default_value=(0.55,0.55,0.55,1)
world_bg.inputs["Strength"].default_value=0.30
# Remove prior temporary camera/light objects if any.
for o in list(bpy.data.objects):
    if o.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(o,do_unlink=True)
center=Vector((-904.2,833.3,2.9))
def aim(o,point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
edge_index=17
fa,fb=GIS[edge_index],GIS[(edge_index+1)%len(GIS)]
dx,dy=fb[0]-fa[0],fb[1]-fa[1]
edge_len=math.hypot(dx,dy)
u=(dx/edge_len,dy/edge_len)
area2=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(GIS,GIS[1:]+GIS[:1]))
normal=(-u[1],u[0]) if area2<0 else (u[1],-u[0])
cam_data=bpy.data.cameras.new("CirclePinesPreviewCamera")
cam=bpy.data.objects.new("CirclePinesPreviewCamera",cam_data); scene.collection.objects.link(cam)
facade_target=Vector(((fa[0]+fb[0])/2,(fa[1]+fb[1])/2,2.9))
cam.location=facade_target+Vector((normal[0]*92,normal[1]*92,22)); aim(cam,facade_target)
cam.data.type='ORTHO'; cam.data.ortho_scale=86; scene.camera=cam
ld=bpy.data.lights.new("LargeSoftbox","AREA"); lo=bpy.data.objects.new("LargeSoftbox",ld); scene.collection.objects.link(lo)
lo.location=center+Vector((-38,-48,72)); lo.data.energy=52000; lo.data.shape='DISK'; lo.data.size=62; aim(lo,center)
sun_data=bpy.data.lights.new("SoftDirectionalFill","SUN"); sun=bpy.data.objects.new("SoftDirectionalFill",sun_data); scene.collection.objects.link(sun)
sun.location=center+Vector((-70,-45,100)); sun.data.energy=1.25; sun.data.angle=math.radians(18); aim(sun,center)
# Neutral preview ground is temporary; it is not part of the saved building asset.
bpy.ops.mesh.primitive_plane_add(size=1600,location=(center.x,center.y,-.04))
ground=bpy.context.object; ground.name="CirclePines_Temporary_PreviewGround"
gm=bpy.data.materials.new("CirclePines_Temporary_PreviewGround_Material"); gm.diffuse_color=(.22,.25,.23,1); gm.use_nodes=True
gb=next(n for n in gm.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
gb.inputs["Base Color"].default_value=(.22,.25,.23,1); gb.inputs["Roughness"].default_value=.92
ground.data.materials.append(gm)
scene.render.filepath=os.path.join(AUDIT,"exterior_preview.png")
bpy.ops.render.render(write_still=True)
print("rendered exterior",scene.render.filepath)

# Straight-on view of the single elevation visible from the Google Street View
# camera direction. This supplements, rather than replaces, the source photo.
cam.location=facade_target+Vector((normal[0]*78,normal[1]*78,6.0))
aim(cam,facade_target)
cam.data.ortho_scale=36
scene.render.filepath=os.path.join(AUDIT,"front_elevation_preview.png")
bpy.ops.render.render(write_still=True)
print("rendered source-facing elevation",scene.render.filepath)

# Render a temporary roof-open, low-perimeter cutaway so the schematic layout
# remains visible. This does not alter the saved .blend or imply an as-built
# floor plan. The visible facade assemblies are omitted from this explanatory
# cutaway; only a low footprint wall trace remains.
source_mesh=obj.data
coords=[tuple(v.co) for v in source_mesh.vertices]
faces=[]; inds=[]
ring_count=len(GIS)
cut_wall_height=1.20
for p_index,p in enumerate(source_mesh.polygons):
    if p.material_index==1: continue # remove cap and roof return
    if p_index<ring_count:
        i,j=p.vertices[0],p.vertices[1]
        a,b=source_mesh.vertices[i].co,source_mesh.vertices[j].co
        top_i=len(coords); coords.append((a.x,a.y,cut_wall_height))
        top_j=len(coords); coords.append((b.x,b.y,cut_wall_height))
        faces.append((i,j,top_j,top_i)); inds.append(p.material_index)
    elif p.material_index>=9:
        continue # observed facade detail belongs in the exterior views
    else:
        faces.append(tuple(p.vertices)); inds.append(p.material_index)
cut_mesh=bpy.data.meshes.new("CirclePines_Temporary_RoofOpen_Preview")
cut_mesh.from_pydata(coords,[],faces)
for material in source_mesh.materials: cut_mesh.materials.append(material)
for poly,mi in zip(cut_mesh.polygons,inds): poly.material_index=mi
cut_obj=bpy.data.objects.new("CirclePines_Temporary_RoofOpen_Preview",cut_mesh)
scene.collection.objects.link(cut_obj)
obj.hide_render=True
interior_cam=Vector((-904.2,833.3,0.8))
# A lower but still high cutaway angle shows partitions and furniture in 3D
# while keeping the entire irregular GIS footprint in frame.
cam.location=interior_cam+Vector((normal[0]*36,normal[1]*36,62)); aim(cam,interior_cam)
cam.data.ortho_scale=92
scene.render.filepath=os.path.join(AUDIT,"interior_cutaway_3d.png")
bpy.ops.render.render(write_still=True)
print("rendered 3D roof-open interior",scene.render.filepath)
