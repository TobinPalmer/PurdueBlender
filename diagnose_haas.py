import bpy
import math

print("=== DIAGNOSING OBJECTS NEAR HAAS ===")
for o in bpy.data.objects:
    if o.type == 'MESH':
        loc = o.matrix_world.translation
        if abs(loc.x - (-190)) < 30 and abs(loc.y - (-64)) < 30:
            cname = o.users_collection[0].name if o.users_collection else "None"
            if not cname.startswith("63_") and not cname.startswith("64_") and not cname.startswith("65_"):
                print(f"Other object: {o.name} in collection {cname} at {loc}")

print("=== CHECKING ROTUNDA AND FLOORS ===")
for o in bpy.data.objects:
    if "Rotunda" in o.name or "Commons" in o.name or "Seminar" in o.name:
        loc = o.matrix_world.translation
        print(f"{o.name}: world loc = {loc}, scale = {o.dimensions}")

print("=== CHECKING CAMERAS ===")
for cname in ['Cam_97_HAAS_East_MemorialSteps_Hero', 'Cam_98_HAAS_1903_Memorial_Rotunda_Interior', 'Cam_99_HAAS_CS_Commons_Interior', 'Cam_100_HAAS_Faculty_Seminar_Interior', 'Cam_101_HAAS_Precinct_Aerial']:
    cam = bpy.data.objects.get(cname)
    if cam:
        loc = cam.matrix_world.translation
        rot = [round(math.degrees(r), 1) for r in cam.rotation_euler]
        print(f"{cname}: world loc = {loc}, rot = {rot}")
