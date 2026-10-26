"""Build the Hi Vine (massing_hi_vine_dbdf0c5) library from saved survey/aerial outline and published project references."""
import bpy, math, json
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular' / 'buildings' / 'massing_hi_vine_dbdf0c5.blend'
REVIEW = ROOT / 'audit' / 'massing_hi_vine_dbdf0c5' / 'review'
ID = 'massing_hi_vine_dbdf0c5'
COLLECTION = 'Asset_' + ID
SCENE = 'Building_' + ID
# Structural roof/wall outline traced from the existing asset, independently checked against current ArcGIS World Imagery.
FOOTPRINT = [
(482.216125,-90.053),(494.420,-89.998),(494.437,-92.407),(513.096,-92.296),
(513.325,-130.405),(524.918,-130.927),(525.113,-170.868),(518.820,-171.024),
(518.803,-169.203),(513.681,-169.225),(513.681,-170.369),(506.964,-170.402),
(506.972,-171.290),(500.993,-171.313),(500.993,-170.746),(494.319,-170.757),
(494.319,-169.869),(488.000,-169.880),(487.992,-163.951),(482.530,-163.962),
(482.504,-147.717),(483.963,-147.717),(483.921,-133.714),(482.428,-133.714)]
HEIGHT=19.7  # estimated, six-story reading of official project rendering; no measured elevation found
GROUND=3.8
UPPER=3.18

# Remove all startup objects and build a clean, single-scene library.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c, do_unlink=True)
root=bpy.context.scene.collection
col=bpy.data.collections.new(COLLECTION); root.children.link(col)
scene=bpy.context.scene; scene.name=SCENE; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0

# Material palette: texturing is procedural and packed/self-contained.
def mat(name,color,rough=.78,metal=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
mats=[mat('Warm brick',(.62,.29,.17)),mat('Light masonry',(.79,.75,.65)),mat('Dark metal',(.20,.24,.26),.42,.42),mat('Reflective glazing',(.17,.30,.38),.22,.20),mat('Retail glazing',(.20,.35,.40),.20,.15),mat('Flat roof membrane',(.30,.31,.30))]
verts=[]; faces=[]; face_mats=[]
def face(points,mi):
    inds=[]
    for p in points: inds.append(len(verts)); verts.append(tuple(p))
    faces.append(tuple(inds)); face_mats.append(mi)
def prism(poly,z0,z1,mi_side,mi_top=None):
    n=len(poly); mi_top=mi_side if mi_top is None else mi_top
    face([(x,y,z0) for x,y in poly],mi_side)
    face([(x,y,z1) for x,y in poly],mi_top)
    area=sum(poly[i][0]*poly[(i+1)%n][1]-poly[(i+1)%n][0]*poly[i][1] for i in range(n))
    ccw=area>0
    for i in range(n):
        a=poly[i]; b=poly[(i+1)%n]
        face([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)],mi_side)
    return ccw
ccw=prism(FOOTPRINT,0,HEIGHT,1,5)
# Each outward facade plane gets consistent metal window surrounds and recessed dark glass.
def panel(a,b,t0,t1,z0,z1,outward,offset,mi):
    dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
    nx=(dy/L if ccw else -dy/L); ny=(-dx/L if ccw else dx/L)
    p0=(a[0]+dx*t0+nx*offset,a[1]+dy*t0+ny*offset,z0)
    p1=(a[0]+dx*t1+nx*offset,a[1]+dy*t1+ny*offset,z0)
    p2=(p1[0],p1[1],z1); p3=(p0[0],p0[1],z1)
    face([p0,p1,p2,p3],mi)

def unitbox(center,tangent,normal,width,depth,z0,z1,mi):
    cx,cy=center; tx,ty=tangent; nx,ny=normal; w=width/2; d=depth/2
    poly=[(cx-tx*w-nx*d,cy-ty*w-ny*d),(cx+tx*w-nx*d,cy+ty*w-ny*d),(cx+tx*w+nx*d,cy+ty*w+ny*d),(cx-tx*w+nx*d,cy-ty*w+ny*d)]
    prism(poly,z0,z1,mi,mi)

# Massing shell with flat parapet roof (the aerial and project image show no pitched roof).
# A light concrete/parapet cap distinguishes the roof edge from the dark flat roof membrane.
# Shell stays continuous beneath the evidence-based facade treatment.
for ei,a in enumerate(FOOTPRINT):
    b=FOOTPRINT[(ei+1)%len(FOOTPRINT)]; dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
    if L<2.8: continue
    tx,ty=dx/L,dy/L
    nx,ny=(dy/L,-dx/L) if ccw else (-dy/L,dx/L)
    # Brick pier rhythm with light-masonry panels; alternating warm brick wraps and pale infill.
    bay=2.65; count=max(1,int(L/bay)); step=L/count
    for j in range(count):
        mid=(j+.5)*step
        # thin brick piers provide the characteristic vertical brick rhythm from the KJG project rendering
        pcenter=(a[0]+tx*mid+nx*.035,a[1]+ty*mid+ny*.035)
        width=min(.34,step*.16)
        unitbox(pcenter,(tx,ty),(nx,ny),width,.10,GROUND,HEIGHT-.20,0)
        # level bands
        for z in [GROUND+i*UPPER for i in range(1,5)]:
            panel(a,b,j/count,(j+1)/count,z-.09,z+.08,(nx,ny),.065,2)
        # upper glazing: dark glass centered in each panel; metal surround edges kept visibly narrow
        for k in range(1,6):
            z0=GROUND+(k-1)*UPPER+.63; z1=min(GROUND+(k-1)*UPPER+2.24,HEIGHT-.45)
            avail=max(.6,step-.40); ww=min(1.55,avail*.82)
            center=mid
            tmid=center/L; half=ww/(2*L)
            panel(a,b,tmid-half,tmid+half,z0,z1,(nx,ny),.075,3)
        # street-level glazing storefront, repeated on each face as evidenced for retail wrapped ground floor
        # Panels are intentionally varied to leave masonry columns and service bays visible.
        if j % 3 != 2:
            ww=min(1.90,max(.8,step-.42)); half=ww/(2*L); tmid=(mid/L)
            panel(a,b,tmid-half,tmid+half,.48,3.22,(nx,ny),.085,4)
            # dark metal transom
            panel(a,b,tmid-half,tmid+half,3.18,3.28,(nx,ny),.09,2)

# Strong glazed vertical corner/core bay, a defining feature in the project's published rendering.
# place it on the long east-facing shoulder and return to the short south facade.
for ei,a in enumerate(FOOTPRINT):
    b=FOOTPRINT[(ei+1)%len(FOOTPRINT)]; dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
    if L>35 and abs(dx)<3:
        # Restrained full-height curtain-wall bay at one corner, rather than glazing the full elevation.
        t0=.03; t1=.27
        panel(a,b,t0,t1,GROUND,HEIGHT-.5,(dy/L if ccw else -dy/L,-dx/L if ccw else dx/L),.13,3)
        for z in [GROUND+i*UPPER for i in range(1,5)]:
            panel(a,b,t0,t1,z-.08,z+.10,(dy/L if ccw else -dy/L,-dx/L if ccw else dx/L),.15,2)

# South-street balconies on two long street-facing runs; balcony locations are design cues,
# not measured unit-by-unit. Use subtle projecting slabs and simple metal rails.
for ei,a in enumerate(FOOTPRINT):
    b=FOOTPRINT[(ei+1)%len(FOOTPRINT)]; dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
    if L>15 and abs(dy)<1.2:
        tx,ty=dx/L,dy/L; nx,ny=(dy/L,-dx/L) if ccw else (-dy/L,dx/L)
        for k in range(1,6):
            z=GROUND+(k-1)*UPPER+.12
            for mid in [L*.28,L*.52,L*.76]:
                # small box balcony slab
                unitbox((a[0]+tx*mid+nx*.65,a[1]+ty*mid+ny*.65),(tx,ty),(nx,ny),1.85,1.25,z-.08,z+.04,1)
                # front rail glass panel
                panel(a,b,(mid-.91)/L,(mid+.91)/L,z+.22,z+.82,(nx,ny),1.30,2)

mesh=bpy.data.meshes.new('HiVine_footprint_shell_facade_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('Hi Vine',mesh); col.objects.link(obj)
for m in mats: mesh.materials.append(m)
for p,mi in zip(mesh.polygons,face_mats): p.material_index=mi
obj['stable_id']=ID; obj['building_type']='six-storey mixed-use apartment and retail; height estimated'; obj['source_footprint']='existing structural outline checked against ArcGIS World Imagery; Indiana LiDAR footprint layer retained as broad context only'; obj['roof']='flat'; obj['height_m_estimate']=HEIGHT; obj['storey_count_estimate']=6
# Recalculate normals/triangulate ngons on shell; retain flat planar walls.
for o in bpy.context.selected_objects: o.select_set(False)
obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
# Clean scene: the collection intentionally contains one direct-coordinate mesh and no linked assets.
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
# Create review renders with temporary camera/lights, then remove them without saving them into the library.
world=bpy.data.worlds.new('Review World') if not bpy.data.worlds else bpy.data.worlds[0]; scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.78,.86,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
target=Vector((503.5,-130.5,9.3))
camd=bpy.data.cameras.new('review camera'); cam=bpy.data.objects.new('review camera',camd); scene.collection.objects.link(cam)
cam.location=(target.x-47,target.y-57,37); aim(cam,target); camd.type='ORTHO'; camd.ortho_scale=100; scene.camera=cam
ld=bpy.data.lights.new('review key','AREA'); lo=bpy.data.objects.new('review key',ld); scene.collection.objects.link(lo); lo.location=(target.x-18,target.y-28,43); ld.energy=12000; ld.shape='DISK'; ld.size=32; aim(lo,target)
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(REVIEW/'hi_vine_hero_r1.png'); bpy.ops.render.render(write_still=True)
# Elevated orthographic review view from southeast.
cam.location=(target.x+72,target.y-4,76); aim(cam,target); camd.ortho_scale=116; scene.render.filepath=str(REVIEW/'hi_vine_aerial_r1.png'); bpy.ops.render.render(write_still=True)

