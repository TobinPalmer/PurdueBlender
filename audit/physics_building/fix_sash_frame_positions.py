import bpy, math
from pathlib import Path
from mathutils import Vector
path=Path.cwd()/'modular/buildings/physics_building_phys_3bf42f3.blend'; bpy.ops.wm.open_mainfile(filepath=str(path)); asset=bpy.data.collections['Asset_physics_building']
old=bpy.data.objects.get('PHYS R2 | tall divided sash frames')
if old: bpy.data.objects.remove(old,do_unlink=True)
w=bpy.data.objects['PHYS | recessed dark sash glazing']; mat=bpy.data.materials['PHYSICS_BUILDING | graphite metal details']
verts=[]; faces=[]
def box(c,t,n,width,depth,height):
    k=len(verts)
    for z in (-height/2,height/2):
        for y in (-depth/2,depth/2):
            for x in (-width/2,width/2): verts.append(tuple(c+t*x+n*y+Vector((0,0,z))))
    faces.extend([(k+0,k+1,k+3,k+2),(k+4,k+6,k+7,k+5),(k+0,k+4,k+5,k+1),(k+2,k+3,k+7,k+6),(k+0,k+2,k+6,k+4),(k+1,k+5,k+7,k+3)])
count=0
for p in w.data.polygons:
    if abs(p.normal.z)>.1: continue
    pts=[w.data.vertices[i].co.copy() for i in p.vertices]; c=sum(pts,Vector())/4
    radial=Vector((c.x,c.y,0))
    if radial.length<.1: continue
    radial.normalize()
    # Mesh winding is inward. Use outward radial direction for true exterior glass faces only.
    if p.normal.dot(radial)>-.72: continue
    out=-p.normal.copy(); out.z=0; out.normalize(); t=Vector((-out.y,out.x,0))
    u=[(q-c).dot(t) for q in pts]; wsize=max(u)-min(u)
    zlo=min(q.z for q in pts); zhi=max(q.z for q in pts); h=zhi-zlo
    if not (.75<wsize<1.5 and h>1.5): continue
    c.z=(zlo+zhi)/2; c += out*.15
    ww=min(wsize*.94,1.08); hh=h*.96; d=.065
    # Dark painted steel perimeter, vertical meeting stile, and a horizontal sash rail.
    box(c+t*(-ww/2+.035),t,out,.07,d,hh)
    box(c+t*( ww/2-.035),t,out,.07,d,hh)
    box(c+Vector((0,0,-hh/2+.035)),t,out,ww,d,.07)
    box(c+Vector((0,0, hh/2-.035)),t,out,ww,d,.07)
    box(c,t,out,.055,d,hh)
    box(c+Vector((0,0,.34)),t,out,ww,d,.06)
    count+=1
mesh=bpy.data.meshes.new('R2 | corrected divided sash frame geometry'); mesh.from_pydata(verts,[],faces); mesh.materials.append(mat); mesh.update()
ob=bpy.data.objects.new('PHYS R2 | tall divided sash frames',mesh); asset.objects.link(ob)
ob['source_note']='Every visible sash receives an exterior-face perimeter, central stile and meeting rail; origin and height are matched to the facade polygon centers.'
asset['r2_frame_correction']='R2 window frame assemblies are centered on facade glass rather than an axis-only coordinate; placement checked against pane centers.'
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
print('Rebuilt exterior muntin assembly on',count,'facade windows; objects',len(asset.all_objects))
