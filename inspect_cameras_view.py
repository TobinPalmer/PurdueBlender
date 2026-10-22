import bpy
import mathutils

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
scene = bpy.context.scene

cams = [
    "Cam_97_HAAS_East_MemorialSteps_Hero",
    "Cam_98_HAAS_1903_Memorial_Rotunda_Interior",
    "Cam_99_HAAS_CS_Commons_Interior",
    "Cam_100_HAAS_Faculty_Seminar_Interior",
    "Cam_101_HAAS_Precinct_Aerial"
]

depsgraph = bpy.context.evaluated_depsgraph_get()

for cname in cams:
    cam = bpy.data.objects.get(cname)
    if not cam:
        continue
    mat = cam.matrix_world
    origin = mat.translation
    fwd = -(mat.to_3x3() @ mathutils.Vector((0, 0, 1))).normalized()
    
    print(f"\n--- {cname} ---")
    print(f"Origin: {origin}")
    print(f"Forward: {fwd}")
    
    # Raycast 50m forward
    hit, loc, norm, index, obj, matrix = scene.ray_cast(depsgraph, origin, fwd)
    if hit:
        dist = (loc - origin).length
        cname_hit = obj.users_collection[0].name if obj.users_collection else "None"
        print(f"Direct Hit: {obj.name} (collection: {cname_hit}) at distance {dist:.2f}m, loc {loc}")
    else:
        print("No direct hit within view.")
