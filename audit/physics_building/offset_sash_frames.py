import bpy
from mathutils import Vector
from pathlib import Path
root=Path.cwd(); path=root/'modular/buildings/physics_building_phys_3bf42f3.blend'
bpy.ops.wm.open_mainfile(filepath=str(path)); asset=bpy.data.collections['Asset_physics_building']
obj=bpy.data.objects['PHYS R2 | tall divided sash frames']; mesh=obj.data
# Our mesh is built from repeated 8-vertex prism chunks. Move each chunk to the exterior side,
# using its position relative to the GIS building's local center.
for start in range(0,len(mesh.vertices),8):
    group=mesh.vertices[start:start+8]
    c=sum((v.co for v in group),Vector())/8
    outward=Vector((c.x,c.y,0))
    if outward.length: outward.normalize()
    for v in group: v.co += outward*.34
mesh.update(); obj['placement_note']='Sash bars sit on the exterior glass plane; corrected to follow outward GIS radial direction.'
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
print('Moved sash frames exterior-side:',len(mesh.vertices),'vertices')
