import bpy, math, json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
asset=P/'modular/buildings/class_of_1950.blend'
c=bpy.data.collections['Asset_class_of_1950']
cream=bpy.data.materials.get('CL50_Photographic_Cream_Textured_Masonry') or bpy.data.materials.get('CL50_Finish_Limestone')
if not cream: raise RuntimeError('Required limestone material missing')
# Photo-backed arcade corrections, using the Purdue Libraries exterior reference.
# The photo shows brick shafts with pale stone footings and broad capitals, and a continuous light soffit band.
ring=[(-30.317,-13.17),(-25,-15.5),(-18,-17.5),(-9,-18.3),(0,-17.3),(8,-14.7),(12.9,-13.25)]
for i,p in enumerate(ring):
    col=bpy.data.objects[f'CL50_New_RoundBrickColumn{i}']
    col.scale.x=col.scale.y=1.20
    cap=bpy.data.objects[f'CL50_New_ColumnCapital{i}']
    cap.scale.x=1.25; cap.scale.y=1.22; cap.scale.z=1.50
    cap.location.z=5.76
    # Light stone plinth at the bottom of each brick shaft, matching visible reference proportions.
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=.62, depth=1.05, location=(p[0],p[1],.675))
    base=bpy.context.object; base.name=f'CL50_PhotoRef_LimestoneColumnBase_{i}'
    for co in list(base.users_collection): co.objects.unlink(base)
    c.objects.link(base); base.data.materials.append(cream)
    # Small bevel gives the stone base a dressed edge without changing the footprint.
    bevel=base.modifiers.new('Dressed limestone arris','BEVEL'); bevel.width=.045; bevel.segments=2
    base.modifiers.new('Weighted stone normals','WEIGHTED_NORMAL')
# Segmented curved fascia/soffit, supported by and aligned to the documented column arc.
# Height is a visual estimate from the archive photograph, not a survey measurement.
for i,(a,b) in enumerate(zip(ring,ring[1:])):
    dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    bpy.ops.mesh.primitive_cube_add(size=1, location=((a[0]+b[0])/2,(a[1]+b[1])/2,6.08))
    beam=bpy.context.object; beam.name=f'CL50_PhotoRef_Curved_Limestone_Soffit_{i}'
    beam.dimensions=(length+.18,1.22,.48); beam.rotation_euler.z=math.atan2(dy,dx)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for co in list(beam.users_collection): co.objects.unlink(beam)
    c.objects.link(beam); beam.data.materials.append(cream)
    bevel=beam.modifiers.new('Soft stone arris','BEVEL'); bevel.width=.035; bevel.segments=2
    beam.modifiers.new('Weighted stone normals','WEIGHTED_NORMAL')
# The current Purdue admissions listing gives CL50's preferred capacity as 470 seats.
# Preserve the 20-row platform geometry and remove ten edge seats, leaving 470 modeled seats.
removed=[]
for row in range(10):
    side='-1' if row%2==0 else '1'
    name=f'CL50_New_Seat_{row:02d}_{side}_11'
    obj=bpy.data.objects.get(name)
    back=bpy.data.objects.get(name.replace('Seat_','Back_'))
    if not obj or not back: raise RuntimeError(f'Missing expected edge seat pair: {name}')
    for x in (obj,back):
        for co in list(x.users_collection): co.objects.unlink(x)
        bpy.data.objects.remove(x, do_unlink=True)
    removed.append(name)
seat_count=sum(1 for o in c.all_objects if o.type=='MESH' and 'CL50_New_Seat_' in o.name)
if seat_count!=470: raise RuntimeError(f'Expected 470 auditorium seat meshes; got {seat_count}')
c['photo_reference_updates']='Purdue Libraries archive photo qualitative match: larger brick columns, pale stone footings/capitals and continuous curved soffit; all vertical dimensions remain estimated.'
c['auditorium_seat_count']=seat_count
c['capacity_reference']='Purdue Admissions, current room listing: CL50 preferred capacity 470; seat count modeled to match listing.'
c['placement_changed']=False
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
Path(P/'audit/batch4_cl50/changes.json').write_text(json.dumps({'asset':str(asset),'placement':'FID230/local placement unchanged','modified':['increased brick column shaft diameter 20%','added pale dressed limestone column bases','enlarged capitals','added segmented curved pale soffit supported by the observed column arcade','adjusted modeled auditorium seat count to current published 470 capacity'],'removed_seat_pairs':removed,'modeled_seat_count':seat_count,'uncertain':['exact plan registration','all vertical dimensions','soffit/column dimensions are image-based estimates','roof/penthouse dimensions','current photo conditions'],'sources':['https://collections.lib.purdue.edu/campus/images/buildings/195-class-of-1950-lecture-hall.jpeg','https://ontour.admissions.purdue.edu/daily-visits/','https://www.roadschool.purdue.edu/maps/2024%20Class%20of%201950%20Lecture%20Hall.pdf']},indent=2))
print('SAVED',len(c.all_objects),'seats',seat_count)
