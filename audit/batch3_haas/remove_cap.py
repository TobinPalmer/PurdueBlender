import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
p=Path('C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/felix_haas_hall.blend');o=bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope'];bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();cut=[]
for f in list(bm.faces):
    co=[o.matrix_world@v.co for v in f.verts]
    if f.normal.z>.99 and all(abs(v.z-11.5)<.001 for v in co):cut.append(f)
for f in cut:bm.faces.remove(f)
bm.to_mesh(o.data);bm.free();o.data.update();o['edit_note']='Removed GIS shell horizontal roof cap so the independently modeled roof is visible; footprint walls retained.'
bpy.ops.wm.save_as_mainfile(filepath=str(p))
Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/topology_fix.json').write_text(json.dumps({'removed_upward_top_faces':len(cut),'retained_shell_faces':len(o.data.polygons),'expected_roof_base_z':11.7,'shell_footprint_and_walls':'retained'},indent=2))
