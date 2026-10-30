"""Open the saved PMU in the foreground for visual inspection; never save it."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/purdue_memorial_union.blend'))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=False
            space.shading.show_shadows=True;space.shading.show_cavity=True
            space.region_3d.view_location=(10,5,8);space.region_3d.view_distance=145
            space.region_3d.view_rotation=Vector((110,-160,100)).to_track_quat('Z','Y');space.region_3d.view_perspective='ORTHO'
print('PMU saved exterior preview opened; file has not been saved or changed.')
