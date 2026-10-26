"""R6: strengthen the physical stair-to-gallery landing overlap."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular'/'buildings'/'university_hall.blend'
col=bpy.data.collections['Asset_university_hall']
parent=bpy.data.objects['AssetRoot_university_hall']

def delete(name):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)

def box(name,loc,dims,material):
    hx,hy,hz=[v/2 for v in dims]
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.location=loc;ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted()
    bevel=ob.modifiers.new('Landing edge softness','BEVEL');bevel.width=0.025;bevel.segments=2
    ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

delete('UNIV_R4_StairLanding_First');delete('UNIV_R4_StairLanding_Second')
delete('UNIV_R6_StairLanding_First');delete('UNIV_R6_StairLanding_Second')
parquet=bpy.data.materials['Univ_Parquet_Wood']
cx=-7.515
# Both flights already meet the gallery elevations. The longer platforms add
# reliable tread overlap; exact egress/landing dimensions remain schematic.
box('UNIV_R6_StairLanding_First',(cx-5.8,-12.48,4.27),(4.7,2.35,0.16),parquet)
box('UNIV_R6_StairLanding_Second',(cx-5.8,-20.14,8.47),(4.7,2.75,0.16),parquet)
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
print('SAVED_R6',asset,'OBJECTS',len(col.all_objects))
print('ROOT_IDENTITY',list(parent.location),list(parent.rotation_euler),list(parent.scale))
print('LANDING_DIMS_M',{'first':[4.7,2.35,0.16],'second':[4.7,2.75,0.16]})
