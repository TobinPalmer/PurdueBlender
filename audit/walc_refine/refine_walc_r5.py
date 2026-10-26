"""WALC R5: image-led roof/eave silhouette and differentiated entry pavilion."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/walc.blend'
expected='01f0ba7bd8fbdee2da267e85c8d35e327cf891d68a05cbeea5876b5b692b5dd4'
actual=hashlib.sha256(ASSET.read_bytes()).hexdigest()
allowed={expected,'f55f9e8be9a0e03bbddada454dd5f2fddaa6fc6170c41ef925ef534e53daa43c',
         'df3adf3e1574a2b346aa6645a6daf1127115d4856d6158f354cf82d7cab0a181'}
if actual not in allowed:
    raise RuntimeError(f'Expected exact R4 or preliminary R5 asset; got {actual}')
asset=bpy.data.collections['Asset_walc']
root=bpy.data.objects['AssetRoot_walc']
assert tuple(root.location)==(0,0,0) and tuple(root.rotation_euler)==(0,0,0) and tuple(root.scale)==(1,1,1)

def remove(name):
    obj=bpy.data.objects.get(name)
    if obj: bpy.data.objects.remove(obj,do_unlink=True)
    me=bpy.data.meshes.get(name+'_Mesh')
    if me and me.users==0: bpy.data.meshes.remove(me)

for name in ('WALC_R5_Roof_West_Hip','WALC_R5_Roof_East_Hip','WALC_R5_Roof_Central_Canopy',
             'WALC_R5_Roof_South_Transition','WALC_R5_Roof_North_Transition',
             'WALC_R5_Central_Glazed_Pavilion','WALC_R5_Pavilion_Frames','WALC_R5_Eave_Undersides',
             'WALC_R5_Eave_Undersides_West_Hip','WALC_R5_Eave_Undersides_East_Hip',
             'WALC_R5_Eave_Undersides_South_Transition','WALC_R5_Eave_Undersides_North_Transition',
             'WALC_R5_Central_Roof_Monitor','WALC_R5_Monitor_Frames','WALC_R5_Roof_Seams_1','WALC_R5_Roof_Seams_2'):
    remove(name)

roof=bpy.data.materials.get('WALC_R5_Standing_Seam_Roof') or bpy.data.materials.new('WALC_R5_Standing_Seam_Roof')
roof.diffuse_color=(0.19,0.22,0.23,1)
roof.use_nodes=True
bs=roof.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(0.075,0.095,0.105,1)
bs.inputs['Metallic'].default_value=.48
bs.inputs['Roughness'].default_value=.36
eave=bpy.data.materials.get('WALC_R5_Eave_Dark') or bpy.data.materials.new('WALC_R5_Eave_Dark')
eave.diffuse_color=(0.065,0.075,0.082,1)
glass=bpy.data.materials['WALC_Reference_Glass']
bronze=bpy.data.materials.get('Bronze.009')

def make_mesh(name, verts, faces, mat):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); asset.objects.link(ob); me.materials.append(mat)
    ob['evidence_note']='Approximate architectural interpretation of Purdue 2018 official exterior photo; roof pitch, dimensions and framing are image-estimated, not measured from drawings.'
    return ob

def hip_roof(name,x0,x1,y0,y1,eave_z=17.0,ridge_z=18.05,ridge_end=0.76,overhang=.75):
    # Shallow hip plane: long ridge runs along Y, with short hip ends and generous eaves.
    x0-=overhang; x1+=overhang; y0-=overhang; y1+=overhang
    xm=(x0+x1)/2; ya=y0+ridge_end; yb=y1-ridge_end
    verts=[(x0,y0,eave_z),(x1,y0,eave_z),(x1,y1,eave_z),(x0,y1,eave_z),
           (xm,ya,ridge_z),(xm,yb,ridge_z)]
    top=[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)]
    # Add a dark continuous eave fascia, with top planes and underside below.
    underz=eave_z-.38
    verts += [(x0,y0,underz),(x1,y0,underz),(x1,y1,underz),(x0,y1,underz)]
    faces=list(top)+[(0,6,7,1),(1,7,8,2),(2,8,9,3),(3,9,6,0)]
    ob=make_mesh(name,verts,faces,roof)
    # Dark soffit plane catches shadow below the eaves.
    soffit=[(x0,y0,underz),(x1,y0,underz),(x1,y1,underz),(x0,y1,underz)]
    make_mesh(name.replace('Roof','Eave_Undersides'),soffit,[(0,1,2,3)],eave)
    return ob

# Photo evidence shows broad, shallow sloped roof planes, deep dark eaves and
# distinct lower roof transitions. These separate masses are image-estimated.
hip_roof('WALC_R5_Roof_West_Hip',-16.5,1.4,-44.0,44.0,eave_z=17.03,ridge_z=18.22,ridge_end=5.3)
hip_roof('WALC_R5_Roof_East_Hip',20.3,42.0,-38.5,38.5,eave_z=16.92,ridge_z=17.82,ridge_end=4.2)
hip_roof('WALC_R5_Roof_South_Transition',1.6,20.4,-39.0,-21.5,eave_z=16.96,ridge_z=17.70,ridge_end=2.1)
hip_roof('WALC_R5_Roof_North_Transition',1.6,20.4,21.5,38.5,eave_z=16.96,ridge_z=17.70,ridge_end=2.1)

# The photo shows a tall glazed entry pavilion inset between masonry wings.
# Place it at the south-frontage entry break (the existing GIS wall run is only
# a plan locator), with a lower roof transition. Dimensions are image estimates.
px0,px1=22.0,36.2; py=-39.78; pz0=1.0; pz1=14.3
pane_verts=[]; pane_faces=[]
for x in (px0,px1):
    pane_verts.extend([(x,py-.16,pz0),(x,py-.16,pz1)])
pane_faces=[(0,1,3,2)]
make_mesh('WALC_R5_Central_Glazed_Pavilion',pane_verts,pane_faces,glass)
# Tall bronze divisions spaced as broad vertical bays, with a strong transom.
frameverts=[]; framefaces=[]
def add_box(x0,y0,z0,x1,y1,z1):
    b=len(frameverts); frameverts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
        (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
    framefaces.extend([tuple(b+i for i in f) for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
for i in range(11):
    x=px0+(px1-px0)*i/10
    add_box(x-.055,py-.30,1.0,x+.055,py-.06,14.2)
add_box(px0,py-.30,9.2,px1,py-.06,9.34)
if bronze: make_mesh('WALC_R5_Pavilion_Frames',frameverts,framefaces,bronze)

# Low canopy with gentle pitch, extended past the glazed face and dark soffit.
cv=[(21.2,-40.65,14.55),(37.0,-40.65,14.55),(37.0,-38.25,15.0),(21.2,-38.25,15.0),
    (21.2,-40.65,14.20),(37.0,-40.65,14.20),(37.0,-38.25,14.65),(21.2,-38.25,14.65)]
cf=[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0),(4,7,6,5)]
make_mesh('WALC_R5_Roof_Central_Canopy',cv,cf,roof)

# Recast the existing atrium roof inset as glazing and raise a narrow monitor
# above it. The floor-plan skylight suggests the location; exact dimensions are
# image-led estimates because no registered roof plan/elevation was found.
panels=bpy.data.objects.get('Atrium roof panels')
if panels:
    panels.data.materials.clear(); panels.data.materials.append(bpy.data.materials['WALC_Roof_Panels_White'])
    panels.data.materials[0]=glass
    glass.diffuse_color=(0.15,0.24,0.29,1)
mx0,mx1,my0,my1=6.5,15.5,-18.5,18.5
monitor=[(mx0,my0,17.08),(mx1,my0,17.08),(mx1,my1,17.08),(mx0,my1,17.08),
         (mx0,my0,18.0),(mx1,my0,18.0),(mx1,my1,18.0),(mx0,my1,18.0)]
monitorfaces=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
make_mesh('WALC_R5_Central_Roof_Monitor',monitor,monitorfaces,glass)
if bronze:
    ribs=[]; ribfaces=[]
    for i in range(9):
        x=mx0+(mx1-mx0)*i/8
        b=len(ribs); w=.045
        ribs.extend([(x-w,my0,17.08),(x+w,my0,17.08),(x+w,my0,18.0),(x-w,my0,18.0),
                     (x-w,my1,17.08),(x+w,my1,17.08),(x+w,my1,18.0),(x-w,my1,18.0)])
        ribfaces.extend([tuple(b+j for j in f) for f in ((0,1,2,3),(4,7,6,5),(0,3,7,4),(1,5,6,2))])
    make_mesh('WALC_R5_Monitor_Frames',ribs,ribfaces,bronze)

# Keep the GIS roof ring as an unchanged plan trace for audit, but remove its
# massive flat gray face from presentation. It is not evidence for roof form.
trace=bpy.data.objects.get('WALC_Official_906_Roof')
if trace:
    trace.hide_render=True
    trace.hide_set(True)
    trace['evidence_note']='Unchanged GIS-derived roof/plan outline retained for reference only; hidden from presentation. It does not establish roof form or height.'

# Add small, repeated standing-seam ribs to break up broad roof planes at oblique scale.
# Ribs follow the long Y ridges, and remain subordinate to the roof silhouette.
ribmat=eave
for wi,(x0,x1,y0,y1,z) in enumerate(((-17.25,2.15,-44.75,44.75,17.05),(19.55,42.75,-39.25,39.25,16.94))):
    verts=[]; faces=[]
    for j in range(1,8):
        x=x0+(x1-x0)*j/8
        b=len(verts); w=.035; h=.035
        verts.extend([(x-w,y0,z+.015),(x+w,y0,z+.015),(x+w,y1,z+.015),(x-w,y1,z+.015),
                      (x-w,y0,z+h),(x+w,y0,z+h),(x+w,y1,z+h),(x-w,y1,z+h)])
        faces.extend([tuple(b+i for i in f) for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
    make_mesh(f'WALC_R5_Roof_Seams_{wi+1}',verts,faces,ribmat)

foliage=next((lib for lib in bpy.data.libraries if 'engineering_foliage_library.blend' in lib.filepath),None)
if foliage: foliage.filepath='//../site/foliage_library/engineering_foliage_library.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET),compress=True)
print('R5 saved SHA-256',hashlib.sha256(ASSET.read_bytes()).hexdigest())
