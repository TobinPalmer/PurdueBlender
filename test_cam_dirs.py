import bpy
import mathutils
import math

for cname in ['Cam_97_HAAS_East_MemorialSteps_Hero', 'Cam_98_HAAS_1903_Memorial_Rotunda_Interior', 'Cam_99_HAAS_CS_Commons_Interior', 'Cam_100_HAAS_Faculty_Seminar_Interior', 'Cam_101_HAAS_Precinct_Aerial']:
    cam = bpy.data.objects.get(cname)
    if cam:
        mat = cam.matrix_world
        # Camera look direction is -Z of its orientation matrix
        fwd = -(mat.to_3x3() @ mathutils.Vector((0, 0, 1)))
        print(f"{cname}:")
        print(f"  loc = {cam.location}")
        print(f"  forward dir = {fwd.normalized()}")
