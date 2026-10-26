"""Rebuild Henni's Hair Shop from its named OSM footprint and storefront evidence."""
import bpy, math
from mathutils import Vector, Matrix

ASSET_ID='massing_henni_s_hair_shop_57f732b'
ASSET_COLLECTION='Asset_'+ASSET_ID
SCENE_NAME='Building_'+ASSET_ID
OUT=bpy.path.abspath('//massing_henni_s_hair_shop_57f732b.blend')
# Campus coordinates X east, Y north; transformed directly from way 116427257.
RING=[(462.379,-309.491),(474.176,-309.580),(474.219,-303.317),(462.489,-303.017)]
HEIGHT=8.35  # estimated from the visible two-level storefront; no survey found
LOWER=3.85

def mat(name,color,rough=0.7):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.roughness=rough
    return m

BRICK=mat('Cool gray brick storefront',(.37,.38,.37))
SIDING=mat('Warm white horizontal siding',(.79,.76,.68))
GLASS=mat('Blue gray storefront glazing',(.09,.19,.23),.25)
FRAME=mat('Dark metal window frames',(.075,.085,.09),.45)
AWNING=mat('Black metal shop awning',(.035,.04,.045),.4)
ROOF=mat('Dark flat roof',(.13,.14,.15),.55)
SIGN=mat('Cream shop sign panel',(.90,.87,.78),.6)
WHITE=mat('Light sign lettering',(.96,.94,.86),.35)
SEAM=mat('Siding grooves',(.68,.66,.60),.8)

def get_collection(scene):
    c=bpy.data.collections.get(ASSET_COLLECTION)
    if c is None: c=bpy.data.collections.new(ASSET_COLLECTION)
    if c.name not in [x.name for x in scene.collection.children]: scene.collection.children.link(c)
    for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
    return c

def add_mesh(name,verts,faces,material,assignments=None):
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    obj=bpy.data.objects.new(name,mesh); target.objects.link(obj)
    if assignments:
        for p,i in zip(mesh.polygons,assignments): p.material_index=i
    return obj

def solid_ring(name,ring,z0,z1,material,roofmat=None):
    n=len(ring); verts=[(x,y,z) for z in (z0,z1) for x,y in ring]
    faces=[]; assign=[]
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n)); assign.append(0)
    faces.append(tuple(range(n,2*n))); assign.append(1 if roofmat else 0)
    faces.append(tuple(reversed(range(n)))); assign.append(0)
    if roofmat:
        mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.materials.append(roofmat); mesh.update()
        obj=bpy.data.objects.new(name,mesh); target.objects.link(obj)
        for p,i in zip(mesh.polygons,assign): p.material_index=i
        return obj
    return add_mesh(name,verts,faces,material,assign)

def wall_box(name,center,tangent,normal,width,depth,height,material):
    cx,cy,cz=center; tx,ty=tangent; nx,ny=normal
    verts=[]
    for dz in (-height/2,height/2):
        for dn in (-depth/2,depth/2):
            for dt in (-width/2,width/2):
                verts.append((cx+tx*dt+nx*dn,cy+ty*dt+ny*dn,cz+dz))
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return add_mesh(name,verts,faces,material)

def text_on_east_face(body,center_y,z,size,material,name,front_offset):
    curve=bpy.data.curves.new(name,'FONT'); curve.body=body; curve.size=size; curve.extrude=.012; curve.align_x='CENTER'; curve.align_y='CENTER'
    obj=bpy.data.objects.new(name,curve); target.objects.link(obj)
    # local X runs north, local Y up, local Z points east toward the viewer
    obj.rotation_euler=Matrix(((0,0,1),(1,0,0),(0,1,0))).to_4x4().to_euler()
    obj.location=(max(x for x,y in RING)+front_offset,center_y,z)
    bpy.context.view_layer.objects.active=obj; obj.select_set(True); bpy.ops.object.convert(target='MESH'); obj.select_set(False)
    obj.data.materials.append(material); return obj

def build_shell():
    # Two separate floor volumes retain legible masonry/siding material breaks.
    solid_ring("Henni's Hair Shop | ground-floor shell",RING,0,LOWER,BRICK)
    solid_ring("Henni's Hair Shop | second-floor shell",RING,LOWER,HEIGHT-.18,SIDING,ROOF)

def facade_details():
    p0,p1,p2,p3=RING
    # OSM ring is counter-clockwise; the east-facing short facade is p1-p2,
    # nearest the mapped Northwestern Avenue alignment.
    edges=[(p1,p2,True),(p0,p1,True),(p2,p3,False),(p3,p0,False)]
    for a,b,visible in edges:
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy); tx,ty=dx/length,dy/length; nx,ny=ty,-tx
        if visible:
            # Upper-story horizontal lap siding seams, shown on the photo-visible faces.
            for z in [4.18+i*.34 for i in range(12) if 4.18+i*.34<8.15]:
                wall_box('Horizontal siding reveal',((a[0]+b[0])/2,(a[1]+b[1])/2,z),(tx,ty),(nx,ny),length,.035,.035,SEAM)
        if (a,b)==(p1,p2):
            # Street-facing shopfront: two display windows and centered door.
            for s,w in ((1.15,1.72),(5.10,1.72)):
                cx=a[0]+tx*s; cy=a[1]+ty*s
                wall_box('Storefront display glazing',(cx+nx*.025,cy+ny*.025,1.83),(tx,ty),(nx,ny),w,.055,2.25,GLASS)
                for side in (-1,1): wall_box('Storefront mullion',(cx+tx*side*(w/2-.035)+nx*.06,cy+ty*side*(w/2-.035)+ny*.06,1.83),(tx,ty),(nx,ny),.07,.10,2.38,FRAME)
                for z in (.67,2.98): wall_box('Storefront glazing rail',(cx+nx*.06,cy+ny*.06,z),(tx,ty),(nx,ny),w,.10,.07,FRAME)
            # Recessed entry door with tall glass panel.
            s=3.15; cx=a[0]+tx*s; cy=a[1]+ty*s
            wall_box('Shop entrance door',(cx+nx*.025,cy+ny*.025,1.35),(tx,ty),(nx,ny),.93,.06,2.7,FRAME)
            wall_box('Shop entrance door glass',(cx+nx*.065,cy+ny*.065,1.55),(tx,ty),(nx,ny),.70,.035,2.15,GLASS)
            # Upper-story paired sash windows.
            for s in (1.55,4.65):
                cx=a[0]+tx*s; cy=a[1]+ty*s
                wall_box('Second-floor sash window',(cx+nx*.025,cy+ny*.025,6.05),(tx,ty),(nx,ny),1.22,.05,1.40,GLASS)
                for side in (-1,1): wall_box('Second-floor window jamb',(cx+tx*side*.65+nx*.055,cy+ty*side*.65+ny*.055,6.05),(tx,ty),(nx,ny),.07,.10,1.52,FRAME)
                wall_box('Second-floor window sill',(cx+nx*.055,cy+ny*.055,5.31),(tx,ty),(nx,ny),1.36,.10,.09,FRAME)
        elif (a,b)==(p0,p1):
            # Glazing wraps the visible return beside the corner entry.
            for s in (2.2,5.0,7.9,10.4):
                cx=a[0]+tx*s; cy=a[1]+ty*s
                wall_box('Side display window',(cx+nx*.025,cy+ny*.025,1.82),(tx,ty),(nx,ny),1.48,.055,2.18,GLASS)
            for s in (2.8,6.0,9.2):
                cx=a[0]+tx*s; cy=a[1]+ty*s
                wall_box('Side upper window',(cx+nx*.025,cy+ny*.025,6.05),(tx,ty),(nx,ny),1.10,.05,1.35,GLASS)

def add_awning_sign_and_roof():
    p0,p1,p2,p3=RING; cx=(p0[0]+p1[0])/2; cy=(p1[1]+p2[1])/2; xmax=max(x for x,y in RING)
    # Black awning wraps the visible east storefront and south return.
    wall_box('East storefront awning', (xmax+.26,cy,3.68),(0,1),(1,0),6.32,.65,.36,AWNING)
    wall_box('South return awning',(cx,p0[1]-.26,3.68),(1,0),(0,-1),11.9,.65,.36,AWNING)
    # Hanging cream sign observed above the awning, with actual shop lettering.
    sign_y=RING[1][1]+.48
    wall_box('Projecting Henni sign panel',(xmax+.12,sign_y,6.83),(0,1),(1,0),1.50,.18,.92,SIGN)
    text_on_east_face("henni's",sign_y,6.83,.36,FRAME,'Henni sign lettering',.235)
    text_on_east_face("henni's hairshop",cy,3.68,.23,WHITE,'Awning lettering',.60)
    # Flat parapet roof, with a slight eave beyond the OSM structural outline.
    n=len(RING); mx=sum(x for x,y in RING)/n; my=sum(y for x,y in RING)/n
    roof_ring=[(mx+(x-mx)*1.018,my+(y-my)*1.018) for x,y in RING]
    solid_ring("Henni's Hair Shop | roof cap",roof_ring,HEIGHT-.16,HEIGHT+.03,ROOF)

def setup(scene):
    scene.render.engine='BLENDER_WORKBENCH'; scene.render.resolution_x=1280; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'; scene.render.film_transparent=False
    scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='BOTH'; scene.display.shading.show_shadows=True; scene.display.shading.studio_light='paint.sl'
    scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'
    center=Vector((468.30,-306.30,4.1))
    for name in ('Review camera','Review softbox'):
        old=bpy.data.objects.get(name)
        if old: bpy.data.objects.remove(old,do_unlink=True)
    cd=bpy.data.cameras.new('Review camera'); cam=bpy.data.objects.new('Review camera',cd); scene.collection.objects.link(cam)
    cam.location=center+Vector((17,-21,13)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cd.lens=54; scene.camera=cam
    scene.render.filepath=bpy.path.abspath('//../../audit/massing_henni_s_hair_shop_57f732b/renders/henni_hair_shop_facade.png')

def main():
    global target
    scene=bpy.data.scenes.get(SCENE_NAME) or bpy.data.scenes.new(SCENE_NAME); bpy.context.window.scene=scene
    target=get_collection(scene)
    for c in list(scene.collection.children):
        if c.name!=target.name: scene.collection.children.unlink(c)
    build_shell(); facade_details(); add_awning_sign_and_roof(); setup(scene)
    bpy.ops.object.select_all(action='DESELECT')
    objs=list(target.objects)
    for o in objs: o.select_set(True)
    shell=bpy.data.objects.get("Henni's Hair Shop | ground-floor shell"); bpy.context.view_layer.objects.active=shell
    bpy.ops.object.join(); shell.name="Henni's Hair Shop"
    # The source massing file carried unused brick-texture image datablocks.
    # Keep only the new palette materials and strip unused image references.
    used=set(shell.data.materials)
    for m in list(bpy.data.materials):
        if m not in used: bpy.data.materials.remove(m)
    for image in list(bpy.data.images):
        bpy.data.images.remove(image)
    bpy.ops.wm.save_as_mainfile(filepath=OUT); bpy.ops.render.render(write_still=True)

if __name__=='__main__': main()
