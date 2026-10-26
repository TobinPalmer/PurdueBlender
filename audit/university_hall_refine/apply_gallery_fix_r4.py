"""Correct the gallery aperture to its documented overall dimensions."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular'/'buildings'/'university_hall.blend'
col=bpy.data.collections['Asset_university_hall']
parent=bpy.data.objects['AssetRoot_university_hall']
cx=-7.515

def box(name,loc,dims,material,bevel=0.02):
    hx,hy,hz=[d/2 for d in dims]
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.location=loc;ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted()
    if bevel:
        b=ob.modifiers.new('Soft architectural edges','BEVEL');b.width=bevel;b.segments=2
        ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

for ob in list(bpy.data.objects):
    if ob.name.startswith(('UNIV_R2_UNIV_Interior_Floor_First_GalleryRing_',
                           'UNIV_R2_UNIV_Interior_Floor_Second_GalleryRing_',
                           'UNIV_R2_Gallery_LibraryFeatureWall','UNIV_R2_Gallery_BookBay_',
                           'UNIV_R2_Gallery_Book_','UNIV_R2_Gallery_Overlook_FeatureWall',
                           'UNIV_R2_Gallery_InterpretivePlaque','UNIV_R2_Overlook_')):
        bpy.data.objects.remove(ob,do_unlink=True)

floor=bpy.data.materials['Univ_Parquet_Wood']
wood=bpy.data.materials['Univ_Dark_Walnut']
iron=bpy.data.materials['UNIV_R2_Painted_Iron']
plaster=bpy.data.materials['Univ_Interior_Plaster']
stone=bpy.data.materials['Univ_Bedford_Limestone']
burgundy=bpy.data.materials['Univ_Burgundy_Leather']
gold=bpy.data.materials['Univ_Gold_Accent']

# Overall openings are 7.6 x 12.0 m on the first-floor gallery ring, and
# 6.6 x 10.8 m at the upper overlook. Half-spans are used for ring geometry.
for name,z,t,hx,hy in (('First',4.2,0.30,3.8,6.0),('Second',8.4,0.30,3.3,5.4)):
    x0,x1=cx-10.36,cx+10.36;y0,y1=-21.02,21.02
    slabs=[((x0+cx-hx)/2,0,cx-hx-x0,y1-y0),((cx+hx+x1)/2,0,x1-cx-hx,y1-y0),
           (cx,(y0-hy)/2,2*hx,-hy-y0),(cx,(hy+y1)/2,2*hx,y1-hy)]
    for i,(x,y,dx,dy) in enumerate(slabs):
        if dx>0.1 and dy>0.1:
            box(f'UNIV_R4_GalleryFloor_{name}_{i}',(x,y,z),(dx,dy,t),floor,0.025)

# North-end library feature wall and book bays face inward toward the gallery.
box('UNIV_R4_Gallery_LibraryFeatureWall',(cx,6.88,4.4),(7.0,0.3,7.4),wood,0.04)
for i in range(9):
    x=cx-3.0+i*0.75
    box(f'UNIV_R4_Gallery_BookBay_{i}',(x,6.67,5.0),(0.56,0.12,5.3),wood,0.02)
    for row in range(8):
        box(f'UNIV_R4_Gallery_Book_{i}_{row}',(x,6.52,3.0+row*0.62),(0.44,0.12,0.43),burgundy if (i+row)%3 else gold,0.01)
box('UNIV_R4_Gallery_InterpretivePlaque_Frame',(cx,6.48,6.25),(2.2,0.10,1.0),stone,0.04)
box('UNIV_R4_Gallery_InterpretivePlaque',(cx,6.41,6.25),(1.95,0.045,0.72),gold,0.02)

# Upper-floor academy overlook guards track the actual opening perimeter.
for i in range(14):
    x=cx-3.2+i*(6.4/13)
    box(f'UNIV_R4_Overlook_South_Baluster_{i}',(x,-5.55,8.95),(0.055,0.055,1.05),iron,0.015)
for i in range(13):
    y=-5.4+i*0.9
    box(f'UNIV_R4_Overlook_East_Baluster_{i}',(cx+3.25,y,8.95),(0.055,0.055,1.05),iron,0.015)
box('UNIV_R4_Overlook_South_Handrail',(cx,-5.55,9.5),(6.5,0.11,0.11),wood,0.03)
box('UNIV_R4_Overlook_East_Handrail',(cx+3.25,0,9.5),(0.11,10.9,0.11),wood,0.03)

bpy.ops.wm.save_as_mainfile(filepath=str(asset))
print('GALLERY_OPENINGS',{'first_m':[7.6,12.0],'second_m':[6.6,10.8]})
print('ROOT_IDENTITY',list(parent.location),list(parent.rotation_euler),list(parent.scale),'objects',len(col.all_objects))
